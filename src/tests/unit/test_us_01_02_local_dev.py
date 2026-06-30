"""Unit tests for US-01.02 — Local Developer Environment."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[3]

EXPECTED_PROMETHEUS_TARGETS = [
    "api-gateway:8080",
    "auth-service:8001",
    "rbac-service:8002",
    "orchestrator-service:8003",
    "workflow-engine:8004",
    "task-engine:8005",
    "approval-service:8006",
    "agent-runtime:8007",
    "agent-registry:8008",
    "model-router:8009",
    "tool-registry:8010",
    "memory-service:8011",
    "audit-service:8012",
    "secrets-service:8013",
    "policy-engine:8014",
    "config-service:8015",
]


def _load_script(name: str, path: str):
    script_path = ROOT / path
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.story_us_01_02
def test_ac_01_05_prometheus_config_scrapes_all_sixteen_services():
    """
    AC-01.05 / CAP-03: Prometheus must scrape all 16 platform service /metrics endpoints.
    """
    config = (ROOT / "observability" / "prometheus" / "prometheus.yml").read_text(
        encoding="utf-8"
    )
    for target in EXPECTED_PROMETHEUS_TARGETS:
        assert target in config, f"Missing scrape target: {target}"
    assert "aep-platform-services" in config
    assert "metrics_path: /metrics" in config


@pytest.mark.story_us_01_02
def test_docker_compose_includes_observability_stack():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    for service in ("otel-collector:", "prometheus:", "grafana:"):
        assert service in compose
    assert "pgvector/pgvector:pg16" in compose
    assert "OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317" in compose


@pytest.mark.story_us_01_02
def test_docker_compose_wires_all_sixteen_platform_services():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    for target in EXPECTED_PROMETHEUS_TARGETS:
        service_name = target.split(":")[0]
        assert f"  {service_name}:" in compose or f"{service_name}:" in compose


@pytest.mark.story_us_01_02
def test_makefile_dev_up_runs_compose_health_and_observability_checks():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "docker compose up" in makefile
    assert "generate_prometheus_config.py" in makefile
    assert "generate_docker_compose.py" in makefile
    assert "wait_for_health.py" in makefile
    assert "verify_dev_environment.py" in makefile


@pytest.mark.story_us_01_02
def test_ac_01_05_readme_documents_clone_to_dev_up_onboarding():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "git clone" in readme
    assert "make dev-up" in readme
    assert "Docker" in readme
    assert "Python 3.12" in readme
    assert "localhost:9090" in readme
    assert "localhost:3001" in readme
    assert "make dev-down" in readme


@pytest.mark.story_us_01_02
def test_observability_config_files_exist():
    required = [
        "observability/otel-collector/otel-config.yaml",
        "observability/grafana/provisioning/datasources/datasources.yml",
        "observability/grafana/dashboards/01-service-health.json",
    ]
    for rel_path in required:
        assert (ROOT / rel_path).is_file(), f"Missing {rel_path}"


@pytest.mark.story_us_01_02
def test_verify_dev_environment_script_checks_observability_endpoints():
    module = _load_script("verify_dev_environment", "scripts/verify_dev_environment.py")

    assert len(module.OBSERVABILITY_CHECKS) == 4
    urls = [url for _, url in module.OBSERVABILITY_CHECKS]
    assert "http://localhost:9090/-/ready" in urls
    assert "http://localhost:3001/api/health" in urls
    assert "http://localhost:13133/health" in urls
    assert "http://localhost:3200/ready" in urls

    with patch.object(module, "check_url", return_value=True) as mock_check:
        assert module.main() == 0
    assert mock_check.call_count == 4


@pytest.mark.story_us_01_02
def test_verify_dev_environment_check_url_succeeds_on_http_200():
    module = _load_script("verify_dev_environment", "scripts/verify_dev_environment.py")

    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.status = 200

    with patch.object(module.urllib.request, "urlopen", return_value=mock_response):
        assert module.check_url("Prometheus", "http://localhost:9090/-/ready") is True


@pytest.mark.story_us_01_02
def test_generate_prometheus_config_writes_sixteen_targets(tmp_path, monkeypatch):
    gen = _load_script(
        "generate_prometheus_config", "scripts/generate_prometheus_config.py"
    )
    monkeypatch.setattr(gen, "ROOT", tmp_path)
    gen.main()
    output = tmp_path / "observability" / "prometheus" / "prometheus.yml"
    content = output.read_text(encoding="utf-8")
    for target in gen.SCRAPE_TARGETS:
        assert target in content
    assert len(gen.SCRAPE_TARGETS) == 16


@pytest.mark.story_us_01_02
def test_generate_prometheus_targets_match_wait_for_health_ports():
    gen = _load_script(
        "generate_prometheus_config", "scripts/generate_prometheus_config.py"
    )
    wait = _load_script("wait_for_health", "scripts/wait_for_health.py")
    prometheus_ports = {int(t.split(":")[1]) for t in gen.SCRAPE_TARGETS}
    health_ports = {port for _, port in wait.SERVICES}
    assert prometheus_ports == health_ports
