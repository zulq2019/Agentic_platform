"""Structured JSON logging factory with correlation ID support."""

from __future__ import annotations

import contextvars
from typing import cast

import structlog
from structlog.types import EventDict, WrappedLogger

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


def clear_correlation_ids() -> None:
    """Clear correlation IDs from the current context."""
    task_id_var.set(None)
    workflow_run_id_var.set(None)
    tenant_id_var.set(None)


def get_logger(service: str) -> structlog.stdlib.BoundLogger:
    """Return a structured logger bound to the given service name."""
    global _configured
    if not _configured:
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
    return cast(
        structlog.stdlib.BoundLogger,
        structlog.get_logger().bind(service=service, emitted_by=service),
    )
