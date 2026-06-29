"""
Contract tests for US-01.05 — validates platform JSON schemas and examples.
Story: US-01.05 (AC-01.04)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest
from jsonschema import Draft202012Validator

from conftest import CONTRACTS_DIR, ROOT, SCRIPT_PATH


@pytest.mark.story_us_01_05
def test_ac_01_04_coding_agent_example_validates_against_agent_schema() -> None:
    """
    AC-01.04: committed example documents must validate against parent schemas.
    A drift between examples and schemas would let invalid registrations reach CI green.
    """
    schema = json.loads(
        (CONTRACTS_DIR / "agent-contract.schema.json").read_text(encoding="utf-8")
    )
    example = json.loads(
        (CONTRACTS_DIR / "examples" / "coding-agent-registration.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(instance=example, schema=schema)


@pytest.mark.story_us_01_05
@pytest.mark.parametrize(
    "schema_name",
    sorted(path.name for path in CONTRACTS_DIR.glob("*.schema.json")),
)
def test_ac_01_04_repo_schema_files_are_valid_json_schema(schema_name: str) -> None:
    """
    AC-01.04: every contracts/*.schema.json must be a valid JSON Schema metaschema.
    Invalid metaschema means CI contract validation cannot trust schema checks.
    """
    schema = json.loads((CONTRACTS_DIR / schema_name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


@pytest.mark.story_us_01_05
def test_ac_01_04_bulk_validate_contracts_script_exits_zero() -> None:
    """
    AC-01.04: the CI entry point `validate_contract.py contracts/` must exit 0
    on the committed contracts tree.
    """
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(CONTRACTS_DIR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "OK:" in result.stdout
