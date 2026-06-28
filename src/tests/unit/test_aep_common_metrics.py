"""Unit tests for aep_common Prometheus metrics. Story: US-01.01."""

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.routing import Route

from aep_common.metrics import metrics_endpoint


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_metrics_endpoint_returns_prometheus_text_format():
    app = Starlette(routes=[Route("/metrics", metrics_endpoint)])
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "# HELP" in response.text or "aep_http" in response.text
