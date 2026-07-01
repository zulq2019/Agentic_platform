"""Platform Object validation use cases."""

from __future__ import annotations

from uuid import UUID

from aep_meta.domain.enums import LifecycleState
from aep_meta.domain.models import PlatformObject
from aep_meta.domain.ports import SchemaValidatorPort
from aep_meta.exceptions import ValidationError


class PlatformObjectValidator:
    def __init__(self, schema_validator: SchemaValidatorPort) -> None:
        self._schema = schema_validator

    def validate(self, obj: PlatformObject) -> None:
        errors: list[str] = []

        if obj.identity.status != obj.lifecycle.state:
            errors.append("identity.status must match lifecycle.state")

        if obj.versioning.semantic_version != obj.identity.version:
            errors.append("versioning.semantic_version must match identity.version")

        try:
            self._schema.validate_contract(obj.to_contract_dict())
        except ValidationError as exc:
            errors.extend(exc.errors)
        except Exception as exc:  # jsonschema raises JSONSchemaValidationError
            errors.append(str(exc))

        if self._has_dependency_cycle(obj):
            errors.append("circular dependency detected in depends_on graph")

        if errors:
            raise ValidationError("Platform Object validation failed", errors=errors)

    @staticmethod
    def _has_dependency_cycle(obj: PlatformObject) -> bool:
        graph: dict[UUID, list[UUID]] = {obj.identity.id: []}
        for dep in obj.dependencies.depends_on:
            graph.setdefault(obj.identity.id, []).append(dep.target_id)
            graph.setdefault(dep.target_id, [])

        visited: set[UUID] = set()
        stack: set[UUID] = set()

        def visit(node: UUID) -> bool:
            if node in stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            stack.add(node)
            for neighbour in graph.get(node, []):
                if visit(neighbour):
                    return True
            stack.remove(node)
            return False

        return visit(obj.identity.id)

    def validate_transition(
        self, obj: PlatformObject, target: LifecycleState
    ) -> None:
        from aep_meta.domain.lifecycle import LifecycleStateMachine

        if not LifecycleStateMachine.can_transition(obj.lifecycle.state, target):
            raise ValidationError(
                f"lifecycle transition {obj.lifecycle.state.value} -> {target.value} "
                "is not permitted"
            )
