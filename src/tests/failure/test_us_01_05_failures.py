"""
Failure mode tests for US-01.05 CI contract validation.
Story: US-01.05 (AC-01.04)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ROOT, SCRIPT_PATH


def _run_validate_contract(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.story_us_01_05
def test_ac_01_04_broken_schema_in_contracts_dir_exits_nonzero(
    tmp_path: Path,
) -> None:
    """
    AC-01.04: modifying contracts/ to break a schema must fail CI validation.
    Without a failing exit code, broken schemas merge and break downstream consumers.
    """
    (tmp_path / "broken.schema.json").write_text(
        json.dumps(
            {
                "type": "object",
                "properties": {"field": {"type": "not-a-valid-json-schema-type"}},
            }
        ),
        encoding="utf-8",
    )

    result = _run_validate_contract(str(tmp_path))

    assert result.returncode != 0


@pytest.mark.story_us_01_05
def test_ac_01_04_broken_example_in_contracts_dir_exits_nonzero(
    tmp_path: Path,
) -> None:
    """
    AC-01.04: an example document that no longer matches its schema must fail CI.
    Examples are the golden path for agent/tool registration payloads.
    """
    (tmp_path / "agent-contract.schema.json").write_text(
        json.dumps(
            {
                "type": "object",
                "required": ["agent_id"],
                "properties": {"agent_id": {"type": "string"}},
            }
        ),
        encoding="utf-8",
    )
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    (examples_dir / "coding-agent-registration.json").write_text(
        json.dumps({"agent_id": 123}),
        encoding="utf-8",
    )

    result = _run_validate_contract(str(tmp_path))

    assert result.returncode != 0


@pytest.mark.story_us_01_05
def test_ac_01_04_unknown_contract_type_exits_nonzero(tmp_path: Path) -> None:
    """
    Single-document mode must reject unknown contract types with a non-zero exit.
    Silent acceptance of typos would skip schema validation entirely.
    """
    doc = tmp_path / "doc.json"
    doc.write_text("{}", encoding="utf-8")

    result = _run_validate_contract("unknown-type", str(doc))

    assert result.returncode != 0
    assert "Unknown contract type" in result.stderr or "Unknown contract type" in (
        result.stdout
    )


@pytest.mark.story_us_01_05
def test_ac_01_04_missing_contracts_directory_exits_nonzero(tmp_path: Path) -> None:
    """Bulk mode must fail clearly when the contracts directory does not exist."""
    missing = tmp_path / "no-such-contracts"
    result = _run_validate_contract(str(missing))
    assert result.returncode != 0
