"""Unit tests for aep_common structured logging. Story: US-01.06."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from aep_common.kafka.envelope import EventEnvelope
from aep_common.logging import (
    HEADER_TASK_ID,
    HEADER_TENANT_ID,
    HEADER_WORKFLOW_RUN_ID,
    _merge_correlation_ids,
    bind_correlation_from_envelope,
    bind_correlation_from_headers,
    bind_correlation_ids,
    clear_correlation_ids,
    correlation_context,
    get_logger,
    render_log_event,
    task_id_var,
    tenant_id_var,
    workflow_run_id_var,
)

TASK_ID = "t-550e8400-e29b-41d4-a716-446655440000"
WORKFLOW_RUN_ID = "wr-550e8400-e29b-41d4-a716-446655440000"
TENANT_ID = "tenant-acme-corp"


@pytest.mark.story_us_01_06
def test_ac_1_json_log_includes_correlation_ids_when_bound():
    """
    US-01.06: Given correlation IDs are bound, when a log event is rendered,
    then task_id, workflow_run_id, and tenant_id appear in the JSON output.
    """
    clear_correlation_ids()
    bind_correlation_ids(
        task_id=TASK_ID,
        workflow_run_id=WORKFLOW_RUN_ID,
        tenant_id=TENANT_ID,
    )

    rendered = render_log_event("task_dispatched")

    assert rendered["task_id"] == TASK_ID
    assert rendered["workflow_run_id"] == WORKFLOW_RUN_ID
    assert rendered["tenant_id"] == TENANT_ID
    assert rendered["event"] == "task_dispatched"


@pytest.mark.story_us_01_06
def test_ac_2_correlation_ids_omitted_when_not_bound():
    """
    US-01.06: Given no correlation context, when a log event is rendered,
    then correlation fields are absent from the JSON output.
    """
    clear_correlation_ids()

    rendered = render_log_event("service_starting")

    assert "task_id" not in rendered
    assert "workflow_run_id" not in rendered
    assert "tenant_id" not in rendered


@pytest.mark.story_us_01_06
def test_get_logger_binds_service_and_emitted_by():
    logger = get_logger("test-service")
    assert logger._context["service"] == "test-service"
    assert logger._context["emitted_by"] == "test-service"


@pytest.mark.story_us_01_06
def test_bind_correlation_from_headers_is_case_insensitive():
    clear_correlation_ids()
    bind_correlation_from_headers(
        {
            "X-Task-Id": TASK_ID,
            "X-Workflow-Run-Id": WORKFLOW_RUN_ID,
            "X-Tenant-Id": TENANT_ID,
        }
    )

    assert task_id_var.get() == TASK_ID
    assert workflow_run_id_var.get() == WORKFLOW_RUN_ID
    assert tenant_id_var.get() == TENANT_ID


@pytest.mark.story_us_01_06
def test_bind_correlation_from_envelope_model():
    clear_correlation_ids()
    envelope = EventEnvelope(
        event_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
        event_type="TaskCreated",
        timestamp=datetime.now(UTC),
        task_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
        workflow_run_id=UUID("550e8400-e29b-41d4-a716-446655440003"),
        tenant_id=TENANT_ID,
        emitted_by="orchestrator-service",
        payload={},
    )

    bind_correlation_from_envelope(envelope)

    assert task_id_var.get() == str(envelope.task_id)
    assert workflow_run_id_var.get() == str(envelope.workflow_run_id)
    assert tenant_id_var.get() == TENANT_ID


@pytest.mark.story_us_01_06
def test_correlation_context_restores_prior_values():
    clear_correlation_ids()
    bind_correlation_ids(task_id="outer-task", tenant_id="outer-tenant")

    with correlation_context(task_id="inner-task", tenant_id="inner-tenant"):
        assert task_id_var.get() == "inner-task"
        assert tenant_id_var.get() == "inner-tenant"

    assert task_id_var.get() == "outer-task"
    assert tenant_id_var.get() == "outer-tenant"


@pytest.mark.story_us_01_06
def test_correlation_header_constants_match_platform_contract():
    assert HEADER_TASK_ID == "x-task-id"
    assert HEADER_WORKFLOW_RUN_ID == "x-workflow-run-id"
    assert HEADER_TENANT_ID == "x-tenant-id"


def test_correlation_ids_merged_when_bound():
    clear_correlation_ids()
    bind_correlation_ids(
        task_id=TASK_ID,
        workflow_run_id=WORKFLOW_RUN_ID,
        tenant_id=TENANT_ID,
    )
    merged = _merge_correlation_ids(None, "info", {"event": "task_event"})
    assert merged["task_id"] == TASK_ID
    assert merged["workflow_run_id"] == WORKFLOW_RUN_ID
    assert merged["tenant_id"] == TENANT_ID


def test_correlation_ids_omitted_when_not_bound():
    clear_correlation_ids()
    merged = _merge_correlation_ids(None, "info", {"event": "startup"})
    assert "task_id" not in merged
    assert "workflow_run_id" not in merged
    assert "tenant_id" not in merged
