"""Integration tests for US-01.02 — local developer environment."""

from __future__ import annotations

import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from observability_stack import observability_stack_running
from services import stack_is_running

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def requires_full_stack():
    if not stack_is_running() or not observability_stack_running():
        pytest.skip("Full US-01.02 stack not running — run make dev-up first")


@pytest.mark.story_us_01_02
@pytest.mark.integration
def test_ac_01_05_prometheus_scrape_config_matches_running_stack(requires_full_stack):
    """Prometheus config targets align with services exposed on localhost."""
    import urllib.error
    import urllib.request

    from services import ALL_SERVICES

    for name, port in ALL_SERVICES:
        url = f"http://localhost:{port}/health/live"
        with urllib.request.urlopen(url, timeout=3) as response:
            assert response.status == 200, f"{name} unhealthy on :{port}"


@pytest.mark.story_us_01_02
@pytest.mark.integration
def test_ac_01_05_observability_stack_healthy(requires_full_stack):
    """
    AC-01.05: Full local environment includes Prometheus, Grafana, OTEL Collector, and Tempo.
    """
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_dev_environment.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "Observability stack healthy" in result.stdout
