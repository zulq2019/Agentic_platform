"""Domain-specific errors."""

from __future__ import annotations


class PlatformObjectError(Exception):
    """Base error for Platform Object operations."""


class ValidationError(PlatformObjectError):
    """Raised when object or contract validation fails."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


class LifecycleTransitionError(PlatformObjectError):
    """Raised when a lifecycle transition is not permitted."""


class DependencyCycleError(PlatformObjectError):
    """Raised when a circular dependency is detected."""


class NotFoundError(PlatformObjectError):
    """Raised when a Platform Object cannot be resolved."""
