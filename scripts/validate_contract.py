#!/usr/bin/env python3
"""Validate platform contract documents against JSON schemas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
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
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate(contract_type: str, document_path: Path) -> None:
    schema_file = SCHEMA_MAP.get(contract_type)
    if not schema_file:
        raise SystemExit(
            f"Unknown contract type: {contract_type}. Use one of: {', '.join(SCHEMA_MAP)}"
        )

    schema = load_json(CONTRACTS / schema_file)
    document = load_json(document_path)

    jsonschema.validate(instance=document, schema=schema)
    print(f"OK: {document_path} validates against {schema_file}")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            f"Usage: {sys.argv[0]} <agent|tool|task|memory|event> <document.json>"
        )

    validate(sys.argv[1], Path(sys.argv[2]))


if __name__ == "__main__":
    main()
