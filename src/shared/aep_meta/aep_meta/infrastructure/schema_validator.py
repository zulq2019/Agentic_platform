"""JSON Schema contract validation adapter."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from aep_meta.exceptions import ValidationError


def _default_schema_path() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "contracts" / "platform-object.schema.json"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("contracts/platform-object.schema.json not found")


class JsonSchemaValidator:
    def __init__(self, schema_path: Path | None = None) -> None:
        path = schema_path or _default_schema_path()
        with path.open(encoding="utf-8") as handle:
            schema = json.load(handle)
        Draft202012Validator.check_schema(schema)
        self._validator = Draft202012Validator(schema)

    def validate_contract(self, document: dict) -> None:
        try:
            self._validator.validate(document)
        except JsonSchemaValidationError as exc:
            raise ValidationError(str(exc), errors=[exc.message]) from exc
