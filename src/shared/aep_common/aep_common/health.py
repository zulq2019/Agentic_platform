"""FastAPI health routers for liveness and readiness probes."""

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter, Response, status

HealthCheckFn = Callable[[], Awaitable[str]]


def create_health_router(checks: dict[str, HealthCheckFn]) -> APIRouter:
    """Create a health router with live and ready endpoints.

    Args:
        checks: Mapping of dependency name to async check function returning
            ``"ok"`` or ``"error"``.
    """
    router = APIRouter(tags=["health"])

    @router.get("/health/live")
    async def liveness() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/health/ready")
    async def readiness(response: Response) -> dict[str, Any]:
        results: dict[str, str] = {}
        for name, check in checks.items():
            try:
                results[name] = await check()
            except Exception:
                results[name] = "error"

        all_ok = all(value == "ok" for value in results.values())
        if all_ok:
            return {"status": "ok", "checks": results}

        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "degraded", "checks": results}

    return router
