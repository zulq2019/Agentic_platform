"""Integration tests for US-01.03 — Kafka topology and round-trip."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[3]


def kafka_topology_ready() -> bool:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_kafka_topology.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0


@pytest.fixture
def requires_kafka():
    if not kafka_topology_ready():
        pytest.skip("Kafka topology not ready — run make dev-up first")


@pytest.mark.story_us_01_03
@pytest.mark.integration
def test_ac_01_02_verify_kafka_topology_script_exits_zero(requires_kafka):
    """AC-01.02: verify_kafka_topology.py confirms topics + DLQ configuration."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_kafka_topology.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "DLQ" in result.stdout


@pytest.mark.story_us_01_03
@pytest.mark.integration
def test_ac_01_02_kafka_round_trip_produce_consume_ack(requires_kafka):
    """
    AC-01.02 / DoD: Produce → consume → ack with valid EventEnvelope.
    """
    from confluent_kafka import Consumer, Producer

    topic = "aep.audit.event"
    group_id = f"us-01-03-roundtrip-{uuid4()}"
    payload = {
        "event_id": str(uuid4()),
        "event_type": "TaskCreated",
        "timestamp": datetime.now(UTC).isoformat(),
        "task_id": str(uuid4()),
        "workflow_run_id": str(uuid4()),
        "tenant_id": "tenant-test",
        "emitted_by": "orchestrator-service",
        "payload": {"integration": True},
    }

    producer = Producer({"bootstrap.servers": "localhost:9094"})
    consumer = Consumer(
        {
            "bootstrap.servers": "localhost:9094",
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([topic])

    producer.produce(topic, json.dumps(payload).encode("utf-8"), key=b"tenant-test")
    producer.flush(10)

    deadline = time.time() + 20
    received = None
    while time.time() < deadline:
        message = consumer.poll(1.0)
        if message is None or message.error():
            continue
        if message.value() is None:
            continue
        candidate = json.loads(message.value().decode("utf-8"))
        if candidate.get("event_id") == payload["event_id"]:
            received = candidate
            consumer.commit(message)
            break

    assert received is not None, "did not receive produced event within timeout"
    assert received["event_id"] == payload["event_id"]
    consumer.close()
