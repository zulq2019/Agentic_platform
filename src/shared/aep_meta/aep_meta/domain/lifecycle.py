"""Universal lifecycle state machine — PLATFORM_PRIMITIVES.md §3.4."""

from __future__ import annotations

from aep_meta.domain.enums import LifecycleState

_ALLOWED: dict[LifecycleState, frozenset[LifecycleState]] = {
    LifecycleState.DRAFT: frozenset({LifecycleState.REVIEW}),
    LifecycleState.REVIEW: frozenset({LifecycleState.APPROVED, LifecycleState.DRAFT}),
    LifecycleState.APPROVED: frozenset({LifecycleState.PUBLISHED}),
    LifecycleState.PUBLISHED: frozenset({LifecycleState.ACTIVE}),
    LifecycleState.ACTIVE: frozenset({LifecycleState.DEPRECATED, LifecycleState.RETIRED}),
    LifecycleState.DEPRECATED: frozenset({LifecycleState.ARCHIVED}),
    LifecycleState.ARCHIVED: frozenset({LifecycleState.RETIRED}),
    LifecycleState.RETIRED: frozenset(),
}


class LifecycleStateMachine:
    @staticmethod
    def can_transition(current: LifecycleState, target: LifecycleState) -> bool:
        return target in _ALLOWED.get(current, frozenset())

    @staticmethod
    def allowed_targets(current: LifecycleState) -> frozenset[LifecycleState]:
        return _ALLOWED.get(current, frozenset())
