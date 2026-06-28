"""Prometheus metrics helpers for platform services."""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response

_requests_total: Counter | None = None
_request_duration: Histogram | None = None


def create_service_metrics(service_name: str) -> tuple[Counter, Histogram]:
    """Return shared HTTP request metrics, pre-labelling the service dimension."""
    global _requests_total, _request_duration
    if _requests_total is None:
        _requests_total = Counter(
            "aep_http_requests_total",
            "Total HTTP requests",
            ["service", "method", "status"],
        )
        _request_duration = Histogram(
            "aep_http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["service", "method"],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )
    _requests_total.labels(service=service_name, method="GET", status="200")
    _request_duration.labels(service=service_name, method="GET")
    return _requests_total, _request_duration


async def metrics_endpoint(_request: Request) -> Response:
    """Expose Prometheus metrics in text format."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
