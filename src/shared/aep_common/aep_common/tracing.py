"""OpenTelemetry tracing factory and FastAPI instrumentation."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from fastapi import FastAPI

_tracer_provider: object | None = None
_configured = False


class _NoOpSpan:
    def set_attribute(self, key: str, value: Any) -> None:
        return None


class _NoOpTracer:
    def start_as_current_span(
        self, name: str, **kwargs: Any
    ) -> AbstractContextManager[_NoOpSpan]:
        @contextmanager
        def _cm() -> Iterator[_NoOpSpan]:
            yield _NoOpSpan()

        return _cm()


class Span(Protocol):
    def set_attribute(self, key: str, value: Any) -> None: ...


def _sdk_disabled() -> bool:
    return os.getenv("OTEL_SDK_DISABLED", "").lower() in ("true", "1", "yes")


def configure_tracing(
    *,
    service_name: str,
    environment: str,
    otlp_endpoint: str | None = None,
) -> bool:
    """Configure OTLP trace export for the process. Returns True when the SDK is active."""
    global _configured, _tracer_provider
    if _configured:
        return _tracer_provider is not None

    _configured = True
    if _sdk_disabled():
        return False

    raw_endpoint = (
        otlp_endpoint
        if otlp_endpoint is not None
        else os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    )
    endpoint = raw_endpoint.strip()
    if not endpoint:
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        return False

    resource = Resource.create(
        {
            "service.name": service_name,
            "deployment.environment": environment,
        }
    )
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _tracer_provider = provider
    return True


def shutdown_tracing() -> None:
    """Flush and shut down the tracer provider."""
    global _configured, _tracer_provider
    if _tracer_provider is not None:
        shutdown = getattr(_tracer_provider, "shutdown", None)
        if callable(shutdown):
            shutdown()
    _tracer_provider = None
    _configured = False


def get_tracer(name: str) -> Any:
    """Return an OTEL tracer or a no-op tracer when the SDK is unavailable."""
    try:
        from opentelemetry import trace

        return trace.get_tracer(name)
    except ImportError:
        return _NoOpTracer()


def instrument_fastapi(app: FastAPI) -> bool:
    """Auto-instrument a FastAPI app when instrumentation packages are installed."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except ImportError:
        return False

    FastAPIInstrumentor.instrument_app(app)
    return True


def reset_tracing_for_tests() -> None:
    """Reset module state — test helper only."""
    shutdown_tracing()
