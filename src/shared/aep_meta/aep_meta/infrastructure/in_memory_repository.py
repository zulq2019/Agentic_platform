"""In-memory Platform Object repository for tests and local development."""

from __future__ import annotations

from uuid import UUID

from aep_meta.domain.models import PlatformObject


class InMemoryPlatformObjectRepository:
    def __init__(self) -> None:
        self._store: dict[tuple[str, UUID], PlatformObject] = {}

    async def save(self, obj: PlatformObject) -> PlatformObject:
        key = (obj.identity.tenant_id, obj.identity.id)
        self._store[key] = PlatformObject.from_contract_dict(obj.to_contract_dict())
        return self._store[key]

    async def get_by_id(self, tenant_id: str, object_id: UUID) -> PlatformObject | None:
        return self._store.get((tenant_id, object_id))

    async def list_by_tenant(
        self, tenant_id: str, *, namespace: str | None = None
    ) -> list[PlatformObject]:
        items = [obj for (tid, _), obj in self._store.items() if tid == tenant_id]
        if namespace is not None:
            items = [obj for obj in items if obj.identity.namespace == namespace]
        return items
