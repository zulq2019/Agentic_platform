# performance-review.md

**Command:** `performance-review`  
**Version:** 2.0 — Architecture v2.0-aware  
**Skill authority:** `.ai/skills/performance-review/SKILL.md` (full pipeline)  
**Applies to:** All PIs, all sprints — mandatory for stories with latency SLOs or hot paths

---

## Purpose

Use this command to assess the performance characteristics of a completed implementation or pull request against the platform's non-functional requirements.

Before reviewing, this command **automatically loads** platform constitution, repository constitution, and contract schemas. It executes 18 performance lenses (13 original + 5 Architecture v2.0 extensions) and evaluates 15 Architecture v2.0 performance dimensions covering metadata resolution, registry lookups, configuration resolution, workflow execution, provider discovery, caching, database access, connection pooling, async processing, event processing, scalability, latency, cost, memory usage, and horizontal scaling. Produces SLO assessment, optimisation recommendations, lens summary, dimension summary table, and merge recommendation.

Run this command on stories or PRs that involve: event processing pipelines, API endpoints with p99 latency SLOs, database queries expected to run at scale, agent execution loops, registry lookups, workflow execution, provider discovery, or tool invocations with network round-trips.

### Invocation (unchanged)

```
/performance-review 42
/performance-review https://github.com/org/Agentic_platform/pull/42
```

See `.ai/skills/performance-review/SKILL.md` for the complete authoritative workflow.

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Platform primitives | `docs/architecture/PLATFORM_PRIMITIVES.md` | Mandatory (v2) |
| Platform contracts | `docs/architecture/PLATFORM_CONTRACTS.md` | Mandatory (v2) |
| Meta model | `docs/architecture/PLATFORM_META_MODEL.md` | Mandatory (v2) |
| UX model | `docs/architecture/PLATFORM_UX_MODEL.md` | Mandatory (v2) |
| Glossary | `docs/architecture/PLATFORM_GLOSSARY.md` | Mandatory (v2) |
| Metadata-driven architecture | `docs/architecture/METADATA_DRIVEN_ENTERPRISE_PLATFORM.md` | Mandatory (v2) |
| Architecture baseline v2 | `docs/architecture/ARCHITECTURE_BASELINE_V2.md` | Mandatory (v2) |
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture — Scalability section | `ARCHITECTURE.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| ADRs — Performance decisions | `docs/architecture/ADR/DECISIONS.md` | Mandatory |
| Architecture — Scalability section | `docs/architecture/REFERENCE_ARCHITECTURE.md` (Section 18) | Mandatory |
| Architecture — Observability section | `docs/architecture/REFERENCE_ARCHITECTURE.md` (Section 16) | Mandatory |
| Non-functional requirements | `docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md` — NFR section | Mandatory |
| Contract schemas | `contracts/` (including `platform-object.schema.json`) | Mandatory |
| PR diff | `gh pr diff <NUMBER>` | Mandatory for PR review |
| Implementation files | `src/{target_folder}/` | Mandatory |
| Database queries | All `.py` files with ORM or SQL | If story touches data |
| Kafka producer/consumer code | All Kafka integration files | If story touches event bus |
| Performance test results | Load test output (k6/Locust) | If available |
| Prometheus metrics | Current metrics snapshot | If service is deployed to dev |

**Substitutions required:**

```
{PI}             = e.g. PI-01-Platform-Core
{pr_number}      = GitHub pull request number
{service_name}   = e.g. task-queue-service
{target_folder}  = src/{location}
{slo_p99}        = target p99 latency from NFRs, e.g. 200ms
{slo_throughput} = target throughput, e.g. 1000 events/sec
```

---

## Preconditions

- [ ] PR is open and diff is fetchable via `gh pr diff` (for PR review)
- [ ] Implementation is complete and tests pass
- [ ] Non-functional requirements (latency SLOs, throughput targets) are defined in ACCEPTANCE_CRITERIA.md
- [ ] Service has been deployed to dev or at minimum integration tests run end-to-end

---

## Execution Steps

### Step 1 — Fetch PR metadata and read non-functional requirements

See `.ai/skills/performance-review/SKILL.md` Step 1. For PR review, fetch metadata and diff via `gh pr view` and `gh pr diff`.

From `docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md`, extract all NFRs for `{story_id}`:

```
Latency SLO:     p99 ≤ {slo_p99} under {expected_load}
Throughput SLO:  {slo_throughput}
Availability:    {availability_target}
Resource limits: CPU ≤ {cpu_request}/{cpu_limit}, Memory ≤ {mem_request}/{mem_limit}
```

If no NFRs are defined, use the platform defaults from `ARCHITECTURE.md`:
- API endpoints: p99 ≤ 200ms at 100 rps per tenant
- Kafka consumers: p99 processing time ≤ 500ms per event
- Database queries: p99 ≤ 50ms (simple read), p99 ≤ 100ms (complex join)

### Step 2 — Load platform and repository constitution (automatic)

Load all platform constitution docs and repository constitution before reviewing any changed file. See skill Step 2.

### Step 3 — Execute 18 performance lenses

**Lenses 1–13 (preserved):** Database Query Performance, pgvector/Memory Service, Kafka Pipeline Throughput, Redis Performance, Async Execution and Concurrency, Memory Usage, Retry Storms, Latency Profiling, CPU Efficiency, Caching Strategy, OpenTelemetry Coverage, Scalability Assessment, Cost Estimation.

**Lenses 14–18 (Architecture v2.0):** Metadata Resolution Performance, Registry Lookup Performance, Configuration Resolution Performance, Workflow Execution Performance, Provider Discovery Performance.

### Step 4 — Database query analysis

Read every database query in the implementation. For each query:

**Hot path queries (executed per request or per event):**
- [ ] Does the query use an index on the filter columns?
- [ ] Is `tenant_id` indexed? (It must be — included in all queries)
- [ ] Is the query N+1 safe? (No ORM lazy loads in loops)
- [ ] Does the query return only needed columns? (No `SELECT *` on large tables)
- [ ] Is pagination used for queries returning unbounded row sets?

**Vector similarity queries:**
- [ ] Is the HNSW index being used?
- [ ] Is the query scoped with metadata filters before vector search? (Prevents full-table scan)
- [ ] Is `ef_search` tuned for the expected recall vs latency balance?

Record each finding:
```
QUERY FINDING
File: {filename}:{line}
Issue: {description}
Estimated impact: {latency increase or throughput reduction}
Recommendation: {specific fix — index, query rewrite, pagination}
```

### Step 5 — Kafka pipeline analysis

For every Kafka consumer in the implementation:

- [ ] Is processing synchronous (blocking) or asynchronous (non-blocking)?
- [ ] Is there a batch size limit to prevent memory pressure?
- [ ] Are downstream failures retried with exponential back-off?
- [ ] Is the DLQ used for poison-pill messages (messages that always fail)?
- [ ] Does the consumer commit offset only after successful processing?
- [ ] Is the consumer group ID unique per service instance?

For every Kafka producer:
- [ ] Is `acks=all` set for messages where durability is required?
- [ ] Is the producer reusing a single connection pool?
- [ ] Are large payloads stored in a reference store and the event carries only the reference?

### Step 6 — Memory footprint analysis

Review implementation for memory risks:

- [ ] Are large objects (task context, agent output) stored in working memory (Redis) or passed by value?
- [ ] Is there any unbounded in-memory cache? (Must have TTL and size limit)
- [ ] Are generator patterns used instead of loading full result sets into memory?
- [ ] Are long-lived connections (DB, Kafka) pooled and bounded?

### Step 7 — Concurrency analysis

- [ ] Are async functions `await`-ed correctly? (No blocking calls inside `async def`)
- [ ] Is there shared mutable state between concurrent requests?
- [ ] Is the connection pool size set below the database's `max_connections` limit?
- [ ] Are there lock contention risks in multi-tenant operations?

### Step 8 — Observability coverage for performance

Verify every critical path emits performance data:

- [ ] Request duration histogram: `aep_{service}_request_duration_seconds`
- [ ] Kafka consumer lag metric exposed to Prometheus
- [ ] Database query duration observable via pg_stat_statements or OTEL spans
- [ ] Circuit breaker state exposed as metric (open/closed/half-open)

### Step 9 — Load test result review (if available)

If load test output is provided:
- Compare p50, p95, p99 latencies against SLOs
- Check for latency cliff at load transition points
- Check for memory growth over sustained load (memory leak indicator)
- Check error rate — should be 0% under normal load

### Step 10 — Produce performance review report

```
## Performance Review: PR #{N} — {title}

### SLO Reference
{latency and throughput SLOs with source}

### Critical Path Estimate
{operation breakdown and SLO verdict}

### Critical / Major / Minor Findings
{file:line findings with failure scenario and specific fix}

### Optimisation Recommendations (priority order)
{dimension-mapped recommendations with expected impact}

### Performance Lens Summary
{18-lens status table}

### Architecture v2.0 Dimension Summary
{15-dimension risk table}

### Performance Risk Assessment
{13 original dimension risk table}

### Merge Recommendation
{1-2 sentences}

### Verdict
APPROVE | REQUEST CHANGES | NEEDS DISCUSSION
```

---

## Architecture v2.0 Review Dimensions

| Dimension | Primary lens |
|-----------|--------------|
| Metadata Resolution | 14 |
| Registry Lookups | 10, 15 |
| Configuration Resolution | 16 |
| Workflow Execution | 17 |
| Provider Discovery | 18 |
| Caching | 10 |
| Database Access | 1 |
| Connection Pooling | 5 |
| Async Processing | 5 |
| Event Processing | 3 |
| Scalability | 12 |
| Latency | 8 |
| Cost | 13 |
| Memory Usage | 6 |
| Horizontal Scaling | 12 |

---

## Expected Outputs

| Artifact | Description |
|----------|-------------|
| Performance review report | Structured report with SLO assessment, 18-lens summary, v2.0 dimension summary |
| Optimisation recommendations | Prioritised fixes with dimension mapping and expected performance impact |
| Remediation list | Specific query rewrites, index additions, config changes required |

---

## Quality Gates

- [ ] Platform constitution loaded before review (Step 2)
- [ ] All hot-path database queries have index coverage verified
- [ ] No N+1 query patterns found
- [ ] All Kafka consumers have DLQ configured
- [ ] No unbounded in-memory caches
- [ ] Request duration metric present for every new endpoint
- [ ] SLO assessment completed against defined NFRs
- [ ] All applicable Architecture v2.0 dimensions reviewed

---

## Completion Checklist

```
[ ] Platform constitution loaded
[ ] NFRs extracted and documented
[ ] PR diff fetched (if PR review)
[ ] Lenses 1–13 executed (or N/A documented)
[ ] Lenses 14–18 executed (or N/A documented)
[ ] Architecture v2.0 dimension summary produced (15 dimensions)
[ ] Database queries reviewed — indexes, N+1, pagination
[ ] Kafka pipeline reviewed — async, DLQ, offset commit
[ ] Memory footprint reviewed — caches, connection pools
[ ] Concurrency reviewed — no shared mutable state
[ ] Observability coverage verified — metrics, spans
[ ] Load test results reviewed (if available)
[ ] Optimisation recommendations produced with dimension mapping
[ ] Performance review report produced with SLO verdict
[ ] Verdict issued (APPROVE | REQUEST CHANGES | NEEDS DISCUSSION)
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Skip platform constitution loading (Step 2)
- Accept an N+1 query pattern as "acceptable for now"
- Skip database query analysis because "the table is small today"
- Accept a Kafka consumer without DLQ configuration
- Recommend disabling `acks=all` to improve throughput
- Accept a missing performance metric as "not critical"
- Mark performance as PASS without evidence against SLOs
- Introduce a new in-memory cache without TTL and size bound
- Skip the concurrency analysis on async code
- Modify implementation files (review only — no edits)
