#!/usr/bin/env python3
"""Verify PI-01 local developer environment after make dev-up."""

from __future__ import annotations

import sys
import urllib.error
import urllib.request

OBSERVABILITY_CHECKS: list[tuple[str, str]] = [
    ("Prometheus", "http://localhost:9090/-/ready"),
    ("Grafana", "http://localhost:3001/api/health"),
    ("OTEL Collector", "http://localhost:13133/health"),
]


def check_url(name: str, url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status != 200:
                print(f"FAIL {name}: HTTP {response.status}", file=sys.stderr)
                return False
            print(f"OK   {name}")
            return True
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"FAIL {name}: {exc}", file=sys.stderr)
        return False


def main() -> int:
    failed = False
    for name, url in OBSERVABILITY_CHECKS:
        if not check_url(name, url):
            failed = True

    if failed:
        print("Observability stack verification failed.", file=sys.stderr)
        return 1

    print("Observability stack healthy (Prometheus, Grafana, OTEL Collector).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
