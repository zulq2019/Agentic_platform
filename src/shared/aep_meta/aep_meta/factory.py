"""Factory helpers for tests and examples."""

from __future__ import annotations

from aep_meta.domain.enums import LifecycleState, PrimitiveType
from aep_meta.domain.models import (
    PlatformObject,
    PlatformObjectIdentity,
    PlatformObjectLifecycle,
    PlatformObjectVersioning,
)


def build_platform_object(
    *,
    tenant_id: str = "tenant-acme-corp",
    name: str = "sample-capability",
    namespace: str = "engineering",
    primitive_type: PrimitiveType = PrimitiveType.CAPABILITY,
    version: str = "1.0.0",
    owner: str = "user:platform-admin",
    created_by: str = "user:platform-admin",
) -> PlatformObject:
    identity = PlatformObjectIdentity(
        name=name,
        display_name="Sample Capability",
        description="Reference Platform Object for contract validation.",
        version=version,
        namespace=namespace,
        tenant_id=tenant_id,
        owner=owner,
        created_by=created_by,
        status=LifecycleState.DRAFT,
    )
    return PlatformObject(
        primitive_type=primitive_type,
        identity=identity,
        lifecycle=PlatformObjectLifecycle(state=LifecycleState.DRAFT),
        versioning=PlatformObjectVersioning(semantic_version=version),
    )
