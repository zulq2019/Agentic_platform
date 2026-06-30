"""Shared dependency health check helpers."""

from __future__ import annotations

import asyncio
import socket

import asyncpg  # type: ignore[import-untyped]
from redis.asyncio import Redis


async def check_postgres(dsn: str, timeout: float = 3.0) -> str:
    """Verify PostgreSQL connectivity."""
    if not dsn:
        return "error"

    async def _ping() -> None:
        conn = await asyncpg.connect(dsn, timeout=timeout)
        try:
            await conn.fetchval("SELECT 1")
        finally:
            await conn.close()

    try:
        await asyncio.wait_for(_ping(), timeout=timeout)
        return "ok"
    except Exception:
        return "error"


async def check_kafka(bootstrap_servers: str, timeout: float = 3.0) -> str:
    """Verify Kafka broker TCP connectivity."""
    if not bootstrap_servers:
        return "error"

    host, _, port_str = bootstrap_servers.partition(":")
    port = int(port_str or "9092")

    def _tcp_ping() -> None:
        with socket.create_connection((host, port), timeout=timeout):
            return

    try:
        await asyncio.wait_for(asyncio.to_thread(_tcp_ping), timeout=timeout)
        return "ok"
    except Exception:
        return "error"


async def check_redis(redis_url: str, timeout: float = 3.0) -> str:
    """Verify Redis connectivity."""
    if not redis_url:
        return "error"

    client = Redis.from_url(redis_url, socket_connect_timeout=timeout)
    try:
        pong = await asyncio.wait_for(client.ping(), timeout=timeout)
        return "ok" if pong else "error"
    except Exception:
        return "error"
    finally:
        await client.aclose()  # type: ignore[attr-defined]
