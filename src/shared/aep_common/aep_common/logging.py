"""Structured JSON logging factory with correlation ID support."""

from __future__ import annotations

import contextvars
import json
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any, cast

import structlog
from structlog.types import EventDict, WrappedLogger

HEADER_TASK_ID = "x-task-id"
HEADER_WORKFLOW_RUN_ID = "x-workflow-run-id"
HEADER_TENANT_ID = "x-tenant-id"

task_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "task_id", default=None
)
workflow_run_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "workflow_run_id", default=None
)
tenant_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "tenant_id", default=None
)

_configured = False


def _merge_correlation_ids(
    _logger: WrappedLogger, _method_name: str, event_dict: EventDict
) -> EventDict:
    for key, var in (
        ("task_id", task_id_var),
        ("workflow_run_id", workflow_run_id_var),
        ("tenant_id", tenant_id_var),
    ):
        value = var.get()
        if value is not None:
            event_dict[key] = value
    return event_dict


def bind_correlation_ids(
    *,
    task_id: str | None = None,
    workflow_run_id: str | None = None,
    tenant_id: str | None = None,
) -> None:
    """Bind correlation IDs for the current async context."""
    if task_id is not None:
        task_id_var.set(task_id)
    if workflow_run_id is not None:
        workflow_run_id_var.set(workflow_run_id)
    if tenant_id is not None:
        tenant_id_var.set(tenant_id)


def bind_correlation_from_headers(headers: Mapping[str, str]) -> None:
    """Bind correlation IDs from HTTP headers (case-insensitive keys)."""
    normalized = {key.lower(): value for key, value in headers.items()}
    bind_correlation_ids(
        task_id=normalized.get(HEADER_TASK_ID),
        workflow_run_id=normalized.get(HEADER_WORKFLOW_RUN_ID),
        tenant_id=normalized.get(HEADER_TENANT_ID),
    )


def bind_correlation_from_envelope(envelope: object) -> None:
    """Bind correlation IDs from an EventEnvelope or envelope-shaped mapping."""
    task_id: object | None
    workflow_run_id: object | None
    tenant_id: object | None

    if isinstance(envelope, Mapping):
        task_id = envelope.get("task_id")
        workflow_run_id = envelope.get("workflow_run_id")
        tenant_id = envelope.get("tenant_id")
    else:
        task_id = getattr(envelope, "task_id", None)
        workflow_run_id = getattr(envelope, "workflow_run_id", None)
        tenant_id = getattr(envelope, "tenant_id", None)

    bind_correlation_ids(
        task_id=str(task_id) if task_id is not None else None,
        workflow_run_id=str(workflow_run_id) if workflow_run_id is not None else None,
        tenant_id=str(tenant_id) if tenant_id is not None else None,
    )


def clear_correlation_ids() -> None:
    """Clear correlation IDs from the current context."""
    task_id_var.set(None)
    workflow_run_id_var.set(None)
    tenant_id_var.set(None)


@contextmanager
def correlation_context(
    *,
    task_id: str | None = None,
    workflow_run_id: str | None = None,
    tenant_id: str | None = None,
) -> Iterator[None]:
    """Bind correlation IDs for a block, then restore the prior context."""
    prior_task = task_id_var.get()
    prior_workflow = workflow_run_id_var.get()
    prior_tenant = tenant_id_var.get()
    bind_correlation_ids(
        task_id=task_id,
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )
    try:
        yield
    finally:
        task_id_var.set(prior_task)
        workflow_run_id_var.set(prior_workflow)
        tenant_id_var.set(prior_tenant)


def configure_structlog() -> None:
    """Configure structlog JSON processors once per process."""
    global _configured
    if _configured:
        return
    structlog.configure(
        processors=[
            _merge_correlation_ids,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    _configured = True


def get_logger(service: str) -> structlog.stdlib.BoundLogger:
    """Return a structured logger bound to the given service name."""
    configure_structlog()
    return cast(
        structlog.stdlib.BoundLogger,
        structlog.get_logger().bind(service=service, emitted_by=service),
    )


def render_log_event(event: str, **fields: Any) -> dict[str, Any]:
    """Render a log event dict as JSON with correlation IDs merged (test helper)."""
    event_dict: EventDict = {"event": event, **fields}
    merged = _merge_correlation_ids(None, "info", event_dict)
    rendered = structlog.processors.JSONRenderer()(None, "info", merged)
    return cast(dict[str, Any], json.loads(rendered))
