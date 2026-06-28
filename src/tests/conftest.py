"""Shared fixtures for US-01.01 platform spine tests."""

from __future__ import annotations

import pytest

from services import stack_is_running


@pytest.fixture
def requires_stack():
    if not stack_is_running():
        pytest.skip("Docker compose stack not running — start with make dev-up")
