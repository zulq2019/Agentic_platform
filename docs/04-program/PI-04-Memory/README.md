# PI-04 — Memory

**Status:** `PLANNED`  
**Depends on:** PI-02 complete (MemoryClient stub replaced with real service)  
**Target:** Sprint 13–15 (weeks 25–30)

## Architecture v2 alignment

| Field | Value |
|-------|-------|
| **Classification** | Unchanged |
| **Report** | [ARCHITECTURE_ALIGNMENT_REPORT.md](../../engineering/ARCHITECTURE_ALIGNMENT_REPORT.md) |
| **Migration note** | Memory primitives and constitutional constraints (M1–M4) unchanged in v2. |

---

## What This PI Delivers

- `memory-service` manages two completely separate memory layers
- Working context (Redis, TTL 24h) — per-task, per-workflow, ephemeral
- Long-term memory (pgvector) — durable, deliberate writes, filtered retrieval
- `ContextAssembler` in orchestrator reads from both layers to build task context packets
- `PostWorkflowWriter` writes verified outcomes to LTM after workflow completes
- Cross-tenant memory leakage = 0 (verified by test suite)
- Memory queries always filter by `tenant_id` + `source_type` + `recency_weight`

## Key Constitutional Constraints

- Working context and LTM are SEPARATE services/classes — never merged (M1)
- LTM writes require explicit provenance (workflow_run_id + task_id + written_by) (M3)
- Vector search always includes metadata filters — no blind similarity search (M4)
- Agents NEVER write to LTM directly — only PostWorkflowWriter (M3, AI3)
