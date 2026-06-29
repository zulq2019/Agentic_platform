"""Optional OpenTelemetry tracing for kafka helpers (no-op when SDK absent)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any


class _NoOpSpan:
    def set_attribute(self, key: str, value: Any) -> None:
        return None


@contextmanager
def kafka_span(name: str, **attributes: Any) -> Iterator[_NoOpSpan]:
    """Start an OTEL span when opentelemetry is installed; otherwise no-op."""
    try:
        from opentelemetry import trace

        tracer = trace.get_tracer("aep_common.kafka")
        with tracer.start_as_current_span(name) as span:
            for key, value in attributes.items():
                if value is not None:
                    span.set_attribute(key, str(value))
            yield span
    except ImportError:
        yield _NoOpSpan()
