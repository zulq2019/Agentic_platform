"""API tests for US-01.06 shared logging correlation middleware."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from services import PYTHON_SERVICES, load_service_app


@pytest.fixture
def auth_app():
    service = next(s for s in PYTHON_SERVICES if s["name"] == "auth-service")
    return load_service_app(service)


@pytest.mark.story_us_01_06
@pytest.mark.asyncio
async def test_ac_3_http_middleware_binds_correlation_headers(auth_app):
    """
    US-01.06: Given inbound HTTP headers carry correlation IDs, when a request
    is processed, then the correlation middleware binds them for the request scope.
    """
    headers = {
        "x-task-id": "t-550e8400-e29b-41d4-a716-446655440000",
        "x-workflow-run-id": "wr-550e8400-e29b-41d4-a716-446655440000",
        "x-tenant-id": "tenant-acme-corp",
    }

    with (
        patch("aep_common.app.bind_correlation_from_headers") as bind_mock,
        patch("aep_common.app.clear_correlation_ids") as clear_mock,
    ):
        transport = ASGITransport(app=auth_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/info", headers=headers)

    assert response.status_code == 200
    bind_mock.assert_called_once()
    bound_headers = bind_mock.call_args[0][0]
    assert bound_headers["x-task-id"] == headers["x-task-id"]
    clear_mock.assert_called_once()


@pytest.mark.story_us_01_06
@pytest.mark.asyncio
async def test_ac_4_all_python_services_use_platform_app_factory():
    """
    US-01.06: Given any Python platform service, when its app is loaded,
    then it is created via create_platform_app (shared logging middleware).
    """
    for service in PYTHON_SERVICES:
        app = load_service_app(service)
        assert any(
            getattr(route, "path", None) == "/info" for route in app.routes
        ), f"{service['name']} missing /info route from platform app factory"
