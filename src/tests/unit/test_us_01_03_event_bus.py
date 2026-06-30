"""Unit tests for US-01.03 — Event Bus Ready."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

from aep_common.kafka.topic_catalog import DLQ_TOPIC, TOPIC_SPECS, business_topic_count

ROOT = Path(__file__).resolve().parents[3]


def _load_script(name: str, path: str):
    script_path = ROOT / path
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.story_us_01_03
def test_ac_01_02_topic_catalog_defines_eleven_topics_plus_dlq():
    """AC-01.02: Platform provisions 11 business topics plus DLQ."""
    assert business_topic_count() == 11
    names = {spec.name for spec in TOPIC_SPECS}
    assert DLQ_TOPIC in names
    assert len(names) == 12


@pytest.mark.story_us_01_03
def test_docker_compose_includes_kafka_init_container():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "kafka-init:" in compose
    assert "provision_kafka_topics.py" in compose


@pytest.mark.story_us_01_03
def test_makefile_dev_up_verifies_kafka_topology():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "verify_kafka_topology.py" in makefile


@pytest.mark.story_us_01_03
def test_acl_catalog_references_only_known_topics():
    catalog = yaml.safe_load((ROOT / "infra" / "kafka" / "acls.yaml").read_text())
    known = {spec.name for spec in TOPIC_SPECS}
    for entry in catalog["acls"]:
        for topic in entry["topics"]:
            assert topic in known


@pytest.mark.story_us_01_03
def test_verify_kafka_topology_module_exposes_verify_topology():
    module = _load_script("verify_kafka_topology", "scripts/verify_kafka_topology.py")
    assert callable(module.verify_topology)
    assert callable(module.main)
