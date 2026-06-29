"""Kafka event bus exceptions."""

from __future__ import annotations


class EventEnvelopeValidationError(ValueError):
    """Raised when an event message fails EventEnvelope validation."""
