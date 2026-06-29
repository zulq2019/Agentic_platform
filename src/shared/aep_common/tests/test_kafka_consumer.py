"""Unit tests for Kafka consumer DLQ routing. Story: US-01.03."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from aep_common.kafka.consumer import EventConsumer


class FakeKafkaMessage:
    def __init__(self, *, topic: str, value: bytes | None) -> None:
        self._topic = topic
        self._value = value

    def value(self) -> bytes | None:
        return self._value

    def topic(self) -> str:
        return self._topic

    def error(self):
        return None


class FakeConsumer:
    def __init__(self, message: FakeKafkaMessage | None) -> None:
        self._message = message
        self.committed: list[FakeKafkaMessage | None] = []
        self.produced: list[tuple[str, bytes]] = []

    def poll(self, timeout: float = 1.0):
        message = self._message
        self._message = None
        return message

    def commit(self, message=None, asynchronous: bool = False) -> None:
        self.committed.append(message)

    def produce(self, topic: str, value: bytes, *, key: bytes | None = None) -> None:
        self.produced.append((topic, value))

    def flush(self, timeout: float = 10) -> int:
        return 0


def _valid_envelope_bytes() -> bytes:
    payload = {
        "event_id": str(uuid4()),
        "event_type": "TaskCreated",
        "timestamp": datetime.now(UTC).isoformat(),
        "task_id": str(uuid4()),
        "workflow_run_id": str(uuid4()),
        "tenant_id": "tenant-acme-corp",
        "emitted_by": "orchestrator-service",
        "payload": {},
    }
    return json.dumps(payload).encode("utf-8")


@pytest.mark.story_us_01_03
def test_ac_01_02_consumer_routes_invalid_envelope_to_dlq_and_commits():
    """
    AC-01.02: Consumer rejects invalid envelope to DLQ and commits offset.
    """
    message = FakeKafkaMessage(
        topic="aep.task.created",
        value=b'{"event_type":"TaskCreated"}',
    )
    fake = FakeConsumer(message)
    handled: list[str] = []

    consumer = EventConsumer(
        fake,
        service_name="agent-runtime",
        handler=lambda envelope: handled.append(envelope.event_type),
    )

    assert consumer.process_next() is True
    assert handled == []
    assert fake.produced
    assert fake.produced[0][0] == "aep.dlq"
    assert fake.committed == [message]


@pytest.mark.story_us_01_03
def test_consumer_invokes_handler_for_valid_envelope():
    message = FakeKafkaMessage(topic="aep.task.created", value=_valid_envelope_bytes())
    fake = FakeConsumer(message)
    handled: list[str] = []

    consumer = EventConsumer(
        fake,
        service_name="agent-runtime",
        handler=lambda envelope: handled.append(envelope.event_type),
    )

    assert consumer.process_next() is True
    assert handled == ["TaskCreated"]
    assert fake.committed == [message]


@pytest.mark.story_us_01_03
def test_consumer_returns_false_when_poll_is_idle():
    fake = FakeConsumer(None)
    consumer = EventConsumer(
        fake,
        service_name="agent-runtime",
        handler=lambda _env: None,
    )
    assert consumer.process_next() is False


@pytest.mark.story_us_01_03
def test_consumer_returns_false_when_message_has_error():
    message = FakeKafkaMessage(topic="aep.task.created", value=_valid_envelope_bytes())
    message.error = lambda: "broker error"  # type: ignore[method-assign]
    fake = FakeConsumer(message)
    consumer = EventConsumer(
        fake,
        service_name="agent-runtime",
        handler=lambda _env: None,
    )
    assert consumer.process_next() is False


@pytest.mark.story_us_01_03
def test_consumer_commits_tombstone_messages_without_dlq():
    message = FakeKafkaMessage(topic="aep.task.created", value=None)
    fake = FakeConsumer(message)
    consumer = EventConsumer(
        fake,
        service_name="agent-runtime",
        handler=lambda _env: None,
    )
    assert consumer.process_next() is True
    assert fake.produced == []
    assert fake.committed == [message]


@pytest.mark.story_us_01_03
def test_consumer_skips_duplicate_event_id_without_calling_handler():
    raw = _valid_envelope_bytes()
    message = FakeKafkaMessage(topic="aep.task.created", value=raw)
    fake = FakeConsumer(message)
    import json

    event_id = json.loads(raw.decode("utf-8"))["event_id"]
    handled: list[str] = []

    consumer = EventConsumer(
        fake,
        service_name="agent-runtime",
        handler=lambda envelope: handled.append(str(envelope.event_id)),
        processed_event_ids={event_id},
    )

    assert consumer.process_next() is True
    assert handled == []
    assert fake.committed == [message]


@pytest.mark.story_us_01_03
def test_consumer_routes_handler_failure_to_dlq_and_commits():
    message = FakeKafkaMessage(topic="aep.task.created", value=_valid_envelope_bytes())
    fake = FakeConsumer(message)

    def _fail(_envelope):
        raise RuntimeError("processing failed")

    consumer = EventConsumer(
        fake,
        service_name="agent-runtime",
        handler=_fail,
    )

    assert consumer.process_next() is True
    assert fake.produced[0][0] == "aep.dlq"
    assert fake.committed == [message]
