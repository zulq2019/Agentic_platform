"""Unit tests for aep_common platform app factory."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_settings import BaseSettings, SettingsConfigDict

from aep_common.app import create_platform_app


class _TestSettings(BaseSettings):
    service_name: str = "test-service"
    service_version: str = "0.1.0"
    contract_version: str = "1.0.0"
    environment: str = "test"
    host: str = "0.0.0.0"
    port: int = 8999
    postgres_dsn: str = ""
    kafka_bootstrap_servers: str = "kafka:9092"
    redis_url: str = "redis://redis:6379/0"
    otel_exporter_otlp_endpoint: str = ""

    model_config = SettingsConfigDict(extra="ignore")


@pytest.mark.asyncio
async def test_create_platform_app_exposes_standard_endpoints():
    settings = _TestSettings()
    app = create_platform_app(settings)

    with (
        patch("aep_common.app.check_postgres", new=AsyncMock(return_value="ok")),
        patch("aep_common.app.check_kafka", new=AsyncMock(return_value="ok")),
        patch("aep_common.app.check_redis", new=AsyncMock(return_value="ok")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            live = await client.get("/health/live")
            ready = await client.get("/health/ready")
            metrics = await client.get("/metrics")
            info = await client.get("/info")

    assert live.status_code == 200
    assert ready.status_code == 200
    assert metrics.status_code == 200
    assert info.status_code == 200
    assert info.json()["service"] == "test-service"
