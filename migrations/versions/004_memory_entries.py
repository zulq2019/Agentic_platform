"""Create memory entries table with pgvector and RLS.

Revision ID: 004_memory_entries
Revises: 003_registry_approval_tables
Create Date: 2026-06-29
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from helpers import disable_tenant_rls, enable_tenant_rls

revision: str = "004_memory_entries"
down_revision: Union[str, None] = "003_registry_approval_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS memory.entries (
            memory_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id      TEXT NOT NULL,
            source_type    TEXT NOT NULL
                CHECK (source_type IN ('standard', 'adr', 'incident', 'codebase')),
            content        TEXT NOT NULL,
            embedding      vector(1536),
            recency_weight FLOAT NOT NULL DEFAULT 1.0,
            provenance     JSONB NOT NULL,
            metadata       JSONB,
            created_at     TIMESTAMPTZ DEFAULT now()
        )
        """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_memory_embedding
            ON memory.entries USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_memory_tenant_type
            ON memory.entries (tenant_id, source_type, recency_weight DESC)
        """)
    enable_tenant_rls("memory", "entries")


def downgrade() -> None:
    disable_tenant_rls("memory", "entries")
    op.execute("DROP TABLE IF EXISTS memory.entries")
