"""Unit tests for bulk contract validation (US-01.05)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import CONTRACTS_DIR, ROOT, SCRIPT_PATH


@pytest.mark.story_us_01_05
def test_validate_contracts_directory_validates_schemas(
    validate_contract_module, tmp_path: Path
) -> None:
    """Happy path: a valid schema directory passes bulk validation."""
    schema = tmp_path / "sample.schema.json"
    schema.write_text(
        json.dumps({"type": "object", "properties": {"id": {"type": "string"}}}),
        encoding="utf-8",
    )
    validate_contract_module.validate_contracts_directory(tmp_path)


@pytest.mark.story_us_01_05
def test_validate_document_agent_mode_with_valid_example(
    validate_contract_module,
) -> None:
    """Single-document mode validates a known-good agent registration example."""
    example = CONTRACTS_DIR / "examples" / "coding-agent-registration.json"
    validate_contract_module.validate_document("agent", example)


@pytest.mark.story_us_01_05
def test_validate_document_rejects_invalid_payload(
    validate_contract_module, tmp_path: Path
) -> None:
    """Single-document mode must raise when the payload violates the schema."""
    invalid = tmp_path / "bad-agent.json"
    invalid.write_text(json.dumps({"agent_id": 123}), encoding="utf-8")

    with pytest.raises(Exception):
        validate_contract_module.validate_document("agent", invalid)


@pytest.mark.story_us_01_05
def test_validate_example_rejects_invalid_document(
    validate_contract_module, tmp_path: Path
) -> None:
    """Example validation must reject documents with wrong field types."""
    schema_path = CONTRACTS_DIR / "agent-contract.schema.json"
    example_path = tmp_path / "coding-agent-registration.json"
    example_path.write_text(json.dumps({"agent_id": 123}), encoding="utf-8")

    with pytest.raises(Exception):
        schema = validate_contract_module.load_json(schema_path)
        document = validate_contract_module.load_json(example_path)
        import jsonschema

        jsonschema.validate(instance=document, schema=schema)


@pytest.mark.story_us_01_05
def test_validate_schema_file_rejects_invalid_schema(
    validate_contract_module, tmp_path: Path
) -> None:
    """Schema metaschema validation must reject malformed JSON Schema definitions."""
    broken = tmp_path / "broken.schema.json"
    broken.write_text(
        json.dumps({"properties": {"x": {"type": "invalid"}}}),
        encoding="utf-8",
    )
    with pytest.raises(Exception):
        validate_contract_module.validate_schema_file(broken)


@pytest.mark.story_us_01_05
def test_validate_example_requires_schema_mapping(
    validate_contract_module, tmp_path: Path
) -> None:
    """Unmapped example files must fail with a clear error, not be silently skipped."""
    unmapped = tmp_path / "unknown-example.json"
    unmapped.write_text("{}", encoding="utf-8")

    with pytest.raises(SystemExit, match="No schema mapping"):
        validate_contract_module.validate_example(unmapped)


@pytest.mark.story_us_01_05
def test_main_usage_exits_when_args_missing() -> None:
    """CLI must print usage and exit non-zero when invoked without arguments."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "Usage:" in result.stderr or "Usage:" in result.stdout


@pytest.mark.story_us_01_05
def test_main_single_document_mode_exits_zero(validate_contract_module) -> None:
    """CLI single-document mode must validate a known-good agent example."""
    example = CONTRACTS_DIR / "examples" / "coding-agent-registration.json"
    import sys as sys_module

    argv = ["validate_contract.py", "agent", str(example)]
    sys_module.argv = argv
    validate_contract_module.main()


@pytest.mark.story_us_01_05
def test_main_bulk_mode_with_contracts_path_exits_zero(validate_contract_module) -> None:
    """CLI bulk mode accepts the repository contracts/ path."""
    import sys as sys_module

    sys_module.argv = ["validate_contract.py", "contracts/"]
    validate_contract_module.main()


@pytest.mark.story_us_01_05
def test_validate_document_unknown_type_raises_system_exit(
    validate_contract_module, tmp_path: Path
) -> None:
    """validate_document must exit when the contract type is not recognised."""
    doc = tmp_path / "doc.json"
    doc.write_text("{}", encoding="utf-8")

    with pytest.raises(SystemExit, match="Unknown contract type"):
        validate_contract_module.validate_document("bogus", doc)


@pytest.mark.story_us_01_05
def test_validate_contracts_directory_without_schemas_raises(
    validate_contract_module, tmp_path: Path
) -> None:
    """Bulk validation must fail when no schema files are present."""
    with pytest.raises(SystemExit, match="No \\*.schema.json"):
        validate_contract_module.validate_contracts_directory(tmp_path)


@pytest.mark.story_us_01_05
def test_validate_contracts_directory_validates_mapped_examples(
    validate_contract_module, tmp_path: Path
) -> None:
    """Bulk validation must validate examples/ when schema mapping exists."""
    repo_example = CONTRACTS_DIR / "examples" / "coding-agent-registration.json"
    (tmp_path / "agent-contract.schema.json").write_text(
        (CONTRACTS_DIR / "agent-contract.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    (examples_dir / "coding-agent-registration.json").write_text(
        repo_example.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    validate_contract_module.validate_contracts_directory(tmp_path)

