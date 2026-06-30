"""Unit tests for US-01.07 observability baseline infrastructure."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from httpx import ASGITransport, AsyncClient
from pydantic_settings import BaseSettings, SettingsConfigDict

from aep_common.app import create_platform_app

ROOT = Path(__file__).resolve().parents[3]


class _ObservabilitySettings(BaseSettings):
    service_name: str = "auth-service"
    service_version: str = "0.1.0"
    contract_version: str = "1.0.0"
    environment: str = "test"
    host: str = "0.0.0.0"
    port: int = 8001
    postgres_dsn: str = ""
    kafka_bootstrap_servers: str = "kafka:9092"
    redis_url: str = "redis://redis:6379/0"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"

    model_config = SettingsConfigDict(extra="ignore")


@pytest.mark.story_us_01_07
def test_ac_4_otel_collector_exports_traces_to_tempo():
    """
    US-01.07: Given the OTEL collector config, when traces are received,
    then they are exported to Tempo via OTLP.
    """
    config = yaml.safe_load(
        (ROOT / "observability" / "otel-collector" / "otel-config.yaml").read_text(
            encoding="utf-8"
        )
    )
    trace_exporters = config["service"]["pipelines"]["traces"]["exporters"]

    assert "otlp/tempo" in trace_exporters
    assert config["exporters"]["otlp/tempo"]["endpoint"] == "tempo:4317"


@pytest.mark.story_us_01_07
def test_ac_5_prometheus_scrapes_all_sixteen_services():
    """
    US-01.07: Given prometheus.yml, when scrape targets are listed,
    then all 16 platform services expose /metrics endpoints.
    """
    prometheus = (ROOT / "observability" / "prometheus" / "prometheus.yml").read_text(
        encoding="utf-8"
    )
    for port in range(8001, 8016):
        assert f":{port}" in prometheus
    assert "api-gateway:8080" in prometheus


@pytest.mark.story_us_01_07
def test_ac_6_grafana_dashboard_and_tempo_datasource_exist():
    """
    US-01.07: Given Grafana provisioning, when datasources and dashboards load,
    then Prometheus and Tempo are available for service health views.
    """
    datasources = yaml.safe_load(
        (
            ROOT
            / "observability"
            / "grafana"
            / "provisioning"
            / "datasources"
            / "datasources.yml"
        ).read_text(encoding="utf-8")
    )
    names = {item["name"] for item in datasources["datasources"]}
    assert {"Prometheus", "Tempo"} <= names

    dashboard = (
        ROOT / "observability" / "grafana" / "dashboards" / "01-service-health.json"
    )
    assert dashboard.exists()
    assert "aep-platform-services" in dashboard.read_text(encoding="utf-8")


@pytest.mark.story_us_01_07
def test_ac_2_gateway_wires_otel_exporter_and_echo_middleware():
    """
    AC-01.07: Given the api-gateway with OTEL_EXPORTER_OTLP_ENDPOINT set,
    when the gateway source is built, then OTLP export and otelecho middleware are wired.
    """
    main_go = (ROOT / "src/platform/gateway/main.go").read_text(encoding="utf-8")
    tracing_go = (ROOT / "src/platform/gateway/tracing.go").read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "otelecho.Middleware" in main_go
    assert "configureTracing" in main_go
    assert "OTEL_EXPORTER_OTLP_ENDPOINT" in tracing_go
    assert "api-gateway:" in compose
    assert "OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317" in compose


@pytest.mark.story_us_01_07
def test_ac_7_compose_includes_tempo_and_otel_collector():
    """
    US-01.07: Given docker-compose.yml, when observability services are defined,
    then Tempo and the OTEL collector are present for trace export.
    """
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "tempo:" in compose
    assert "otel-collector:" in compose
    assert "OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317" in compose


@pytest.mark.story_us_01_07
@pytest.mark.asyncio
async def test_ac_8_platform_app_exposes_prometheus_metrics():
    """
    US-01.07: Given a platform service app, when /metrics is requested,
    then Prometheus text format is returned.
    """
    app = create_platform_app(_ObservabilitySettings())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert "aep_http_requests_total" in response.text
