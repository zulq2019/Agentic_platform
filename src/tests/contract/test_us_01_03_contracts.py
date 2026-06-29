"""Contract tests for US-01.03 — EventEnvelope schema compliance."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import jsonschema
import pytest

from aep_common.kafka.envelope import (
    EventEnvelope,
    load_event_schema,
    validate_envelope_dict,
)

ROOT = Path(__file__).resolve().parents[3]


def _valid_envelope_dict() -> dict:
    return {
        "event_id": str(uuid4()),
        "event_type": "TaskCreated",
        "timestamp": datetime.now(UTC).isoformat(),
        "task_id": str(uuid4()),
        "workflow_run_id": str(uuid4()),
        "tenant_id": "tenant-acme-corp",
        "emitted_by": "orchestrator-service",
        "payload": {"step": "coding"},
    }


@pytest.mark.story_us_01_03
def test_ac_01_02_valid_envelope_validates_against_contract_schema():
    """
    AC-01.02: Valid platform events must conform to event-envelope.schema.json.
    """
    message = _valid_envelope_dict()
    schema = load_event_schema()
    jsonschema.validate(instance=message, schema=schema)
    envelope = validate_envelope_dict(message)
    assert isinstance(envelope, EventEnvelope)


@pytest.mark.story_us_01_03
def test_ac_01_02_contract_schema_file_exists_at_repo_root():
    schema_path = ROOT / "contracts" / "event-envelope.schema.json"
    assert schema_path.is_file()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "event_id" in schema["properties"]
    assert "TaskCreated" in schema["properties"]["event_type"]["enum"]


@pytest.mark.story_us_01_03
def test_agent_failed_payload_requires_error_fields_per_contract():
    """Contract allOf: AgentFailed payload must include error_code and retry_count."""
    message = _valid_envelope_dict()
    message["event_type"] = "AgentFailed"
    message["payload"] = {"error_message": "timeout"}

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=message, schema=load_event_schema())
