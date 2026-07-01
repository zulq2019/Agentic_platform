"""Integration tests for metadata-engine Platform Object API (US-02.01)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from metadata_engine.dependencies import build_platform_object_service, reset_service_for_tests
from metadata_engine.main import create_app

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "contracts" / "examples" / "sample-platform-object.json"


@pytest.fixture(autouse=True)
def _reset_metadata_service() -> None:
    reset_service_for_tests()


@pytest.fixture
def example_payload() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


@pytest.mark.story_us_02_01
@pytest.mark.asyncio
async def test_register_and_fetch_platform_object_via_api(example_payload: dict) -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post("/api/v1/platform-objects", json=example_payload)
        assert create_response.status_code == 201
        body = create_response.json()
        object_id = body["identity"]["id"]
        tenant_id = body["identity"]["tenant_id"]

        get_response = await client.get(
            f"/api/v1/platform-objects/{object_id}",
            params={"tenant_id": tenant_id},
        )
        assert get_response.status_code == 200
        assert get_response.json()["identity"]["name"] == "generates-unit-tests"


@pytest.mark.story_us_02_01
@pytest.mark.asyncio
async def test_lifecycle_transition_via_api(example_payload: dict) -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/api/v1/platform-objects", json=example_payload)
        body = created.json()
        object_id = body["identity"]["id"]
        tenant_id = body["identity"]["tenant_id"]

        transition = await client.post(
            f"/api/v1/platform-objects/{object_id}/lifecycle/transitions",
            params={"tenant_id": tenant_id},
            json={
                "target_state": "Review",
                "actor": "user:reviewer",
                "reason": "ready for governance",
            },
        )
        assert transition.status_code == 200
        assert transition.json()["lifecycle"]["state"] == "Review"
