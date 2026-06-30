"""Create agent, tool, and approval registry tables with RLS.

Revision ID: 003_registry_approval_tables
Revises: 002_orchestrator_tables
Create Date: 2026-06-29
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from helpers import disable_tenant_rls, enable_tenant_rls

revision: str = "003_registry_approval_tables"
down_revision: Union[str, None] = "002_orchestrator_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS agents.registrations (
            agent_id                  TEXT PRIMARY KEY,
            tenant_id                 TEXT NOT NULL,
            capabilities              JSONB NOT NULL DEFAULT '[]'::jsonb,
            input_schema              TEXT NOT NULL,
            output_schema             TEXT NOT NULL,
            required_tools            JSONB NOT NULL DEFAULT '[]'::jsonb,
            cost_class                TEXT NOT NULL
                CHECK (cost_class IN ('low', 'medium', 'high')),
            approval_required         BOOLEAN NOT NULL DEFAULT false,
            idempotency_key_strategy  TEXT NOT NULL,
            contract_version          TEXT NOT NULL,
            active                    BOOLEAN NOT NULL DEFAULT true,
            registered_at             TIMESTAMPTZ DEFAULT now()
        )
        """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_agents_capabilities
            ON agents.registrations USING GIN (capabilities)
        """)
    enable_tenant_rls("agents", "registrations")

    op.execute("""
        CREATE TABLE IF NOT EXISTS tools.registrations (
            tool_id              TEXT PRIMARY KEY,
            tenant_id            TEXT NOT NULL,
            capability_tags      JSONB NOT NULL DEFAULT '[]'::jsonb,
            auth_strategy        TEXT NOT NULL,
            scope                TEXT NOT NULL,
            rate_limit_policy    JSONB NOT NULL DEFAULT '{}'::jsonb,
            response_normaliser  TEXT NOT NULL,
            contract_version     TEXT NOT NULL,
            active               BOOLEAN NOT NULL DEFAULT true,
            registered_at        TIMESTAMPTZ DEFAULT now()
        )
        """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_tools_capability_tags
            ON tools.registrations USING GIN (capability_tags)
        """)
    enable_tenant_rls("tools", "registrations")

    op.execute("""
        CREATE TABLE IF NOT EXISTS approval.approval_records (
            approval_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            task_id            UUID NOT NULL
                REFERENCES orchestrator.tasks(task_id),
            tenant_id          TEXT NOT NULL,
            gate_id            TEXT NOT NULL,
            approver           TEXT,
            decision           TEXT,
            reviewed_artifacts JSONB NOT NULL DEFAULT '{}'::jsonb,
            feedback           TEXT,
            decided_at         TIMESTAMPTZ,
            created_at         TIMESTAMPTZ DEFAULT now(),
            updated_at         TIMESTAMPTZ DEFAULT now()
        )
        """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_approval_task
            ON approval.approval_records (task_id)
        """)
    enable_tenant_rls("approval", "approval_records")


def downgrade() -> None:
    disable_tenant_rls("approval", "approval_records")
    op.execute("DROP TABLE IF EXISTS approval.approval_records")
    disable_tenant_rls("tools", "registrations")
    op.execute("DROP TABLE IF EXISTS tools.registrations")
    disable_tenant_rls("agents", "registrations")
    op.execute("DROP TABLE IF EXISTS agents.registrations")
