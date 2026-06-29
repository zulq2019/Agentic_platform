"""Cross-tenant RLS isolation tests for US-01.04."""

from __future__ import annotations

import asyncio

import asyncpg
import pytest

from aep_common.db import get_app_postgres_dsn, get_postgres_dsn, set_tenant_context

from .test_migrations import _run_migrations


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


@pytest.mark.story_us_01_04
@pytest.mark.integration
def test_rls_isolation_tools_registrations(requires_postgres):
    """Cross-tenant query on tools.registrations returns zero foreign rows."""
    assert _run_migrations() == 0

    async def _verify() -> None:
        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                """
                INSERT INTO tools.registrations (
                    tool_id, tenant_id, capability_tags, auth_strategy,
                    scope, rate_limit_policy, response_normaliser, contract_version
                ) VALUES ($1, $2, $3::jsonb, $4, $5, $6::jsonb, $7, $8)
                """,
                "github-prod",
                "tenant-a",
                '["create-pull-request"]',
                "oauth",
                "read",
                "{}",
                "github.v1",
                "1.0.0",
            )
            await admin.execute(
                """
                INSERT INTO tools.registrations (
                    tool_id, tenant_id, capability_tags, auth_strategy,
                    scope, rate_limit_policy, response_normaliser, contract_version
                ) VALUES ($1, $2, $3::jsonb, $4, $5, $6::jsonb, $7, $8)
                """,
                "jira-tenant-b",
                "tenant-b",
                '["create-issue"]',
                "oauth",
                "read",
                "{}",
                "jira.v1",
                "1.0.0",
            )
        finally:
            await admin.close()

        app_conn = await asyncpg.connect(get_app_postgres_dsn())
        try:
            await set_tenant_context(app_conn, "tenant-a")
            rows = await app_conn.fetch(
                "SELECT tool_id FROM tools.registrations WHERE tenant_id = $1",
                "tenant-b",
            )
            assert rows == []
        finally:
            await app_conn.close()

        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                "DELETE FROM tools.registrations WHERE tool_id = ANY($1::text[])",
                ["github-prod", "jira-tenant-b"],
            )
        finally:
            await admin.close()

    asyncio.run(_verify())


@pytest.mark.story_us_01_04
@pytest.mark.integration
def test_rls_isolation_approval_records(requires_postgres):
    """Cross-tenant query on approval.approval_records returns zero foreign rows."""
    assert _run_migrations() == 0

    task_a = "550e8400-e29b-41d4-a716-446655440001"
    task_b = "550e8400-e29b-41d4-a716-446655440002"
    wfr_a = "650e8400-e29b-41d4-a716-446655440001"
    wfr_b = "650e8400-e29b-41d4-a716-446655440002"

    async def _verify() -> None:
        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                """
                INSERT INTO orchestrator.workflow_runs (
                    workflow_run_id, tenant_id, workflow_type,
                    workflow_template_version, current_state
                ) VALUES ($1::uuid, $2, $3, $4, $5)
                """,
                wfr_a,
                "tenant-a",
                "greenfield-product-development",
                "1.0.0",
                "Started",
            )
            await admin.execute(
                """
                INSERT INTO orchestrator.tasks (
                    task_id, workflow_run_id, tenant_id, state
                ) VALUES ($1::uuid, $2::uuid, $3, $4)
                """,
                task_a,
                wfr_a,
                "tenant-a",
                "pending",
            )
            await admin.execute(
                """
                INSERT INTO approval.approval_records (
                    task_id, tenant_id, gate_id, decision
                ) VALUES ($1::uuid, $2, $3, $4)
                """,
                task_a,
                "tenant-a",
                "architecture-review",
                "approved",
            )

            await admin.execute(
                """
                INSERT INTO orchestrator.workflow_runs (
                    workflow_run_id, tenant_id, workflow_type,
                    workflow_template_version, current_state
                ) VALUES ($1::uuid, $2, $3, $4, $5)
                """,
                wfr_b,
                "tenant-b",
                "greenfield-product-development",
                "1.0.0",
                "Started",
            )
            await admin.execute(
                """
                INSERT INTO orchestrator.tasks (
                    task_id, workflow_run_id, tenant_id, state
                ) VALUES ($1::uuid, $2::uuid, $3, $4)
                """,
                task_b,
                wfr_b,
                "tenant-b",
                "pending",
            )
            await admin.execute(
                """
                INSERT INTO approval.approval_records (
                    task_id, tenant_id, gate_id, decision
                ) VALUES ($1::uuid, $2, $3, $4)
                """,
                task_b,
                "tenant-b",
                "architecture-review",
                "approved",
            )
        finally:
            await admin.close()

        app_conn = await asyncpg.connect(get_app_postgres_dsn())
        try:
            await set_tenant_context(app_conn, "tenant-a")
            rows = await app_conn.fetch(
                """
                SELECT approval_id
                FROM approval.approval_records
                WHERE tenant_id = $1
                """,
                "tenant-b",
            )
            assert rows == []
        finally:
            await app_conn.close()

        admin = await asyncpg.connect(get_postgres_dsn())
        try:
            await admin.execute(
                "DELETE FROM approval.approval_records WHERE tenant_id = ANY($1::text[])",
                ["tenant-a", "tenant-b"],
            )
            await admin.execute(
                "DELETE FROM orchestrator.tasks WHERE tenant_id = ANY($1::text[])",
                ["tenant-a", "tenant-b"],
            )
            await admin.execute(
                "DELETE FROM orchestrator.workflow_runs WHERE tenant_id = ANY($1::text[])",
                ["tenant-a", "tenant-b"],
            )
        finally:
            await admin.close()

    asyncio.run(_verify())
