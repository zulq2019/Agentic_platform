"""Unit tests for Kafka provisioning scripts. Story: US-01.03."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aep_common.kafka.topic_catalog import TOPIC_SPECS, topic_names

ROOT = Path(__file__).resolve().parents[3]


def _load_script(name: str, path: str):
    script_path = ROOT / path
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.story_us_01_03
def test_topic_names_returns_all_catalog_entries():
    assert len(topic_names()) == len(TOPIC_SPECS)


@pytest.mark.story_us_01_03
def test_provision_topics_creates_missing_topics():
    module = _load_script("provision_kafka_topics", "scripts/provision_kafka_topics.py")

    topic_meta = MagicMock()
    topic_meta.error = None
    topic_meta.partitions = {0: MagicMock(replicas=[0])}

    metadata = MagicMock()
    metadata.topics = {}

    mock_admin = MagicMock()
    mock_admin.list_topics.return_value = metadata
    mock_future = MagicMock()
    mock_future.result.return_value = None
    mock_admin.create_topics.return_value = {
        spec.name: mock_future for spec in TOPIC_SPECS
    }

    with patch("confluent_kafka.admin.AdminClient", return_value=mock_admin):
        module.provision_topics(bootstrap_servers="localhost:9094")

    mock_admin.create_topics.assert_called_once()
    created = mock_admin.create_topics.call_args[0][0]
    assert len(created) == len(TOPIC_SPECS)


@pytest.mark.story_us_01_03
def test_verify_acl_catalog_flags_unknown_topic_references(tmp_path):
    module = _load_script("verify_kafka_topology", "scripts/verify_kafka_topology.py")
    bad_acl = tmp_path / "acls.yaml"
    bad_acl.write_text("acls:\n  - topics: [unknown.topic]\n", encoding="utf-8")

    with patch.object(module, "ACL_CATALOG", bad_acl):
        errors = module.verify_acl_catalog()

    assert any("unknown topic" in error for error in errors)


@pytest.mark.story_us_01_03
def test_verify_topics_flags_partition_mismatch():
    module = _load_script("verify_kafka_topology", "scripts/verify_kafka_topology.py")
    spec = TOPIC_SPECS[0]

    topic_meta = MagicMock()
    topic_meta.error = None
    topic_meta.partitions = {0: MagicMock(replicas=[0])}

    metadata = MagicMock()
    metadata.topics = {spec.name: topic_meta}

    mock_admin = MagicMock()
    mock_admin.list_topics.return_value = metadata

    with patch("confluent_kafka.admin.AdminClient", return_value=mock_admin):
        errors = module.verify_topics(bootstrap_servers="localhost:9094")

    assert any("expected" in error and spec.name in error for error in errors)
