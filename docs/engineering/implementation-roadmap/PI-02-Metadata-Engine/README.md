# PI-02 — Agent Runtime

**Status:** `PLANNED`  
**Depends on:** PI-01 complete  
**Target:** Sprint 5–8 (weeks 9–16)  
**Owner:** Agent Runtime Lead

## Architecture v2 alignment

| Field | Value |
|-------|-------|
| **Classification** | Renamed (conceptual) + Extended |
| **v2 concept** | Provider Framework — hosts `provider_kind: ai-agent` |
| **Report** | [ARCHITECTURE_ALIGNMENT_REPORT.md](../../architecture-alignment/ARCHITECTURE_ALIGNMENT_REPORT.md) |
| **Migration note** | Service paths unchanged. O3 evolves to Execution Profile resolution when PI-09 delivers schema (G-04). |

---

## What This PI Delivers

The Agent Runtime is the execution host for all specialist agents. By the end of PI-02:

- `agent-runtime` service receives `TaskCreated` events, executes agents, publishes results
- `agent-registry` service stores and resolves agents by capability tag
- `model-router` service routes tasks to the correct LLM tier based on cost_class
- The `aep-agent-sdk` Python package provides the base class all agents inherit
- A reference agent (`echo-agent`) demonstrates the full SDK contract
- Retry logic (Tier 1: exponential backoff) is operational
- Every agent execution produces a distributed trace and structured log

## Handoff Requirements from PI-01

- All 16 service skeletons running
- Kafka topics provisioned
- `agents.registrations` table migrated
- `aep-common` importable

## Handoff to PI-03

PI-03 (Orchestrator) requires:
- `agent-runtime` consuming `aep.task.created` and producing `aep.agent.completed` / `aep.agent.failed`
- `agent-registry` resolving agents by capability tag via REST
- `model-router` accepting a `cost_class` and returning a model endpoint
- `aep-agent-sdk` installable from the monorepo
