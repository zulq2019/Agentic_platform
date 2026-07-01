"""Domain enumerations aligned with PLATFORM_PRIMITIVES.md."""

from __future__ import annotations

from enum import StrEnum


class PrimitiveType(StrEnum):
    STUDIO = "studio"
    CAPABILITY = "capability"
    WORKFLOW = "workflow"
    PROVIDER = "provider"
    EXECUTION_PROFILE = "execution-profile"
    POLICY = "policy"
    CONTEXT = "context"
    RESOURCE = "resource"
    ARTIFACT = "artifact"
    PLUGIN = "plugin"
    SOLUTION_PACK = "solution-pack"
    COMMERCIAL_PACK = "commercial-pack"
    ENTITLEMENT = "entitlement"


class LifecycleState(StrEnum):
    DRAFT = "Draft"
    REVIEW = "Review"
    APPROVED = "Approved"
    PUBLISHED = "Published"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"
    ARCHIVED = "Archived"
    RETIRED = "Retired"


class RelationshipType(StrEnum):
    PARENT = "parent"
    CHILD = "child"
    ASSOCIATION = "association"
    COMPOSITION = "composition"
    INHERITANCE = "inheritance"
    REFERENCE = "reference"
    LINKED = "linked"


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class SecurityVisibility(StrEnum):
    TENANT = "tenant"
    NAMESPACE = "namespace"
    RESTRICTED = "restricted"


class SecurityClassification(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
