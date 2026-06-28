"""Unit tests for aep_common health router. Story: US-01.01."""

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from aep_common.health import create_health_router


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_ac_01_02_readiness_returns_503_and_identifies_database_failure():
    """
    AC-01.01: When a dependency is down, /health/ready returns 503 with the
    failing check identified in the response body.
    """
    router = create_health_router(
        {
            "database": AsyncMock(return_value="error"),
            "kafka": AsyncMock(return_value="ok"),
            "redis": AsyncMock(return_value="ok"),
        }
    )
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "error"
    assert body["checks"]["kafka"] == "ok"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_readiness_identifies_kafka_failure():
    router = create_health_router(
        {
            "database": AsyncMock(return_value="ok"),
            "kafka": AsyncMock(return_value="error"),
            "redis": AsyncMock(return_value="ok"),
        }
    )
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["checks"]["kafka"] == "error"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_readiness_returns_200_when_all_checks_ok():
    router = create_health_router(
        {
            "database": AsyncMock(return_value="ok"),
            "kafka": AsyncMock(return_value="ok"),
            "redis": AsyncMock(return_value="ok"),
        }
    )
    app = FastAPI()
    app.include_router(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
