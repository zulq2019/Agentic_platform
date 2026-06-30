"""Shared FastAPI application factory for PI-01 platform services."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Protocol

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.responses import Response

from aep_common.dependencies import check_kafka, check_postgres, check_redis
from aep_common.health import create_health_router
from aep_common.logging import (
    bind_correlation_from_headers,
    clear_correlation_ids,
    get_logger,
)
from aep_common.metrics import create_service_metrics, metrics_endpoint
from aep_common.tracing import (
    configure_tracing,
    instrument_fastapi,
    shutdown_tracing,
)

__all__ = ["PlatformServiceSettings", "create_platform_app"]


class PlatformServiceSettings(Protocol):
    service_name: str
    service_version: str
    contract_version: str
    environment: str
    host: str
    port: int
    postgres_dsn: str
    kafka_bootstrap_servers: str
    redis_url: str
    otel_exporter_otlp_endpoint: str


def create_platform_app(settings: PlatformServiceSettings) -> FastAPI:
    """Create a standard platform service FastAPI app with health, metrics, and info."""
    logger = get_logger(settings.service_name)
    requests_total, request_duration = create_service_metrics(settings.service_name)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        tracing_active = configure_tracing(
            service_name=settings.service_name,
            environment=settings.environment,
            otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        )
        if tracing_active:
            logger.info(
                "tracing_configured", endpoint=settings.otel_exporter_otlp_endpoint
            )
        logger.info("service_starting")
        yield
        shutdown_tracing()
        logger.info("service_stopped")

    app = FastAPI(
        title=settings.service_name,
        version=settings.service_version,
        lifespan=lifespan,
    )

    health_router = create_health_router(
        {
            "database": lambda: check_postgres(settings.postgres_dsn),
            "kafka": lambda: check_kafka(settings.kafka_bootstrap_servers),
            "redis": lambda: check_redis(settings.redis_url),
        }
    )
    app.include_router(health_router)

    @app.get("/metrics")
    async def metrics(request: Request) -> Response:
        return await metrics_endpoint(request)

    @app.get("/info")
    async def info() -> dict[str, str]:
        return {
            "service": settings.service_name,
            "version": settings.service_version,
            "contract_version": settings.contract_version,
            "environment": settings.environment,
        }

    @app.middleware("http")
    async def bind_request_correlation(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        bind_correlation_from_headers(request.headers)
        try:
            return await call_next(request)
        finally:
            clear_correlation_ids()

    @app.middleware("http")
    async def record_metrics(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path.startswith("/health"):
            return await call_next(request)
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        requests_total.labels(
            service=settings.service_name,
            method=request.method,
            status=str(response.status_code),
        ).inc()
        request_duration.labels(
            service=settings.service_name, method=request.method
        ).observe(duration)
        return response

    instrument_fastapi(app)
    return app
