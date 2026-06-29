"""E2E tests for US-01.02 — full local developer environment."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from services import ALL_SERVICES, stack_is_running

ROOT = Path(__file__).resolve().parents[3]


def observability_stack_running() -> bool:
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(
            "http://localhost:9090/-/ready", timeout=2
        ) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


@pytest.fixture
def requires_full_stack():
    if not stack_is_running() or not observability_stack_running():
        pytest.skip("Full US-01.02 stack not running — run make dev-up first")


@pytest.mark.story_us_01_02
@pytest.mark.e2e
def test_ac_01_05_make_dev_up_brings_full_environment_healthy(requires_full_stack):
    """
    AC-01.05: After make dev-up, all 16 services and the observability stack
    are reachable on localhost.
    """
    health = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "wait_for_health.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=70,
    )
    assert health.returncode == 0, health.stderr or health.stdout
    assert "All 16 services healthy" in health.stdout

    observability = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_dev_environment.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert observability.returncode == 0, observability.stderr or observability.stdout


@pytest.mark.story_us_01_02
@pytest.mark.e2e
def test_ac_01_05_all_sixteen_service_ports_exposed(requires_full_stack):
    """Each platform service port from the registry responds on /health/live."""
    import urllib.error
    import urllib.request

    for name, port in ALL_SERVICES:
        url = f"http://localhost:{port}/health/live"
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                assert (
                    response.status == 200
                ), f"{name} on :{port} returned {response.status}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            pytest.fail(f"{name} on :{port} not reachable: {exc}")
