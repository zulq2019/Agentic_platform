"""Unit tests for aep_common OpenTelemetry tracing. Story: US-01.07."""

from __future__ import annotations

import pytest

from aep_common.tracing import (
    _NoOpTracer,
    configure_tracing,
    get_tracer,
    instrument_fastapi,
    reset_tracing_for_tests,
    shutdown_tracing,
)


@pytest.fixture(autouse=True)
def _reset_tracing_state():
    reset_tracing_for_tests()
    yield
    reset_tracing_for_tests()


@pytest.mark.story_us_01_07
def test_ac_1_configure_tracing_returns_false_without_endpoint(monkeypatch):
    """
    US-01.07: Given no OTLP endpoint, when tracing is configured,
    then the SDK remains inactive (safe local/CI default).
    """
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    monkeypatch.delenv("OTEL_SDK_DISABLED", raising=False)

    assert (
        configure_tracing(
            service_name="auth-service",
            environment="test",
            otlp_endpoint="",
        )
        is False
    )


@pytest.mark.story_us_01_07
def test_ac_2_configure_tracing_returns_false_when_sdk_disabled(monkeypatch):
    """
    US-01.07: Given OTEL_SDK_DISABLED=true, when tracing is configured,
    then export is not activated.
    """
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")

    assert (
        configure_tracing(
            service_name="auth-service",
            environment="test",
            otlp_endpoint="http://otel-collector:4317",
        )
        is False
    )


@pytest.mark.story_us_01_07
def test_ac_3_get_tracer_returns_noop_without_sdk():
    """
    US-01.07: Given OpenTelemetry is unavailable, when get_tracer is called,
    then a no-op tracer is returned so callers do not crash.
    """
    from unittest.mock import patch

    with patch.dict(
        "sys.modules", {"opentelemetry": None, "opentelemetry.trace": None}
    ):
        tracer = get_tracer("test.module")

    assert isinstance(tracer, _NoOpTracer)


@pytest.mark.story_us_01_07
def test_configure_tracing_activates_with_otlp_endpoint():
    """
    US-01.07: Given OTLP endpoint and SDK installed, when tracing is configured,
    then the tracer provider is active.
    """
    assert (
        configure_tracing(
            service_name="orchestrator-service",
            environment="test",
            otlp_endpoint="http://127.0.0.1:4317",
        )
        is True
    )
    shutdown_tracing()


@pytest.mark.story_us_01_07
def test_instrument_fastapi_returns_false_when_package_missing():
    """Edge case: missing instrumentation package must not crash app startup."""
    from unittest.mock import patch

    with patch.dict("sys.modules", {"opentelemetry.instrumentation.fastapi": None}):
        assert instrument_fastapi(object()) is False


@pytest.mark.story_us_01_07
def test_instrument_fastapi_returns_true_for_fastapi_app():
    """US-01.07: Given a FastAPI app, when instrumented, then OTEL hooks are attached."""
    from fastapi import FastAPI

    app = FastAPI()
    assert instrument_fastapi(app) is True
    assert getattr(app, "_is_instrumented_by_opentelemetry", False) is True


@pytest.mark.story_us_01_07
def test_kafka_span_uses_shared_tracer():
    from aep_common.kafka.tracing import kafka_span

    with kafka_span(
        "kafka.test", topic="aep.task.created", service="task-engine"
    ) as span:
        span.set_attribute("probe", "ok")
