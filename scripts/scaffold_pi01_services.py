#!/usr/bin/env python3
"""Generate PI-01 Python service scaffolds for US-01.01."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PYTHON_SERVICES: list[tuple[str, str, int]] = [
    ("auth-service", "platform/services/auth-service", 8001),
    ("rbac-service", "platform/services/rbac-service", 8002),
    ("orchestrator-service", "platform/orchestrator", 8003),
    ("workflow-engine", "platform/workflow", 8004),
    ("task-engine", "platform/task", 8005),
    ("approval-service", "platform/services/approval-service", 8006),
    ("agent-runtime", "platform/runtime", 8007),
    ("agent-registry", "platform/registry/agent-registry", 8008),
    ("model-router", "platform/registry/model-router", 8009),
    ("tool-registry", "platform/registry/tool-registry", 8010),
    ("memory-service", "platform/services/memory-service", 8011),
    ("audit-service", "platform/services/audit-service", 8012),
    ("secrets-service", "platform/services/secrets-service", 8013),
    ("policy-engine", "platform/services/policy-engine", 8014),
    ("config-service", "platform/services/config-service", 8015),
]

PYPROJECT = """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{service_name}"
version = "0.1.0"
description = "Agentic Engineering Platform — {service_name}"
requires-python = ">=3.12"
dependencies = [
    "aep-common[health]",
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "httpx>=0.27.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.hatch.build.targets.wheel]
packages = ["{package_name}"]
"""

CONFIG_PY = """\
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "{service_name}"
    service_version: str = "0.1.0"
    contract_version: str = "1.0.0"
    environment: str = "dev"
    host: str = "0.0.0.0"
    port: int = {port}
    log_level: str = "INFO"
    postgres_dsn: str = ""
    kafka_bootstrap_servers: str = "kafka:9092"
    redis_url: str = "redis://redis:6379/0"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
"""

MAIN_PY = """\
from aep_common.app import create_platform_app
from fastapi import FastAPI

from {package_name}.config import Settings

settings = Settings()


def create_app() -> FastAPI:
    return create_platform_app(settings)


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("{package_name}.main:app", host=settings.host, port=settings.port, reload=False)
"""

TEST_HEALTH = """\
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from {package_name}.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_health_live_returns_200(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_ready_returns_200_when_dependencies_ok(app):
    with (
        patch("aep_common.app.check_postgres", new=AsyncMock(return_value="ok")),
        patch("aep_common.app.check_kafka", new=AsyncMock(return_value="ok")),
        patch("aep_common.app.check_redis", new=AsyncMock(return_value="ok")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"


@pytest.mark.asyncio
async def test_health_ready_returns_503_when_database_down(app):
    with (
        patch("aep_common.app.check_postgres", new=AsyncMock(return_value="error")),
        patch("aep_common.app.check_kafka", new=AsyncMock(return_value="ok")),
        patch("aep_common.app.check_redis", new=AsyncMock(return_value="ok")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "error"


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_prometheus_format(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/metrics")
    assert response.status_code == 200
    assert "aep_http_requests_total" in response.text


@pytest.mark.asyncio
async def test_info_endpoint_returns_metadata(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/info")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "{service_name}"
    assert body["version"] == "0.1.0"
"""

DOCKERFILE = """\
FROM python:3.12-slim AS builder

WORKDIR /build
COPY src/shared/aep_common /build/aep-common
RUN pip install --no-cache-dir --prefix=/install \\
    "/build/aep-common[health]" "fastapi>=0.110.0" "uvicorn[standard]>=0.27.0"

FROM python:3.12-slim AS runtime

RUN groupadd --gid 1000 aep && useradd --uid 1000 --gid aep --create-home aep

WORKDIR /app
COPY --from=builder /install /usr/local
COPY {service_path}/src /app/src
ENV PYTHONPATH=/app/src
ENV PORT={port}

USER aep
EXPOSE {port}
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:{port}/health/live')" || exit 1
CMD ["uvicorn", "{package_name}.main:app", "--host", "0.0.0.0", "--port", "{port}"]
"""

ENV_EXAMPLE = """\
SERVICE_NAME={service_name}
SERVICE_VERSION=0.1.0
CONTRACT_VERSION=1.0.0
ENVIRONMENT=dev
HOST=0.0.0.0
PORT={port}
LOG_LEVEL=INFO
POSTGRES_DSN=postgresql://USER:PASSWORD@localhost:5432/aep
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379/0
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
"""


def package_name(service_name: str) -> str:
    return service_name.replace("-", "_")


def write_service(service_name: str, rel_path: str, port: int) -> None:
    pkg = package_name(service_name)
    base = ROOT / "src" / rel_path
    src_dir = base / "src" / pkg
    tests_dir = base / "tests"
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("domain", "infrastructure"):
        sub_dir = src_dir / sub
        sub_dir.mkdir(parents=True, exist_ok=True)
        (sub_dir / "__init__.py").write_text(
            '"""Placeholder for future implementation."""\n', encoding="utf-8"
        )

    (src_dir / "__init__.py").write_text('"""Service package."""\n', encoding="utf-8")
    (src_dir / "config.py").write_text(
        CONFIG_PY.replace("{service_name}", service_name).replace("{port}", str(port)),
        encoding="utf-8",
    )
    (src_dir / "main.py").write_text(
        MAIN_PY.replace("{package_name}", pkg).replace("{service_name}", service_name),
        encoding="utf-8",
    )
    (tests_dir / "test_health.py").write_text(
        TEST_HEALTH.replace("{package_name}", pkg).replace(
            "{service_name}", service_name
        ),
        encoding="utf-8",
    )
    (base / "pyproject.toml").write_text(
        PYPROJECT.replace("{service_name}", service_name).replace(
            "{package_name}", pkg
        ),
        encoding="utf-8",
    )
    (base / "Dockerfile").write_text(
        DOCKERFILE.replace("{service_path}", f"src/{rel_path}")
        .replace("{port}", str(port))
        .replace("{package_name}", pkg),
        encoding="utf-8",
    )
    (base / ".env.example").write_text(
        ENV_EXAMPLE.replace("{service_name}", service_name).replace(
            "{port}", str(port)
        ),
        encoding="utf-8",
    )


def main() -> None:
    for service_name, rel_path, port in PYTHON_SERVICES:
        write_service(service_name, rel_path, port)
        print(f"Scaffolded {service_name} -> src/{rel_path}")


if __name__ == "__main__":
    main()
