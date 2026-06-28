from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from aep_common.health import create_health_router


@pytest.mark.asyncio
async def test_liveness_returns_ok():
    app = FastAPI()
    app.include_router(create_health_router({}))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_returns_503_when_check_fails():
    failing = AsyncMock(return_value="error")
    ok = AsyncMock(return_value="ok")
    app = FastAPI()
    app.include_router(create_health_router({"database": failing, "kafka": ok}))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "error"
