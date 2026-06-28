"""Failure mode tests for US-01.01 readiness probes."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from services import PYTHON_SERVICES, load_service_app


@pytest.fixture
def auth_app():
    service = next(s for s in PYTHON_SERVICES if s["name"] == "auth-service")
    return load_service_app(service)


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_ac_01_02_multiple_dependencies_down_all_identified(auth_app):
    """
    AC-01.01: Each failing dependency must appear in the checks map — not just
    the first failure. Operators need full visibility to diagnose outages.
    """
    with (
        patch("auth_service.main.check_postgres", new=AsyncMock(return_value="error")),
        patch("auth_service.main.check_kafka", new=AsyncMock(return_value="error")),
        patch("auth_service.main.check_redis", new=AsyncMock(return_value="ok")),
    ):
        transport = ASGITransport(app=auth_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/ready")

    assert response.status_code == 503
    checks = response.json()["checks"]
    assert checks["database"] == "error"
    assert checks["kafka"] == "error"
    assert checks["redis"] == "ok"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_ac_01_02_redis_failure_identified_in_ready_response(auth_app):
    with (
        patch("auth_service.main.check_postgres", new=AsyncMock(return_value="ok")),
        patch("auth_service.main.check_kafka", new=AsyncMock(return_value="ok")),
        patch("auth_service.main.check_redis", new=AsyncMock(return_value="error")),
    ):
        transport = ASGITransport(app=auth_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["checks"]["redis"] == "error"
