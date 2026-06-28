# PI-04 — Sprint Plan

## Sprint 13 (Days 121–130): Working Context Service

| # | Task | Points |
|---|------|--------|
| 13.1 | Implement `WorkingContextService.set(task_id, key, value)` — Redis TTL 24h | 3 |
| 13.2 | Implement `WorkingContextService.get(task_id, key)` | 2 |
| 13.3 | Implement `WorkingContextService.get_all(task_id)` | 1 |
| 13.4 | Wire `ContextAssembler` in orchestrator to read working context | 2 |
| 13.5 | Update `aep-agent-sdk` MemoryClient to use real memory-service | 2 |
| 13.6 | Tests: working context TTL expires after 24h | 2 |

**Sprint Goal:** Agents can read/write working context across a workflow.

---

## Sprint 14 (Days 131–140): Long-Term Memory

| # | Task | Points |
|---|------|--------|
| 14.1 | Implement `LongTermMemoryService.query(tenant_id, source_type, embedding, limit)` | 4 |
| 14.2 | Implement `LongTermMemoryService.write(entry)` with provenance validation | 3 |
| 14.3 | Implement embedding generation (OpenAI text-embedding-3-small or equivalent) | 2 |
| 14.4 | Implement `recency_weight` decay — older entries receive lower weight | 2 |
| 14.5 | Test: query without tenant_id filter raises error — no blind search allowed | 2 |

**Sprint Goal:** LTM queryable with filtered vector search.

---

## Sprint 15 (Days 141–150): PostWorkflowWriter + PI-04 Close

| # | Task | Points |
|---|------|--------|
| 15.1 | Implement `PostWorkflowWriter` — triggered on workflow terminal state | 3 |
| 15.2 | Implement LTM write gate: only verified outcomes written | 3 |
| 15.3 | Cross-tenant isolation test: tenant A memory not visible to tenant B | 3 |
| 15.4 | Memory service load test: 10,000 queries/hour on pgvector | 2 |
| 15.5 | PI-04 retrospective + PI-05 kick-off | 1 |

**Sprint Goal:** Full memory architecture operational. Zero cross-tenant leakage.
