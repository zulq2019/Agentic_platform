# PI-03 — Orchestrator

**Status:** `PLANNED`  
**Depends on:** PI-02 complete  
**Target:** Sprint 9–12 (weeks 17–24)

## Architecture v2 alignment

| Field | Value |
|-------|-------|
| **Classification** | Extended |
| **v2 concept** | Planner + Workflow Framework |
| **Report** | [ARCHITECTURE_ALIGNMENT_REPORT.md](../../architecture-alignment/ARCHITECTURE_ALIGNMENT_REPORT.md) |
| **Migration note** | Greenfield JSON template remains MVP authority. Workflow Platform Objects deferred (G-09). |

---

## What This PI Delivers

The Orchestrator is the brain of the platform. It plans, dispatches, enforces human gates, and recovers from failures — but never executes anything itself.

- `orchestrator-service` decomposes a workflow request into tasks and dispatches them
- `workflow-engine` loads workflow templates and manages state machine transitions
- `task-engine` persists every task before it is acted upon (write-before-act)
- `approval-service` manages human-in-the-loop gates (non-bypassable)
- Tier 2 (saga compensation) and Tier 3 (human escalation) retry implemented
- Full greenfield workflow runs end-to-end with all gates requiring real approval records

## Key Constitutional Constraints

- Orchestrator MUST NOT contain any LLM call, code generation, or test execution logic (A2)
- Gate transitions MUST be blocked without an `approval_record` — no bypass flag exists (H2)
- Every task MUST be persisted before dispatched — write-before-act (T1)
