# performance-review.md

**Command:** `performance-review`  
**Version:** 1.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs, all sprints — mandatory for stories with latency SLOs or hot paths

---

## Purpose

Use this command to assess the performance characteristics of a completed implementation against the platform's non-functional requirements.

This command measures latency, throughput, resource consumption, scalability risk, and observability coverage. It identifies performance-blocking issues before they reach production.

Run this command on stories that involve: event processing pipelines, API endpoints with p99 latency SLOs, database queries expected to run at scale, agent execution loops, or tool invocations with network round-trips.

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Architecture — Scalability section | `docs/architecture/REFERENCE_ARCHITECTURE.md` (Section 18) | Mandatory |
| Architecture — Observability section | `docs/architecture/REFERENCE_ARCHITECTURE.md` (Section 16) | Mandatory |
| Non-functional requirements | `docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md` — NFR section | Mandatory |
| Implementation files | `src/{target_folder}/` | Mandatory |
| Database queries | All `.py` files with ORM or SQL | If story touches data |
| Kafka producer/consumer code | All Kafka integration files | If story touches event bus |
| Performance test results | Load test output (k6/Locust) | If available |
| Prometheus metrics | Current metrics snapshot | If service is deployed to dev |

**Substitutions required:**

```
{PI}             = e.g. PI-01-Platform-Core
{service_name}   = e.g. task-queue-service
{slo_p99}        = target p99 latency from NFRs, e.g. 200ms
{slo_throughput} = target throughput, e.g. 1000 events/sec
```

---

## Preconditions

- [ ] Implementation is complete and tests pass
- [ ] Non-functional requirements (latency SLOs, throughput targets) are defined in ACCEPTANCE_CRITERIA.md
- [ ] Service has been deployed to dev or at minimum integration tests run end-to-end

---

## Execution Steps

### Step 1 — Read non-functional requirements

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

### Step 2 — Database query analysis

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

### Step 3 — Kafka pipeline analysis

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

### Step 4 — Memory footprint analysis

Review implementation for memory risks:

- [ ] Are large objects (task context, agent output) stored in working memory (Redis) or passed by value?
- [ ] Is there any unbounded in-memory cache? (Must have TTL and size limit)
- [ ] Are generator patterns used instead of loading full result sets into memory?
- [ ] Are long-lived connections (DB, Kafka) pooled and bounded?

### Step 5 — Concurrency analysis

- [ ] Are async functions `await`-ed correctly? (No blocking calls inside `async def`)
- [ ] Is there shared mutable state between concurrent requests?
- [ ] Is the connection pool size set below the database's `max_connections` limit?
- [ ] Are there lock contention risks in multi-tenant operations?

### Step 6 — Observability coverage for performance

Verify every critical path emits performance data:

- [ ] Request duration histogram: `aep_{service}_request_duration_seconds`
- [ ] Kafka consumer lag metric exposed to Prometheus
- [ ] Database query duration observable via pg_stat_statements or OTEL spans
- [ ] Circuit breaker state exposed as metric (open/closed/half-open)

### Step 7 — Load test result review (if available)

If load test output is provided:
- Compare p50, p95, p99 latencies against SLOs
- Check for latency cliff at load transition points
- Check for memory growth over sustained load (memory leak indicator)
- Check error rate — should be 0% under normal load

### Step 8 — Produce performance review report

```
## Performance Review Report: {service_name}

### Verdict: PASS | FAIL | PASS WITH WARNINGS

### SLO Assessment
Latency SLO ({slo_p99}):       MET | AT RISK | MISSED — evidence
Throughput SLO ({slo_throughput}): MET | AT RISK | MISSED — evidence

### Blockers (must fix before merge)
1. ...

### Warnings (should fix, tracked)
1. ...

### Database Analysis
Hot path queries reviewed:  N
N+1 risks found:            N
Missing indexes:             N
Vector query optimised:     YES | NO | N/A

### Kafka Analysis
Consumer processing model:  synchronous | async
DLQ configured:             YES | NO
Batch size bounded:         YES | NO

### Memory Analysis
Unbounded caches found:     N
Large in-memory objects:    N

### Observability Coverage
Request duration metric:    PRESENT | MISSING
Consumer lag metric:        PRESENT | MISSING | N/A
Query duration spans:       PRESENT | MISSING

### Summary
{one paragraph}
```

---

## Expected Outputs

| Artifact | Description |
|----------|-------------|
| Performance review report | Structured report with SLO assessment, findings, recommendations |
| Remediation list | Specific query rewrites, index additions, config changes required |

---

## Quality Gates

- [ ] All hot-path database queries have index coverage verified
- [ ] No N+1 query patterns found
- [ ] All Kafka consumers have DLQ configured
- [ ] No unbounded in-memory caches
- [ ] Request duration metric present for every new endpoint
- [ ] SLO assessment completed against defined NFRs

---

## Completion Checklist

```
[ ] NFRs extracted and documented
[ ] Database queries reviewed — indexes, N+1, pagination
[ ] Kafka pipeline reviewed — async, DLQ, offset commit
[ ] Memory footprint reviewed — caches, connection pools
[ ] Concurrency reviewed — no shared mutable state
[ ] Observability coverage verified — metrics, spans
[ ] Load test results reviewed (if available)
[ ] Performance review report produced with SLO verdict
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Accept an N+1 query pattern as "acceptable for now"
- Skip database query analysis because "the table is small today"
- Accept a Kafka consumer without DLQ configuration
- Recommend disabling `acks=all` to improve throughput
- Accept a missing performance metric as "not critical"
- Mark performance as PASS without evidence against SLOs
- Introduce a new in-memory cache without TTL and size bound
- Skip the concurrency analysis on async code
- Modify implementation files (review only — no edits)
