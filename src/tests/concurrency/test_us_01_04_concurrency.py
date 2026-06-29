"""Concurrency and cross-tenant isolation tests for US-01.04."""

from __future__ import annotations

import asyncio

import asyncpg
import pytest

from aep_common.db import get_app_postgres_dsn, get_postgres_dsn, set_tenant_context

from db.test_migrations import _run_migrations


@pytest.fixture(scope="module")
def requires_postgres():
    from aep_common.db import postgres_is_reachable

    if not asyncio.run(postgres_is_reachable()):
        pytest.skip("PostgreSQL not reachable — start with make dev-up")


async def _count_foreign_workflow_rows(tenant_id: str, foreign_tenant: str) -> int:
    conn = await asyncpg.connect(get_app_postgres_dsn())
    try:
        await set_tenant_context(conn, tenant_id)
        rows = await conn.fetch(
            """
            SELECT workflow_run_id
            FROM orchestrator.workflow_runs
            WHERE tenant_id = $1
            """,
            foreign_tenant,
        )
        return len(rows)
    finally:
        await conn.close()


@pytest.mark.story_us_01_04
@pytest.mark.integration
def test_concurrent_tenant_queries_return_zero_foreign_rows(requires_postgres):
    """
    Constitution MT1: concurrent tenant A and B sessions must not observe each
    other's workflow rows even when queries run in parallel.
    """
    assert _run_migrations() == 0

    async def _verify() -> None:
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

        foreign_a, foreign_b = await asyncio.gather(
            _count_foreign_workflow_rows("tenant-a", "tenant-b"),
            _count_foreign_workflow_rows("tenant-b", "tenant-a"),
        )

        assert foreign_a == 0
        assert foreign_b == 0

        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                "DELETE FROM orchestrator.workflow_runs WHERE tenant_id = ANY($1::text[])",
                ["tenant-a", "tenant-b"],
            )
        finally:
            await admin.close()

    asyncio.run(_verify())
