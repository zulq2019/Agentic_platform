"""PostgreSQL Platform Object repository with tenant RLS."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

import asyncpg

from aep_meta.domain.models import PlatformObject


def parse_envelope(raw: object) -> dict[str, Any]:
    """Normalise JSONB envelope values returned by asyncpg."""
    if isinstance(raw, str):
        return json.loads(raw)
    if isinstance(raw, dict):
        return dict(raw)
    raise TypeError(f"unexpected envelope type: {type(raw)!r}")


async def set_tenant_context(conn: asyncpg.Connection, tenant_id: str) -> None:
    """Set session tenant for row-level security policies."""
    await conn.execute(
        "SELECT set_config('app.current_tenant_id', $1, false)",
        tenant_id,
    )


class PostgresPlatformObjectRepository:
    """Persist Platform Objects to metadata.platform_objects under RLS."""

    def __init__(self, app_dsn: str) -> None:
        if not app_dsn.strip():
            raise ValueError("app_dsn must be a non-empty PostgreSQL DSN")
        self._app_dsn = app_dsn

    async def save(self, obj: PlatformObject) -> PlatformObject:
        envelope = obj.to_contract_dict()
        tenant_id = obj.identity.tenant_id
        conn = await asyncpg.connect(self._app_dsn)
        try:
            await set_tenant_context(conn, tenant_id)
            await conn.execute(
                """
                INSERT INTO metadata.platform_objects (
                    id, tenant_id, primitive_type, name, namespace, version,
                    lifecycle_state, envelope, created_at, modified_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10
                )
                ON CONFLICT (id) DO UPDATE SET
                    primitive_type = EXCLUDED.primitive_type,
                    name = EXCLUDED.name,
                    namespace = EXCLUDED.namespace,
                    version = EXCLUDED.version,
                    lifecycle_state = EXCLUDED.lifecycle_state,
                    envelope = EXCLUDED.envelope,
                    modified_at = EXCLUDED.modified_at
                """,
                obj.identity.id,
                tenant_id,
                obj.primitive_type.value,
                obj.identity.name,
                obj.identity.namespace,
                obj.identity.version,
                obj.lifecycle.state.value,
                json.dumps(envelope),
                obj.identity.created_at,
                obj.identity.modified_at,
            )
        finally:
            await conn.close()
        return PlatformObject.from_contract_dict(envelope)

    async def get_by_id(self, tenant_id: str, object_id: UUID) -> PlatformObject | None:
        conn = await asyncpg.connect(self._app_dsn)
        try:
            await set_tenant_context(conn, tenant_id)
            row = await conn.fetchrow(
                """
                SELECT envelope
                FROM metadata.platform_objects
                WHERE id = $1
                """,
                object_id,
            )
        finally:
            await conn.close()
        if row is None:
            return None
        return PlatformObject.from_contract_dict(parse_envelope(row["envelope"]))

    async def list_by_tenant(
        self, tenant_id: str, *, namespace: str | None = None
    ) -> list[PlatformObject]:
        conn = await asyncpg.connect(self._app_dsn)
        try:
            await set_tenant_context(conn, tenant_id)
            if namespace is None:
                rows = await conn.fetch("""
                    SELECT envelope
                    FROM metadata.platform_objects
                    ORDER BY modified_at DESC
                    """)
            else:
                rows = await conn.fetch(
                    """
                    SELECT envelope
                    FROM metadata.platform_objects
                    WHERE namespace = $1
                    ORDER BY modified_at DESC
                    """,
                    namespace,
                )
        finally:
            await conn.close()
        return [
            PlatformObject.from_contract_dict(parse_envelope(row["envelope"]))
            for row in rows
        ]
