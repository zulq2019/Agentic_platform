"""Service registry and helpers for US-01.01 tests."""

from __future__ import annotations

import importlib
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[2]

PYTHON_SERVICES: list[dict[str, str | int]] = [
    {"name": "auth-service", "module": "auth_service", "path": "src/platform/services/auth-service/src", "port": 8001},
    {"name": "rbac-service", "module": "rbac_service", "path": "src/platform/services/rbac-service/src", "port": 8002},
    {"name": "orchestrator-service", "module": "orchestrator_service", "path": "src/platform/orchestrator/src", "port": 8003},
    {"name": "workflow-engine", "module": "workflow_engine", "path": "src/platform/workflow/src", "port": 8004},
    {"name": "task-engine", "module": "task_engine", "path": "src/platform/task/src", "port": 8005},
    {"name": "approval-service", "module": "approval_service", "path": "src/platform/services/approval-service/src", "port": 8006},
    {"name": "agent-runtime", "module": "agent_runtime", "path": "src/platform/runtime/src", "port": 8007},
    {"name": "agent-registry", "module": "agent_registry", "path": "src/platform/registry/agent-registry/src", "port": 8008},
    {"name": "model-router", "module": "model_router", "path": "src/platform/registry/model-router/src", "port": 8009},
    {"name": "tool-registry", "module": "tool_registry", "path": "src/platform/registry/tool-registry/src", "port": 8010},
    {"name": "memory-service", "module": "memory_service", "path": "src/platform/services/memory-service/src", "port": 8011},
    {"name": "audit-service", "module": "audit_service", "path": "src/platform/services/audit-service/src", "port": 8012},
    {"name": "secrets-service", "module": "secrets_service", "path": "src/platform/services/secrets-service/src", "port": 8013},
    {"name": "policy-engine", "module": "policy_engine", "path": "src/platform/services/policy-engine/src", "port": 8014},
    {"name": "config-service", "module": "config_service", "path": "src/platform/services/config-service/src", "port": 8015},
]

ALL_SERVICES: list[tuple[str, int]] = [("api-gateway", 8080)] + [
    (str(s["name"]), int(s["port"])) for s in PYTHON_SERVICES
]


def port_is_live(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/health/live", timeout=2) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def stack_is_running() -> bool:
    return port_is_live(8080) and port_is_live(8001)


def load_service_app(service: dict[str, str | int]) -> FastAPI:
    src_path = str(ROOT / str(service["path"]))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    module = importlib.import_module(f"{service['module']}.main")
    create_app: Callable[[], FastAPI] = module.create_app
    return create_app()
