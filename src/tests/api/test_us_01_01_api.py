"""API tests for US-01.01 standard service endpoints.

All 15 Python services are generated from an identical scaffold template
(scripts/scaffold_pi01_services.py). auth-service is the reference implementation;
integration tests verify all 16 running services against docker compose.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from services import load_service_app, PYTHON_SERVICES


@pytest.fixture
def auth_app():
    service = next(s for s in PYTHON_SERVICES if s["name"] == "auth-service")
    return load_service_app(service)


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_ac_01_01_health_live_returns_200(auth_app):
    """
    AC-01.01: Scaffolded services expose GET /health/live returning 200 OK.
    """
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_ac_01_02_health_ready_returns_503_with_failing_check_identified(auth_app):
    """
    AC-01.01: When a dependency is down, /health/ready returns 503 and names the
    failing check in the response body.
    """
    with (
        patch("auth_service.main.check_postgres", new=AsyncMock(return_value="error")),
        patch("auth_service.main.check_kafka", new=AsyncMock(return_value="ok")),
        patch("auth_service.main.check_redis", new=AsyncMock(return_value="ok")),
    ):
        transport = ASGITransport(app=auth_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "error"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_metrics_endpoint_exposes_prometheus_counters(auth_app):
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert "aep_http_requests_total" in response.text


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_info_endpoint_returns_service_metadata(auth_app):
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/info")

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "auth-service"
    assert body["version"] == "0.1.0"
    assert body["contract_version"] == "1.0.0"
    assert "environment" in body
