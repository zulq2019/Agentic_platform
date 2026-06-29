"""Unit tests for EventEnvelope validation. Story: US-01.03."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from aep_common.kafka.envelope import validate_envelope_dict
from aep_common.kafka.exceptions import EventEnvelopeValidationError


def _valid_payload() -> dict:
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
def test_validate_envelope_dict_accepts_valid_message():
    envelope = validate_envelope_dict(_valid_payload())
    assert envelope.event_type == "TaskCreated"
    assert envelope.tenant_id == "tenant-acme-corp"


@pytest.mark.story_us_01_03
def test_validate_envelope_dict_rejects_missing_required_field():
    payload = _valid_payload()
    del payload["task_id"]
    with pytest.raises(EventEnvelopeValidationError):
        validate_envelope_dict(payload)


@pytest.mark.story_us_01_03
def test_validate_envelope_dict_rejects_invalid_tenant_id_pattern():
    payload = _valid_payload()
    payload["tenant_id"] = "INVALID_TENANT"
    with pytest.raises(EventEnvelopeValidationError):
        validate_envelope_dict(payload)


@pytest.mark.story_us_01_03
def test_event_envelope_forbids_extra_fields():
    payload = _valid_payload()
    payload["schema_version"] = "1.0"
    with pytest.raises(EventEnvelopeValidationError):
        validate_envelope_dict(payload)


@pytest.mark.story_us_01_03
def test_parse_envelope_bytes_rejects_invalid_json():
    from aep_common.kafka.envelope import parse_envelope_bytes

    with pytest.raises(EventEnvelopeValidationError, match="invalid JSON"):
        parse_envelope_bytes(b"not-json")


@pytest.mark.story_us_01_03
def test_parse_envelope_bytes_rejects_non_object_json():
    from aep_common.kafka.envelope import parse_envelope_bytes

    with pytest.raises(EventEnvelopeValidationError, match="JSON object"):
        parse_envelope_bytes(b"[1, 2, 3]")


@pytest.mark.story_us_01_03
def test_envelope_to_bytes_round_trip():
    from aep_common.kafka.envelope import envelope_to_bytes, parse_envelope_bytes

    envelope = validate_envelope_dict(_valid_payload())
    restored = parse_envelope_bytes(envelope_to_bytes(envelope))
    assert restored.event_id == envelope.event_id


@pytest.mark.story_us_01_03
def test_load_event_schema_reads_contract_file():
    from aep_common.kafka.envelope import load_event_schema

    schema = load_event_schema()
    assert schema["title"] == "Event Envelope"


@pytest.mark.story_us_01_03
def test_validate_envelope_dict_applies_jsonschema_allof_rules():
    """Pydantic accepts loose payload; jsonschema enforces event-type payload rules."""
    payload = _valid_payload()
    payload["event_type"] = "AgentFailed"
    payload["payload"] = {"error_message": "timeout only"}

    with pytest.raises(EventEnvelopeValidationError):
        validate_envelope_dict(payload)

