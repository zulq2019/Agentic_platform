"""Unit tests for Postgres repository helpers (US-02.02)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from aep_meta.factory import build_platform_object
from aep_meta.infrastructure.postgres_repository import (
    PostgresPlatformObjectRepository,
    parse_envelope,
    set_tenant_context,
)


@pytest.mark.story_us_02_02
def test_parse_envelope_from_json_string() -> None:
    payload = {"identity": {"name": "sample"}}
    assert parse_envelope(json.dumps(payload)) == payload


@pytest.mark.story_us_02_02
def test_parse_envelope_from_dict() -> None:
    payload = {"identity": {"name": "sample"}}
    assert parse_envelope(payload) == payload


@pytest.mark.story_us_02_02
def test_parse_envelope_rejects_invalid_type() -> None:
    with pytest.raises(TypeError):
        parse_envelope(42)


@pytest.mark.story_us_02_02
def test_postgres_repository_requires_non_empty_dsn() -> None:
    with pytest.raises(ValueError, match="app_dsn"):
        PostgresPlatformObjectRepository("")


@pytest.mark.story_us_02_02
@pytest.mark.asyncio
async def test_ac_us_02_02_01_save_executes_upsert_with_tenant_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    AC-US-02.02-01: save must set tenant context and upsert the envelope.
    """
    obj = build_platform_object(tenant_id="tenant-a", name="pg-unit-save")
    conn = AsyncMock()
    conn.execute = AsyncMock()
    conn.close = AsyncMock()

    async def _connect(_dsn: str) -> AsyncMock:
        return conn

    tenant_context = AsyncMock()
    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.asyncpg.connect", _connect
    )
    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.set_tenant_context",
        tenant_context,
    )

    repo = PostgresPlatformObjectRepository("postgresql://aep_app:secret@localhost/aep")
    saved = await repo.save(obj)

    assert saved.identity.name == "pg-unit-save"
    tenant_context.assert_awaited_once_with(conn, "tenant-a")
    conn.execute.assert_awaited_once()
    conn.close.assert_awaited_once()


@pytest.mark.story_us_02_02
@pytest.mark.asyncio
async def test_ac_us_02_02_02_get_returns_none_when_row_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    AC-US-02.02-02: cross-tenant or missing rows surface as None at repository layer.
    """
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)
    conn.close = AsyncMock()

    async def _connect(_dsn: str) -> AsyncMock:
        return conn

    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.asyncpg.connect", _connect
    )
    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.set_tenant_context",
        AsyncMock(),
    )

    repo = PostgresPlatformObjectRepository("postgresql://aep_app:secret@localhost/aep")
    result = await repo.get_by_id("tenant-b", uuid4())

    assert result is None


@pytest.mark.story_us_02_02
@pytest.mark.asyncio
async def test_ac_us_02_02_02_get_returns_platform_object_when_row_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    obj = build_platform_object(tenant_id="tenant-a", name="pg-unit-get")
    envelope = obj.to_contract_dict()
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value={"envelope": envelope})
    conn.close = AsyncMock()

    async def _connect(_dsn: str) -> AsyncMock:
        return conn

    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.asyncpg.connect", _connect
    )
    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.set_tenant_context",
        AsyncMock(),
    )

    repo = PostgresPlatformObjectRepository("postgresql://aep_app:secret@localhost/aep")
    result = await repo.get_by_id("tenant-a", obj.identity.id)

    assert result is not None
    assert result.identity.name == "pg-unit-get"


@pytest.mark.story_us_02_02
@pytest.mark.asyncio
async def test_set_tenant_context_sets_rls_session_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    AC-US-02.02-03 helper: tenant session variable must be set before queries.
    """
    conn = AsyncMock()
    conn.execute = AsyncMock()

    await set_tenant_context(conn, "tenant-a")

    conn.execute.assert_awaited_once_with(
        "SELECT set_config('app.current_tenant_id', $1, false)",
        "tenant-a",
    )


@pytest.mark.story_us_02_02
@pytest.mark.asyncio
async def test_list_by_tenant_without_namespace_fetches_all_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    obj = build_platform_object(tenant_id="tenant-a", name="listed-all")
    envelope = json.dumps(obj.to_contract_dict())
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[{"envelope": envelope}])
    conn.close = AsyncMock()

    async def _connect(_dsn: str) -> AsyncMock:
        return conn

    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.asyncpg.connect", _connect
    )
    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.set_tenant_context",
        AsyncMock(),
    )

    repo = PostgresPlatformObjectRepository("postgresql://aep_app:secret@localhost/aep")
    results = await repo.list_by_tenant("tenant-a")

    assert len(results) == 1
    conn.fetch.assert_awaited_once()
    assert len(conn.fetch.await_args.args) == 1


@pytest.mark.story_us_02_02
@pytest.mark.asyncio
async def test_list_by_tenant_filters_namespace_when_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    obj = build_platform_object(tenant_id="tenant-a", name="listed", namespace="billing")
    envelope = json.dumps(obj.to_contract_dict())
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[{"envelope": envelope}])
    conn.close = AsyncMock()

    async def _connect(_dsn: str) -> AsyncMock:
        return conn

    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.asyncpg.connect", _connect
    )
    monkeypatch.setattr(
        "aep_meta.infrastructure.postgres_repository.set_tenant_context",
        AsyncMock(),
    )

    repo = PostgresPlatformObjectRepository("postgresql://aep_app:secret@localhost/aep")
    results = await repo.list_by_tenant("tenant-a", namespace="billing")

    assert len(results) == 1
    assert results[0].identity.namespace == "billing"
    conn.fetch.assert_awaited_once()
    assert conn.fetch.await_args.args[1] == "billing"
