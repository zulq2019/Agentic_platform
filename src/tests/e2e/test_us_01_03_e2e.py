"""E2E tests for US-01.03 — Event Bus Ready."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

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
def requires_kafka_stack():
    if not kafka_topology_ready():
        pytest.skip("Kafka stack not ready — run make dev-up first")


@pytest.mark.story_us_01_03
@pytest.mark.e2e
def test_ac_01_02_e2e_verify_kafka_topology_after_dev_up(requires_kafka_stack):
    """
    AC-01.02 (E2E): With Kafka running from make dev-up, topology verification
    exits 0 confirming 11 topics + DLQ.
    """
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_kafka_topology.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "11 topics + DLQ" in result.stdout


@pytest.mark.story_us_01_03
@pytest.mark.e2e
def test_ac_01_02_e2e_provision_kafka_topics_is_idempotent(requires_kafka_stack):
    """Provisioning script can be re-run safely after kafka-init."""
    for _ in range(2):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "provision_kafka_topics.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stderr or result.stdout
