#!/usr/bin/env python3
"""Wait for all platform services to return HTTP 200 from /health/live."""

from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request

SERVICES: list[tuple[str, int]] = [
    ("api-gateway", 8080),
    ("auth-service", 8001),
    ("rbac-service", 8002),
    ("orchestrator-service", 8003),
    ("workflow-engine", 8004),
    ("task-engine", 8005),
    ("approval-service", 8006),
    ("agent-runtime", 8007),
    ("agent-registry", 8008),
    ("model-router", 8009),
    ("tool-registry", 8010),
    ("memory-service", 8011),
    ("audit-service", 8012),
    ("secrets-service", 8013),
    ("policy-engine", 8014),
    ("config-service", 8015),
]

TIMEOUT_SECONDS = 60
POLL_INTERVAL = 2


def check_health(name: str, port: int) -> bool:
    url = f"http://localhost:{port}/health/live"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def main() -> int:
    deadline = time.time() + TIMEOUT_SECONDS
    pending = set(range(len(SERVICES)))

    while pending and time.time() < deadline:
        for idx in list(pending):
            name, port = SERVICES[idx]
            if check_health(name, port):
                print(f"OK  {name} (: {port})")
                pending.remove(idx)
        if pending:
            time.sleep(POLL_INTERVAL)

    if pending:
        print("FAILED — services not healthy within 60 seconds:", file=sys.stderr)
        for idx in pending:
            name, port = SERVICES[idx]
            print(f"  - {name} (:{port})", file=sys.stderr)
        return 1

    print("All 16 services healthy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
