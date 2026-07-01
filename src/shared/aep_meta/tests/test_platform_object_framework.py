"""Unit tests for Platform Object framework (US-02.01)."""

from __future__ import annotations

import pytest

from aep_meta.application.platform_object_service import PlatformObjectService
from aep_meta.application.validation import PlatformObjectValidator
from aep_meta.domain.enums import LifecycleState, PrimitiveType
from aep_meta.domain.models import DependencyReference, PlatformObjectDependencies
from aep_meta.domain.lifecycle import LifecycleStateMachine
from aep_meta.exceptions import LifecycleTransitionError, ValidationError
from aep_meta.factory import build_platform_object
from aep_meta.infrastructure.in_memory_repository import InMemoryPlatformObjectRepository
from aep_meta.infrastructure.observability import InMemoryAuditRecorder, InMemoryMetricsRecorder
from aep_meta.infrastructure.schema_validator import JsonSchemaValidator


@pytest.fixture
def validator() -> PlatformObjectValidator:
    return PlatformObjectValidator(JsonSchemaValidator())


@pytest.fixture
def service(validator: PlatformObjectValidator) -> PlatformObjectService:
    return PlatformObjectService(
        repository=InMemoryPlatformObjectRepository(),
        validator=validator,
        audit=InMemoryAuditRecorder(),
        metrics=InMemoryMetricsRecorder(),
    )


@pytest.mark.story_us_02_01
def test_lifecycle_state_machine_allows_draft_to_review() -> None:
    assert LifecycleStateMachine.can_transition(LifecycleState.DRAFT, LifecycleState.REVIEW)


@pytest.mark.story_us_02_01
def test_lifecycle_state_machine_rejects_draft_to_active() -> None:
    assert not LifecycleStateMachine.can_transition(LifecycleState.DRAFT, LifecycleState.ACTIVE)


@pytest.mark.story_us_02_01
def test_platform_object_model_transition_updates_history() -> None:
    obj = build_platform_object()
    obj.transition_lifecycle(LifecycleState.REVIEW, actor="user:tester")
    assert obj.lifecycle.state == LifecycleState.REVIEW
    assert len(obj.lifecycle.transition_history) == 1


@pytest.mark.story_us_02_01
def test_invalid_lifecycle_transition_raises() -> None:
    obj = build_platform_object()
    with pytest.raises(LifecycleTransitionError):
        obj.transition_lifecycle(LifecycleState.ACTIVE, actor="user:tester")


@pytest.mark.story_us_02_01
def test_validator_accepts_valid_object(validator: PlatformObjectValidator) -> None:
    obj = build_platform_object()
    validator.validate(obj)


@pytest.mark.story_us_02_01
def test_validator_rejects_identity_lifecycle_mismatch(validator: PlatformObjectValidator) -> None:
    obj = build_platform_object()
    obj.identity.status = LifecycleState.ACTIVE
    with pytest.raises(ValidationError):
        validator.validate(obj)


@pytest.mark.story_us_02_01
def test_validator_detects_dependency_cycle(validator: PlatformObjectValidator) -> None:
    obj = build_platform_object()
    self_id = obj.identity.id
    obj.dependencies = PlatformObjectDependencies(
        depends_on=[
            DependencyReference(
                target_id=self_id,
                primitive_type=PrimitiveType.WORKFLOW,
                version_constraint="^1.0.0",
            )
        ]
    )
    with pytest.raises(ValidationError):
        validator.validate(obj)


@pytest.mark.story_us_02_01
@pytest.mark.asyncio
async def test_service_register_and_get(service: PlatformObjectService) -> None:
    obj = build_platform_object()
    saved = await service.register(obj, actor="user:tester")
    loaded = await service.get(saved.identity.tenant_id, saved.identity.id)
    assert loaded.identity.name == "sample-capability"


@pytest.mark.story_us_02_01
@pytest.mark.asyncio
async def test_service_lifecycle_transition(service: PlatformObjectService) -> None:
    obj = build_platform_object()
    saved = await service.register(obj, actor="user:tester")
    updated = await service.transition(
        saved.identity.tenant_id,
        saved.identity.id,
        LifecycleState.REVIEW,
        actor="user:reviewer",
    )
    assert updated.lifecycle.state == LifecycleState.REVIEW


@pytest.mark.story_us_02_01
def test_effective_configuration_merge() -> None:
    obj = build_platform_object()
    obj.configuration.defaults = {"a": 1, "b": 2}
    obj.configuration.customer_overrides = {"b": 3}
    assert obj.configuration.effective_configuration() == {"a": 1, "b": 3}
