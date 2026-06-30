"""Locate platform contract schemas from source tree or environment."""

from __future__ import annotations

import os
from pathlib import Path


def find_event_envelope_schema_path() -> Path:
    env_dir = os.environ.get("AEP_CONTRACTS_DIR")
    if env_dir:
        path = Path(env_dir) / "event-envelope.schema.json"
        if path.is_file():
            return path

    for parent in Path(__file__).resolve().parents:
        candidate = parent / "contracts" / "event-envelope.schema.json"
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        "event-envelope.schema.json not found; set AEP_CONTRACTS_DIR or install from repo root"
    )
