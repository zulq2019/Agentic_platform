"""Structured JSON logging factory."""

import structlog


def get_logger(service: str) -> structlog.stdlib.BoundLogger:
    """Return a structured logger bound to the given service name."""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger().bind(service=service)
