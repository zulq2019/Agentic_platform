"""Create orchestrator workflow and task tables with RLS.

Revision ID: 002_orchestrator_tables
Revises: 001_extensions_schemas
Create Date: 2026-06-29
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from helpers import disable_tenant_rls, enable_tenant_rls

revision: str = "002_orchestrator_tables"
down_revision: Union[str, None] = "001_extensions_schemas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS orchestrator.workflow_runs (
            workflow_run_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id                 TEXT NOT NULL,
            workflow_type             TEXT NOT NULL,
            workflow_template_version TEXT NOT NULL,
            current_state             TEXT NOT NULL,
            started_at                TIMESTAMPTZ DEFAULT now(),
            completed_at              TIMESTAMPTZ,
            metadata                  JSONB DEFAULT '{}'::jsonb,
            created_at                TIMESTAMPTZ DEFAULT now(),
            updated_at                TIMESTAMPTZ DEFAULT now()
        )
        """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_wfr_tenant_state
            ON orchestrator.workflow_runs (tenant_id, current_state)
        """)
    enable_tenant_rls("orchestrator", "workflow_runs")

    op.execute("""
        CREATE TABLE IF NOT EXISTS orchestrator.tasks (
            task_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            workflow_run_id  UUID NOT NULL
                REFERENCES orchestrator.workflow_runs(workflow_run_id),
            tenant_id        TEXT NOT NULL,
            assigned_agent_id TEXT,
            state            TEXT NOT NULL DEFAULT 'pending',
            context          JSONB NOT NULL DEFAULT '{}'::jsonb,
            retry_count      INT NOT NULL DEFAULT 0,
            approval_record  JSONB,
            model_tier       TEXT,
            created_at       TIMESTAMPTZ DEFAULT now(),
            updated_at       TIMESTAMPTZ DEFAULT now()
        )
        """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_wfr
            ON orchestrator.tasks (workflow_run_id, state)
        """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_agent
            ON orchestrator.tasks (assigned_agent_id, state)
        """)
    enable_tenant_rls("orchestrator", "tasks")


def downgrade() -> None:
    disable_tenant_rls("orchestrator", "tasks")
    op.execute("DROP TABLE IF EXISTS orchestrator.tasks")
    disable_tenant_rls("orchestrator", "workflow_runs")
    op.execute("DROP TABLE IF EXISTS orchestrator.workflow_runs")
