"""Database utilities for tenant-scoped PostgreSQL access."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg

DEFAULT_POSTGRES_DSN = "postgresql://aep:aep@localhost:5432/aep"
DEFAULT_APP_POSTGRES_DSN = "postgresql://aep_app:aep_app@localhost:5432/aep"


def get_postgres_dsn() -> str:
    """Return the configured PostgreSQL DSN from environment variables."""
    return os.environ.get("POSTGRES_DSN") or os.environ.get(
        "DATABASE_URL",
        DEFAULT_POSTGRES_DSN,
    )


def get_app_postgres_dsn() -> str:
    """Return the tenant-scoped application role DSN subject to RLS policies."""
    return os.environ.get("AEP_APP_POSTGRES_DSN") or os.environ.get(
        "APP_POSTGRES_DSN",
        DEFAULT_APP_POSTGRES_DSN,
    )


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
        conn = await asyncpg.connect(get_postgres_dsn())
    except (OSError, asyncpg.PostgresError):
        return False
    await conn.close()
    return True
