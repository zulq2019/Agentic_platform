---
name: aep-review
description: |
  When the engineer types /aep-review <PR_NUMBER> or /aep-review <GitHub PR URL>,
  fetch the PR diff and perform a Principal Engineer level review of a pull request
  against the Agentic Engineering Platform. Executes 12 review lenses in priority order:
  Story Compliance → Architecture → Capability Boundary → Contracts → Infrastructure →
  API → Events → Security → Performance → Observability → AI Engineering →
  Production Readiness. Constitution and contract violations are always Critical.
  Architecture violations always outrank formatting findings. Output findings by
  severity with file:line references. Never approve a PR with an unresolved Critical.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq
  file: read
---

## Phase 0 — Repository Discovery (mandatory)

**Execute before all other steps in this skill.** Repository-agnostic; reusable in any
software repository. Never hardcode repository names or folder structures. Never fail
because a document is missing — record `NOT FOUND` and continue with graceful degradation.

**Authority:** Full discovery procedure, bash patterns, and Discovery Record template:
[`.ai/skills/_shared/REPOSITORY_DISCOVERY.md`](../_shared/REPOSITORY_DISCOVERY.md).
If the relative path does not resolve, discover via glob: `**/skills/_shared/REPOSITORY_DISCOVERY.md`.

**Auto-detect and record:**

| Item | Action |
|------|--------|
| Repository type | Infer from manifests and layout |
| Architecture documents | Glob/search `ARCHITECTURE*.md`, `PLATFORM_*.md`, architecture doc trees |
| Platform constitutions | Discover `CONSTITUTION.md`, platform baseline docs — **load automatically if present** |
| Repository constitution | Discover `CLAUDE.md`, `REPOSITORY_GUIDE.md`, `AGENTS.md`, `CONTRIBUTING.md` |
| Engineering roadmap | Discover `ROADMAP.md`, `TASKS.md`, implementation-roadmap / program trees |
| Current PI | Active program folder (`PI-*` or discovered pattern) |
| Current Sprint | Active section in `SPRINT_PLAN.md` when present |
| Current Story | In Progress / next Planned from `STATUS.md` + story catalogues |
| STATUS.md | Nearest program status file |
| CHANGELOG.md | Root or discovered changelog |
| METRICS.md | Root or discovered metrics doc |
| README hierarchy | Root + nested `README.md` files |
| Skills library | `**/skills/**/SKILL.md` |
| Prompt library | Command libraries (`commands/`, `.ai/commands/`, etc.) |

**Before proceeding:** Emit a **Discovery Record** per the shared template. If Platform
Constitution documents exist, confirm they were loaded. Then continue to this skill's
existing steps unchanged.

---


# AEP Pull Request Review

<purpose>
Principal Engineer level review for the Agentic Engineering Platform. Every PR is
reviewed through 12 lenses in priority order. Constitution and contract violations
are Critical and block merge. Architecture violations outrank all code-quality findings.
Review only the diff — never invent findings not present in the changed code.
</purpose>

---

## When To Activate

Trigger when the engineer types `/aep-review` followed by a PR number or GitHub PR URL.

```
/aep-review 42
/aep-review https://github.com/org/Agentic_platform/pull/42
```

---

## Step 1 — Fetch PR Metadata and Diff

```bash
# Fetch PR metadata
gh pr view <NUMBER> --json \
  title,body,author,baseRefName,headRefName,additions,deletions,changedFiles,labels,milestone

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

If any of these are absent from the PR body, flag as **Major** — PR description does not link to a User Story.

---

## Step 2 — Load Reference Documents

Read these documents as review context. Do not re-output their contents. They are the authoritative standards this PR is measured against.

```bash
# Read platform authorities
cat CONSTITUTION.md
cat ARCHITECTURE.md
cat DECISIONS.md
cat CLAUDE.md

# Read PI context (substitute {PI} from Step 1)
cat docs/engineering/implementation-roadmap/{PI}/CAPABILITIES.md
cat docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md
cat docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md
cat docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md
cat docs/engineering/implementation-roadmap/{PI}/IMPLEMENTATION.md

# Read contracts
ls contracts/
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
cat contracts/tool-contract.schema.json
cat contracts/task-schema.schema.json
cat contracts/memory-schema.schema.json
```

**Stop condition:** If `CONSTITUTION.md` or `ARCHITECTURE.md` cannot be read, stop and report. Review cannot proceed without these.

---

## Step 3 — Execute Review Lenses

Execute every lens in this exact order. Priority is top-down: a Critical finding in Lens 0 is not superseded by a clean result in Lens 11.

---

### Lens 0 — Story Compliance

**Priority: Highest. A PR that does not satisfy its User Story is incomplete regardless of code quality.**

Identify the User Story from the PR body. Read `USER_STORIES.md` and `ACCEPTANCE_CRITERIA.md` for that story.

**Check:**

- Does the PR title or body reference a specific User Story ID?
- Does the implementation address the User Story's stated need (As a... I want... so that...)?
- Is every acceptance criterion in `ACCEPTANCE_CRITERIA.md` for this story satisfied by the diff?
  - For each Given/When/Then criterion: identify which changed file and method satisfies it
  - For each criterion: identify which test file and test function covers it
- Is every item in the Story-Level Gate of `DEFINITION_OF_DONE.md` met?
- Does the PR implement exactly one User Story, or does it expand scope into additional stories?

**Flag as Critical when:**
- An acceptance criterion has no corresponding implementation
- An acceptance criterion has no corresponding test
- The implementation addresses a story not referenced in the PR body

**Flag as Major when:**
- PR implements partial story (some AC met, some not) without documenting what is deferred
- PR mixes multiple User Stories without separate commits or justification

---

### Lens 1 — Architecture Compliance

**Priority: Second-highest. Architecture violations have higher severity than any code-quality finding.**

Review every changed file against `CONSTITUTION.md` and `ARCHITECTURE.md`. Work through each principle.

**A-series — Structural principles:**

- **A1:** Does any changed code invoke another agent's module, API, or class directly?
  ```bash
  rg "from agents\." --include="*.py" -- <changed_files>
  rg "import.*Agent" --include="*.py" -- <changed_files>
  ```
- **A2:** Does `orchestrator-service` now contain specialist logic — LLM calls, code generation, scoring, tool execution?
  ```bash
  rg "anthropic|openai|generate_code|execute_tool" src/platform/orchestrator/ --include="*.py"
  ```
- **A3:** Was a new agent added by modifying the orchestrator switch/dispatch logic instead of registering in the Agent Registry?
- **A4:** Does any service make a direct HTTP call to another platform service for business logic?
  ```bash
  rg "httpx|requests|aiohttp" --include="*.py" -- <changed_files>
  ```
  If found, verify: is the target a registry lookup (permitted) or a business-logic call (violation)?
- **A5:** Does any service read or write another service's database schema directly?
  ```bash
  rg "orchestrator\." src/platform/agent-runtime/ --include="*.py"
  rg "agents\." src/platform/orchestrator/ --include="*.py"
  ```

**H-series — Human oversight:**

- **H2:** Is there any flag, timeout, environment variable, or condition that can auto-approve a human gate without a human decision?
  ```bash
  rg "bypass|skip_gate|auto_approve|EMERGENCY" -- <changed_files>
  rg "approval_required.*False|approval_required.*false" -- <changed_files>
  ```

**S-series — Security architecture:**

- **S1:** Do RBAC, Policy Engine, and Secrets remain three separate services? Does any changed file import from more than one of these within the same module?

**Flag as Critical when:**
- A1 violated — agent calls agent directly
- A2 violated — specialist logic in orchestrator
- H2 violated — gate bypass mechanism introduced
- Any Constitution principle violated

**Flag as Major when:**
- A4 violated — new inter-service HTTP business call
- A5 violated — cross-schema data access
- Architecture boundary erosion that does not yet break a constitution principle but moves toward violation

---

### Lens 2 — Capability Boundary

**Priority: Third. Scope creep into unrelated capabilities is a merge blocker.**

Identify the capability this story belongs to from the PR body (e.g. `CAP-04`). Read `CAPABILITIES.md` for that capability.

**Check:**

- Do all changed files belong to the service(s) owned by this capability?
- Does the implementation introduce logic described by a *different* capability?
  - Example: a PR for CAP-04 (Kafka Topic Provisioning) should not add agent registration logic (CAP-01 or PI-02)
- Are any new modules created in a service that does not own this capability?
- Does the diff introduce public API endpoints, Kafka topics, or database tables that belong to a different service's ownership domain?

```bash
# Identify which services are touched
gh pr diff <NUMBER> --name-status | grep -E "^[AM]" | awk '{print $2}' | cut -d/ -f1-3 | sort -u
```

Compare the touched service paths against the capability's owned services in `CAPABILITIES.md`.

**Flag as Critical when:**
- Business logic for capability X is implemented inside the service owned by capability Y

**Flag as Major when:**
- PR touches files outside the stated capability's scope without justification
- New utility or shared module introduced that belongs to `aep-common` but is placed inside a specific service

---

### Lens 3 — Contracts

**Priority: Critical violations block merge unconditionally.**

**Event Envelope compliance:**

For every Kafka message produced or consumed in the diff:
```bash
# Find all event publish calls
rg "producer\.send|kafka.*produce|publish.*event" -- <changed_files>

# Validate envelope fields are present
rg "event_id|event_type|schema_version|emitted_by|tenant_id|task_id|workflow_run_id|timestamp|payload" -- <changed_files>
```

Verify every produced message contains all required fields from `contracts/event-envelope.schema.json`.

**Agent Contract compliance (if agent registered or modified):**
```bash
# Find agent registration files
rg "agent_id|capabilities|input_schema|output_schema|cost_class|idempotency_key_strategy" -- <changed_files>
```

Verify registration JSON validates against `contracts/agent-contract.schema.json`.

**Tool Contract compliance (if tool registered or modified):**

Verify tool registration against `contracts/tool-contract.schema.json`.

**Schema versioning:**
- Does the diff change an existing contract schema in `contracts/`?
- If yes: is there a corresponding ADR in `DECISIONS.md`?
- Is the change backward compatible? (New required fields without defaults are breaking changes)

**Event naming:**
- Event types must be PascalCase: `TaskCreated`, not `task_created` or `TASK_CREATED`
- Topic names must follow `aep.{domain}.{event-type-kebab}`: `aep.task.created`, not `task-created` or `aep_task_created`

**Flag as Critical when:**
- Published event is missing a required envelope field
- Agent or tool registration fails to validate against its contract schema
- A contract schema is modified without an ADR

**Flag as Major when:**
- Event type string does not follow PascalCase convention
- Topic name does not follow `aep.{domain}.{event-type-kebab}` convention
- Idempotency key strategy missing or malformed on agent registration

---

### Lens 4 — Infrastructure

**Every infrastructure component introduced must be traceable to an acceptance criterion of the current story.**

Detect introduction of new infrastructure in the diff:

```bash
# Docker Compose changes
rg "docker-compose|docker_compose" -- <changed_files>

# Kubernetes manifests
rg "apiVersion|kind: Deployment|kind: Service|kind: ConfigMap" -- <changed_files>

# Kafka topic additions
rg "topic.*create|create.*topic|NewTopic|AdminClient" -- <changed_files>

# Database migrations
find . -name "*.py" -path "*/alembic/versions/*" -newer HEAD~1

# Redis configuration
rg "redis.*cluster|RedisCluster|REDIS_URL" -- <changed_files>

# Vault / secrets configuration
rg "vault|VAULT_ADDR|SecretClient" -- <changed_files>

# Prometheus / Grafana
rg "prometheus|grafana|scrape_config" -- <changed_files>

# OpenTelemetry
rg "opentelemetry|OTEL_" -- <changed_files>

# GitHub Actions workflow changes
find .github/workflows/ -newer HEAD~1
```

For each new infrastructure component found:
- Is it listed in the story's `INFRASTRUCTURE.md` assessment section?
- Is its introduction justified by a specific acceptance criterion?
- Is it the minimum configuration needed — or does it over-provision for future stories?

**Flag as Major when:**
- New infrastructure introduced with no traceability to an acceptance criterion
- Infrastructure provisioned "for later" without an explicit deferral record
- New Kafka topic introduced without ACL configuration
- New database table introduced without RLS policy

**Flag as Minor when:**
- Infrastructure configuration present but commented out
- Resource limits not set on new Docker/Kubernetes resources

---

### Lens 5 — API Review

For every new or modified HTTP endpoint in the diff:

**REST correctness:**
- HTTP methods semantically correct: GET reads, POST creates, PUT replaces, PATCH updates, DELETE removes
- Status codes correct: 200 (ok), 201 (created), 204 (no content), 400 (bad input), 401 (unauthenticated), 403 (unauthorised), 404 (not found), 409 (conflict), 422 (validation failed), 429 (rate limited), 500 (server error)
- No business logic returning 200 with an error payload — use the correct HTTP status

**Authentication and authorisation:**
```bash
rg "Depends(get_verified_tenant_context)|Depends(get_verified_service_context)" -- <changed_files>
```
Every public endpoint must use `get_verified_tenant_context`. Every internal-only endpoint must use `get_verified_service_context`. No unprotected endpoints.

**Input validation:**
- Every request body uses a Pydantic model with `model_config = ConfigDict(extra="forbid")`
- UUIDs typed as `uuid.UUID`, not `str`
- Timestamps typed as `datetime`, not `str`
- `tenant_id` never accepted from the request body — always extracted from auth context

**Idempotency:**
- POST endpoints that create resources: does the endpoint handle duplicate requests gracefully (409 or idempotency key)?
- Is there protection against double-submit?

**Pagination:**
- Any endpoint returning a collection must have pagination (cursor-based preferred, offset acceptable)
- No unbounded `SELECT *` results returned in a single response

**Versioning:**
- New endpoints must use `/api/v1/` prefix
- If an existing endpoint contract changes: is this a breaking change? Is there a migration path?

**Error responses:**
- Domain exceptions must map to specific HTTP status codes via the exception handler map
- Internal exception messages must not appear in HTTP response bodies

**Flag as Critical when:**
- A public endpoint has no authentication dependency
- `tenant_id` is accepted from the request body

**Flag as Major when:**
- Collection endpoint has no pagination
- Domain exception exposed as raw 500 with internal message
- New endpoint missing OpenAPI summary and description annotations

---

### Lens 6 — Event Review

For every Kafka producer and consumer in the diff:

**Event naming:**
- Event type: PascalCase — `AgentCompleted`, not `agent_completed`
- Topic: `aep.{domain}.{event-type-kebab}` — `aep.agent.completed`, not `agent.completed`

**Envelope compliance:** (see Lens 3 — apply detailed checks here)

**Correlation IDs:**
```bash
rg "task_id|workflow_run_id|tenant_id" -- <changed_files>
```
Every event must carry `task_id`, `workflow_run_id`, and `tenant_id` in the envelope.

**Consumer resilience:**
- Offset committed only after successful processing — not at message receipt
  ```bash
  rg "commit|ack" -- <changed_files>
  # Verify ack/commit comes AFTER handler completes, not before
  ```
- Retry with exponential back-off on processing failure
- Dead Letter Queue configured — failed messages after max retries go to `aep.dlq`
- Consumer is idempotent — same message processed twice must not produce duplicate side effects
  ```bash
  rg "idempotency|already_processed|dedup" -- <changed_files>
  ```

**Producer safety:**
- `acks=all` for messages where durability is required
- Producer reuses connection pool — not instantiated per-message
- Large payloads stored by reference, not embedded in the event body

**Event ordering:**
- Partition key set to `tenant_id` for tenant-scoped ordering
- Events that must be processed in order go to the same partition key

**Flag as Critical when:**
- Consumer commits offset before processing completes
- Consumer has no DLQ path — messages can be silently dropped after failure
- Consumer has no idempotency check

**Flag as Major when:**
- Event missing `task_id` or `workflow_run_id` correlation fields
- Retry implemented without exponential back-off
- Producer creates a new connection per message

---

### Lens 7 — Security

**Credential management:**
```bash
# Scan for hardcoded secrets
rg "(password|secret|token|api_key|apikey)\s*=\s*['\"][^'\"]{8,}" -- <changed_files> -i
rg "sk-[a-zA-Z0-9]{20,}" -- <changed_files>
rg "Bearer [a-zA-Z0-9\-._~+/]+=*" -- <changed_files>
python -m detect_secrets scan -- <changed_files>
```

**Tenant isolation:**
```bash
# Every ORM query must include tenant_id
rg "\.filter\(|\.where\(|SELECT" -- <changed_files>
# Verify tenant_id is present in every query
```
- Every database query includes `tenant_id` in the WHERE clause or relies on an active RLS policy
- `current_setting('app.current_tenant_id')` set before every raw query
- Every Redis key follows `aep:{tenant_id}:*` pattern
- Every pgvector similarity query includes `tenant_id` metadata filter — no unscoped vector search

**Secrets management:**
- Secrets fetched from `secrets-service` at invocation time — not cached beyond TTL
- Token scope set to minimum required (read vs write vs admin)
- Tokens never logged, even at DEBUG level
- Tokens never included in API response bodies

**RBAC / Policy / Secrets separation (Constitution S1):**
```bash
# Detect merged concerns
rg "from.*rbac.*import|from.*policy.*import|from.*secrets.*import" src/platform/rbac/ --include="*.py"
rg "from.*rbac.*import|from.*policy.*import|from.*secrets.*import" src/platform/policy/ --include="*.py"
```
No single module may perform RBAC evaluation, policy enforcement, and secret issuance.

**Input validation at boundaries:**
- All Kafka message payloads validated against Pydantic model before processing
- All task context validated at agent runtime entry point
- All tool response payloads normalised through response normaliser before use

**Dependency vulnerabilities:**
```bash
pip-audit --requirement requirements.txt 2>/dev/null || echo "pip-audit not available"
```
Note any critical or high CVEs introduced by new dependencies.

**Flag as Critical when:**
- Credential, API key, or token hardcoded anywhere in changed files
- `tenant_id` missing from a database query in changed code
- `detect-secrets` finds a new finding
- RBAC, Policy, and Secrets logic merged into a single module

**Flag as Major when:**
- Token TTL not enforced (cached indefinitely)
- Token scope broader than minimum required
- Input not validated at a service boundary
- New dependency with known high CVE introduced

---

### Lens 8 — Performance

**Database query analysis:**
```bash
# Find ORM calls inside loops — N+1 risk
rg "for.*in.*:" -A 5 -- <changed_files> | rg "\.filter\(|\.get\(|session\.query"
```

- Hot-path queries (executed per request or per event): do they use indexes on filter columns?
- Is `tenant_id` indexed on every queried table?
- Is there any `SELECT *` on a large table? (Should select only needed columns)
- Are collection queries paginated with a LIMIT?
- Are N+1 query patterns present (ORM lazy loads inside loops)?

**pgvector queries:**
- Is the HNSW or IVFFlat index being used?
- Is the vector query scoped with `tenant_id` metadata filter before similarity search?

**Kafka consumer:**
- Is processing synchronous and blocking inside the consumer? (Should be async)
- Is there a bounded batch size (`max_poll_records`) to prevent memory pressure?

**Memory:**
- Any unbounded in-memory cache introduced without a TTL and size limit?
- Are generator patterns used where full result sets are loaded into memory?
- Are large objects (task context, agent output) stored by reference (Redis) or passed by value?

**Concurrency:**
- Any blocking calls (`time.sleep`, synchronous HTTP) inside `async def` functions?
  ```bash
  rg "time\.sleep|requests\." -- <changed_files>
  ```
- Shared mutable state between concurrent requests?
- Connection pool size set below the database's `max_connections` limit?

**Retry storms:**
- Retry logic uses exponential back-off with jitter — not fixed-interval retry
- Maximum retry count bounded — infinite retry loops not possible

**Backpressure:**
- Kafka consumer applies backpressure when processing is slow — does not continue consuming if handler is behind

**Flag as Major when:**
- N+1 query pattern found in a hot path
- Blocking synchronous call inside an async function
- Unbounded in-memory cache without TTL
- Retry loop with no maximum bound

**Flag as Minor when:**
- Collection query missing pagination on a table that will grow
- Connection pool size not configured (uses library default)

---

### Lens 9 — Observability

For every new service, endpoint, domain method, or event handler in the diff:

**Tracing:**
```bash
rg "start_as_current_span|get_tracer" -- <changed_files>
```
- Every new public method in `domain/` is wrapped in an OTEL trace span
- Spans include `task_id` and `tenant_id` as attributes
- Span names are descriptive: `agent_registry.resolve` not `method_1`

**Metrics:**
```bash
rg "Counter|Histogram|Gauge|prometheus" -- <changed_files>
```
Every new service must expose:
- `aep_{service}_requests_total` — counter by status
- `aep_{service}_request_duration_seconds` — histogram
- `aep_{service}_errors_total` — counter by error type

**Logging:**
```bash
# No print() in production code
rg "print(" -- <changed_files>

# Structured logger used
rg "aep_common\.logging|get_logger" -- <changed_files>
```
- All log lines use `aep_common.logging` — not `print()` or Python's built-in `logging` directly
- Every log line in task context includes `task_id`, `workflow_run_id`, `tenant_id`
- Log levels appropriate: DEBUG for trace data, INFO for state transitions, WARNING for recoverable anomalies, ERROR for failures

**Health endpoints:**
- New services include `/health/live` and `/health/ready`
- `/health/ready` checks all dependencies (DB, Kafka, Redis) and returns 503 if any are down

**Flag as Major when:**
- New domain method has no OTEL trace span
- New service exposes no Prometheus metrics
- `print()` statements present in production code paths
- Log lines in task context missing correlation IDs

**Flag as Minor when:**
- Span attributes missing `tenant_id`
- Log level appears incorrect for the event being logged

---

### Lens 10 — AI Engineering

**Apply this lens when the diff touches:** agent code, model routing, prompt construction, memory reads/writes, or tool invocations.

**Prompt usage:**
```bash
rg "system_prompt|user_message|anthropic|openai|model\.invoke" -- <changed_files>
```
- Is the prompt constructed from `CAPABILITIES.md` and PI-defined patterns, not hardcoded inline strings?
- Does the prompt enforce "one question at a time" and "specific feedback only" (platform AI rules)?
- Is there any unbounded prompt growth — context appended without a size ceiling?

**Model routing:**
- Are agents selecting models directly by name (violation of Constitution MI3)?
  ```bash
  rg "claude-|gpt-4|gemini-" -- <changed_files>
  ```
  Agents must request a `cost_class` (low/medium/high) — model selection belongs to `model-router`
- Is `cost_class` declared in the agent contract?

**Context window:**
- Is there a maximum context size enforced before calling the model?
- Is the working context trimmed if it exceeds the limit?

**Memory usage:**
- Memory writes go through `memory-service` — not direct database inserts
  ```bash
  rg "memory\.entries|INSERT INTO memory" -- <changed_files>
  ```
- Memory reads include `tenant_id` metadata filter and `source_type` filter — no unscoped vector search
- Is the `recency_weight` factored into retrieval ranking?

**Token efficiency:**
- Are embeddings cached where the same content is embedded repeatedly?
- Is the retrieved context ranked and truncated before injection into the prompt?

**Hallucination safeguards:**
- Agent output validated against a schema before it is acted upon
- Structured output (JSON mode or tool-use) preferred over free-text parsing

**Retry behaviour:**
- LLM call retries have a maximum bound
- Retry storms from back-to-back failed LLM calls are not possible

**Flag as Critical when:**
- Agent selects a model by name (Constitution MI3 violation)
- Agent writes to `memory.entries` directly, bypassing `memory-service`

**Flag as Major when:**
- Unbounded prompt growth with no context ceiling
- LLM call inside a loop without batching justification
- Agent output not validated before acting on it
- Memory read not scoped by `tenant_id`

**Flag as Minor when:**
- Embeddings for repeated content not cached
- Retrieved context not ranked before injection

---

### Lens 11 — Production Readiness

**Docker:**
```bash
# Multi-stage build
rg "FROM.*AS" -- <changed_dockerfiles>

# Non-root user
rg "USER" -- <changed_dockerfiles>

# Health check instruction
rg "HEALTHCHECK" -- <changed_dockerfiles>
```
Every service Dockerfile must use multi-stage build, non-root user, and `HEALTHCHECK`.

**Tests:**
```bash
# Coverage on changed files
gh pr diff <NUMBER> --name-status | grep "^[AM].*\.py$" | awk '{print $2}'
# For each changed source file, verify a corresponding test file exists
```
- Unit test coverage ≥ 80% on new code
- One acceptance test per Given/When/Then criterion
- Cross-tenant isolation test present if story touches data

**CI pipeline:**
```bash
cat .github/workflows/ci.yml
```
- Does CI run lint + type check + unit tests + contract validation + build?
- Does CI include `detect-secrets` scan?
- Does CI include `pip-audit` or equivalent?

**Database migrations:**
- Every migration has a `downgrade()` function
- Migration is idempotent — safe to run twice
- Column additions use `nullable=True` or have a safe `server_default`
- No migration locks a table for more than 1 second

**Rollback strategy:**
- Can the deployment be rolled back without data loss?
- If a migration adds a NOT NULL column with no default, rollback requires a schema change — document this

**Release notes:**
- Is `CHANGELOG.md` updated under `[Unreleased]`?
- Does the PR description include deployment notes for any migration or environment variable change?

**Flag as Critical when:**
- Database migration has no `downgrade()` function
- New column is NOT NULL with no default and no backfill strategy
- Dockerfile runs as root

**Flag as Major when:**
- Unit test coverage below 80% on new code
- CI pipeline missing contract validation step
- `CHANGELOG.md` not updated
- New environment variable not documented in `.env.example`

**Flag as Minor when:**
- Test file exists but does not cover a specific edge case
- Migration missing index that will be needed at scale

---

## Step 4 — Produce the Review Output

```
## PR #{N} — {title}
Author: {author} | {additions}+ {deletions}- | {files_changed} files

---

### Story Compliance  📋
Story: {US-XX.XX} — {story_title}
Capability: {CAP-XX}

AC coverage:
  AC-{n}: COVERED — {test_file}::{test_function}
  AC-{n}: NOT COVERED — no test found
  ...

Definition of Done: {N}/{N} items met

---

### Summary
{2-4 sentences describing what the PR does, its overall quality, and the primary area of concern if any}

---

### Critical  🔴
{file/path.py}:{line} — {what is wrong}
  Why it matters: {concrete failure scenario}
  Fix: {specific action required}

---

### Major  🟠
{file/path.py}:{line} — {what is wrong}
  Why it matters: {impact}
  Fix: {specific action required}

---

### Minor  🟡
{file/path.py}:{line} — {what is wrong}
  Fix: {specific action required}

---

### Suggested Refactoring  🔧
1. {concrete suggestion with rationale — not style, only structural improvements}
2. ...

---

### Architecture Concerns  🏛️
{Any finding that does not yet violate the Constitution but erodes the architectural boundary or sets a precedent that will cause problems later}

---

### Production Risks  ⚠️
{Deployment risks, rollback concerns, migration risks, performance risks at scale}

---

### Lens Results
| Lens | Status | Findings |
|------|--------|---------|
| 0 Story Compliance | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 1 Architecture | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 2 Capability Boundary | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 3 Contracts | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 4 Infrastructure | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 5 API | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 6 Events | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 7 Security | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 8 Performance | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 9 Observability | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |
| 10 AI Engineering | ✅ PASS / ⚠️ WARN / N/A | {summary} |
| 11 Production Readiness | ✅ PASS / ⚠️ WARN / ❌ FAIL | {summary} |

---

### Merge Recommendation
{1-2 sentences. State clearly what must change before merge, or confirm the PR is ready.}

### Verdict
APPROVE | REQUEST CHANGES | NEEDS DISCUSSION
```

---

## Mandatory Verdict Rules

**`REQUEST CHANGES`** — required when any of the following are present, regardless of other lens results:

- Any Critical finding in any lens
- Constitution violation (any principle — A-series, H-series, S-series, MI-series)
- Contract violation — published event fails schema validation
- Agent selects model by name (MI3)
- Gate bypass mechanism introduced (H2)
- Unprotected API endpoint (no auth dependency)
- Database migration with no `downgrade()` function
- Dockerfile running as root
- Hardcoded credential anywhere in the diff

**`NEEDS DISCUSSION`** — required when:

- New infrastructure introduced that is not traceable to an acceptance criterion but may be intentional
- PR implements what appears to be multiple stories without clear justification
- Architectural boundary erosion that does not yet violate the Constitution but sets a problematic precedent
- AI cost impact appears significant and is undocumented

**`APPROVE`** — only when:

- All Critical and Major findings are resolved
- All acceptance criteria are covered
- Definition of Done Story-Level Gate is met
- No Constitution or contract violations

---

## Review Rules

1. Review only the PR diff — do not invent findings not present in the changed code
2. Architecture violations have higher priority than any code-quality finding
3. Constitution violations are always Critical
4. Contract violations are always Critical
5. Always explain why a finding matters — not just what is wrong
6. Always suggest a concrete fix — not general advice
7. Cite exact `file:line` from the diff for every finding
8. Do not review style before correctness
9. If a lens produces no findings, omit it from the output (show in the Lens Results table as ✅ PASS)
10. Maximum 20 findings total — prioritise severity, then impact, then frequency
11. Never approve a PR with an unresolved Critical finding
