"""Platform Object application service."""

from __future__ import annotations

from uuid import UUID

from aep_meta.application.validation import PlatformObjectValidator
from aep_meta.domain.enums import LifecycleState
from aep_meta.domain.models import PlatformObject
from aep_meta.domain.ports import AuditRecorderPort, MetricsRecorderPort, PlatformObjectRepository
from aep_meta.exceptions import NotFoundError


class PlatformObjectService:
    def __init__(
        self,
        repository: PlatformObjectRepository,
        validator: PlatformObjectValidator,
        audit: AuditRecorderPort | None = None,
        metrics: MetricsRecorderPort | None = None,
    ) -> None:
        self._repository = repository
        self._validator = validator
        self._audit = audit
        self._metrics = metrics

    async def register(self, obj: PlatformObject, *, actor: str) -> PlatformObject:
        self._validator.validate(obj)
        saved = await self._repository.save(obj)
        await self._record_audit(
            saved, action="register", actor=actor, payload={"primitive_type": saved.primitive_type.value}
        )
        self._record_metric(saved, "register")
        return saved

    async def get(self, tenant_id: str, object_id: UUID) -> PlatformObject:
        obj = await self._repository.get_by_id(tenant_id, object_id)
        if obj is None:
            raise NotFoundError(f"platform object {object_id} not found for tenant {tenant_id}")
        return obj

    async def list_objects(
        self, tenant_id: str, *, namespace: str | None = None
    ) -> list[PlatformObject]:
        return await self._repository.list_by_tenant(tenant_id, namespace=namespace)

    async def transition(
        self,
        tenant_id: str,
        object_id: UUID,
        target: LifecycleState,
        *,
        actor: str,
        reason: str | None = None,
    ) -> PlatformObject:
        obj = await self.get(tenant_id, object_id)
        self._validator.validate_transition(obj, target)
        obj.transition_lifecycle(target, actor=actor, reason=reason)
        self._validator.validate(obj)
        saved = await self._repository.save(obj)
        await self._record_audit(
            saved,
            action="lifecycle_transition",
            actor=actor,
            payload={"to_state": target.value, "reason": reason},
        )
        self._record_metric(saved, "lifecycle_transition")
        return saved

    async def _record_audit(
        self,
        obj: PlatformObject,
        *,
        action: str,
        actor: str,
        payload: dict,
    ) -> None:
        if self._audit is None:
            return
        audit_id = await self._audit.record(
            tenant_id=obj.identity.tenant_id,
            object_id=obj.identity.id,
            action=action,
            actor=actor,
            payload=payload,
        )
        obj.attach_audit_ref(audit_id)
        await self._repository.save(obj)

    def _record_metric(self, obj: PlatformObject, metric: str) -> None:
        if self._metrics is None:
            return
        self._metrics.increment(
            tenant_id=obj.identity.tenant_id,
            object_id=obj.identity.id,
            primitive_type=obj.primitive_type.value,
            metric=metric,
        )
