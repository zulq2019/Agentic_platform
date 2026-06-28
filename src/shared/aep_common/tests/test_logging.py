"""Unit tests for aep_common structured logging."""

from aep_common.logging import (
    _merge_correlation_ids,
    bind_correlation_ids,
    clear_correlation_ids,
    get_logger,
)


def test_get_logger_binds_service_and_emitted_by():
    logger = get_logger("test-service")
    assert logger._context["service"] == "test-service"
    assert logger._context["emitted_by"] == "test-service"


def test_correlation_ids_merged_when_bound():
    clear_correlation_ids()
    bind_correlation_ids(
        task_id="t-550e8400-e29b-41d4-a716-446655440000",
        workflow_run_id="wr-550e8400-e29b-41d4-a716-446655440000",
        tenant_id="tenant-acme-corp",
    )
    merged = _merge_correlation_ids(None, "info", {"event": "task_event"})
    assert merged["task_id"] == "t-550e8400-e29b-41d4-a716-446655440000"
    assert merged["workflow_run_id"] == "wr-550e8400-e29b-41d4-a716-446655440000"
    assert merged["tenant_id"] == "tenant-acme-corp"


def test_correlation_ids_omitted_when_not_bound():
    clear_correlation_ids()
    merged = _merge_correlation_ids(None, "info", {"event": "startup"})
    assert "task_id" not in merged
    assert "workflow_run_id" not in merged
    assert "tenant_id" not in merged
