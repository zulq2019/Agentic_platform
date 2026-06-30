"""Unit tests for Kafka producer DLQ routing. Story: US-01.03."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from aep_common.kafka.envelope import EventEnvelope
from aep_common.kafka.producer import EventProducer


class FakeProducer:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bytes, bytes | None]] = []

    def produce(
        self,
        topic: str,
        value: bytes,
        *,
        key: bytes | None = None,
        on_delivery=None,
    ) -> None:
        self.messages.append((topic, value, key))

    def flush(self, timeout: float = 10) -> int:
        return 0


@pytest.mark.story_us_01_03
def test_ac_01_02_producer_routes_invalid_envelope_to_dlq():
    """
    AC-01.02: Invalid envelope at publish time is rejected to DLQ with error logged.
    """
    fake = FakeProducer()
    producer = EventProducer(fake, service_name="orchestrator-service")

    producer.publish("aep.task.created", {"event_type": "TaskCreated"})

    assert len(fake.messages) == 1
    topic, payload, _key = fake.messages[0]
    assert topic == "aep.dlq"
    assert b"original_topic" in payload
    assert b"aep.task.created" in payload


@pytest.mark.story_us_01_03
def test_producer_publishes_valid_envelope_to_target_topic():
    fake = FakeProducer()
    producer = EventProducer(fake, service_name="orchestrator-service")
    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="TaskCreated",
        timestamp=datetime.now(UTC),
        task_id=uuid4(),
        workflow_run_id=uuid4(),
        tenant_id="tenant-acme-corp",
        emitted_by="orchestrator-service",
        payload={"step": "coding"},
    )

    producer.publish("aep.task.created", envelope)

    assert len(fake.messages) == 1
    topic, _payload, key = fake.messages[0]
    assert topic == "aep.task.created"
    assert key == b"tenant-acme-corp"
