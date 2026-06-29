"""Event envelope model and validation (contracts/event-envelope.schema.json)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from aep_common.kafka.exceptions import EventEnvelopeValidationError

EventType = Literal[
    "TaskCreated",
    "AgentStarted",
    "AgentCompleted",
    "AgentFailed",
    "ApprovalRequested",
    "ApprovalGranted",
    "ApprovalDenied",
    "StateTransitioned",
    "RollbackTriggered",
]

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[5] / "contracts" / "event-envelope.schema.json"
)


class EventEnvelope(BaseModel):
    """Platform event envelope — every Kafka message must conform."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    event_id: UUID
    event_type: EventType
    timestamp: datetime
    task_id: UUID
    workflow_run_id: UUID
    tenant_id: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    emitted_by: str = Field(min_length=1)
    payload: dict[str, Any]

    @field_validator("payload")
    @classmethod
    def payload_must_be_object(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("payload must be an object")
        return value


def load_event_schema() -> dict[str, Any]:
    with _SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_envelope_dict(message: dict[str, Any]) -> EventEnvelope:
    """Validate a raw dict against the EventEnvelope contract."""
    try:
        envelope = EventEnvelope.model_validate(message)
    except Exception as exc:
        raise EventEnvelopeValidationError(str(exc)) from exc

    try:
        import jsonschema
    except ImportError:
        return envelope

    schema = load_event_schema()
    try:
        jsonschema.validate(instance=message, schema=schema)
    except jsonschema.ValidationError as exc:
        raise EventEnvelopeValidationError(exc.message) from exc

    return envelope


def parse_envelope_bytes(raw: bytes) -> EventEnvelope:
    """Deserialize and validate Kafka message bytes."""
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EventEnvelopeValidationError(f"invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise EventEnvelopeValidationError("envelope must be a JSON object")

    return validate_envelope_dict(data)


def envelope_to_bytes(envelope: EventEnvelope) -> bytes:
    """Serialize a validated envelope for Kafka."""
    payload = envelope.model_dump(mode="json")
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")
