"""Platform Object sub-models and aggregate root."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from aep_meta.domain.enums import (
    HealthStatus,
    LifecycleState,
    PrimitiveType,
    RelationshipType,
    RiskLevel,
    SecurityClassification,
    SecurityVisibility,
)
from aep_meta.domain.lifecycle import LifecycleStateMachine
from aep_meta.exceptions import LifecycleTransitionError

KEBAB_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"


class PlatformObjectIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
    display_name: str
    description: str
    version: str
    namespace: str
    tenant_id: str
    owner: str
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: LifecycleState = LifecycleState.DRAFT
    tags: list[str] = Field(default_factory=list)
    category: str | None = None

    @field_validator("name", "namespace", "tenant_id")
    @classmethod
    def validate_kebab(cls, value: str) -> str:
        import re

        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", value):
            raise ValueError(f"must be kebab-case: {value}")
        return value


class PlatformObjectMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    business: dict[str, Any] = Field(default_factory=dict)
    technical: dict[str, Any] = Field(default_factory=dict)
    custom: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    classification: str | None = None
    documentation_links: list[str] = Field(default_factory=list)
    examples: list[dict[str, Any]] = Field(default_factory=list)


class ConfigurationHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recorded_at: datetime
    snapshot: dict[str, Any]


class PlatformObjectConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    defaults: dict[str, Any] = Field(default_factory=dict)
    customer_overrides: dict[str, Any] = Field(default_factory=dict)
    environment_overrides: dict[str, Any] = Field(default_factory=dict)
    validation_schema_ref: str | None = None
    templates: list[dict[str, Any]] = Field(default_factory=list)
    history: list[ConfigurationHistoryEntry] = Field(default_factory=list)

    def effective_configuration(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        merged.update(self.defaults)
        merged.update(self.customer_overrides)
        merged.update(self.environment_overrides)
        return merged


class LifecycleTransitionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_state: LifecycleState
    to_state: LifecycleState
    actor: str
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str | None = None


class PlatformObjectLifecycle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: LifecycleState = LifecycleState.DRAFT
    transition_history: list[LifecycleTransitionRecord] = Field(default_factory=list)

    def transition_to(
        self, target: LifecycleState, *, actor: str, reason: str | None = None
    ) -> None:
        if not LifecycleStateMachine.can_transition(self.state, target):
            raise LifecycleTransitionError(
                f"transition {self.state.value} -> {target.value} is not permitted"
            )
        record = LifecycleTransitionRecord(
            from_state=self.state,
            to_state=target,
            actor=actor,
            reason=reason,
        )
        self.transition_history.append(record)
        self.state = target


class DependencyReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_id: UUID
    primitive_type: PrimitiveType
    version_constraint: str
    optional: bool = False
    runtime_required: bool = True


class PlatformObjectDependencies(BaseModel):
    model_config = ConfigDict(extra="forbid")

    depends_on: list[DependencyReference] = Field(default_factory=list)
    required_by: list[DependencyReference] = Field(default_factory=list)
    optional: list[DependencyReference] = Field(default_factory=list)


class RelationshipEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: RelationshipType
    target_id: UUID
    target_primitive_type: PrimitiveType
    version_constraint: str | None = None
    pin: str | None = None


class PlatformObjectRelationships(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parent_id: UUID | None = None
    edges: list[RelationshipEdge] = Field(default_factory=list)


class RbacBinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str
    principal: str


class PlatformObjectSecurity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visibility: SecurityVisibility = SecurityVisibility.TENANT
    classification: SecurityClassification = SecurityClassification.INTERNAL
    rbac_bindings: list[RbacBinding] = Field(default_factory=list)
    secret_refs: list[str] = Field(default_factory=list)
    approval_requirements: list[str] = Field(default_factory=list)


class DependencyHealth(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dependency_id: UUID
    status: str


class PlatformObjectHealth(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: HealthStatus = HealthStatus.UNKNOWN
    last_checked_at: datetime | None = None
    dependency_health: list[DependencyHealth] = Field(default_factory=list)


class PlatformObjectMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invocation_count: int = 0
    error_count: int = 0
    last_invoked_at: datetime | None = None


class PlatformObjectObservability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    health: PlatformObjectHealth = Field(default_factory=PlatformObjectHealth)
    metrics: PlatformObjectMetrics = Field(default_factory=PlatformObjectMetrics)
    audit_ref_ids: list[UUID] = Field(default_factory=list)


class PlatformObjectGovernance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: RiskLevel = RiskLevel.LOW
    business_owner: str | None = None
    technical_owner: str | None = None
    compliance_tags: list[str] = Field(default_factory=list)
    retention_policy_ref: str | None = None


class PublishedVersionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    published_at: datetime
    changelog: str | None = None


class PlatformObjectVersioning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    semantic_version: str
    draft_version: str | None = None
    published_versions: list[PublishedVersionRecord] = Field(default_factory=list)
    compatibility_matrix: list[dict[str, Any]] = Field(default_factory=list)
    migration_rules: list[dict[str, Any]] = Field(default_factory=list)


class PlatformObjectExtensions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plugin_refs: list[UUID] = Field(default_factory=list)
    hook_refs: list[str] = Field(default_factory=list)
    event_subscriptions: list[str] = Field(default_factory=list)
    callback_refs: list[str] = Field(default_factory=list)
    policy_refs: list[UUID] = Field(default_factory=list)
    custom_actions: list[str] = Field(default_factory=list)
    custom_metadata_schema_ref: str | None = None


class PlatformObject(BaseModel):
    """Aggregate root for the universal Platform Object envelope."""

    model_config = ConfigDict(extra="forbid")

    contract_version: str = "1.0.0"
    primitive_type: PrimitiveType
    identity: PlatformObjectIdentity
    metadata: PlatformObjectMetadata = Field(default_factory=PlatformObjectMetadata)
    configuration: PlatformObjectConfiguration = Field(
        default_factory=PlatformObjectConfiguration
    )
    lifecycle: PlatformObjectLifecycle = Field(default_factory=PlatformObjectLifecycle)
    dependencies: PlatformObjectDependencies = Field(
        default_factory=PlatformObjectDependencies
    )
    relationships: PlatformObjectRelationships = Field(
        default_factory=PlatformObjectRelationships
    )
    security: PlatformObjectSecurity = Field(default_factory=PlatformObjectSecurity)
    observability: PlatformObjectObservability = Field(
        default_factory=PlatformObjectObservability
    )
    governance: PlatformObjectGovernance = Field(default_factory=PlatformObjectGovernance)
    versioning: PlatformObjectVersioning
    extensions: PlatformObjectExtensions = Field(
        default_factory=PlatformObjectExtensions
    )

    def touch(self, *, modified_at: datetime | None = None) -> None:
        self.identity.modified_at = modified_at or datetime.now(timezone.utc)
        self.identity.status = self.lifecycle.state

    def transition_lifecycle(
        self, target: LifecycleState, *, actor: str, reason: str | None = None
    ) -> None:
        self.lifecycle.transition_to(target, actor=actor, reason=reason)
        self.touch()

    def record_metric_invocation(self, *, success: bool = True) -> None:
        self.observability.metrics.invocation_count += 1
        if not success:
            self.observability.metrics.error_count += 1
        self.observability.metrics.last_invoked_at = datetime.now(timezone.utc)
        self.touch()

    def attach_audit_ref(self, audit_id: UUID) -> None:
        if audit_id not in self.observability.audit_ref_ids:
            self.observability.audit_ref_ids.append(audit_id)
        self.touch()

    def to_contract_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)

    @classmethod
    def from_contract_dict(cls, data: dict[str, Any]) -> PlatformObject:
        return cls.model_validate(data)
