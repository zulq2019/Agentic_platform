"""Database migration and RLS tests for US-01.04."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

import asyncpg
import pytest

from aep_common.db import (
    get_app_postgres_dsn,
    get_postgres_dsn,
    postgres_is_reachable,
    set_tenant_context,
)

ROOT = Path(__file__).resolve().parents[3]

EXPECTED_TABLES: tuple[tuple[str, str], ...] = (
    ("orchestrator", "workflow_runs"),
    ("orchestrator", "tasks"),
    ("agents", "registrations"),
    ("tools", "registrations"),
    ("memory", "entries"),
    ("approval", "approval_records"),
    ("metadata", "platform_objects"),
    ("metadata", "platform_object_relationships"),
    ("metadata", "platform_object_audit"),
    ("metadata", "platform_object_versions"),
)

MIGRATION_HEAD_REVISION = "006_platform_object_tables"


def _run_migrations() -> int:
    return subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "run_migrations.py")],
        cwd=ROOT,
    )


@pytest.fixture(scope="module")
def requires_postgres():
    import os

    required = ("POSTGRES_DSN", "AEP_APP_POSTGRES_DSN", "AEP_APP_DB_PASSWORD")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        pytest.skip(
            "Set POSTGRES_DSN, AEP_APP_POSTGRES_DSN, and AEP_APP_DB_PASSWORD "
            "for integration tests (see .env.example)"
        )
    if not asyncio.run(postgres_is_reachable()):
        pytest.skip("PostgreSQL not reachable — start with make dev-up")


@pytest.mark.story_us_01_04
@pytest.mark.integration
def test_ac_01_03_migrate_creates_tables_with_rls(requires_postgres):
    """
    AC-01.03: make migrate creates all tables with RLS and records migration history.
    """
    assert _run_migrations() == 0

    async def _verify() -> None:
        conn = await asyncpg.connect(get_postgres_dsn())
        try:
            head_revision = await conn.fetchval(
                "SELECT version_num FROM alembic_version"
            )
            assert head_revision == MIGRATION_HEAD_REVISION

            for schema, table in EXPECTED_TABLES:
                exists = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = $1 AND table_name = $2
                    )
                    """,
                    schema,
                    table,
                )
                assert exists, f"Missing table {schema}.{table}"

                rls_enabled = await conn.fetchval(
                    """
                    SELECT relrowsecurity
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = $1 AND c.relname = $2
                    """,
                    schema,
                    table,
                )
                assert rls_enabled, f"RLS not enabled on {schema}.{table}"

                policy_count = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM pg_policies
                    WHERE schemaname = $1 AND tablename = $2
                        AND policyname = 'tenant_isolation'
                    """,
                    schema,
                    table,
                )
                assert (
                    policy_count == 1
                ), f"Missing tenant_isolation policy on {schema}.{table}"
        finally:
            await conn.close()

    asyncio.run(_verify())


@pytest.mark.story_us_01_04
@pytest.mark.integration
def test_ac_01_03_migrate_is_idempotent(requires_postgres):
    """TESTING.md: make migrate runs twice with no error."""
    assert _run_migrations() == 0
    assert _run_migrations() == 0


@pytest.mark.story_us_01_04
@pytest.mark.integration
def test_ac_01_03_cross_tenant_query_returns_zero_foreign_rows(requires_postgres):
    """
    AC-01.03: Queries in tenant A's context return zero rows belonging to tenant B.
    """
    assert _run_migrations() == 0

    async def _verify_isolation() -> None:
        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                """
                INSERT INTO orchestrator.workflow_runs (
                    tenant_id, workflow_type, workflow_template_version, current_state
                ) VALUES ($1, $2, $3, $4)
                """,
                "tenant-a",
                "greenfield-product-development",
                "1.0.0",
                "Started",
            )
            await admin.execute(
                """
                INSERT INTO orchestrator.workflow_runs (
                    tenant_id, workflow_type, workflow_template_version, current_state
                ) VALUES ($1, $2, $3, $4)
                """,
                "tenant-b",
                "greenfield-product-development",
                "1.0.0",
                "Started",
            )
        finally:
            await admin.close()

        app_conn = await asyncpg.connect(get_app_postgres_dsn())
        try:
            await set_tenant_context(app_conn, "tenant-a")
            tenant_a_rows = await app_conn.fetch(
                "SELECT tenant_id FROM orchestrator.workflow_runs"
            )
            assert len(tenant_a_rows) == 1
            assert tenant_a_rows[0]["tenant_id"] == "tenant-a"

            await set_tenant_context(app_conn, "tenant-b")
            tenant_b_rows = await app_conn.fetch(
                "SELECT tenant_id FROM orchestrator.workflow_runs"
            )
            assert len(tenant_b_rows) == 1
            assert tenant_b_rows[0]["tenant_id"] == "tenant-b"

            await set_tenant_context(app_conn, "tenant-a")
            foreign_rows = await app_conn.fetch(
                "SELECT tenant_id FROM orchestrator.workflow_runs WHERE tenant_id = $1",
                "tenant-b",
            )
            assert foreign_rows == []
        finally:
            await app_conn.close()

        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                "DELETE FROM orchestrator.workflow_runs WHERE tenant_id = ANY($1::text[])",
                ["tenant-a", "tenant-b"],
            )
        finally:
            await admin.close()

    asyncio.run(_verify_isolation())
