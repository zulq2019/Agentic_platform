#!/usr/bin/env python3
"""Validate platform contract documents against JSON schemas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    print("Install jsonschema: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "contracts"

SCHEMA_MAP = {
    "agent": "agent-contract.schema.json",
    "tool": "tool-contract.schema.json",
    "task": "task-schema.schema.json",
    "memory": "memory-schema.schema.json",
    "event": "event-envelope.schema.json",
    "platform-object": "platform-object.schema.json",
}

EXAMPLE_SCHEMA_MAP = {
    "coding-agent-registration.json": "agent-contract.schema.json",
    "sample-platform-object.json": "platform-object.schema.json",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_document(contract_type: str, document_path: Path) -> None:
    """Validate a single JSON document against a contract type schema."""
    schema_file = SCHEMA_MAP.get(contract_type)
    if not schema_file:
        raise SystemExit(
            f"Unknown contract type: {contract_type}. "
            f"Use one of: {', '.join(SCHEMA_MAP)}"
        )

    schema = load_json(CONTRACTS / schema_file)
    document = load_json(document_path)
    jsonschema.validate(instance=document, schema=schema)
    print(f"OK: {document_path} validates against {schema_file}")


def validate_schema_file(schema_path: Path) -> None:
    """Ensure a schema file is valid JSON Schema."""
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    print(f"OK: {schema_path.name} is a valid JSON Schema")


def validate_example(example_path: Path) -> None:
    """Validate a contracts/examples JSON file against its parent schema."""
    schema_name = EXAMPLE_SCHEMA_MAP.get(example_path.name)
    if schema_name is None:
        raise SystemExit(
            f"No schema mapping for example {example_path.name}. "
            f"Update EXAMPLE_SCHEMA_MAP in {Path(__file__).name}"
        )
    schema = load_json(CONTRACTS / schema_name)
    document = load_json(example_path)
    jsonschema.validate(instance=document, schema=schema)
    print(f"OK: {example_path.name} validates against {schema_name}")


def validate_contracts_directory(contracts_dir: Path) -> None:
    """Validate all platform schemas and example documents (CI entry point)."""
    if not contracts_dir.is_dir():
        raise SystemExit(f"Contracts directory not found: {contracts_dir}")

    schema_files = sorted(contracts_dir.glob("*.schema.json"))
    if not schema_files:
        raise SystemExit(f"No *.schema.json files in {contracts_dir}")

    for schema_path in schema_files:
        validate_schema_file(schema_path)

    examples_dir = contracts_dir / "examples"
    if examples_dir.is_dir():
        for example_path in sorted(examples_dir.glob("*.json")):
            validate_example(example_path)


def main() -> None:
    if len(sys.argv) == 2 and Path(sys.argv[1]).resolve() == CONTRACTS.resolve():
        validate_contracts_directory(CONTRACTS)
        return

    if len(sys.argv) == 2 and Path(sys.argv[1]).is_dir():
        validate_contracts_directory(Path(sys.argv[1]).resolve())
        return

    if len(sys.argv) != 3:
        raise SystemExit(
            f"Usage: {sys.argv[0]} <agent|tool|task|memory|event> <document.json>\n"
            f"   or: {sys.argv[0]} contracts/"
        )

    validate_document(sys.argv[1], Path(sys.argv[2]))


if __name__ == "__main__":
    main()
