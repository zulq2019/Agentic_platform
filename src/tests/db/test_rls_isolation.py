"""Cross-tenant RLS isolation tests for US-01.04."""

from __future__ import annotations

import asyncio

import asyncpg
import pytest

from aep_common.db import get_app_postgres_dsn, get_postgres_dsn, set_tenant_context

from .test_migrations import _run_migrations


@pytest.fixture(scope="module")
def requires_postgres():
    from aep_common.db import postgres_is_reachable

    if not asyncio.run(postgres_is_reachable()):
        pytest.skip("PostgreSQL not reachable — start with make dev-up")


@pytest.mark.story_us_01_04
@pytest.mark.integration
def test_rls_isolation_agents_registrations(requires_postgres):
    """Cross-tenant query on agents.registrations returns zero foreign rows."""
    assert _run_migrations() == 0

    async def _verify() -> None:
        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                """
                INSERT INTO agents.registrations (
                    agent_id, tenant_id, input_schema, output_schema,
                    cost_class, idempotency_key_strategy, contract_version
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                "coding-agent-v1",
                "tenant-a",
                "input",
                "output",
                "medium",
                "task_id",
                "1.0.0",
            )
            await admin.execute(
                """
                INSERT INTO agents.registrations (
                    agent_id, tenant_id, input_schema, output_schema,
                    cost_class, idempotency_key_strategy, contract_version
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                "coding-agent-v2",
                "tenant-b",
                "input",
                "output",
                "medium",
                "task_id",
                "1.0.0",
            )
        finally:
            await admin.close()

        app_conn = await asyncpg.connect(get_app_postgres_dsn())
        try:
            await set_tenant_context(app_conn, "tenant-a")
            rows = await app_conn.fetch(
                "SELECT agent_id FROM agents.registrations WHERE tenant_id = $1",
                "tenant-b",
            )
            assert rows == []
        finally:
            await app_conn.close()

        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                "DELETE FROM agents.registrations WHERE agent_id = ANY($1::text[])",
                ["coding-agent-v1", "coding-agent-v2"],
            )
        finally:
            await admin.close()

    asyncio.run(_verify())


@pytest.mark.story_us_01_04
@pytest.mark.integration
def test_rls_isolation_memory_entries(requires_postgres):
    """Cross-tenant query on memory.entries returns zero foreign rows."""
    assert _run_migrations() == 0

    async def _verify() -> None:
        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                """
                INSERT INTO memory.entries (
                    tenant_id, source_type, content, provenance
                ) VALUES ($1, $2, $3, $4::jsonb)
                """,
                "tenant-a",
                "standard",
                "tenant-a memory",
                '{"source": "test"}',
            )
            await admin.execute(
                """
                INSERT INTO memory.entries (
                    tenant_id, source_type, content, provenance
                ) VALUES ($1, $2, $3, $4::jsonb)
                """,
                "tenant-b",
                "standard",
                "tenant-b memory",
                '{"source": "test"}',
            )
        finally:
            await admin.close()

        app_conn = await asyncpg.connect(get_app_postgres_dsn())
        try:
            await set_tenant_context(app_conn, "tenant-a")
            foreign = await app_conn.fetch(
                "SELECT memory_id FROM memory.entries WHERE tenant_id = $1",
                "tenant-b",
            )
            assert foreign == []
        finally:
            await app_conn.close()

        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                "DELETE FROM memory.entries WHERE tenant_id = ANY($1::text[])",
                ["tenant-a", "tenant-b"],
            )
        finally:
            await admin.close()

    asyncio.run(_verify())
