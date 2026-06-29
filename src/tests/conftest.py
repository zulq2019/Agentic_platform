"""Shared fixtures for US-01.01 platform spine tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from services import stack_is_running

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "validate_contract.py"
CONTRACTS_DIR = ROOT / "contracts"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


@pytest.fixture
def requires_stack():
    if not stack_is_running():
        pytest.skip("Docker compose stack not running — start with make dev-up")


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def validate_contract_module():
    """Load scripts/validate_contract.py as a testable module."""
    spec = importlib.util.spec_from_file_location("validate_contract", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_contract"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def ci_workflow_text() -> str:
    return CI_WORKFLOW.read_text(encoding="utf-8")
