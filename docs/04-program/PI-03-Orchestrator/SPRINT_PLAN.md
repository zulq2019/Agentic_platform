# PI-03 — Sprint Plan

## Sprint 9 (Days 81–90): Workflow Engine + Task Engine

| # | Task | Points |
|---|------|--------|
| 9.1 | Implement `workflow-engine` TemplateLoader — load greenfield-v1.0.0.json | 3 |
| 9.2 | Implement `workflow-engine` StateMachineProcessor — pure state transition | 3 |
| 9.3 | Implement `workflow-engine` TransitionValidator — pre-condition checks | 2 |
| 9.4 | Implement `task-engine` write-before-act persistence | 3 |
| 9.5 | Implement `task-engine` task state machine (pending → running → complete/failed) | 3 |

**Sprint Goal:** State machine loads template and validates transitions. Tasks persisted.

---

## Sprint 10 (Days 91–100): Orchestrator Planner + Dispatcher

| # | Task | Points |
|---|------|--------|
| 10.1 | Implement `PlannerService` — decompose workflow into ordered task list | 3 |
| 10.2 | Implement `AgentSelector` — query agent-registry by capability tag | 2 |
| 10.3 | Implement `ContextAssembler` — build explicit context packet per task | 3 |
| 10.4 | Implement `CostAwareDispatcher` — classify + route to model tier | 2 |
| 10.5 | Implement `TaskCreated` event publish via Kafka | 2 |
| 10.6 | Integration test: workflow POST → TaskCreated consumed by agent-runtime | 3 |

**Sprint Goal:** Orchestrator dispatches tasks. Agent-runtime processes them.

---

## Sprint 11 (Days 101–110): Gate Enforcer + Approval Service

| # | Task | Points |
|---|------|--------|
| 11.1 | Implement `GateEnforcer` — blocks state transition without approval_record | 4 |
| 11.2 | Implement `approval-service` gate management API | 3 |
| 11.3 | Implement `approval-service` Kafka consumer for ApprovalRequested | 2 |
| 11.4 | Implement `approval-service` decision recording (ApprovalGranted/Denied) | 3 |
| 11.5 | Test: gate blocks without approval, passes with approval, no bypass exists | 3 |

**Sprint Goal:** Human gates non-bypassable. Approval service operational.

---

## Sprint 12 (Days 111–120): Failure Recovery + PI-03 Close

| # | Task | Points |
|---|------|--------|
| 12.1 | Implement `RetryCompensationManager` Tier 2 (saga) | 3 |
| 12.2 | Implement `RetryCompensationManager` Tier 3 (human escalation) | 3 |
| 12.3 | Implement `RollbackStrategist` per-workflow rollback | 2 |
| 12.4 | Chaos test: kill orchestrator mid-workflow, verify resume | 2 |
| 12.5 | End-to-end greenfield workflow test with all gates | 3 |
| 12.6 | PI-03 retrospective + PI-04 kick-off | 1 |

**Sprint Goal:** All failure tiers working. Platform restart recovers workflows.
