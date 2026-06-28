#!/usr/bin/env python3
"""Run PI-01 unit tests (cross-platform)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> int:
    print("+", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT, env=env)


def main() -> int:
    if run([sys.executable, "-m", "pytest", "src/shared/aep_common/tests", "-v"]) != 0:
        return 1

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src/platform/services/auth-service/src")
    return run(
        [
            sys.executable,
            "-m",
            "pytest",
            "src/platform/services/auth-service/tests",
            "-v",
        ],
        env=env,
    )


if __name__ == "__main__":
    raise SystemExit(main())
