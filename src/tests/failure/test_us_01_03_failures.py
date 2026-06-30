"""Failure-mode tests for US-01.03 — Event Bus Ready."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[3]


def _load_script(name: str, path: str):
    script_path = ROOT / path
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.story_us_01_03
def test_verify_kafka_topology_returns_nonzero_when_topics_missing():
    module = _load_script("verify_kafka_topology", "scripts/verify_kafka_topology.py")

    with patch.object(
        module, "verify_topology", return_value=(False, ["missing topic"])
    ):
        assert module.main() == 1


@pytest.mark.story_us_01_03
def test_verify_kafka_topology_returns_zero_when_ok():
    module = _load_script("verify_kafka_topology", "scripts/verify_kafka_topology.py")

    with patch.object(module, "verify_topology", return_value=(True, [])):
        assert module.main() == 0


@pytest.mark.story_us_01_03
def test_provision_kafka_topics_exits_nonzero_on_failure():
    module = _load_script("provision_kafka_topics", "scripts/provision_kafka_topics.py")

    with patch.object(
        module, "provision_topics", side_effect=RuntimeError("broker down")
    ):
        assert module.main() == 1


@pytest.mark.story_us_01_03
def test_verify_topics_reports_unreachable_broker():
    module = _load_script("verify_kafka_topology", "scripts/verify_kafka_topology.py")

    with patch("confluent_kafka.admin.AdminClient") as mock_admin:
        mock_admin.return_value.list_topics.side_effect = OSError("connection refused")
        errors = module.verify_topics(bootstrap_servers="localhost:9094")

    assert any("cannot reach Kafka" in error for error in errors)
