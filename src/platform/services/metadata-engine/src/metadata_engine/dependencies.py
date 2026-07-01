"""Application wiring for Metadata Engine."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from aep_meta.application.platform_object_service import PlatformObjectService
from aep_meta.application.validation import PlatformObjectValidator
from aep_meta.domain.ports import PlatformObjectRepository
from aep_meta.infrastructure.in_memory_repository import (
    InMemoryPlatformObjectRepository,
)
from aep_meta.infrastructure.postgres_repository import (
    PostgresPlatformObjectRepository,
)
from aep_meta.infrastructure.observability import (
    InMemoryAuditRecorder,
    InMemoryMetricsRecorder,
)
from aep_meta.infrastructure.schema_validator import JsonSchemaValidator

from metadata_engine.config import Settings

_service: PlatformObjectService | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _resolve_repository(cfg: Settings) -> PlatformObjectRepository:
    dsn = (cfg.aep_app_postgres_dsn or cfg.postgres_dsn or "").strip()
    if not dsn:
        try:
            from aep_common.db import DatabaseConfigurationError, get_app_postgres_dsn

            dsn = get_app_postgres_dsn()
        except DatabaseConfigurationError:
            return InMemoryPlatformObjectRepository()
    return PostgresPlatformObjectRepository(dsn)


def build_platform_object_service(
    settings: Settings | None = None,
) -> PlatformObjectService:
    global _service
    if _service is not None:
        return _service

    cfg = settings or get_settings()
    schema_path = (
        Path(cfg.platform_object_schema_path)
        if cfg.platform_object_schema_path
        else None
    )
    validator = PlatformObjectValidator(JsonSchemaValidator(schema_path))
    _service = PlatformObjectService(
        repository=_resolve_repository(cfg),
        validator=validator,
        audit=InMemoryAuditRecorder(),
        metrics=InMemoryMetricsRecorder(),
    )
    return _service


def reset_service_for_tests() -> None:
    global _service
    _service = None
    get_settings.cache_clear()
