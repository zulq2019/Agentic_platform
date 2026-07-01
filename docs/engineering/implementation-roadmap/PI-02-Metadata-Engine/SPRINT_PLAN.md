# PI-02 — Sprint Plan

## Sprint 5 (Days 41–50): Agent Registry + SDK Base

| # | Task | Points |
|---|------|--------|
| 5.1 | Implement `agent-registry` POST /agents — register agent with contract validation | 3 |
| 5.2 | Implement `agent-registry` GET /agents?capability={tag} — capability-based query | 3 |
| 5.3 | Implement `aep-agent-sdk` base `Agent` class with execute() lifecycle | 3 |
| 5.4 | Implement `aep-agent-sdk` ToolClient (stub — resolves by capability tag) | 2 |
| 5.5 | Implement `aep-agent-sdk` MemoryClient (stub) | 1 |
| 5.6 | Implement `aep-agent-sdk` EventClient (publishes AgentStarted/Completed/Failed) | 2 |
| 5.7 | Write `echo-agent` reference implementation | 2 |

**Sprint Goal:** Agent registered in registry, echo-agent runs and publishes events.

---

## Sprint 6 (Days 51–60): Agent Runtime Executor

| # | Task | Points |
|---|------|--------|
| 6.1 | Implement `agent-runtime` Kafka consumer for `aep.task.created` | 3 |
| 6.2 | Implement `AgentLoader` — dynamic import + contract validation at load time | 3 |
| 6.3 | Implement `AgentExecutor` — orchestrates agent lifecycle, calls execute() | 3 |
| 6.4 | Implement `IdempotencyKeyResolver` — prevents duplicate side-effects on retry | 2 |
| 6.5 | Integration test: TaskCreated → AgentCompleted round-trip | 3 |

**Sprint Goal:** Full task lifecycle working end-to-end on Kafka.

---

## Sprint 7 (Days 61–70): Model Router + Retry

| # | Task | Points |
|---|------|--------|
| 7.1 | Implement `model-router` POST /route — cost_class → model endpoint | 3 |
| 7.2 | Implement per-tenant quota enforcement in Redis | 3 |
| 7.3 | Implement Tier 1 retry (exponential backoff, max 3 attempts) | 3 |
| 7.4 | Implement AgentFailed → DLQ routing after retry exhaustion | 2 |
| 7.5 | OTEL tracing across full task lifecycle | 2 |

**Sprint Goal:** Retries working, model routing tested, traces visible in Tempo.

---

## Sprint 8 (Days 71–80): SDK Polish + PI-02 Close

| # | Task | Points |
|---|------|--------|
| 8.1 | SDK documentation (quickstart + API reference) | 3 |
| 8.2 | SDK contract validation tests | 2 |
| 8.3 | Developer trial: build new agent from scratch (timed) | 1 |
| 8.4 | Performance: agent-runtime p99 task dispatch latency < 200ms | 2 |
| 8.5 | Security: secrets-service stub (returns placeholder token) | 2 |
| 8.6 | PI-02 retrospective + PI-03 kick-off | 1 |

**Sprint Goal:** All PI-02 acceptance criteria met. SDK docs published.
