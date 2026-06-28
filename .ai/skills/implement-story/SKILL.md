---
name: implement-story
description: |
  When the engineer types /implement-story <story_id>, execute the complete
  implementation workflow for a single User Story. Automatically validates
  story readiness, capability readiness, dependencies, infrastructure,
  and architecture before writing production code. One execution = one story.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq, pytest
  file: read, write
---

# implement-story

<purpose>
Complete implementation workflow for a single User Story on the Agentic Engineering
Platform. Validates story readiness, capability integrity, dependency satisfaction,
infrastructure requirements, and constitutional compliance before writing a single
line of production code. Engineers who skip phases ship to an unvalidated foundation.
One activation = one User Story. Never more.
</purpose>

---

## When To Activate

Trigger when the engineer types `/implement-story` followed by a User Story ID.

```
/implement-story US-01.03
/implement-story US-02.07
```

The story ID must exist in `docs/04-program/{PI}/USER_STORIES.md`.

---

## Workflow Position

```
implement-story → generate-tests → regression-review → aep-review
    → security-review (optional) → performance-review (optional) → release-story
```

This skill is the **single implementation entry point**. Do not write code before
completing all phases. Do not proceed to `generate-tests` until Phase 9 handoff is
produced.

---

## Substitutions Required

Before executing, resolve these substitutions from the story ID and context documents:

```
{story_id}      = the story ID passed by the engineer, e.g. US-02.03
{PI}            = the PI folder the story belongs to, e.g. PI-02-Agent-Runtime
{service_name}  = the service this story implements, e.g. agent-registry-service
{target_folder} = source path, e.g. src/platform/registry/
{CAP-XX}        = the capability this story belongs to, e.g. CAP-03
```

---

## Phase 1 — Read Context

**Read ALL of the following before doing anything else. No exceptions.**

```bash
# Platform authorities
cat CONSTITUTION.md
cat ARCHITECTURE.md
cat CLAUDE.md
cat DECISIONS.md

# Target PI
cat docs/04-program/{PI}/README.md
cat docs/04-program/{PI}/CAPABILITIES.md
cat docs/04-program/{PI}/USER_STORIES.md
cat docs/04-program/{PI}/ACCEPTANCE_CRITERIA.md
cat docs/04-program/{PI}/IMPLEMENTATION.md
cat docs/04-program/{PI}/PROMPT_MAPPING.md
cat docs/04-program/{PI}/DEFINITION_OF_DONE.md

# Contracts
ls contracts/
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
cat contracts/tool-contract.schema.json
cat contracts/task-schema.schema.json
cat contracts/memory-schema.schema.json

# Existing implementation (if any)
ls src/{target_folder}/
```

**Stop condition:** If `CONSTITUTION.md`, `ARCHITECTURE.md`, or the PI's `README.md`
cannot be read, stop immediately and report exactly which document is missing and why
it is required. Do not proceed until all mandatory inputs are available.

---

## Phase 2 — Story Readiness

**Validate before ANY other work. This phase has hard STOP conditions.**

### Story Validation

Confirm all of the following in order:

1. The story ID exists in `USER_STORIES.md`
2. The story follows the `As a / I want / so that` format
3. The story references exactly one Capability (`Capability: CAP-XX`)
4. The story references exactly one Sprint (`Sprint: N`)
5. An entry for this story ID exists in `ACCEPTANCE_CRITERIA.md`
6. Every criterion in `ACCEPTANCE_CRITERIA.md` for this story is written in Given/When/Then format
7. Every "Then" clause is observable and testable — not subjective ("works correctly" = FAIL)
8. The Story-Level Gate section exists in `DEFINITION_OF_DONE.md`

Output exactly this block:

```
Story ID:        {story_id}
Story title:     {title}
Capability:      {CAP-XX} — {name}
Sprint:          {N}
AC count:        {N} criteria found
DoD gate:        EXISTS / MISSING
Status:          READY / BLOCKED
```

**STOP if Status = BLOCKED.** List every missing or invalid item before stopping.
Do not continue to Phase 3 until Status = READY.

### Capability Validation

Cross-reference `CAPABILITIES.md` for the capability this story belongs to:

1. The capability section (`## CAP-XX`) exists in `CAPABILITIES.md`
2. The capability section contains technical contract content — not a one-line description
3. Required contract schemas are identified (cross-reference `contracts/`)
4. Dependencies between capabilities are documented

```bash
# Verify capability section exists and has content
rg "^## {CAP-XX}" docs/04-program/{PI}/CAPABILITIES.md
```

**STOP if the capability section is missing or incomplete.** A story cannot be
implemented against a capability with no technical specification.

---

## Phase 3 — Dependency Validation

**Verify all dependencies are satisfied before any planning begins.**

Check each of the following:

```bash
# Check sprint plan for story dependencies
rg "{story_id}" docs/04-program/{PI}/SPRINT_PLAN.md -A 10

# Verify aep-common is importable (PI-02+)
python -c "import aep_common; print('aep_common OK')" 2>/dev/null || echo "aep_common NOT AVAILABLE"

# Verify contract schemas referenced by this story exist
ls contracts/
```

Produce this output:

```
Dependencies check:
  Dependent stories:   {N} required, {N} complete, {N} BLOCKED
  Shared libraries:    EXISTS / MISSING
  Contract schemas:    {N} required, {N} found, {N} MISSING
  Unresolved:          {list any blocking items, or NONE}
  Status:              CLEAR / BLOCKED
```

For each dependent story: check whether it appears in the sprint plan as complete.
If a dependency story has not been implemented, list it as BLOCKED.

**STOP if Status = BLOCKED.** List every unresolved dependency with the action
required to clear it.

---

## Phase 4 — Infrastructure Assessment

**Determine the minimum infrastructure required by this story's acceptance criteria.**

Evaluate each component against the story's AC — not against future stories.
Write the completed table to `docs/04-program/{PI}/INFRASTRUCTURE.md` under a
section headed `## {story_id}`.

| Component | Required for this story | Already Exists | Action |
|-----------|------------------------|----------------|--------|
| Docker Compose | Yes/No | Yes/No/N/A | Use existing / Configure / Add service / Defer |
| PostgreSQL | Yes/No | Yes/No/N/A | Use existing / Add migration / Defer |
| Kafka | Yes/No | Yes/No/N/A | Use existing / Add topic / Defer |
| Redis | Yes/No | Yes/No/N/A | Use existing / Add key schema / Defer |
| OpenTelemetry | Yes/No | Yes/No/N/A | Use existing / Wire to service / Defer |
| Prometheus | Yes/No | Yes/No/N/A | Use existing / Add scrape config / Defer |
| Grafana | Yes/No | Yes/No/N/A | Use existing / Add dashboard / Defer |
| Vault | Yes/No | Yes/No/N/A | Use existing / Register secret / Defer |
| Kubernetes | Yes/No | Yes/No/N/A | Use existing / Add manifest / Defer |

### Infrastructure Rules

- **Only provision infrastructure required by the current story.** "May be needed
  later" = Defer.
- **Do not remove existing infrastructure** — mark it as existing and used, or note
  it is not needed for this story.
- If a required component does not exist, add only the minimum configuration needed
  for this story's AC to pass.

**STOP if a required infrastructure component cannot be determined from the AC.**
Clarify the acceptance criteria before proceeding.

---

## Phase 5 — Architecture Validation

**Check ALL of the following against `CONSTITUTION.md` and `ARCHITECTURE.md`.**

### Constitution Checks

Work through each principle in the changed service's scope:

| Principle | Check |
|-----------|-------|
| **A1** | No agent invokes another agent's module, API, or class directly |
| **A2** | `orchestrator-service` contains no specialist logic (LLM calls, code generation, scoring) |
| **A3** | New agents added via Agent Registry only — no orchestrator switch/dispatch modification |
| **A4** | No direct HTTP calls between services for business logic |
| **A5** | No service reads or writes another service's owned data store directly |
| **H2** | No flag, timeout, env var, or condition that can auto-approve a human gate |
| **SR1** | No hardcoded API keys, tokens, passwords, or connection strings |
| **SR3** | `tenant_id` in every memory query, task query, and policy check |
| **S1** | RBAC, Policy Engine, and Secrets Vault remain three separate services |
| **MI3** | No model name in agent code — `cost_class` only (low/medium/high) |

```bash
# Check for forbidden patterns in the target service
rg "from agents\." src/{target_folder}/ --include="*.py"
rg "bypass|skip_gate|auto_approve|EMERGENCY" src/{target_folder}/
rg "claude-|gpt-4|gemini-" src/{target_folder}/ --include="*.py"
rg "anthropic|openai" src/platform/orchestrator/ --include="*.py"
```

### ADR Validation

Read `DECISIONS.md`. If the planned implementation would contradict any existing ADR,
STOP and report the conflict with the specific ADR number and the conflicting design
choice.

### Capability Boundary Check

Confirm all planned files belong to the service owned by `{CAP-XX}`. No implementation
logic for this capability should land in a service owned by a different capability.

Output:

```
Architecture validation:
  Constitution:  PASS / VIOLATIONS (list each with principle ID)
  ADRs:          PASS / CONFLICTS (list each with ADR number)
  Boundaries:    PASS / VIOLATIONS (list each file out of scope)
  Status:        CLEAR / BLOCKED
```

**STOP if Status = BLOCKED.** Do not write implementation code against a violated
architecture.

---

## Phase 6 — Implementation Plan

**Produce this plan before writing any code. Do not proceed until the plan is confirmed correct.**

```
## Implementation Plan: {story_id} — {story_title}

### Files to create
- {path}: {purpose and which AC it serves}

### Files to modify
- {path}: {what changes and why}

### Package structure
{only if new packages or modules are introduced — otherwise omit}

### APIs
{new endpoints: method, path, auth dependency, purpose}
{NONE if story produces no endpoints}

### Events
{new Kafka topics/event types: topic name, producer service, consumer service}
{NONE if story produces no events}

### Database changes
{new tables, columns, indexes, and migration file path}
{NONE if story requires no schema changes}

### Configuration changes
{new environment variables — name, type, description, example value}
{NONE if no new env vars}

### Observability changes
{new Prometheus metrics, OTEL trace spans, structured log events, Grafana dashboards}
{NONE if story requires no new observability}

### Infrastructure to provision (from Phase 4)
{what is being added, referencing the specific AC that requires it}
{NONE if no new infrastructure}

### Constitutional constraints applied
- {principle_id}: {how compliance is enforced in this implementation}
```

This plan must cover **this story only**. Any item that references a future story
or a "nice to have" must be removed before proceeding.

---

## Phase 7 — Production Implementation

**Implement exactly what is in the approved plan. Nothing more.**

### Non-Negotiable Code Standards

**Architecture:**
- All inter-service communication via Kafka using `aep_common.kafka` — no direct HTTP
  calls between services for business logic
- All database queries include `tenant_id` — RLS enforced at the storage layer
- No vendor SDK imports in agent or tool code — all external tools accessed via
  Tool Registry

**Configuration:**
- All configuration from environment variables via Pydantic Settings
- No hardcoded values — credentials, URLs, tenant IDs, topic names, model names

**Error handling:**
- All exceptions are typed — no bare `except:` or `except Exception: pass`
- All errors logged with structured context before re-raising or returning
- Agent and tool failures publish `AgentFailed` or `ToolFailed` events
- No silent failures

**Logging:**
- All log lines use `aep_common.logging` — never `print()` or Python's built-in
  `logging` directly
- Every log line in task context includes `task_id`, `workflow_run_id`, `tenant_id`

**Observability — on every new public domain method:**

```python
from aep_common.tracing import get_tracer

tracer = get_tracer(__name__)

with tracer.start_as_current_span("method_name") as span:
    span.set_attribute("task_id", str(task_id))
    span.set_attribute("tenant_id", tenant_id)
```

Every new service exposes:
- `aep_{service}_requests_total` — counter by status
- `aep_{service}_request_duration_seconds` — histogram
- `aep_{service}_errors_total` — counter by error type

**Code quality:**
- Type hints on every function signature
- Docstrings on public methods describe intent, not mechanics
- No `TODO`, `FIXME`, or `HACK` in production code paths
- No placeholder implementations or stubs

### Tests (written alongside implementation)

- **Unit tests** — one test file per `domain/` module, happy path and at least two
  edge cases per method
- **Integration test** — end-to-end test for the primary Kafka event flow
- **Acceptance tests** — one test per Given/When/Then criterion, named
  `test_ac_{criterion_id}_{description}`
- **Isolation test** — cross-tenant query returns zero rows, if the story touches data

Every test must fail when the code it tests is removed. No vacuous assertions.

---

## Phase 8 — Self Validation

**Work through every check before declaring the story complete.**

### Acceptance Criteria Coverage

For each criterion defined in Phase 2:

```
AC-{n}: {criterion text}
  Satisfied by: {file and method}
  Tested by:    {test file and test name}
  Status:       SATISFIED / NOT SATISFIED
```

**Return to Phase 7 if any criterion is NOT SATISFIED.**

### Definition of Done — Story-Level Gate

Work through every item. Report each as checked or blocked with the file/line that
needs to change:

```
[ ] Architecture — no direct HTTP calls between services
[ ] Architecture — config from environment variables only
[ ] Architecture — no hardcoded credentials
[ ] Database — tenant_id in every query
[ ] Database — RLS policy on every new table
[ ] Database — migration has downgrade()
[ ] Kafka — offset committed after successful processing
[ ] Kafka — failed messages routed to DLQ
[ ] Code quality — ruff check exits 0
[ ] Code quality — black --check exits 0
[ ] Code quality — mypy --strict exits 0
[ ] Code quality — no TODO/FIXME in production paths
[ ] Testing — unit coverage ≥ 80% on new code
[ ] Testing — acceptance test per AC criterion
[ ] Security — detect-secrets finds zero new secrets
[ ] Security — non-root user in Dockerfile (if applicable)
[ ] Observability — OTEL traces on all public domain methods
[ ] Observability — Prometheus metrics exposed
[ ] Observability — structured logs with correlation IDs
[ ] Documentation — .env.example updated for new variables
```

### Contract Compliance

If the story produces or consumes Kafka events:
- [ ] Every published message validates against `contracts/event-envelope.schema.json`
- [ ] Event type follows PascalCase convention (`AgentCompleted`, not `agent_completed`)
- [ ] Topic name follows `aep.{domain}.{event-type-kebab}` convention

If the story registers an agent or tool:
- [ ] Registration validates against `contracts/agent-contract.schema.json` or
  `contracts/tool-contract.schema.json`

### Constitution Compliance Re-check

Re-run the checks from Phase 5 against the implemented code. A passing Phase 5 plan
does not guarantee a passing implementation.

```bash
rg "from agents\." src/{target_folder}/ --include="*.py"
rg "bypass|skip_gate|auto_approve|EMERGENCY" src/{target_folder}/
rg "claude-|gpt-4|gemini-" src/{target_folder}/ --include="*.py"
rg "print(" src/{target_folder}/ --include="*.py"
python -m detect_secrets scan src/{target_folder}/
ruff check src/{target_folder}/
black --check src/{target_folder}/
mypy --strict src/{target_folder}/
```

**Do not declare the story complete with any unmet item.** Report every failure with
the specific file and line that needs to change, then return to Phase 7.

---

## Phase 9 — Handoff

**Produce this summary when all Phase 8 checks pass.**

```
## Implementation Summary: {story_id} — {story_title}

### Files created
- {path}: {one-line description}

### Files modified
- {path}: {what changed}

### Infrastructure added
- {component}: {what was configured, which AC required it}

### Infrastructure deferred
- {component}: {why not needed for this story}

### Commands to run

  # Install
  {command}

  # Migrations (if applicable)
  alembic upgrade head

  # Tests
  pytest src/tests/unit/{service_name}/ -v --cov={target_folder}
  pytest src/tests/integration/{service_name}/ -v

  # Lint and type check
  ruff check src/{target_folder}/
  black --check src/{target_folder}/
  mypy --strict src/{target_folder}/

### Known limitations
{anything not covered that a reviewer should know — or NONE}

### Recommended next story
{story_id from SPRINT_PLAN.md that logically follows}

### Next workflow step
Run: /generate-tests {story_id}
Then: /regression-review <PR_NUMBER>
Then: /aep-review <PR_NUMBER>
Then: /release-story <PR_NUMBER>
```

---

## Engineering Rules

- Never redesign the architecture
- Never modify `CONSTITUTION.md`, `ARCHITECTURE.md`, `CLAUDE.md`, or any PI document
- Never introduce new platform capabilities not defined in `CAPABILITIES.md`
- Never implement more than one story per execution
- Never provision infrastructure not required by the current story's AC
- Never generate placeholder code or leave `TODO` comments in production paths
- Always produce production-ready code — assume Principal Engineer review
- Always stop and report when a required input is missing or a dependency is unmet
- Always optimise for maintainability over speed

---

## Forbidden Actions

- Skip any phase or reorder phases
- Proceed past a Stop condition without resolving it
- Implement more than one User Story
- Add infrastructure "for later" — every infrastructure decision must trace to an AC
- Import vendor SDKs in agent or tool code
- Hardcode credentials, URLs, topic names, model names, or tenant IDs
- Silent exception handling
- Placeholder implementations or stubs
- Add a new direct HTTP call between platform services
- Modify a contract schema without an ADR in `DECISIONS.md`
- Omit type hints or use `any` in TypeScript
- Invoke `/generate-tests`, `/aep-review`, `/regression-review`, or `/release-story`
  during this skill — those are separate steps run after Phase 9 completes
- Sprint planning, velocity tracking, risk register management, or PI objectives review
  are not part of this skill
