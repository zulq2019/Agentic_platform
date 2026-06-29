"""Failure mode tests for US-01.04 — Database Migrated."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[3]


def _load_script_module(name: str, relative_path: str):
    script_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def migration_env(monkeypatch):
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://aep:secret@db:5432/aep")
    monkeypatch.setenv("AEP_APP_DB_PASSWORD", "secret-app-password")


@pytest.mark.story_us_01_04
def test_run_migrations_exits_nonzero_when_alembic_fails(migration_env):
    """
    When PostgreSQL is unreachable, make migrate must exit non-zero so CI and
    dev-up do not report success on a broken database foundation.
    """
    module = _load_script_module("run_migrations", "scripts/run_migrations.py")

    with patch.object(module.subprocess, "call", return_value=1):
        assert module.main() == 1


@pytest.mark.story_us_01_04
def test_run_migrations_propagates_alembic_success(migration_env):
    module = _load_script_module("run_migrations", "scripts/run_migrations.py")

    with patch.object(module.subprocess, "call", return_value=0):
        assert module.main() == 0


@pytest.mark.story_us_01_04
def test_run_migrations_sets_postgres_dsn_from_database_url(monkeypatch):
    """Runner must normalise DATABASE_URL into POSTGRES_DSN for Alembic env."""
    module = _load_script_module("run_migrations", "scripts/run_migrations.py")
    monkeypatch.delenv("POSTGRES_DSN", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://aep:secret@db:5432/aep")
    monkeypatch.setenv("AEP_APP_DB_PASSWORD", "secret-app-password")

    with patch.object(module.subprocess, "call", return_value=0) as mock_call:
        assert module.main() == 0

    assert module.os.environ["POSTGRES_DSN"] == "postgresql://aep:secret@db:5432/aep"
    mock_call.assert_called_once()


@pytest.mark.story_us_01_04
def test_run_migrations_exits_nonzero_when_dsn_missing(monkeypatch):
    module = _load_script_module("run_migrations", "scripts/run_migrations.py")
    monkeypatch.delenv("POSTGRES_DSN", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("AEP_APP_DB_PASSWORD", "secret-app-password")

    assert module.main() == 1


@pytest.mark.story_us_01_04
def test_run_migrations_exits_nonzero_when_app_password_missing(monkeypatch):
    module = _load_script_module("run_migrations", "scripts/run_migrations.py")
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://aep:secret@db:5432/aep")
    monkeypatch.delenv("AEP_APP_DB_PASSWORD", raising=False)

    assert module.main() == 1
