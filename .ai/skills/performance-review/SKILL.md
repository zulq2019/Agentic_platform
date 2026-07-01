---
name: performance-review
description: |
  When the engineer types /performance-review <PR_NUMBER> or /performance-review <GitHub PR URL>,
  fetch the PR diff and perform a Principal Performance Engineer level audit of that pull request
  against the Agentic Engineering Platform. Executes 13 performance and scalability lenses:
  Database Query Performance → pgvector / Memory Service → Kafka Pipeline Throughput →
  Redis Performance → Async Execution and Concurrency → Memory Usage → Retry Storms →
  Latency Profiling → CPU Efficiency → Caching Strategy → OpenTelemetry Coverage →
  Scalability Assessment → Cost Estimation. Produces SLO-referenced verdicts, back-of-envelope
  latency budget calculations, and prioritised optimisation recommendations with concrete expected
  performance impact. This is a deep performance audit — not a surface-level check. It is invoked
  on PRs touching hot paths, event pipelines, or data access at scale. aep-review Lens 8 is a
  quick performance check; this skill is a full scalability and performance audit. Critical
  performance blockers (blocking async calls, N+1 on hot paths, shared mutable state under
  horizontal scale) always result in REQUEST CHANGES regardless of other lens results.
allowed-tools: |
  bash: gh git grep rg python jq
---

# Performance Review — Principal Performance Engineer Audit

<purpose>
Full scalability and performance audit for the Agentic Engineering Platform. Distinct from
aep-review Lens 8, which performs a surface performance check as one of twelve review dimensions.
This skill is the authoritative performance deep-dive: 13 lenses, SLO-referenced verdicts,
back-of-envelope latency budget calculations, and concrete optimisation recommendations with
expected impact. Invoke this skill on any PR that touches a hot path, event pipeline, data access
at scale, or any code with explicit latency SLOs in ACCEPTANCE_CRITERIA.md.

Review only the diff — never invent findings not present in the changed code. Every finding must
cite an exact file:line from the diff and explain the concrete failure scenario at production load.
</purpose>

---

## When To Activate

Trigger when the engineer types `/performance-review` followed by a PR number or GitHub PR URL.

```
/performance-review 42
/performance-review https://github.com/org/Agentic_platform/pull/42
```

**Mandatory invocation** — this skill MUST be used (not aep-review alone) when the PR touches:

- Hot-path API endpoints expected to receive >100 rps per tenant
- Kafka producer or consumer pipelines on high-volume topics
- Database queries on large tables: `workflow_runs`, `tasks`, `memory.entries`, `agents.registrations`
- Redis operations expected to scale with tenant count or task volume
- Agent execution loops or tool invocation chains
- The `memory-service` (pgvector similarity queries)
- The `aep-common` shared library (performance regression here affects every service)
- Any code with explicit latency SLOs defined in `ACCEPTANCE_CRITERIA.md`

---

## Step 1 — Fetch PR Metadata, Diff, and SLOs

```bash
# Fetch PR metadata
gh pr view <NUMBER> --json title,body,author,baseRefName,headRefName,additions,deletions,changedFiles,labels,milestone

# Fetch the full diff
gh pr diff <NUMBER>

# Fetch file-level change summary
gh pr diff <NUMBER> --name-status

# Fetch line-level statistics per file
gh pr diff <NUMBER> --numstat
```

Extract and record before proceeding:

```
PR #:           {number}
Title:          {title}
Author:         {author}
Base branch:    {base}
Head branch:    {head}
Files changed:  {N}
Additions:      +{N}
Deletions:      -{N}
```

Parse the PR body to identify:
- Story ID (e.g. `US-01.03`)
- PI (e.g. `PI-01-Platform-Core`)
- Capability (e.g. `CAP-04`)

Then read `ACCEPTANCE_CRITERIA.md` for the story and extract all NFRs:
- Latency SLOs (p50, p95, p99 targets and the load they apply at)
- Throughput SLOs (requests/sec, events/sec)
- Resource budgets (CPU limit, memory limit, DB connection budget)

**If no SLOs are defined in ACCEPTANCE_CRITERIA.md, use platform defaults from ARCHITECTURE.md:**

| Component | Platform Default SLO |
|-----------|---------------------|
| API endpoints | p99 ≤ 200ms at 100 rps per tenant |
| Kafka consumers | p99 processing ≤ 500ms per event |
| DB simple read (indexed) | p99 ≤ 50ms |
| DB complex join | p99 ≤ 100ms |
| pgvector similarity search | p99 ≤ 200ms with metadata filter |
| Health endpoints | p99 ≤ 20ms |
| Redis get/set | p99 ≤ 5ms |

Document which SLOs are story-specific and which are platform defaults. The distinction matters
for risk assessment — a story with no explicit SLOs carries the platform defaults as implicit
obligations, but findings are weighted accordingly.

---

## Step 2 — Load Reference Documents

Read these documents as review context. Do not re-output their full contents. They are the
authoritative standards this PR is measured against.

```bash
# Core platform authorities
cat CONSTITUTION.md
cat ARCHITECTURE.md            # Focus: Scalability section, Service boundaries
cat DECISIONS.md

# PI context (substitute {PI} from Step 1)
cat docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md   # Primary — SLOs live here
cat docs/engineering/implementation-roadmap/{PI}/REFERENCE_ARCHITECTURE.md  # Sections 16 (Observability), 18 (Scalability)
cat docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md

# Contracts (relevant to throughput and event volume)
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
```

**Stop condition:** If `CONSTITUTION.md` or `ARCHITECTURE.md` cannot be read, stop and report.
The review cannot proceed without these documents — SLOs and platform defaults cannot be validated.

---

## Step 3 — Execute 13 Performance Lenses

Execute every lens. No lens may be skipped if its subject area is present in the diff.
Lenses whose subject area is not touched may be marked N/A in the results table.

---

### Lens 1 — Database Query Performance

For every ORM query, raw SQL, or SQLAlchemy expression in changed files:

```bash
# Find all ORM queries
rg "\.filter\(|\.where\(|session\.query|\.all\(\)|\.first\(\)|\.one_or_none\(\)" -- <changed_files>

# Find N+1 patterns — ORM calls inside loops
rg "for .* in" -A 10 -- <changed_files> | rg "\.filter\(|\.get\(|session\.query"

# Find SELECT * patterns
rg "SELECT \*|\.all\(\)" -- <changed_files>

# Find aggregation queries
rg "COUNT\(|SUM\(|AVG\(|\.count\(\)" -- <changed_files>

# Find raw SQL
rg "text\(|execute\(|raw_query|SELECT|INSERT|UPDATE|DELETE" -- <changed_files>
```

**Checks:**

- Does every WHERE clause filter on an indexed column? (`tenant_id` is always indexed — verify all others against the migration schema)
- Is there any `SELECT *` on a table expected to have >10,000 rows? (Select only needed columns)
- Are N+1 patterns present? (ORM lazy load inside a loop = N queries instead of 1)
  - Fix: use eager loading (`.options(joinedload(...))`) or a single JOIN query with the parent
- Are collection queries paginated with `LIMIT` and a cursor? (Unpaginated queries on large tables are unbounded)
- Are aggregation queries (`COUNT`, `SUM`) using indexed columns? (Unindexed aggregation = full table scan)
- Do JOIN queries have indexes on the join columns on both sides?
- Is `EXPLAIN ANALYZE` output available or can query plan shape be inferred from the query structure?
- Are bulk inserts using `session.bulk_insert_mappings` or `INSERT ... VALUES (...)` batching rather than one `session.add()` per row in a loop?

**Why it matters:** An unindexed query on `workflow_runs` (millions of rows at scale) turns a 5ms
operation into a 5-second full table scan. At 100 rps, this exhausts the connection pool in under
1 second and renders the service unresponsive.

**Flag as Critical:** N+1 query on a hot path, full table scan on a table expected to exceed 1M rows at production scale
**Flag as Major:** Missing index on a filter column, `SELECT *` on a large table, unpaginated collection query on growing data, row-by-row insert inside a loop

---

### Lens 2 — pgvector / Memory Service Queries

For any query on `memory.entries`, vector similarity operations, or embedding calls:

```bash
rg "memory\.entries|vector_cosine|embedding|<->|<#>|<=>|ivfflat|hnsw" -- <changed_files>
rg "similarity_search|vector_search|nearest_neighbor" -- <changed_files>
```

**Checks:**

- Is the HNSW or IVFFlat index being used? (Query planner must not fall back to a sequential scan — verify with EXPLAIN)
- Is the query scoped with a `tenant_id` metadata filter **before** the vector similarity computation? (Metadata pre-filtering reduces the search space before the vector index is consulted — without it, the index scans the entire corpus)
- Is `ef_search` tuned for the recall-vs-latency balance required by the SLO? (Higher `ef_search` = better recall but higher latency — default is often too low for production recall requirements or too high for latency SLOs)
- Is the result set bounded with `LIMIT`? (Top-K retrieval only — never return all similarity matches above a threshold)
- Is the embedding cached for repeated content? (Embedding the same text twice wastes both time and token cost)
- Is `recency_weight` applied in the re-ranking step? (Not just raw cosine similarity — recency matters for agent context relevance)
- Does the query include a `source_type` filter where applicable? (Reduces false positives and search space)

**Why it matters:** An unscoped pgvector search on a large corpus is O(N) against the full table —
the vector index provides no benefit without the metadata filter. At 10,000 memory entries per
tenant and 100 tenants, an unscoped search scans 1M rows. The metadata filter reduces this to
~10,000 entries before the index is consulted, cutting query time by ~99%.

**Flag as Critical:** pgvector query without `tenant_id` scope filter — this is both a performance and a security violation
**Flag as Major:** No `LIMIT` on similarity results, repeated embedding of identical content without caching, no `source_type` filter where context type is known

---

### Lens 3 — Kafka Pipeline Throughput

For every producer and consumer in changed files:

```bash
# Producers
rg "producer\.send|kafka.*produce|KafkaProducer|AIOKafkaProducer" -- <changed_files>

# Consumers
rg "@kafka_consumer|subscribe|KafkaConsumer|AIOKafkaConsumer|poll\(" -- <changed_files>

# Configuration
rg "max_poll_records|acks|batch_size|linger_ms|compression_type|group_id" -- <changed_files>
```

**Producer checks:**

- Is the producer connection reused (singleton or pool) or created per-message? (Per-message instantiation = catastrophic — connection setup alone is 50-200ms)
- Is `acks=all` set for durability-required messages? (`acks=0` is fast but data-lossy; `acks=1` loses data on leader failure)
- Is the message payload size bounded? (Payloads >1MB should store object-store reference, not embed content — Kafka is not an object store)
- Is the partition key set to `tenant_id`? (Ensures ordering per tenant and prevents hot partitions — a missing key means round-robin which loses ordering guarantees)
- Is `linger_ms` and `batch_size` configured for throughput? (Default settings prioritise latency over throughput — for high-volume topics, batching matters)
- Is `compression_type` configured? (`snappy` or `lz4` reduces network and disk I/O significantly for JSON payloads)

**Consumer checks:**

- Is processing synchronous and blocking inside the consumer loop? (Blocks further consumption — must be async or offloaded)
- Is `max_poll_records` bounded? (Default is 500 — a spike of large messages can cause memory pressure or processing timeout)
- Is the consumer committing offset **after** processing completes, not before? (Commit before processing = data loss on crash; commit after = exactly-once semantics with idempotent processing)
- Is there exponential back-off on retry? (Fixed-interval retry at scale = retry storm — see Lens 7)
- Is there a maximum retry count before DLQ? (Infinite retry = consumer lag grows unboundedly)
- Is the DLQ sized and monitored? (DLQ back-pressure must not block the main topic consumer)
- Is the consumer group ID stable across deployments? (Changing the group ID loses the committed offset and forces replay from the beginning or end)

**Throughput estimation:**

Estimate messages/sec the consumer can handle:
- If processing time per message = T ms, and concurrency = C, then throughput = C × (1000 / T) msg/sec
- Compare against expected production throughput from ACCEPTANCE_CRITERIA.md
- If estimate < required throughput, flag the gap with the required concurrency to meet the SLO

**Why it matters:** A synchronous blocking consumer on a high-volume topic creates processing
backlog that grows unboundedly. At 1000 events/sec arriving with 600ms processing time and
concurrency=1, the lag grows by 400 events/sec — within 15 minutes, the consumer is 360,000
messages behind with no recovery path except scaling.

**Flag as Critical:** Producer created per-message, consumer blocking synchronously at high volume without concurrency mechanism, offset committed before processing
**Flag as Major:** Unbounded `max_poll_records`, missing back-off on retry, consumer group ID unstable across deployments, no DLQ configured

---

### Lens 4 — Redis Performance

For every Redis operation in changed files:

```bash
rg "redis|Redis|aioredis|SETEX|GET|HGET|ZADD|MGET|PIPELINE|TTL" -- <changed_files>
rg "\.get\(|\.set\(|\.hset\(|\.expire\(|\.scan\(" -- <changed_files>
```

**Checks:**

- Are pipeline/batch operations used where multiple keys are read or written? (`MGET` > N×`GET`; `pipeline()` for multiple writes — each individual command is a round trip)
- Is TTL set on **every** key? (Unbounded key growth = Redis memory exhaustion; for `aep:{tenant_id}:working_context:{task_id}`, the TTL must outlive the task but expire after completion)
- Is the key space designed to avoid hot keys? (All working-context keys for a high-volume tenant on a single Redis shard creates a hot-key bottleneck — use sharding or hash tags deliberately)
- Are `SCAN` operations absent from hot paths? (`SCAN` is O(N) over the keyspace — use indexed data structures instead)
- Is Lua scripting used for atomic check-and-set operations? (Check-then-set without Lua is a race condition under concurrent execution)
- Is the connection pool bounded? (Unbounded pool = Redis connection exhaustion under load; `max_connections` must be set below the Redis server's `maxclients`)
- Are large values stored as `HASH` fields rather than a single serialised string? (Allows partial updates without deserialising and reserialising the entire structure)
- Is `WAIT` used after writes that must be durable before the response is returned?

**Why it matters:** A missing TTL on a working-context key means Redis memory grows with every
task forever. At 1000 tasks/day with 10KB average context, unmanaged keys consume 10MB/day.
Within 6 months at 10 tenants, this is ~18GB — beyond Redis's configured memory limit,
triggering eviction of active keys and silent data loss.

**Flag as Major:** Key without TTL, `SCAN` in a hot-path operation, connection pool unbounded, pipeline not used where multiple keys are accessed in sequence

---

### Lens 5 — Async Execution and Concurrency

For every async function in changed files:

```bash
# Find async functions
rg "async def" -- <changed_files>

# Find blocking calls inside async — the critical anti-pattern
rg "time\.sleep|requests\.|urllib\.request|subprocess\.run" -- <changed_files>

# Find parallel vs sequential async operations
rg "asyncio\.gather|await asyncio" -- <changed_files>

# Find shared mutable state
rg "^[a-z_]+ = \[\]|^[a-z_]+ = \{\}|^[a-z_]+: List|^[a-z_]+: Dict" -- <changed_files>
```

**Checks:**

- Are there blocking synchronous calls inside `async def`? (Blocks the event loop — all other coroutines on the same thread stall until the blocking call returns)
  - Blocking: `time.sleep`, `requests.get`, `urllib.request`, synchronous SQLAlchemy drivers, `subprocess.run` without `asyncio.create_subprocess_exec`
  - Fix: use `asyncio.sleep`, `httpx.AsyncClient`, `asyncpg`/`sqlalchemy.ext.asyncio`, `asyncio.create_subprocess_exec`, or `asyncio.run_in_executor` for CPU-bound work
- Is there shared mutable state between concurrent requests? (Module-level lists, dicts, or sets mutated by request handlers = race condition — use connection-scoped or request-scoped state only)
- Are database connection pools bounded below `max_connections`? (At 50 concurrent requests with pool_size=20, the 30 waiting requests queue or time out — this is invisible locally but catastrophic at production concurrency)
- Is `asyncio.gather` used for parallel independent operations instead of sequential `await`? (Fetching agent registration then fetching tool registration sequentially = 2× the latency of fetching both in parallel)
- Are long-running CPU operations offloaded to a thread pool via `asyncio.run_in_executor`? (CPU-bound work on the event loop thread starves I/O-bound coroutines)
- Is there a timeout on every external call? (`asyncio.wait_for(coro, timeout=N)` — no timeout = hung coroutine that holds a connection pool slot forever)
- Are semaphores used to bound concurrency for operations with external rate limits? (Unbounded `asyncio.gather` on 1000 items = 1000 simultaneous external calls)

**Why it matters:** One `time.sleep(1)` inside an `async def` handler running on a busy service
stalls all other coroutines on that event loop thread for the full 1 second. At 100 rps on a
single-worker service, this means requests queue for up to 100 seconds — the entire service
becomes unresponsive to a single blocking call.

**Flag as Critical:** Blocking synchronous call inside `async def` in a hot-path function, shared mutable module-level state mutated by concurrent request handlers
**Flag as Major:** No timeout on external call, sequential `await` where `asyncio.gather` would halve latency, connection pool size that can be exhausted at expected concurrency

---

### Lens 6 — Memory Usage

For data loading and caching patterns in changed files:

```bash
# Find full result set loads
rg "\.all\(\)|fetch_all|fetchall\(\)|list\(cursor\)" -- <changed_files>

# Find in-memory collections
rg "\[\]|\{\}|list\(|dict\(" -- <changed_files>

# Find cache definitions
rg "@lru_cache|@cache|TTLCache|maxsize" -- <changed_files>

# Find large object handling
rg "agent_output|task_context|payload|content" -- <changed_files>
```

**Checks:**

- Are generator patterns used instead of loading full result sets into memory? (`yield` from cursor vs `fetchall()` into a list — critical for queries on large tables)
- Is pagination applied before loading results into memory? (Loading page 1 of a 100,000-row result set is fine; loading all 100,000 rows to slice client-side is not)
- Are there unbounded in-memory caches without size limits? (LRU cache must have `maxsize`; unconstrained `dict` growth must be documented and bounded)
- Is working context (task context blob) stored in Redis, not in process memory? (Process-memory task context does not survive restarts and prevents horizontal scaling)
- Are large agent outputs stored by reference (object store URL) and not held in process memory? (A 50KB agent output held per concurrent task at 200 concurrent tasks = 10MB per worker — acceptable; but at 10,000 concurrent tasks across the platform it's 500MB per worker)
- Is streaming used for large file processing? (Reading a 100MB file into memory with `file.read()` vs streaming with `aiofiles` async read in chunks)
- Are connection objects (DB sessions, Kafka producers, Redis clients) pooled and reused? (Creating a new DB connection per request = 10-100ms connection overhead added to every request)

**Why it matters:** Loading 10,000 `workflow_runs` rows into a Python list for in-memory
processing consumes ~20MB per request (at ~2KB/row). With 50 concurrent requests, that is
1GB of process memory allocated simultaneously — exceeding the K8s memory limit and triggering
an OOMKill, which crashes the pod and routes traffic to the remaining replicas, cascading.

**Flag as Critical:** Unbounded result set loaded into memory on a hot path (e.g., `session.query(WorkflowRun).all()` without LIMIT on a large table)
**Flag as Major:** In-memory cache without size limit, large agent output stored in process memory rather than object store reference, connection object created per-request

---

### Lens 7 — Retry Storms

For every retry implementation in changed files:

```bash
rg "retry|backoff|tenacity|@retry|max_attempts|wait_exponential" -- <changed_files>
rg "except.*retry|for.*attempt|while.*retry" -- <changed_files>
```

**Checks:**

- Is exponential back-off implemented? (Fixed-interval retry at scale = thundering herd — all retrying clients hit the recovering dependency simultaneously)
- Is jitter added to the back-off calculation? (Without jitter, all clients that experienced the same failure at the same moment retry at exactly the same future moment)
- Is the maximum retry count bounded? (`max_attempts=3` or `max_attempts=5` — never infinite; infinite retry = consumer or worker permanently stuck)
- Is the retry scope correct? (Retry the individual operation, not the entire request handler — retrying the handler may replay already-completed side effects)
- Are retries on Kafka consumers bounded before DLQ handoff? (Max 3 retries before the message moves to `aep.dlq` — not unbounded)
- Is circuit breaker implemented for external dependencies? (Open circuit prevents retry storms from propagating to an already-failing dependency)
- Is rate limiting respected before retry? (Retrying a rate-limited dependency without honouring `Retry-After` headers makes the rate limit worse)

**Required pattern for all retries:**

```python
@retry(
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((TransientError, ConnectionError)),
    reraise=True,
    before_sleep=log_retry_attempt,
)
async def call_external_dependency():
    ...
```

**Why it matters:** 100 Kafka consumers retrying a failed dependency every 1 second = 100
requests/second to an already-overwhelmed dependency, guaranteed to keep it overwhelmed.
Exponential back-off with jitter at `min=1, max=60` means that after the initial failure burst,
retries spread across a 60-second window with random offsets — giving the dependency time to
recover.

**Flag as Major:** Fixed-interval retry without jitter, unbounded retry count, no circuit breaker on an external dependency, retry-before-DLQ not bounded on Kafka consumers

---

### Lens 8 — Latency Profiling

For the critical request path of the changed code:

```bash
# Find OTEL spans
rg "start_as_current_span|get_tracer|with tracer" -- <changed_files>

# Find sequential awaits that could be parallelised
rg "await " -- <changed_files>

# Find lock acquisitions
rg "asyncio\.Lock|threading\.Lock|\.acquire\(" -- <changed_files>
```

**Checks:**

- Does the critical path have OTEL trace spans that will reveal latency in production? (Without spans, performance regressions are invisible until they become outages)
- Are there serial operations that could be parallelised?
  - Example: fetching agent registration then fetching tool registration sequentially = 2× latency vs `asyncio.gather`
  - Example: loading task context from Redis then loading tenant config from DB sequentially can be parallelised
- Is there any synchronous remote call in the critical request path that could be moved async or cached?
- Are there any lock acquisitions that could be replaced with lock-free patterns? (A lock serialises all concurrent requests for that resource)
- Is there any regex or computation repeated on every request that could be compiled or cached once at module level?

**Back-of-envelope latency budget check:**

For the story's p99 SLO, construct the critical path estimate:

| Operation | Estimated Latency | Source |
|-----------|------------------|--------|
| Auth token validation | ~5ms | JWT verify (cached public key) |
| Redis working context load | ~2ms | Local Redis |
| DB query (indexed) | ~10ms | Platform default |
| Agent registry lookup | ~15ms | DB query (or ~1ms if cached) |
| Tool registry lookup | ~15ms | DB query (or ~1ms if cached) |
| LLM API call | ~200-2000ms | model-router |
| Kafka produce | ~5ms | Local broker |
| **Serialisation overhead** | ~3ms | JSON encode/decode |

Sum of estimates for the specific critical path must be < SLO with headroom for P99 variance
(tail latency is typically 2-5× the median — budget accordingly).

**State explicitly:** Is the p99 SLO mathematically achievable given the operation sequence?
Options: WITHIN BUDGET / AT RISK / EXCEEDS SLO

**Why it matters:** A p99 SLO of 200ms is mathematically impossible if the critical path
includes two sequential external HTTP calls at 150ms each. Identifying this in review prevents
a false-green test environment from shipping code that will miss SLO in production on day one.

**Flag as Major:** Serial operations on a latency-sensitive path where parallelisation would meet the SLO, SLO mathematically impossible given the operation sequence, hot-path method with no OTEL span making latency invisible

---

### Lens 9 — CPU Efficiency

For compute-intensive operations in changed files:

```bash
# JSON serialisation
rg "json\.loads|json\.dumps" -- <changed_files>

# Base64, hashing, encryption
rg "base64|hashlib|hmac|Fernet|encrypt" -- <changed_files>

# Regex usage
rg "re\.compile|re\.match|re\.search|re\.findall" -- <changed_files>

# String operations in loops
rg "for .* in" -A 5 -- <changed_files> | rg '+=.*str|\.join|f"'

# O(n²) candidates
rg "for .* in.*for .* in" -- <changed_files>
```

**Checks:**

- Is JSON serialisation/deserialisation on the hot path using standard `json`? (Use `orjson` for 3-5× throughput on typical payloads — drop-in replacement)
- Is there repeated string concatenation in a loop? (Use `''.join(parts)` instead of `result += chunk` — the latter is O(n²) due to string immutability)
- Is regex compiled once at module level or recompiled per-request?
  - `re.compile(pattern)` at module level = compiled once
  - `re.match(pattern, text)` called per-request = recompiled every call (the internal cache helps but is not guaranteed)
- Are cryptographic operations (hashing, signing) called only when necessary? (Hashing the full task context on every read to check integrity adds CPU overhead — consider checksums only on write)
- Is there any O(n²) algorithm operating on a dataset that grows with production load? (Nested loops over task lists, agent lists, or capability lists that grow with platform usage)
- Are embeddings batched? (One API call for 100 texts vs 100 API calls = 100× fewer round trips and lower per-token cost from batching efficiency)

**Why it matters:** Standard `json.loads` on a 100KB agent output payload in a tight consumer
loop at 1000 events/sec uses ~40% CPU on a 2-vCPU pod. Switching to `orjson` reduces this
to ~10% — freeing CPU headroom for actual business logic and allowing the pod to handle 3-4×
the throughput before autoscaling triggers.

**Flag as Minor:** Uncompiled regex on a hot-path, standard `json` vs `orjson` on high-throughput paths, string concatenation in loop
**Flag as Major:** O(n²) algorithm on a dataset that grows with production platform usage, repeated cryptographic operations that could be cached

---

### Lens 10 — Caching Strategy

For expensive repeated operations in changed files:

```bash
# Existing cache usage
rg "@lru_cache|@cache|TTLCache|cachetools|functools.cache" -- <changed_files>

# Registry lookups (candidates for caching)
rg "agent_registry|tool_registry|registry\.get|registry\.resolve" -- <changed_files>

# Configuration lookups
rg "config\.get|settings\.|tenant_config" -- <changed_files>

# Cache metrics
rg "cache_hit|cache_miss|cache_evict" -- <changed_files>
```

**Checks:**

- Are agent and tool registry lookups cached? (Registry does not change per-request — a 60-second TTL cache on agent/tool registration lookups eliminates repeated DB round trips for the most common read path on the platform)
- Are expensive configuration lookups cached? (Tenant configuration, policy rules, and feature flags should be cached with a short TTL, not read from DB on every request)
- Is cache invalidation correct? (A stale cache after an agent re-registers with new capabilities = wrong agent selected for a task — the cache must be invalidated or short-TTL enough to self-correct)
- Is the cache bounded with `maxsize`? (Unbounded LRU cache grows with the number of distinct lookup keys — at 10,000 tenants this can exhaust process memory)
- Is cache hit/miss rate observable via Prometheus metrics? (Without cache hit rate metrics, cache effectiveness cannot be validated in production)
- Is caching applied at the right layer? (Cache the resolved agent registration object, not the raw SQL query result — the former is the correct unit of reuse)
- Is cache warming considered for cold-start latency? (A fresh pod with empty cache will miss SLO on the first requests — consider prewarming from Redis on startup)

**Why it matters:** Resolving an agent by capability tag involves a database query on
`agents.registrations`. At 1000 task dispatches/second, without caching this is 1000 DB
queries/second for a table that changes perhaps once per deployment. A 60-second TTL in-process
cache with Redis backing reduces this to ~17 DB queries/minute — a 3,600× reduction in DB load
for the most critical read path on the platform.

**Flag as Major:** No caching on registry lookups expected to receive >100 rps, cache without TTL (unbounded growth), cache without `maxsize`, no cache hit rate observable

---

### Lens 11 — OpenTelemetry Coverage

For performance observability in changed files:

```bash
# Trace spans
rg "start_as_current_span|get_tracer|with.*tracer\." -- <changed_files>

# Prometheus metrics
rg "Histogram|Counter|Gauge|prometheus_client|Summary" -- <changed_files>

# Slow query logging
rg "slow_query|pool_timeout|echo.*True|pool_pre_ping" -- <changed_files>

# Kafka consumer lag metric
rg "consumer_lag|records_lag|consumer_group_offset" -- <changed_files>
```

**Checks:**

- Does every hot-path method have an OTEL span? (Without spans, latency regressions are invisible — you cannot SLO-alert on what you cannot measure)
- Do spans include the relevant filtering attributes? (`tenant_id`, `task_id`, `agent_id`, `workflow_run_id` — without these, traces cannot be correlated to specific tenants or tasks)
- Is request duration emitted as a Prometheus **Histogram** (not Gauge)? (Histograms compute p50/p95/p99 — a Gauge only records the most recent value and is useless for percentile SLO alerting)
- Is Kafka consumer lag exposed as a metric? (Consumer lag is the leading indicator of throughput problems — by the time errors appear, the backlog may be unrecoverable within the SLO window)
- Is database query duration observable? (Either via `pg_stat_statements` integration, ORM echo with slow-query threshold, or OTEL DB instrumentation)
- Are slow query thresholds configured? (Log queries exceeding 100ms to expose regressions before they become SLO violations)
- Is cache hit rate observable? (Without `cache_hits_total` and `cache_misses_total` counters, cache effectiveness is unmeasurable — the cache is unvalidated infrastructure)
- Is the `aep_{service}_request_duration_seconds` histogram present for every new endpoint or consumer?

**Required metric naming pattern:**

```python
# Request duration — histogram with SLO-relevant buckets
request_duration = Histogram(
    "aep_{service}_request_duration_seconds",
    "Duration of requests in seconds",
    ["method", "endpoint", "tenant_id"],
    buckets=[.005, .01, .025, .05, .1, .2, .5, 1.0, 2.5, 5.0],
)

# Errors — counter by error type
errors_total = Counter(
    "aep_{service}_errors_total",
    "Total error count",
    ["error_type", "tenant_id"],
)
```

**Why it matters:** Without histograms, you only see average latency — and average is useless
for SLO compliance. A system with p50=10ms and p99=5000ms has an acceptable average but is
catastrophically slow for 1% of requests. p99 is what affects real users and triggers SLO
budget burn.

**Flag as Major:** Hot-path method with no OTEL span, request duration emitted as Gauge instead of Histogram, no consumer lag metric for Kafka consumers, no slow-query threshold configured

---

### Lens 12 — Scalability Assessment

For the overall design of changed code under horizontal scale:

```bash
# Module-level mutable state
rg "^[A-Za-z_]+ = \[\]|^[A-Za-z_]+ = \{\}" -- <changed_files>

# In-process state that won't survive replica restart
rg "global |class.*_cache|_REGISTRY|_STORE" -- <changed_files>

# Idempotency markers
rg "idempotency|already_processed|dedup|if.*exists" -- <changed_files>

# K8s resource limits
rg "resources:|limits:|requests:" -- <changed_files>
```

**Checks:**

- Is the service stateless? (Stateful services cannot scale horizontally — any per-request state must live in Redis or the DB, not in process memory)
- Is any shared mutable state stored in process memory instead of Redis? (Works with 1 replica in development; with 3 replicas in production, each replica sees different state — silent correctness failure)
- Is the Kafka consumer group designed for horizontal scaling? (One consumer per partition — if the topic has 6 partitions, scaling beyond 6 replicas adds idle replicas that do no work)
- Are database connections bounded per-replica? (10 replicas × 20 connections/replica = 200 total DB connections — must remain below the DB's `max_connections` limit, typically 100-200 for managed Postgres)
- Is the implementation idempotent under horizontal scale? (If two replicas process the same task simultaneously due to a rebalance or at-least-once delivery, the outcome must be the same as processing once)
- Is there any per-process state that causes different replicas to behave differently? (Module-level counters, in-memory bloom filters, or local file caches that diverge across replicas)
- Does the implementation respect the K8s resource limits declared in the manifest? (A pod that consistently uses 2× its memory limit will be OOMKilled — limits must be set based on realistic load profiling, not defaults)

**Why it matters:** A service that stores working state in a module-level dict works perfectly
in a local development environment with 1 process. Deployed to K8s with 3 replicas, requests
are load-balanced across all 3 — each replica sees only ~33% of the state it should see.
The failure is silent until a user reports missing data, by which point the inconsistency may
be days old.

**Flag as Critical:** Shared mutable process-level state that will produce incorrect results under horizontal scale (more than 1 replica)
**Flag as Major:** Service not idempotent under concurrent execution of the same task, DB connection budget per-replica that exceeds capacity at the planned replica count

---

### Lens 13 — Cost Estimation

For LLM calls, model invocations, and expensive token-consuming operations:

```bash
# LLM calls
rg "cost_class|model_router|invoke_model|anthropic|openai|claude|gpt" -- <changed_files>

# Embedding calls
rg "embed|get_embedding|create_embedding" -- <changed_files>

# LLM calls in loops
rg "for .* in" -A 10 -- <changed_files> | rg "invoke_model|embed|anthropic|openai"
```

**Checks:**

- Is `cost_class` declared correctly in the agent contract? (`low`/`medium`/`high` maps to model tier via `model-router` — `high` is justified only when reasoning quality demonstrably requires it)
- Are LLM calls inside loops? (Each loop iteration = one API call = cost multiplied by loop count × call frequency)
- Is the context window usage bounded? (Unbounded context growth = cost grows linearly with conversation length — implement context windowing or summarisation)
- Are embeddings batched? (100 texts as a single API call vs 100 separate calls = 1× vs 100× API overhead, plus typically better throughput pricing)
- Is the expected token budget documented in the agent contract? (Without a token budget, cost is unpredictable and unmonitorable)
- Are expensive operations (embeddings, LLM calls) triggered only when necessary? (Not on every request — only when context changes, when cached embeddings are stale, or when explicitly required by the task)
- Is prompt construction optimised to minimise tokens? (Verbose system prompts that repeat the same instructions on every call add cost with no quality benefit)

**Cost impact estimation pattern:**

```
New LLM call:
  Tokens per call:      ~{N} input + ~{M} output
  Calls per task:       ~{K}
  Tasks per day:        ~{T} (from ACCEPTANCE_CRITERIA.md throughput SLO)
  Cost per 1K tokens:   ${rate} (from model-router cost_class mapping)
  
  Daily cost estimate:  {N+M} × K × T / 1000 × ${rate}
  Monthly estimate:     daily × 30
  
  Delta vs baseline:    +${X}/month — {acceptable / needs justification / needs discussion}
```

**Why it matters:** An agent that calls `cost_class=high` for every small subtask can cost 10×
more than one using `cost_class=low` for the same output quality. An embedding call inside a
loop processing 1000 tasks/day = 1000 API calls/day = ~$30/month for text-embedding-3-small,
vs batching them = the same cost with 10× less API overhead and latency.

**Flag as Major:** LLM calls in loop without batching justification, unbounded context growth with no windowing, `cost_class=high` without documented justification, no token budget in agent contract
**Flag as Minor:** Verbose prompt with repeated boilerplate that could be condensed, embeddings not cached for repeated content

---

## Step 4 — Produce the Review Output

```
## Performance Review: PR #{N} — {title}
Author: {author} | {additions}+ {deletions}- | {files_changed} files

---

### SLO Reference
Latency SLO:    p99 ≤ {target}ms at {load} rps per tenant  [{story-specific | platform default}]
Throughput SLO: {target} rps / events/sec                   [{story-specific | platform default}]
Resource limit: CPU {cpu_limit}, Memory {mem_limit}
Source: {ACCEPTANCE_CRITERIA.md story ID | ARCHITECTURE.md platform defaults}

---

### Critical Path Estimate
{operation_1}: ~{N}ms
{operation_2}: ~{N}ms
{operation_3}: ~{N}ms
─────────────────────────
Total estimate: ~{N}ms  vs  SLO {target}ms

Verdict: WITHIN BUDGET / AT RISK (margin < 20%) / EXCEEDS SLO (estimate > target)

---

### Critical  🔴
{file/path.py}:{line} — {concise issue statement}
  Why it matters: {concrete failure scenario at production load — include numbers}
  Fix: {specific optimisation with expected performance impact}

---

### Major  🟠
{file/path.py}:{line} — {concise issue statement}
  Why it matters: {impact at scale}
  Fix: {specific optimisation with expected performance impact}

---

### Minor  🟡
{file/path.py}:{line} — {note}
  Fix: {specific optimisation}

---

### Optimisation Recommendations (priority order)
1. {recommendation} — expected impact: {latency reduction / throughput increase / cost saving}
2. {recommendation} — expected impact: {latency reduction / throughput increase / cost saving}
3. ...

---

### Performance Risk Assessment
| Dimension             | Risk         | Evidence                              |
|-----------------------|--------------|---------------------------------------|
| Database              | HIGH/MED/LOW | {finding summary or "No issues found"} |
| pgvector              | HIGH/MED/LOW | {finding summary or "N/A"}             |
| Kafka Pipeline        | HIGH/MED/LOW | {finding summary or "N/A"}             |
| Redis                 | HIGH/MED/LOW | {finding summary or "N/A"}             |
| Async / Concurrency   | HIGH/MED/LOW | {finding summary}                      |
| Memory                | HIGH/MED/LOW | {finding summary}                      |
| Retry Storms          | HIGH/MED/LOW | {finding summary or "N/A"}             |
| Latency Budget        | HIGH/MED/LOW | {SLO verdict}                          |
| CPU                   | HIGH/MED/LOW | {finding summary}                      |
| Caching               | HIGH/MED/LOW | {finding summary}                      |
| Observability         | HIGH/MED/LOW | {finding summary}                      |
| Scalability           | HIGH/MED/LOW | {finding summary}                      |
| Cost                  | HIGH/MED/LOW | {finding summary or "N/A"}             |

---

### Merge Recommendation
{1-2 sentences stating clearly what must change before merge, or confirming performance
is acceptable for production load at the stated SLOs.}

### Verdict
APPROVE — performance acceptable for production SLOs
REQUEST CHANGES — performance blockers found (see Critical findings above)
NEEDS DISCUSSION — at-risk performance requiring load testing or further analysis before production
```

---

## Mandatory Verdict Rules

**`REQUEST CHANGES`** — required when any of the following are present:

- Any Critical finding in any lens
- SLO mathematically impossible given the operation sequence in the critical path
- Blocking synchronous call inside `async def` on a hot-path function
- N+1 query pattern on a table expected to exceed 100,000 rows
- Shared mutable process-level state that will produce incorrect results under horizontal scale (>1 replica)
- pgvector query without `tenant_id` scope filter (performance AND security violation)
- Producer connection created per-message on a high-volume Kafka topic
- Unbounded result set loaded into memory on a hot path

**`NEEDS DISCUSSION`** — required when:

- SLO is achievable in development/test environment but at-risk in production (estimate within budget but margin < 20%)
- Cost increase exceeds 50% of current baseline without documented justification
- A design decision creates acceptable performance today but will degrade as tenant or task volume grows (document the scale breakpoint)
- Performance improvement requires architectural change beyond the scope of this PR (create a follow-up issue)

**`APPROVE`** — only when:

- All 13 lenses executed with no Critical or Major findings, OR all Major findings have documented mitigations accepted by the team
- Critical path estimate is WITHIN BUDGET (SLO margin ≥ 20%)
- No blocking calls in async hot-path functions
- No N+1 patterns on high-volume tables
- Hot-path operations are observable via OTEL spans and Prometheus histograms
- Scalability is confirmed for the planned horizontal scale target

---

## Completion Checklist

Before declaring the review complete, confirm:

- [ ] All 13 lenses executed (or explicitly marked N/A with justification)
- [ ] SLO reference documented (story-specific or platform default — source stated)
- [ ] Critical path estimate produced with operation-level breakdown
- [ ] Every Critical finding has: file:line reference, concrete failure scenario at scale, specific fix with expected performance impact
- [ ] Optimisation recommendations prioritised by expected impact
- [ ] Performance Risk Assessment table complete with evidence for every dimension
- [ ] Merge recommendation is unambiguous
- [ ] Verdict is one of: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION

---

## Review Rules

1. Review only the PR diff — do not invent findings not present in the changed code
2. Every finding must cite an exact `file:line` reference from the diff
3. Every finding must explain the concrete failure scenario at production load, not just what is wrong
4. Every finding must include a specific fix with expected performance impact (e.g., "reduces p99 by ~40ms", "eliminates 3,600 DB queries/minute")
5. Back-of-envelope calculations are required for latency budget and cost estimation — show the maths
6. Performance and scalability only — do not review style, naming, or business logic
7. Never approve a PR with a blocking call inside an async hot-path function
8. Never accept "it works locally" — validate against production SLOs at production load
9. Never skip the N+1 check on any hot-path database query
10. Never skip the retry storm check on any retry implementation in the diff
11. Never accept unbounded memory usage or unbounded key growth
12. Never approve without confirming scalability under the planned horizontal replica count
13. If a lens has no findings and the subject area is not present in the diff, mark it N/A — do not fabricate findings

---

## Forbidden Actions

- **Never approve** a PR with a blocking synchronous call inside an `async def` function on a hot path
- **Never accept** "it's fast enough locally" — validate against production SLOs at production load
- **Never skip** the N+1 check on hot-path database queries
- **Never skip** the retry storm check on any retry implementation
- **Never accept** unbounded memory usage (no `maxsize` on caches, no LIMIT on queries, no size cap on in-process collections)
- **Never approve** without confirming the implementation is correct under horizontal scale (>1 replica)
- **Never review** style issues, naming conventions, or business logic — performance and scalability only
- **Never invent** findings not present in the changed code — if the diff does not touch a Kafka consumer, Lens 3 is N/A
