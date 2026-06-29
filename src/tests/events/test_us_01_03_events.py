"""Event flow tests for US-01.03 — Kafka envelope and DLQ routing."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from aep_common.kafka.consumer import EventConsumer
from aep_common.kafka.dlq import build_dlq_record, dlq_record_to_bytes, dlq_topic_name
from aep_common.kafka.envelope import envelope_to_bytes, parse_envelope_bytes
from aep_common.kafka.producer import EventProducer
from aep_common.kafka.topic_catalog import DLQ_TOPIC, topic_names


class RecordingProducer:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bytes, bytes | None]] = []

    def produce(self, topic, value, *, key=None, on_delivery=None):
        self.messages.append((topic, value, key))

    def flush(self, timeout: float = 10) -> int:
        return 0


class SingleMessageConsumer:
    def __init__(self, topic: str, value: bytes) -> None:
        self._pending = _FakeMessage(topic, value)
        self.produced: list[tuple[str, bytes]] = []
        self.committed = 0

    def poll(self, timeout: float = 1.0):
        if self._pending is None:
            return None
        message = self._pending
        self._pending = None
        return message

    def commit(self, message=None, asynchronous: bool = False) -> None:
        self.committed += 1

    def produce(self, topic: str, value: bytes, *, key=None) -> None:
        self.produced.append((topic, value))

    def flush(self, timeout: float = 10) -> int:
        return 0


class _FakeMessage:
    def __init__(self, topic: str, value: bytes) -> None:
        self._topic = topic
        self._value = value

    def value(self):
        return self._value

    def topic(self):
        return self._topic

    def error(self):
        return None


@pytest.mark.story_us_01_03
def test_ac_01_02_invalid_publish_never_reaches_business_topic():
    """
    AC-01.02: Invalid envelope at publish time is routed to DLQ, not the target topic.
    """
    producer = RecordingProducer()
    event_producer = EventProducer(producer, service_name="orchestrator-service")

    event_producer.publish("aep.task.created", {"event_type": "TaskCreated"})

    assert all(topic != "aep.task.created" for topic, _, _ in producer.messages)
    assert producer.messages[0][0] == DLQ_TOPIC


@pytest.mark.story_us_01_03
def test_ac_01_02_valid_envelope_round_trips_through_bytes_serialization():
    """Valid envelope survives serialize → deserialize for Kafka transport."""
    from aep_common.kafka.envelope import EventEnvelope

    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="AgentStarted",
        timestamp=datetime.now(UTC),
        task_id=uuid4(),
        workflow_run_id=uuid4(),
        tenant_id="tenant-test",
        emitted_by="agent-runtime",
        payload={"agent_id": "coding-agent-v1"},
    )
    restored = parse_envelope_bytes(envelope_to_bytes(envelope))
    assert restored.event_id == envelope.event_id
    assert restored.event_type == "AgentStarted"


@pytest.mark.story_us_01_03
def test_dlq_record_preserves_original_topic_and_error_context():
    record = build_dlq_record(
        original_topic="aep.task.created",
        error="missing task_id",
        raw_message=b'{"event_type":"TaskCreated"}',
        tenant_id="tenant-test",
        task_id=None,
    )
    decoded = json.loads(dlq_record_to_bytes(record).decode("utf-8"))
    assert decoded["original_topic"] == "aep.task.created"
    assert decoded["error"] == "missing task_id"
    assert decoded["tenant_id"] == "tenant-test"


@pytest.mark.story_us_01_03
def test_topic_catalog_lists_twelve_platform_topics():
    names = topic_names()
    assert len(names) == 12
    assert dlq_topic_name() in names


@pytest.mark.story_us_01_03
def test_consumer_dlq_for_non_json_payload():
    consumer_backend = SingleMessageConsumer("aep.audit.event", b"not-json")
    consumer = EventConsumer(
        consumer_backend,
        service_name="audit-service",
        handler=lambda _env: None,
    )

    assert consumer.process_next() is True
    assert consumer_backend.produced[0][0] == DLQ_TOPIC
