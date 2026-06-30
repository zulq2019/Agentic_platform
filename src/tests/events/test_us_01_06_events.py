"""Event-path tests for US-01.06 shared logging correlation binding."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from aep_common.kafka.consumer import EventConsumer
from aep_common.logging import task_id_var, tenant_id_var, workflow_run_id_var


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
        "task_id": "550e8400-e29b-41d4-a716-446655440010",
        "workflow_run_id": "550e8400-e29b-41d4-a716-446655440011",
        "tenant_id": "tenant-acme-corp",
        "emitted_by": "orchestrator-service",
        "payload": {},
    }
    return json.dumps(payload).encode("utf-8")


@pytest.mark.story_us_01_06
def test_ac_5_consumer_handler_receives_envelope_correlation_context():
    """
    US-01.06: Given a valid Kafka envelope, when the consumer invokes the handler,
    then correlation IDs from the envelope are bound in the handler context.
    """
    message = FakeKafkaMessage(topic="aep.task.created", value=_valid_envelope_bytes())
    fake = FakeConsumer(message)
    captured: list[dict[str, str | None]] = []

    def handler(envelope) -> None:
        captured.append(
            {
                "task_id": task_id_var.get(),
                "workflow_run_id": workflow_run_id_var.get(),
                "tenant_id": tenant_id_var.get(),
            }
        )

    consumer = EventConsumer(
        fake,
        service_name="agent-runtime",
        handler=handler,
    )

    assert consumer.process_next() is True
    assert captured == [
        {
            "task_id": "550e8400-e29b-41d4-a716-446655440010",
            "workflow_run_id": "550e8400-e29b-41d4-a716-446655440011",
            "tenant_id": "tenant-acme-corp",
        }
    ]
    assert task_id_var.get() is None
    assert workflow_run_id_var.get() is None
    assert tenant_id_var.get() is None
