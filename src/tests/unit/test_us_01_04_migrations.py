"""Unit tests for US-01.04 — Database Migrated."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]

EXPECTED_MIGRATIONS: tuple[str, ...] = (
    "001_extensions_schemas.py",
    "002_orchestrator_tables.py",
    "003_registry_approval_tables.py",
    "004_memory_entries.py",
    "005_app_role_grants.py",
)

EXPECTED_TABLES: tuple[str, ...] = (
    "orchestrator.workflow_runs",
    "orchestrator.tasks",
    "agents.registrations",
    "tools.registrations",
    "memory.entries",
    "approval.approval_records",
)


@pytest.mark.story_us_01_04
def test_makefile_migrate_runs_alembic():
    """Makefile exposes make migrate wired to Alembic runner."""
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "migrate:" in makefile
    assert "run_migrations.py" in makefile
    assert "Migrations deferred to US-01.04" not in makefile


@pytest.mark.story_us_01_04
def test_alembic_versions_cover_platform_tables():
    """All CAP-05 core tables have dedicated migration revisions."""
    versions_dir = ROOT / "migrations" / "versions"
    present = {path.name for path in versions_dir.glob("*.py")}
    for migration in EXPECTED_MIGRATIONS:
        assert migration in present, f"Missing migration file: {migration}"

    combined = "\n".join(
        (versions_dir / name).read_text(encoding="utf-8")
        for name in EXPECTED_MIGRATIONS
    )
    for table in EXPECTED_TABLES:
        schema, name = table.split(".")
        assert f"{schema}.{name}" in combined


@pytest.mark.story_us_01_04
def test_migrations_apply_rls_policy_pattern():
    """Every table migration enables tenant_isolation RLS policy."""
    versions_dir = ROOT / "migrations" / "versions"
    table_migrations = tuple(
        name for name in EXPECTED_MIGRATIONS if name != "005_app_role_grants.py"
    )
    for migration in table_migrations[1:]:
        content = (versions_dir / migration).read_text(encoding="utf-8")
        assert "enable_tenant_rls" in content
        assert "def downgrade()" in content


@pytest.mark.story_us_01_04
def test_env_example_documents_postgres_dsn():
    """Root .env.example documents database connection variables."""
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "POSTGRES_DSN=" in env_example
    assert "AEP_APP_DB_PASSWORD=" in env_example
    assert "AEP_APP_POSTGRES_DSN=" in env_example


@pytest.mark.story_us_01_04
def test_app_role_migration_reads_password_from_environment():
    """Migration 005 must not embed application role credentials in source."""
    content = (ROOT / "migrations" / "versions" / "005_app_role_grants.py").read_text(
        encoding="utf-8"
    )
    assert "AEP_APP_DB_PASSWORD" in content
    assert "APP_PASSWORD =" not in content


@pytest.mark.story_us_01_04
def test_aep_common_db_exports_tenant_helpers():
    """aep_common.db provides tenant context helpers for RLS queries."""
    from aep_common.db import (  # noqa: PLC0415
        DatabaseConfigurationError,
        get_app_postgres_dsn,
        get_postgres_dsn,
        set_tenant_context,
        tenant_connection,
    )

    assert callable(get_postgres_dsn)
    assert callable(get_app_postgres_dsn)
    assert callable(set_tenant_context)
    assert callable(tenant_connection)
    assert issubclass(DatabaseConfigurationError, RuntimeError)
