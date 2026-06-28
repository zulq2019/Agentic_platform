from contextlib import asynccontextmanager
from typing import AsyncIterator

from aep_common.dependencies import check_kafka, check_postgres, check_redis
from aep_common.health import create_health_router
from aep_common.logging import get_logger
from aep_common.metrics import create_service_metrics, metrics_endpoint
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
import time

from audit_service.config import Settings

settings = Settings()
logger = get_logger(settings.service_name)
requests_total, request_duration = create_service_metrics(settings.service_name)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("service_starting", service=settings.service_name)
    yield
    logger.info("service_stopped", service=settings.service_name)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.service_name, version=settings.service_version, lifespan=lifespan)

    health_router = create_health_router(
        {
            "database": lambda: check_postgres(settings.postgres_dsn),
            "kafka": lambda: check_kafka(settings.kafka_bootstrap_servers),
            "redis": lambda: check_redis(settings.redis_url),
        }
    )
    app.include_router(health_router)

    @app.get("/metrics")
    async def metrics(request: Request):
        return await metrics_endpoint(request)

    @app.get("/info")
    async def info() -> dict[str, str]:
        return {
            "service": settings.service_name,
            "version": settings.service_version,
            "contract_version": settings.contract_version,
            "environment": settings.environment,
        }

    @app.middleware("http")
    async def record_metrics(request: Request, call_next):
        if request.url.path.startswith("/health"):
            return await call_next(request)
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        requests_total.labels(
            service=settings.service_name,
            method=request.method,
            status=str(response.status_code),
        ).inc()
        request_duration.labels(service=settings.service_name, method=request.method).observe(duration)
        return response

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)
