"""Failure mode tests for US-01.02 — local developer environment."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[3]


def _load_script_module(name: str, relative_path: str):
    script_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.story_us_01_02
def test_verify_dev_environment_exits_nonzero_when_prometheus_unreachable():
    """
    When observability endpoints are down, verification must fail loudly so
    make dev-up does not report success on a partial stack.
    """
    module = _load_script_module(
        "verify_dev_environment", "scripts/verify_dev_environment.py"
    )

    with patch.object(module, "check_url", return_value=False):
        assert module.main() == 1


@pytest.mark.story_us_01_02
def test_verify_dev_environment_check_url_returns_false_on_http_error():
    module = _load_script_module(
        "verify_dev_environment", "scripts/verify_dev_environment.py"
    )

    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.status = 503

    with patch.object(module.urllib.request, "urlopen", return_value=mock_response):
        assert module.check_url("Prometheus", "http://localhost:9090/-/ready") is False


@pytest.mark.story_us_01_02
def test_verify_dev_environment_check_url_returns_false_on_connection_error():
    module = _load_script_module("verify_dev_environment", "scripts/verify_dev_environment.py")

    with patch.object(
        module.urllib.request,
        "urlopen",
        side_effect=module.urllib.error.URLError("connection refused"),
    ):
        assert module.check_url("Grafana", "http://localhost:3000/api/health") is False


@pytest.mark.story_us_01_02
def test_wait_for_health_check_health_returns_true_on_http_200():
    module = _load_script_module("wait_for_health", "scripts/wait_for_health.py")

    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.status = 200

    with patch.object(module.urllib.request, "urlopen", return_value=mock_response):
        assert module.check_health("auth-service", 8001) is True


@pytest.mark.story_us_01_02
def test_wait_for_health_check_health_returns_false_on_connection_error():
    module = _load_script_module("wait_for_health", "scripts/wait_for_health.py")

    with patch.object(
        module.urllib.request,
        "urlopen",
        side_effect=module.urllib.error.URLError("refused"),
    ):
        assert module.check_health("auth-service", 8001) is False


@pytest.mark.story_us_01_02
def test_wait_for_health_main_succeeds_when_all_services_respond():
    module = _load_script_module("wait_for_health", "scripts/wait_for_health.py")

    with patch.object(module, "check_health", return_value=True):
        assert module.main() == 0


@pytest.mark.story_us_01_02
def test_wait_for_health_polls_until_service_becomes_healthy():
    module = _load_script_module("wait_for_health", "scripts/wait_for_health.py")

    with patch.object(module, "SERVICES", [("auth-service", 8001)]):
        with patch.object(module, "check_health", side_effect=[False, True]):
            with patch.object(module.time, "time", side_effect=[0, 1, 2]):
                with patch.object(module, "POLL_INTERVAL", 0):
                    assert module.main() == 0


@pytest.mark.story_us_01_02
def test_wait_for_health_exits_nonzero_when_deadline_passes_with_pending_services():
    module = _load_script_module("wait_for_health", "scripts/wait_for_health.py")

    with patch.object(module, "TIMEOUT_SECONDS", 0):
        with patch.object(module.time, "time", return_value=0):
            assert module.main() == 1
