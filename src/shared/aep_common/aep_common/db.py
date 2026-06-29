"""Database utilities for tenant-scoped PostgreSQL access."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfigurationError(RuntimeError):
    """Raised when required database environment variables are missing."""


class DatabaseSettings(BaseSettings):
    """Database connection settings loaded from environment variables."""

    model_config = SettingsConfigDict(extra="ignore")

    postgres_dsn: str | None = Field(default=None, validation_alias="POSTGRES_DSN")
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    aep_app_postgres_dsn: str | None = Field(
        default=None, validation_alias="AEP_APP_POSTGRES_DSN"
    )
    app_postgres_dsn: str | None = Field(
        default=None, validation_alias="APP_POSTGRES_DSN"
    )


def _load_settings() -> DatabaseSettings:
    """Load settings from the current process environment."""
    return DatabaseSettings()


def get_postgres_dsn() -> str:
    """Return the configured PostgreSQL DSN from environment variables."""
    settings = _load_settings()
    dsn = settings.postgres_dsn or settings.database_url
    if not dsn:
        raise DatabaseConfigurationError(
            "POSTGRES_DSN or DATABASE_URL must be set (see .env.example)"
        )
    return dsn


def get_app_postgres_dsn() -> str:
    """Return the tenant-scoped application role DSN subject to RLS policies."""
    settings = _load_settings()
    dsn = settings.aep_app_postgres_dsn or settings.app_postgres_dsn
    if not dsn:
        raise DatabaseConfigurationError(
            "AEP_APP_POSTGRES_DSN or APP_POSTGRES_DSN must be set (see .env.example)"
        )
    return dsn


async def set_tenant_context(conn: asyncpg.Connection, tenant_id: str) -> None:
    """Set the session tenant for row-level security policies."""
    await conn.execute(
        "SELECT set_config('app.current_tenant_id', $1, false)",
        tenant_id,
    )


@asynccontextmanager
async def tenant_connection(tenant_id: str) -> AsyncIterator[asyncpg.Connection]:
    """Open an application-role connection with tenant context for RLS queries."""
    conn = await asyncpg.connect(get_app_postgres_dsn())
    try:
        await set_tenant_context(conn, tenant_id)
        yield conn
    finally:
        await conn.close()


async def postgres_is_reachable() -> bool:
    """Return True when PostgreSQL accepts connections using the configured DSN."""
    try:
        dsn = get_postgres_dsn()
    except DatabaseConfigurationError:
        return False
    try:
        conn = await asyncpg.connect(dsn)
    except (OSError, asyncpg.PostgresError):
        return False
    await conn.close()
    return True
