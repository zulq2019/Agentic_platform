"""Service repository wiring tests for US-02.02."""

from __future__ import annotations

import pytest

from aep_meta.infrastructure.in_memory_repository import InMemoryPlatformObjectRepository
from aep_meta.infrastructure.postgres_repository import PostgresPlatformObjectRepository
from metadata_engine.config import Settings
from metadata_engine.dependencies import (
    _resolve_repository,
    build_platform_object_service,
    reset_service_for_tests,
)


@pytest.fixture(autouse=True)
def _reset_service() -> None:
    reset_service_for_tests()


@pytest.mark.story_us_02_02
def test_ac_us_02_02_04_uses_postgres_when_app_dsn_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    AC-US-02.02-04: metadata-engine must wire PostgresPlatformObjectRepository
    when AEP_APP_POSTGRES_DSN is configured.
    """
    monkeypatch.setenv(
        "AEP_APP_POSTGRES_DSN",
        "postgresql://aep_app:secret@localhost:5432/aep",
    )
    repo = _resolve_repository(Settings())
    assert isinstance(repo, PostgresPlatformObjectRepository)


@pytest.mark.story_us_02_02
def test_ac_us_02_02_04_uses_postgres_when_postgres_dsn_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AEP_APP_POSTGRES_DSN", raising=False)
    monkeypatch.setenv(
        "POSTGRES_DSN",
        "postgresql://aep_app:secret@localhost:5432/aep",
    )
    repo = _resolve_repository(Settings())
    assert isinstance(repo, PostgresPlatformObjectRepository)


@pytest.mark.story_us_02_02
def test_ac_us_02_02_04_service_uses_postgres_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "AEP_APP_POSTGRES_DSN",
        "postgresql://aep_app:secret@localhost:5432/aep",
    )
    service = build_platform_object_service(Settings())
    assert isinstance(service._repository, PostgresPlatformObjectRepository)


@pytest.mark.story_us_02_02
def test_resolve_repository_falls_back_to_in_memory_without_dsn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AEP_APP_POSTGRES_DSN", raising=False)
    monkeypatch.delenv("POSTGRES_DSN", raising=False)
    monkeypatch.delenv("APP_POSTGRES_DSN", raising=False)
    repo = _resolve_repository(Settings())
    assert isinstance(repo, InMemoryPlatformObjectRepository)
