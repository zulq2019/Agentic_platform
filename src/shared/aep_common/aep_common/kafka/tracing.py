"""Optional OpenTelemetry tracing for kafka helpers (no-op when SDK absent)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from aep_common.tracing import get_tracer


@contextmanager
def kafka_span(name: str, **attributes: Any) -> Iterator[Any]:
    """Start an OTEL span for a Kafka operation."""
    tracer = get_tracer("aep_common.kafka")
    with tracer.start_as_current_span(name) as span:
        for key, value in attributes.items():
            if value is not None:
                span.set_attribute(key, str(value))
        yield span
