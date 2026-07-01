"""Shared helpers for Alembic migrations."""

from __future__ import annotations

from alembic import op

PLATFORM_SCHEMAS: tuple[str, ...] = (
    "orchestrator",
    "agents",
    "tools",
    "memory",
    "approval",
    "metadata",
)

PLATFORM_TABLES: tuple[tuple[str, str], ...] = (
    ("orchestrator", "workflow_runs"),
    ("orchestrator", "tasks"),
    ("agents", "registrations"),
    ("tools", "registrations"),
    ("memory", "entries"),
    ("approval", "approval_records"),
)

METADATA_TABLES: tuple[tuple[str, str], ...] = (
    ("metadata", "platform_objects"),
    ("metadata", "platform_object_relationships"),
    ("metadata", "platform_object_audit"),
    ("metadata", "platform_object_versions"),
)

APP_ROLE = "aep_app"


def create_schemas() -> None:
    """Create platform PostgreSQL schemas if they do not exist."""
    for schema in PLATFORM_SCHEMAS:
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")


def drop_schemas() -> None:
    """Drop platform PostgreSQL schemas."""
    for schema in reversed(PLATFORM_SCHEMAS):
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")


def enable_tenant_rls(schema: str, table: str) -> None:
    """Enable row-level security with the standard tenant isolation policy."""
    qualified = f"{schema}.{table}"
    op.execute(f"ALTER TABLE {qualified} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {qualified} FORCE ROW LEVEL SECURITY")
    op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {qualified}")
    op.execute(f"""
        CREATE POLICY tenant_isolation ON {qualified}
            USING (tenant_id = current_setting('app.current_tenant_id'))
            WITH CHECK (tenant_id = current_setting('app.current_tenant_id'))
        """)


def grant_app_role_on_tables(tables: tuple[tuple[str, str], ...]) -> None:
    """Grant tenant-scoped DML on tables to the application role."""
    for schema, table in tables:
        qualified = f"{schema}.{table}"
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {qualified} TO {APP_ROLE}")


def revoke_app_role_on_tables(tables: tuple[tuple[str, str], ...]) -> None:
    """Revoke application role access from tables."""
    for schema, table in reversed(tables):
        qualified = f"{schema}.{table}"
        op.execute(f"REVOKE ALL ON {qualified} FROM {APP_ROLE}")


def disable_tenant_rls(schema: str, table: str) -> None:
    """Remove tenant isolation policy from a table."""
    qualified = f"{schema}.{table}"
    op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {qualified}")
    op.execute(f"ALTER TABLE {qualified} NO FORCE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {qualified} DISABLE ROW LEVEL SECURITY")
