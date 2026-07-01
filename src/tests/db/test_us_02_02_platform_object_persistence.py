"""Database persistence and RLS tests for US-02.02."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from uuid import UUID

import asyncpg
import pytest

from aep_common.db import get_app_postgres_dsn, get_postgres_dsn, set_tenant_context
from aep_meta.application.platform_object_service import PlatformObjectService
from aep_meta.application.validation import PlatformObjectValidator
from aep_meta.domain.enums import LifecycleState
from aep_meta.factory import build_platform_object
from aep_meta.infrastructure.in_memory_repository import InMemoryAuditRecorder
from aep_meta.infrastructure.observability import InMemoryMetricsRecorder
from aep_meta.infrastructure.postgres_repository import PostgresPlatformObjectRepository
from aep_meta.infrastructure.schema_validator import JsonSchemaValidator

from .test_migrations import _run_migrations

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "contracts" / "examples" / "sample-platform-object.json"


@pytest.fixture(scope="module")
def requires_postgres():
    import os

    from aep_common.db import postgres_is_reachable

    required = ("POSTGRES_DSN", "AEP_APP_POSTGRES_DSN", "AEP_APP_DB_PASSWORD")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        pytest.skip(
            "Set POSTGRES_DSN, AEP_APP_POSTGRES_DSN, and AEP_APP_DB_PASSWORD "
            "for integration tests (see .env.example)"
        )
    if not asyncio.run(postgres_is_reachable()):
        pytest.skip("PostgreSQL not reachable — start with make dev-up")


def _example_object(*, tenant_id: str, name: str) -> dict:
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    payload["identity"]["tenant_id"] = tenant_id
    payload["identity"]["name"] = name
    payload["identity"]["id"] = str(UUID(int=hash((tenant_id, name)) % (2**128)))
    return payload


async def _delete_object(object_id: UUID) -> None:
    admin = await asyncpg.connect(get_postgres_dsn())
    try:
        await admin.execute(
            "DELETE FROM metadata.platform_objects WHERE id = $1",
            object_id,
        )
    finally:
        await admin.close()


@pytest.mark.story_us_02_02
@pytest.mark.integration
def test_ac_us_02_02_01_postgres_repository_persists_platform_object(
    requires_postgres,
) -> None:
    assert _run_migrations() == 0

    async def _verify() -> None:
        repo = PostgresPlatformObjectRepository(get_app_postgres_dsn())
        obj = build_platform_object(tenant_id="tenant-a", name="pg-persist-a")
        saved = await repo.save(obj)
        loaded = await repo.get_by_id("tenant-a", saved.identity.id)
        assert loaded is not None
        assert loaded.identity.name == "pg-persist-a"
        await _delete_object(saved.identity.id)

    asyncio.run(_verify())


@pytest.mark.story_us_02_02
@pytest.mark.integration
def test_ac_us_02_02_02_postgres_repository_rls_isolates_tenants(
    requires_postgres,
) -> None:
    assert _run_migrations() == 0

    async def _verify() -> None:
        repo = PostgresPlatformObjectRepository(get_app_postgres_dsn())
        obj_a = build_platform_object(tenant_id="tenant-a", name="pg-rls-a")
        saved = await repo.save(obj_a)
        cross = await repo.get_by_id("tenant-b", saved.identity.id)
        assert cross is None
        await _delete_object(saved.identity.id)

    asyncio.run(_verify())


@pytest.mark.story_us_02_02
@pytest.mark.integration
def test_postgres_service_round_trip_with_rls(requires_postgres) -> None:
    assert _run_migrations() == 0

    async def _verify() -> None:
        service = PlatformObjectService(
            repository=PostgresPlatformObjectRepository(get_app_postgres_dsn()),
            validator=PlatformObjectValidator(JsonSchemaValidator()),
            audit=InMemoryAuditRecorder(),
            metrics=InMemoryMetricsRecorder(),
        )
        obj = build_platform_object(tenant_id="tenant-a", name="pg-service-a")
        saved = await service.register(obj, actor="user:tester")
        updated = await service.transition(
            saved.identity.tenant_id,
            saved.identity.id,
            LifecycleState.REVIEW,
            actor="user:reviewer",
        )
        assert updated.lifecycle.state == LifecycleState.REVIEW
        await _delete_object(saved.identity.id)

    asyncio.run(_verify())


@pytest.mark.story_us_02_02
@pytest.mark.integration
def test_ac_us_02_02_03_postgres_rls_list_returns_no_foreign_rows(
    requires_postgres,
) -> None:
    """Cross-tenant SELECT on metadata.platform_objects returns zero foreign rows."""
    assert _run_migrations() == 0

    async def _verify() -> None:
        admin = await asyncpg.connect(get_postgres_dsn())
        object_id = UUID("660e8400-e29b-41d4-a716-446655440099")
        try:
            await admin.execute(
                """
                INSERT INTO metadata.platform_objects (
                    id, tenant_id, primitive_type, name, namespace, version,
                    lifecycle_state, envelope, created_at, modified_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8::jsonb, now(), now()
                )
                """,
                object_id,
                "tenant-b",
                "capability",
                "foreign-object",
                "engineering",
                "1.0.0",
                "Draft",
                json.dumps(
                    _example_object(tenant_id="tenant-b", name="foreign-object")
                ),
            )
        finally:
            await admin.close()

        app_conn = await asyncpg.connect(get_app_postgres_dsn())
        try:
            await set_tenant_context(app_conn, "tenant-a")
            rows = await app_conn.fetch(
                """
                SELECT id FROM metadata.platform_objects
                WHERE tenant_id = $1
                """,
                "tenant-b",
            )
            assert rows == []
        finally:
            await app_conn.close()

        await _delete_object(object_id)

    asyncio.run(_verify())
