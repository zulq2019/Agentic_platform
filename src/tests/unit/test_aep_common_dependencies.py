"""Unit tests for aep_common dependency health checks. Story: US-01.01."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aep_common.dependencies import check_kafka, check_postgres, check_redis


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_check_postgres_returns_error_when_dsn_empty():
    assert await check_postgres("") == "error"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_check_postgres_returns_ok_when_select_succeeds():
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=1)
    mock_conn.close = AsyncMock()

    with patch("aep_common.dependencies.asyncpg.connect", new=AsyncMock(return_value=mock_conn)):
        result = await check_postgres("postgresql://aep:aep@localhost:5432/aep")

    assert result == "ok"
    mock_conn.fetchval.assert_awaited_once()


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_check_postgres_returns_error_on_connection_failure():
    with patch(
        "aep_common.dependencies.asyncpg.connect",
        new=AsyncMock(side_effect=ConnectionRefusedError("refused")),
    ):
        result = await check_postgres("postgresql://aep:aep@localhost:5432/aep")

    assert result == "error"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_check_kafka_returns_error_when_bootstrap_servers_empty():
    assert await check_kafka("") == "error"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_check_kafka_returns_ok_when_tcp_connects():
    with patch("aep_common.dependencies.asyncio.to_thread", new=AsyncMock(return_value=None)):
        result = await check_kafka("kafka:9092")

    assert result == "ok"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_check_kafka_returns_error_when_tcp_fails():
    with patch(
        "aep_common.dependencies.asyncio.to_thread",
        new=AsyncMock(side_effect=ConnectionRefusedError("refused")),
    ):
        result = await check_kafka("kafka:9092")

    assert result == "error"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_check_redis_returns_error_when_url_empty():
    assert await check_redis("") == "error"


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_check_redis_returns_ok_when_ping_succeeds():
    mock_client = MagicMock()
    mock_client.ping = AsyncMock(return_value=True)
    mock_client.aclose = AsyncMock()

    with patch("aep_common.dependencies.Redis.from_url", return_value=mock_client):
        result = await check_redis("redis://localhost:6379/0")

    assert result == "ok"
    mock_client.ping.assert_awaited_once()


@pytest.mark.story_us_01_01
@pytest.mark.asyncio
async def test_check_redis_returns_error_when_ping_fails():
    mock_client = MagicMock()
    mock_client.ping = AsyncMock(side_effect=ConnectionRefusedError("refused"))
    mock_client.aclose = AsyncMock()

    with patch("aep_common.dependencies.Redis.from_url", return_value=mock_client):
        result = await check_redis("redis://localhost:6379/0")

    assert result == "error"
