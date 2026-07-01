"""In-memory audit and metrics adapters."""

from __future__ import annotations

from uuid import UUID, uuid4


class InMemoryAuditRecorder:
    def __init__(self) -> None:
        self.records: list[dict] = []

    async def record(
        self,
        *,
        tenant_id: str,
        object_id: UUID,
        action: str,
        actor: str,
        payload: dict,
    ) -> UUID:
        audit_id = uuid4()
        self.records.append(
            {
                "audit_id": audit_id,
                "tenant_id": tenant_id,
                "object_id": object_id,
                "action": action,
                "actor": actor,
                "payload": payload,
            }
        )
        return audit_id


class InMemoryMetricsRecorder:
    def __init__(self) -> None:
        self.counters: list[dict] = []

    def increment(
        self,
        *,
        tenant_id: str,
        object_id: UUID,
        primitive_type: str,
        metric: str,
        value: float = 1.0,
    ) -> None:
        self.counters.append(
            {
                "tenant_id": tenant_id,
                "object_id": object_id,
                "primitive_type": primitive_type,
                "metric": metric,
                "value": value,
            }
        )
