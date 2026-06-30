"""Shared helpers for integration and e2e environment tests."""

from __future__ import annotations

import urllib.error
import urllib.request

OBSERVABILITY_HEALTH_URLS: tuple[str, ...] = (
    "http://localhost:9090/-/ready",
    "http://localhost:3001/api/health",
    "http://localhost:13133/health",
    "http://localhost:3200/ready",
)


def url_is_healthy(url: str, *, timeout: float = 2) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def observability_stack_running() -> bool:
    """True when Prometheus, Grafana, OTEL Collector, and Tempo are all reachable."""
    return all(url_is_healthy(url) for url in OBSERVABILITY_HEALTH_URLS)
