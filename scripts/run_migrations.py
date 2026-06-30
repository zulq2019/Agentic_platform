#!/usr/bin/env python3
"""Run Alembic migrations against POSTGRES_DSN."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _require_env(name: str) -> str | None:
    value = os.environ.get(name)
    if not value:
        print(f"{name} must be set (see .env.example)", file=sys.stderr)
        return None
    return value


def main() -> int:
    from aep_common.db import DatabaseConfigurationError, get_postgres_dsn

    try:
        dsn = get_postgres_dsn()
    except DatabaseConfigurationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if _require_env("AEP_APP_DB_PASSWORD") is None:
        return 1
    os.environ["POSTGRES_DSN"] = dsn
    print(f"Running Alembic migrations against {dsn.split('@')[-1]}")
    return subprocess.call(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
