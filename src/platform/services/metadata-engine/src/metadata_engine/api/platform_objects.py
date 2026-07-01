"""REST API for Platform Objects — US-02.01."""

from __future__ import annotations

from uuid import UUID

from aep_meta.domain.enums import LifecycleState
from aep_meta.domain.models import PlatformObject
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from metadata_engine.dependencies import build_platform_object_service
from aep_meta.application.platform_object_service import PlatformObjectService
from aep_meta.exceptions import NotFoundError, PlatformObjectError, ValidationError

router = APIRouter(prefix="/api/v1/platform-objects", tags=["platform-objects"])


def get_service() -> PlatformObjectService:
    return build_platform_object_service()


class TransitionRequest(BaseModel):
    target_state: LifecycleState
    actor: str = Field(min_length=1)
    reason: str | None = None


@router.post("", response_model=dict, status_code=201)
async def register_platform_object(
    payload: dict,
    service: PlatformObjectService = Depends(get_service),
) -> dict:
    try:
        obj = PlatformObject.from_contract_dict(payload)
        actor = obj.identity.created_by
        saved = await service.register(obj, actor=actor)
        return saved.to_contract_dict()
    except ValidationError as exc:
        raise HTTPException(
            status_code=422, detail={"message": str(exc), "errors": exc.errors}
        ) from exc
    except PlatformObjectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{object_id}", response_model=dict)
async def get_platform_object(
    object_id: UUID,
    tenant_id: str,
    service: PlatformObjectService = Depends(get_service),
) -> dict:
    try:
        obj = await service.get(tenant_id, object_id)
        return obj.to_contract_dict()
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("", response_model=list[dict])
async def list_platform_objects(
    tenant_id: str,
    namespace: str | None = None,
    service: PlatformObjectService = Depends(get_service),
) -> list[dict]:
    objects = await service.list_objects(tenant_id, namespace=namespace)
    return [obj.to_contract_dict() for obj in objects]


@router.post("/{object_id}/lifecycle/transitions", response_model=dict)
async def transition_platform_object(
    object_id: UUID,
    tenant_id: str,
    body: TransitionRequest,
    service: PlatformObjectService = Depends(get_service),
) -> dict:
    try:
        saved = await service.transition(
            tenant_id,
            object_id,
            body.target_state,
            actor=body.actor,
            reason=body.reason,
        )
        return saved.to_contract_dict()
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=422, detail={"message": str(exc), "errors": exc.errors}
        ) from exc
    except PlatformObjectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
