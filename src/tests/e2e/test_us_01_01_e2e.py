"""E2E tests for US-01.01 — full stack health within 60 seconds."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.story_us_01_01
@pytest.mark.e2e
def test_ac_01_01_wait_for_health_script_exits_zero(requires_stack):
    """
    AC-01.01: All 16 services return HTTP 200 from /health/live within 60 seconds.
    Exercises scripts/wait_for_health.py against the running docker compose stack.
    """
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "wait_for_health.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=70,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "All 16 services healthy" in result.stdout
