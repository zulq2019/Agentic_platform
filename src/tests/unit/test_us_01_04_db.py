"""Unit tests for aep_common.db tenant helpers (US-01.04)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import asyncpg
import pytest

from aep_common.db import (
    DatabaseConfigurationError,
    get_app_postgres_dsn,
    get_postgres_dsn,
    postgres_is_reachable,
    set_tenant_context,
    tenant_connection,
)


@pytest.mark.story_us_01_04
def test_get_postgres_dsn_prefers_postgres_dsn_env(monkeypatch):
    """Migration runner must honour POSTGRES_DSN over DATABASE_URL."""
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://aep:secret@db:5432/aep")
    monkeypatch.setenv("DATABASE_URL", "postgresql://other@db:5432/other")

    assert get_postgres_dsn() == "postgresql://aep:secret@db:5432/aep"


@pytest.mark.story_us_01_04
def test_get_postgres_dsn_falls_back_to_database_url(monkeypatch):
    """DATABASE_URL is used when POSTGRES_DSN is unset."""
    monkeypatch.delenv("POSTGRES_DSN", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://aep:secret@db:5432/aep")

    assert get_postgres_dsn() == "postgresql://aep:secret@db:5432/aep"


@pytest.mark.story_us_01_04
def test_get_app_postgres_dsn_prefers_aep_app_env(monkeypatch):
    """RLS-scoped queries must use the application role DSN."""
    monkeypatch.setenv(
        "AEP_APP_POSTGRES_DSN",
        "postgresql://aep_app:secret@db:5432/aep",
    )
    monkeypatch.delenv("APP_POSTGRES_DSN", raising=False)

    assert get_app_postgres_dsn() == "postgresql://aep_app:secret@db:5432/aep"


@pytest.mark.story_us_01_04
@pytest.mark.asyncio
async def test_set_tenant_context_executes_set_config():
    """
    RLS policies depend on app.current_tenant_id; missing context would
    expose cross-tenant rows or block all reads.
    """
    conn = AsyncMock()

    await set_tenant_context(conn, "tenant-acme")

    conn.execute.assert_awaited_once_with(
        "SELECT set_config('app.current_tenant_id', $1, false)",
        "tenant-acme",
    )


@pytest.mark.story_us_01_04
@pytest.mark.asyncio
async def test_postgres_is_reachable_returns_false_on_connection_error():
    """Unreachable PostgreSQL must be detectable before migrate runs."""
    with patch(
        "aep_common.db.asyncpg.connect",
        side_effect=OSError("connection refused"),
    ):
        assert await postgres_is_reachable() is False


@pytest.mark.story_us_01_04
@pytest.mark.asyncio
async def test_postgres_is_reachable_returns_false_on_postgres_error():
    with patch(
        "aep_common.db.asyncpg.connect",
        side_effect=asyncpg.PostgresError("auth failed"),
    ):
        assert await postgres_is_reachable() is False


@pytest.mark.story_us_01_04
@pytest.mark.asyncio
async def test_postgres_is_reachable_returns_true_when_connect_succeeds():
    conn = AsyncMock()
    conn.close = AsyncMock()
    with patch("aep_common.db.asyncpg.connect", return_value=conn):
        assert await postgres_is_reachable() is True
    conn.close.assert_awaited_once()


@pytest.mark.story_us_01_04
def test_get_postgres_dsn_raises_when_unconfigured(monkeypatch):
    """Missing DSN must fail fast instead of using embedded credentials."""
    monkeypatch.delenv("POSTGRES_DSN", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(DatabaseConfigurationError, match="POSTGRES_DSN"):
        get_postgres_dsn()


@pytest.mark.story_us_01_04
def test_get_app_postgres_dsn_raises_when_unconfigured(monkeypatch):
    monkeypatch.delenv("AEP_APP_POSTGRES_DSN", raising=False)
    monkeypatch.delenv("APP_POSTGRES_DSN", raising=False)

    with pytest.raises(DatabaseConfigurationError, match="AEP_APP_POSTGRES_DSN"):
        get_app_postgres_dsn()


@pytest.mark.story_us_01_04
@pytest.mark.asyncio
async def test_tenant_connection_sets_context_and_closes(monkeypatch):
    """tenant_connection must scope RLS and always release the connection."""
    monkeypatch.setenv(
        "AEP_APP_POSTGRES_DSN",
        "postgresql://aep_app:secret@db:5432/aep",
    )
    conn = AsyncMock()
    with patch("aep_common.db.asyncpg.connect", return_value=conn):
        async with tenant_connection("tenant-beta") as scoped:
            assert scoped is conn
        conn.execute.assert_awaited_once_with(
            "SELECT set_config('app.current_tenant_id', $1, false)",
            "tenant-beta",
        )
        conn.close.assert_awaited_once()
