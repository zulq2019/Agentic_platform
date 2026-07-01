"""Unit tests for Postgres repository helpers (US-02.02)."""

from __future__ import annotations

import json

import pytest

from aep_meta.infrastructure.postgres_repository import (
    PostgresPlatformObjectRepository,
    parse_envelope,
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
