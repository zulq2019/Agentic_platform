"""Integration tests for US-01.01 — all 16 services against running stack."""

import json
import urllib.error
import urllib.request

import pytest

from services import ALL_SERVICES


def _get_json(url: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {}


@pytest.mark.story_us_01_01
@pytest.mark.integration
@pytest.mark.parametrize("service_name,port", ALL_SERVICES)
def test_ac_01_01_health_live_returns_200(service_name, port, requires_stack):
    """
    AC-01.01: With docker compose running, every service returns HTTP 200 from
    GET /health/live.
    """
    status, body = _get_json(f"http://localhost:{port}/health/live")
    assert status == 200, f"{service_name} live check failed with {status}"
    assert body.get("status") == "ok"


@pytest.mark.story_us_01_01
@pytest.mark.integration
@pytest.mark.parametrize("service_name,port", ALL_SERVICES)
def test_health_ready_returns_checks_map_when_infra_up(service_name, port, requires_stack):
    """Readiness must expose database, kafka, and redis check results."""
    status, body = _get_json(f"http://localhost:{port}/health/ready")
    assert status == 200, f"{service_name} ready check failed with {status}: {body}"
    assert "checks" in body
    for dep in ("database", "kafka", "redis"):
        assert dep in body["checks"], f"{service_name} missing check: {dep}"
        assert body["checks"][dep] == "ok"


@pytest.mark.story_us_01_01
@pytest.mark.integration
@pytest.mark.parametrize("service_name,port", ALL_SERVICES)
def test_metrics_endpoint_available(service_name, port, requires_stack):
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/metrics", timeout=5) as response:
            text = response.read().decode()
    except urllib.error.URLError as exc:
        pytest.fail(f"{service_name} metrics unavailable: {exc}")

    assert "aep_http_requests_total" in text


@pytest.mark.story_us_01_01
@pytest.mark.integration
@pytest.mark.parametrize("service_name,port", ALL_SERVICES)
def test_info_endpoint_returns_service_name(service_name, port, requires_stack):
    status, body = _get_json(f"http://localhost:{port}/info")
    assert status == 200
    assert body.get("service") == service_name
