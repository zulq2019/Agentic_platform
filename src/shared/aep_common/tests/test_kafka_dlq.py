"""Unit tests for DLQ helpers. Story: US-01.03."""

from __future__ import annotations

import json

import pytest

from aep_common.kafka.dlq import (
    build_dlq_record,
    dlq_record_to_bytes,
    dlq_topic_name,
)


@pytest.mark.story_us_01_03
def test_build_dlq_record_accepts_string_raw_message():
    record = build_dlq_record(
        original_topic="aep.task.created",
        error="bad payload",
        raw_message='{"partial": true}',
    )
    assert record["raw_message"] == '{"partial": true}'


@pytest.mark.story_us_01_03
def test_build_dlq_record_accepts_dict_raw_message():
    record = build_dlq_record(
        original_topic="aep.task.created",
        error="bad payload",
        raw_message={"event_type": "TaskCreated"},
    )
    assert record["raw_message"]["event_type"] == "TaskCreated"


@pytest.mark.story_us_01_03
def test_dlq_topic_name_matches_catalog():
    assert dlq_topic_name() == "aep.dlq"


@pytest.mark.story_us_01_03
def test_dlq_record_to_bytes_is_valid_json():
    record = build_dlq_record(
        original_topic="aep.audit.event",
        error="test",
        raw_message=None,
    )
    parsed = json.loads(dlq_record_to_bytes(record))
    assert "rejected_at" in parsed
