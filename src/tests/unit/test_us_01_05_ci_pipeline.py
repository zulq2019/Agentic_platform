"""Acceptance tests for US-01.05 / AC-01.04 CI pipeline."""

from __future__ import annotations

import subprocess
import sys

import pytest

from conftest import CONTRACTS_DIR, ROOT, SCRIPT_PATH

EXPECTED_CONTAINER_IDS = {
    "gateway",
    "orchestrator",
    "workflow",
    "task",
    "runtime",
    "agent-registry",
    "tool-registry",
    "model-router",
    "auth-service",
    "rbac-service",
    "approval-service",
    "memory-service",
    "audit-service",
    "secrets-service",
    "policy-engine",
    "config-service",
}


@pytest.mark.story_us_01_05
def test_ac_01_04_ci_pipeline_includes_required_stages(ci_workflow_text: str) -> None:
    """
    AC-01.04: PR CI runs lint, unit tests, contract validation, and build.
    Missing any stage allows defects to merge undetected.
    """
    assert "timeout-minutes: 8" in ci_workflow_text
    assert "quality:" in ci_workflow_text or "lint-and-test" in ci_workflow_text
    assert "golangci" in ci_workflow_text
    assert "container-build:" in ci_workflow_text
    assert "ruff check" in ci_workflow_text
    assert "black --check" in ci_workflow_text
    assert "mypy --strict" in ci_workflow_text
    assert "pytest" in ci_workflow_text
    assert "validate_contract.py contracts/" in ci_workflow_text
    assert "docker build" in ci_workflow_text
    assert "trivy-action" in ci_workflow_text


@pytest.mark.story_us_01_05
def test_ac_01_04_ci_jobs_complete_within_eight_minutes(ci_workflow_text: str) -> None:
    """
    AC-01.04: each CI job declares an 8-minute ceiling so feedback stays fast.
    """
    timeout_lines = [
        line.strip()
        for line in ci_workflow_text.splitlines()
        if line.strip().startswith("timeout-minutes:")
    ]
    assert timeout_lines, "CI workflow must declare job timeouts"
    assert all("8" in line for line in timeout_lines)


@pytest.mark.story_us_01_05
def test_ac_01_04_ci_includes_security_gates(ci_workflow_text: str) -> None:
    """
    CAP-06 requires pip-audit and detect-secrets in the quality job.
    Without these, vulnerable dependencies and leaked secrets reach main.
    """
    assert "pip-audit" in ci_workflow_text
    assert "detect-secrets" in ci_workflow_text
    assert ".secrets.baseline" in ci_workflow_text


@pytest.mark.story_us_01_05
def test_ac_01_04_container_build_matrix_covers_sixteen_services(
    ci_workflow_text: str,
) -> None:
    """
    CAP-06 requires all 16 platform container images to build in CI.
    """
    found = {
        line.strip().removeprefix("- id: ")
        for line in ci_workflow_text.splitlines()
        if line.strip().startswith("- id: ")
    }
    assert found == EXPECTED_CONTAINER_IDS


@pytest.mark.story_us_01_05
def test_ac_01_04_contract_validation_passes_for_repo_contracts() -> None:
    """AC-01.04: contract validation succeeds for the committed contracts tree."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(CONTRACTS_DIR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
