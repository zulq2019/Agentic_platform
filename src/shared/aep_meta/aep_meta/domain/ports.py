"""Hexagonal architecture ports."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from aep_meta.domain.models import PlatformObject


class PlatformObjectRepository(Protocol):
    async def save(self, obj: PlatformObject) -> PlatformObject: ...

    async def get_by_id(self, tenant_id: str, object_id: UUID) -> PlatformObject | None: ...

    async def list_by_tenant(
        self, tenant_id: str, *, namespace: str | None = None
    ) -> list[PlatformObject]: ...


class SchemaValidatorPort(Protocol):
    def validate_contract(self, document: dict) -> None: ...


class AuditRecorderPort(Protocol):
    async def record(
        self,
        *,
        tenant_id: str,
        object_id: UUID,
        action: str,
        actor: str,
        payload: dict,
    ) -> UUID: ...


class MetricsRecorderPort(Protocol):
    def increment(
        self,
        *,
        tenant_id: str,
        object_id: UUID,
        primitive_type: str,
        metric: str,
        value: float = 1.0,
    ) -> None: ...
