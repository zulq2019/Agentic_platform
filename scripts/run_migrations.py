#!/usr/bin/env python3
"""Run Alembic migrations against POSTGRES_DSN."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    dsn = os.environ.get("POSTGRES_DSN") or os.environ.get(
        "DATABASE_URL",
        "postgresql://aep:aep@localhost:5432/aep",
    )
    os.environ["POSTGRES_DSN"] = dsn
    print(f"Running Alembic migrations against {dsn.split('@')[-1]}")
    return subprocess.call(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
