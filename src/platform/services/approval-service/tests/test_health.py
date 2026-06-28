from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from approval_service.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_health_live_returns_200(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_ready_returns_200_when_dependencies_ok(app):
    with (
        patch("approval_service.main.check_postgres", new=AsyncMock(return_value="ok")),
        patch("approval_service.main.check_kafka", new=AsyncMock(return_value="ok")),
        patch("approval_service.main.check_redis", new=AsyncMock(return_value="ok")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"


@pytest.mark.asyncio
async def test_health_ready_returns_503_when_database_down(app):
    with (
        patch("approval_service.main.check_postgres", new=AsyncMock(return_value="error")),
        patch("approval_service.main.check_kafka", new=AsyncMock(return_value="ok")),
        patch("approval_service.main.check_redis", new=AsyncMock(return_value="ok")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "error"


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_prometheus_format(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/metrics")
    assert response.status_code == 200
    assert "aep_http_requests_total" in response.text


@pytest.mark.asyncio
async def test_info_endpoint_returns_metadata(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/info")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "approval-service"
    assert body["version"] == "0.1.0"
