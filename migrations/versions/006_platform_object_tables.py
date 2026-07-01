"""Create metadata engine Platform Object tables with RLS.

Revision ID: 006_platform_object_tables
Revises: 005_app_role_grants
Create Date: 2026-07-01
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from helpers import (
    METADATA_TABLES,
    disable_tenant_rls,
    enable_tenant_rls,
    grant_app_role_on_tables,
    revoke_app_role_on_tables,
)

revision: str = "006_platform_object_tables"
down_revision: Union[str, None] = "005_app_role_grants"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS metadata")

    op.execute("""
        CREATE TABLE IF NOT EXISTS metadata.platform_objects (
            id                UUID PRIMARY KEY,
            tenant_id         TEXT NOT NULL,
            primitive_type    TEXT NOT NULL,
            name              TEXT NOT NULL,
            namespace         TEXT NOT NULL,
            version           TEXT NOT NULL,
            lifecycle_state   TEXT NOT NULL,
            envelope          JSONB NOT NULL,
            created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
            modified_at       TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_platform_objects_tenant_name_ns_version
            ON metadata.platform_objects (tenant_id, name, namespace, version)
        """)
    enable_tenant_rls("metadata", "platform_objects")

    op.execute("""
        CREATE TABLE IF NOT EXISTS metadata.platform_object_relationships (
            id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id               TEXT NOT NULL,
            source_object_id        UUID NOT NULL
                REFERENCES metadata.platform_objects(id),
            target_object_id        UUID NOT NULL,
            relationship_type       TEXT NOT NULL,
            target_primitive_type   TEXT NOT NULL,
            version_constraint      TEXT,
            pin                     TEXT,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """)
    enable_tenant_rls("metadata", "platform_object_relationships")

    op.execute("""
        CREATE TABLE IF NOT EXISTS metadata.platform_object_audit (
            audit_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id       TEXT NOT NULL,
            object_id       UUID NOT NULL
                REFERENCES metadata.platform_objects(id),
            action          TEXT NOT NULL,
            actor           TEXT NOT NULL,
            payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
            recorded_at     TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """)
    enable_tenant_rls("metadata", "platform_object_audit")

    op.execute("""
        CREATE TABLE IF NOT EXISTS metadata.platform_object_versions (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id       TEXT NOT NULL,
            object_id       UUID NOT NULL
                REFERENCES metadata.platform_objects(id),
            semantic_version TEXT NOT NULL,
            snapshot        JSONB NOT NULL,
            published_at    TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """)
    enable_tenant_rls("metadata", "platform_object_versions")

    grant_app_role_on_tables(METADATA_TABLES)


def downgrade() -> None:
    revoke_app_role_on_tables(METADATA_TABLES)

    disable_tenant_rls("metadata", "platform_object_versions")
    op.execute("DROP TABLE IF EXISTS metadata.platform_object_versions")

    disable_tenant_rls("metadata", "platform_object_audit")
    op.execute("DROP TABLE IF EXISTS metadata.platform_object_audit")

    disable_tenant_rls("metadata", "platform_object_relationships")
    op.execute("DROP TABLE IF EXISTS metadata.platform_object_relationships")

    disable_tenant_rls("metadata", "platform_objects")
    op.execute("DROP TABLE IF EXISTS metadata.platform_objects")

    op.execute("DROP SCHEMA IF EXISTS metadata CASCADE")
