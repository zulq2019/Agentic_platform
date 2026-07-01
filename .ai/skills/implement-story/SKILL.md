---
name: implement-story
description: |
  When the engineer types /implement-story <story_ref>, execute the complete
  Architecture v2.0-aware implementation workflow for a single User Story.
  Automatically builds full execution context (platform constitution, PI context,
  dependency analysis), validates story readiness, then implements with DDD,
  hexagonal architecture, and metadata-driven patterns. One execution = one story.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq, pytest
  file: read, write
---

# implement-story

**Version:** 4.0 — Architecture v2.0-aware execution pipeline  
**Backward compatible:** `/implement-story US-01.03` works exactly as before.

<purpose>
Complete implementation workflow for a single User Story on the Agentic Engineering
Platform. Before writing production code, automatically builds the full Architecture
v2.0 execution context — platform constitution, repository constitution, PI context,
and dependency graph. Validates story readiness, capability integrity, dependency
satisfaction, infrastructure requirements, and constitutional compliance. Engineers
who skip phases ship to an unvalidated foundation. One activation = one User Story.
Never more.
</purpose>

---

## When To Activate

Trigger when the engineer types `/implement-story` followed by any story reference.
The invocation format is **unchanged** for existing users; additional forms are
supported for Architecture v2.0.

```
/implement-story US-01.03
/implement-story PI-02 US-02.01
/implement-story US-02.01
/implement-story Platform Object Framework
/implement-story current story
/implement-story next story
```

| Input form | Resolution behaviour |
|------------|---------------------|
| Story ID only (`US-02.01`) | Search all `docs/engineering/implementation-roadmap/*/USER_STORIES.md` |
| PI + Story ID (`PI-02 US-02.01`) | Resolve PI folder, then locate story within that PI |
| Story name (`Platform Object Framework`) | Case-insensitive title match across all PI `USER_STORIES.md` files |
| `current story` | First story marked **In Progress** or first **Planned** in target PI `STATUS.md` |
| `next story` | First **Planned** story after the last **Complete** story in `STATUS.md` + `SPRINT_PLAN.md` |

The resolved story must exist in `docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md`.

---

## Architecture v2.0 Execution Pipeline

Execute **all steps in order**. Steps map to phases below — phases are not removed,
only extended. Do not write production code until Step 6 (Phase 6) planning is complete.

| Step | Name | Phase |
|------|------|-------|
| 1 | Read Platform Constitution | Phase 1 |
| 2 | Read Repository Constitution | Phase 1 |
| 3 | Resolve Story | Pre-Phase 2 |
| 4 | Read PI Context | Phase 1 |
| 5 | Dependency Analysis | Phase 3 |
| 6 | Generate Implementation Plan | Phase 6 |
| 7 | Implement | Phase 7 |
| 8 | Generate Tests | Phase 7 + Phase 8 |
| 9 | Run Reviews | Phase 8 (Reviews subsection) |
| 10 | Update Documentation | Phase 8 (Documentation subsection) |
| 11 | Generate Summary & Handoff | Phase 9 |

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

Before executing, resolve these substitutions from the story reference and context documents:

```
{story_id}      = the resolved story ID, e.g. US-02.01
{story_title}   = human-readable title from USER_STORIES.md
{PI}            = the PI folder the story belongs to, e.g. PI-02-Metadata-Engine
{PI_SHORT}      = shorthand prefix, e.g. PI-02
{service_name}  = the service this story implements, e.g. metadata-engine
{target_folder} = source path, e.g. src/shared/aep_meta/ or src/platform/services/metadata-engine/
{CAP-XX}        = the capability this story belongs to, e.g. CAP-03
```

### PI folder resolution

When the engineer supplies a PI shorthand (`PI-02`), resolve to the v2 folder name:

```bash
ls docs/engineering/implementation-roadmap/ | rg "^{PI_SHORT}"
# PI-01 → PI-01-Platform-Core
# PI-02 → PI-02-Metadata-Engine
# PI-03 → PI-03-Provider-Framework
# PI-04 → PI-04-Workflow-Framework
# PI-05 → PI-05-Execution-Framework
# PI-06 → PI-06-Studio-Framework
# PI-07 → PI-07-Platform-Services
# PI-08 → PI-08-Solution-Packs
# PI-09 → PI-09-Platform-UX
# PI-10 → PI-10-General-Availability
```

---

## Phase 1 — Read Context (Steps 1, 2, 4)

**Read ALL of the following before doing anything else. No exceptions.**

### Step 1 — Platform Constitution (Architecture v2.0)

Always load these documents first. They define primitives, contracts, meta-model,
UX model, glossary, and metadata-driven architecture for v2.

```bash
# Platform constitution — Architecture v2.0 baseline
cat docs/architecture/PLATFORM_PRIMITIVES.md
cat docs/architecture/PLATFORM_CONTRACTS.md
cat docs/architecture/PLATFORM_META_MODEL.md
cat docs/architecture/PLATFORM_UX_MODEL.md
cat docs/architecture/PLATFORM_GLOSSARY.md
cat docs/architecture/METADATA_DRIVEN_ENTERPRISE_PLATFORM.md
cat docs/architecture/ARCHITECTURE_BASELINE_V2.md
```

**Stop condition:** If any of the above cannot be read, stop and report which
document is missing. These are mandatory for Architecture v2.0 stories.

### Step 2 — Repository Constitution

```bash
# Repository authorities
cat CONSTITUTION.md
cat ARCHITECTURE.md
cat CLAUDE.md
cat docs/architecture/ADR/DECISIONS.md   # ADR authority (root DECISIONS.md is a redirect stub)
```

### Step 4 — PI Context

After Step 3 resolves `{PI}` and `{story_id}`, read the complete PI execution context:

```bash
# Target PI — full context pack
cat docs/engineering/implementation-roadmap/{PI}/README.md
cat docs/engineering/implementation-roadmap/{PI}/OBJECTIVES.md
cat docs/engineering/implementation-roadmap/{PI}/CAPABILITIES.md
cat docs/engineering/implementation-roadmap/{PI}/FEATURES.md
cat docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md
cat docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md
cat docs/engineering/implementation-roadmap/{PI}/IMPLEMENTATION.md
cat docs/engineering/implementation-roadmap/{PI}/API_SPEC.md
cat docs/engineering/implementation-roadmap/{PI}/DATA_MODEL.md
cat docs/engineering/implementation-roadmap/{PI}/TESTING.md
cat docs/engineering/implementation-roadmap/{PI}/PROMPT_MAPPING.md
cat docs/engineering/implementation-roadmap/{PI}/SPRINT_PLAN.md
cat docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md
cat docs/engineering/implementation-roadmap/{PI}/REVIEW_CHECKLIST.md
cat docs/engineering/implementation-roadmap/{PI}/STATUS.md
cat docs/engineering/implementation-roadmap/{PI}/CHANGELOG.md
cat docs/engineering/implementation-roadmap/{PI}/METRICS.md

# Contracts — v1 + v2 schemas relevant to this story
ls contracts/
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
cat contracts/tool-contract.schema.json
cat contracts/task-schema.schema.json
cat contracts/memory-schema.schema.json
cat contracts/platform-object.schema.json    # v2 — Platform Object envelope

# Existing implementation (if any)
ls src/{target_folder}/ 2>/dev/null || ls src/shared/ src/platform/services/
```

**Stop condition:** If `CONSTITUTION.md`, `ARCHITECTURE.md`, `ARCHITECTURE_BASELINE_V2.md`,
or the PI's `README.md` cannot be read, stop immediately and report exactly which
document is missing and why it is required. Do not proceed until all mandatory
inputs are available.

---

## Step 3 — Resolve Story (Pre-Phase 2)

**Resolve `{story_id}`, `{story_title}`, and `{PI}` before story readiness validation.**

### Resolution algorithm

```bash
# 1. If engineer passed PI shorthand + story ID
#    e.g. /implement-story PI-02 US-02.01
#    → {PI} = PI-02-Metadata-Engine, {story_id} = US-02.01

# 2. If engineer passed story ID only
rg "^## {story_id}" docs/engineering/implementation-roadmap/*/USER_STORIES.md -l

# 3. If engineer passed story name (fuzzy title match)
rg -i "{story_name}" docs/engineering/implementation-roadmap/*/USER_STORIES.md -B 1

# 4. If engineer passed "current story"
#    Read STATUS.md — first row with status In Progress, else first Planned
cat docs/engineering/implementation-roadmap/{PI}/STATUS.md

# 5. If engineer passed "next story"
#    Read STATUS.md + SPRINT_PLAN.md — first Planned after last Complete
cat docs/engineering/implementation-roadmap/{PI}/STATUS.md
rg "{story_id}" docs/engineering/implementation-roadmap/{PI}/SPRINT_PLAN.md -A 5
```

### Resolution output (required before Phase 2)

```
Story reference:   {what the engineer typed}
Story ID:          {story_id}
Story title:       {story_title}
PI:                {PI}
PI README:         docs/engineering/implementation-roadmap/{PI}/README.md
Resolution:        FOUND / AMBIGUOUS / NOT FOUND
```

**STOP if Resolution = NOT FOUND or AMBIGUOUS.** List candidate matches and ask the
engineer to disambiguate. Do not guess.

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
rg "^## {CAP-XX}" docs/engineering/implementation-roadmap/{PI}/CAPABILITIES.md
```

**STOP if the capability section is missing or incomplete.** A story cannot be
implemented against a capability with no technical specification.

---

## Phase 3 — Dependency Validation (Step 5)

**Verify all dependencies are satisfied before any planning begins.**

### Architecture v2.0 dependency dimensions

Identify and document dependencies across all applicable dimensions:

| Dimension | Where to check | What to verify |
|-----------|----------------|----------------|
| Architecture dependencies | `ARCHITECTURE_BASELINE_V2.md`, `CAPABILITIES.md`, ADRs | Required framework/container exists or is in scope for this story |
| Story dependencies | `SPRINT_PLAN.md`, `STATUS.md` | Prerequisite stories marked **Complete** |
| Platform Object dependencies | `PLATFORM_PRIMITIVES.md` §3, `platform-object.schema.json` | Story extends or consumes Platform Object envelope correctly |
| Provider dependencies | `PLATFORM_META_MODEL.md`, PI `DATA_MODEL.md` | Provider Contract / Provider Registry readiness |
| Workflow dependencies | `workflows/`, PI `SEQUENCE_DIAGRAMS.md` | Workflow templates or state machines this story assumes |
| Execution Profile dependencies | `ARCHITECTURE_BASELINE_V2.md`, ADRs 012/027 | Execution Profile schema or runtime hooks required |
| Configuration dependencies | PI `IMPLEMENTATION.md`, `INFRASTRUCTURE.md` | Env vars, feature flags, tenant config surfaces |
| Plugin dependencies | `PLATFORM_PRIMITIVES.md`, PI `CAPABILITIES.md` | Extension points, registries, or plugin slots required |

```bash
# Check sprint plan for story dependencies
rg "{story_id}" docs/engineering/implementation-roadmap/{PI}/SPRINT_PLAN.md -A 10

# Verify shared libraries
python -c "import aep_common; print('aep_common OK')" 2>/dev/null || echo "aep_common NOT AVAILABLE"
python -c "import aep_meta; print('aep_meta OK')" 2>/dev/null || echo "aep_meta NOT AVAILABLE (OK if story does not need it)"

# Verify contract schemas referenced by this story exist
ls contracts/

# Platform Object consumers — check aep_meta if story touches metadata engine
rg "PlatformObject|aep_meta|platform-object" docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md
```

Produce this output:

```
Dependencies check:
  Architecture:        {N} required, {N} satisfied, {N} BLOCKED
  Story dependencies:  {N} required, {N} complete, {N} BLOCKED
  Platform Objects:    {required / not applicable}
  Providers:           {required / not applicable}
  Workflows:           {required / not applicable}
  Execution Profiles:  {required / not applicable}
  Configuration:       {required / not applicable}
  Plugins:             {required / not applicable}
  Shared libraries:    aep_common EXISTS / MISSING | aep_meta EXISTS / MISSING / N/A
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
Write the completed table to `docs/engineering/implementation-roadmap/{PI}/INFRASTRUCTURE.md` under a
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

Read `docs/architecture/ADR/DECISIONS.md`. If the planned implementation would
contradict any existing ADR, STOP and report the conflict with the specific ADR
number and the conflicting design choice.

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

## Phase 6 — Implementation Plan (Step 6)

**Produce this plan before writing any code. Do not proceed until the plan is confirmed correct.**

```
## Implementation Plan: {story_id} — {story_title}

### Design
{high-level design: aggregate roots, bounded context, service boundaries, event flows}
{how this story fits Architecture v2.0 primitives and metadata-driven model}

### Files to create
- {path}: {purpose and which AC it serves}

### Files to modify
- {path}: {what changes and why}

### Interfaces
{domain ports, application services, API handlers, Kafka producers/consumers}
{hexagonal: domain → application → infrastructure adapters}

### Contracts
{JSON Schema files, event envelope shapes, Platform Object envelope usage}
{NONE if story produces no new contracts}

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
{NONE if no new env vars — everything configurable, no hardcoded business logic}

### Observability changes
{new Prometheus metrics, OTEL trace spans, structured log events, Grafana dashboards}
{NONE if story requires no new observability}

### Infrastructure to provision (from Phase 4)
{what is being added, referencing the specific AC that requires it}
{NONE if no new infrastructure}

### Risks
{technical risks, migration risks, tenancy risks, performance risks}
{mitigation for each}

### Testing strategy
{unit / integration / contract / regression / tenancy isolation — mapped to ACs}

### Rollback
{how to revert: migration downgrade, feature flag, deployment order}
{NONE if purely additive with safe downgrade}

### Constitutional constraints applied
- {principle_id}: {how compliance is enforced in this implementation}
```

This plan must cover **this story only**. Any item that references a future story
or a "nice to have" must be removed before proceeding.

---

## Phase 7 — Production Implementation (Step 7)

**Implement exactly what is in the approved plan. Nothing more.**

### Architecture v2.0 Implementation Principles

Apply these in addition to all code standards below:

| Principle | Requirement |
|-----------|-------------|
| **DDD** | Bounded contexts, aggregates, domain events; business rules in `domain/` only |
| **SOLID** | Single responsibility per module; depend on ports not adapters |
| **Hexagonal** | `domain/` → `application/` → `infrastructure/`; no infrastructure imports in domain |
| **Platform Contracts** | Validate at boundaries against JSON Schema in `contracts/` |
| **Metadata Driven** | Platform Objects use `aep_meta` + `platform-object.schema.json` envelope |
| **Configurable** | No hardcoded business logic, tenant rules, or workflow definitions in code |
| **Generic primitives** | No business-specific logic in shared libraries (`aep_common`, `aep_meta`) |

### Non-Negotiable Code Standards

**Architecture:**
- All inter-service communication via Kafka using `aep_common.kafka` — no direct HTTP
  calls between services for business logic
- All database queries include `tenant_id` — RLS enforced at the storage layer
- No vendor SDK imports in agent or tool code — all external tools accessed via
  Tool Registry / Provider Framework
- Platform Objects inherit the universal envelope — identity, lifecycle, versioning,
  relationships, audit, health, metrics, extensions per `PLATFORM_PRIMITIVES.md` §3

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

### Tests (Step 8 — written alongside implementation)

Generate all test categories required by the story. Mark tests with `@pytest.mark.story_{story_id}`.

- **Unit tests** — one test file per `domain/` module, happy path and at least two
  edge cases per method
- **Integration tests** — end-to-end test for the primary flow (Kafka event flow,
  REST API, or DB migration as applicable)
- **Contract tests** — validate payloads against `contracts/*.schema.json` at boundaries;
  include `platform-object.schema.json` when story produces Platform Objects
- **Regression tests** — verify no breaking change to existing shared interfaces,
  event schemas, or API paths touched by this story
- **Acceptance tests** — one test per Given/When/Then criterion, named
  `test_ac_{criterion_id}_{description}`
- **Isolation test** — cross-tenant query returns zero rows, if the story touches data

Every test must fail when the code it tests is removed. No vacuous assertions.

```bash
# Run story tests before leaving Phase 7
pytest -m "story_{story_id}" -v
python scripts/validate_contract.py contracts/
```

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

If the story produces or consumes Platform Objects:
- [ ] Payload validates against `contracts/platform-object.schema.json`
- [ ] Lifecycle transitions follow FSM in `PLATFORM_PRIMITIVES.md` §3.4

### Step 9 — Architecture-Aware Reviews

Perform inline review passes before declaring the story complete. Use the PI
`REVIEW_CHECKLIST.md` and the criteria from each review skill. Produce a verdict
for each review.

#### Architecture Review
- [ ] Bounded context respected — no cross-service data access (AR5)
- [ ] Hexagonal layers correct — domain has no infrastructure imports
- [ ] Platform Object envelope complete if applicable
- [ ] No constitutional violations (re-run Phase 5 checks on implemented code)
- **Verdict:** PASS / FAIL — {findings}

#### Security Review
- [ ] No credentials in code, images, or config (SR1)
- [ ] `tenant_id` in every data query (SR3)
- [ ] RBAC, Policy, Secrets remain separate (SR1/S4)
- [ ] Input validated at boundaries (SR5)
- [ ] `detect-secrets` finds zero new secrets
- **Verdict:** PASS / FAIL — {findings}

#### Performance Review
- [ ] No unbounded queries or N+1 patterns in new hot paths
- [ ] Indexes on tenant-scoped query columns where applicable
- [ ] Kafka consumer commits offset after successful processing
- **Verdict:** PASS / N/A / FAIL — {findings}

#### Regression Review
- [ ] No breaking changes to existing contract schemas (additive only, or version bumped + ADR)
- [ ] No renamed/removed exports in `aep_common` without importer audit
- [ ] No breaking API path or payload changes without version increment
- [ ] Database migration is additive or has documented migration path
- [ ] If PR is open: recommend `/regression-review <PR_NUMBER>` for full 11-lens review
- **Verdict:** PASS / NEEDS PR REVIEW / FAIL — {findings}

#### Documentation Review
- [ ] PI `STATUS.md`, `CHANGELOG.md`, `METRICS.md` updated (Step 10)
- [ ] Contract README updated if new schema added
- [ ] `.env.example` updated for new variables
- [ ] ADR added if architectural decision made
- **Verdict:** PASS / FAIL — {findings}

**Return to Phase 7 if any review verdict is FAIL.**

### Step 10 — Update Documentation

Update PI tracking documents for `{story_id}`:

```bash
# Required updates in docs/engineering/implementation-roadmap/{PI}/
# STATUS.md    — mark story Complete; update deliverable table
# CHANGELOG.md — add entry under [version] with story changes
# METRICS.md   — update test counts, coverage, endpoints, tables
```

Also update when applicable:
- `docs/engineering/implementation-roadmap/{PI}/diagrams/` — architecture diagram if story changes structure
- `docs/architecture/ADR/DECISIONS.md` — new ADR if constitutional or architectural decision made
- `contracts/README.md` — if new contract schema added
- `docs/engineering/implementation-roadmap/{PI}/docs/US-{PI}-{NN}-implementation-plan.md` — if not already written in Phase 6
- `docs/engineering/implementation-roadmap/{PI}/docs/US-{PI}-{NN}-implementation-summary.md` — draft in Phase 9

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

## Phase 9 — Handoff (Step 11)

**Produce this summary when all Phase 8 checks and Step 9 reviews pass.**

```
## Implementation Summary: {story_id} — {story_title}

### Architecture v2.0 context
PI:                {PI}
Capability:        {CAP-XX} — {name}
Primitives used:   {list Platform Object types, Providers, etc. or NONE}
Contracts:         {list contract schemas touched}

### Files created
- {path}: {one-line description}

### Files modified
- {path}: {what changed}

### Infrastructure added
- {component}: {what was configured, which AC required it}

### Infrastructure deferred
- {component}: {why not needed for this story}

### Review verdicts (Step 9)
| Review | Verdict |
|--------|---------|
| Architecture | PASS / FAIL |
| Security | PASS / FAIL |
| Performance | PASS / N/A / FAIL |
| Regression | PASS / NEEDS PR REVIEW / FAIL |
| Documentation | PASS / FAIL |

### Commands to run

  # Install
  {command}

  # Migrations (if applicable)
  alembic upgrade head

  # Tests
  pytest -m "story_{story_id}" -v
  pytest src/tests/unit/{service_name}/ -v --cov={target_folder}
  pytest src/tests/integration/{service_name}/ -v

  # Lint and type check
  ruff check src/{target_folder}/
  black --check src/{target_folder}/
  mypy --strict src/{target_folder}/

  # Contract validation
  python scripts/validate_contract.py contracts/

### Known risks
{residual risks from implementation plan — or NONE}

### Known limitations
{anything not covered that a reviewer should know — or NONE}

### PR summary (draft)
**Title:** feat({scope}): {story_id} {story_title}
**Summary:** {2-3 bullets}
**Test plan:** {checklist}

### Recommended next story
{story_id from STATUS.md / SPRINT_PLAN.md that logically follows}

### Next workflow step
Run: /generate-tests {story_id}   # if additional test coverage needed
Then: /regression-review <PR_NUMBER>
Then: /aep-review <PR_NUMBER>
Then: /release-story <PR_NUMBER>
```

---

## Engineering Rules

- Never redesign the architecture
- Never modify `CONSTITUTION.md`, `ARCHITECTURE.md`, `CLAUDE.md`, or PI tracking
  documents (`STATUS.md`, `CHANGELOG.md`, `METRICS.md`) **except** as required by
  Step 10 documentation updates for the current story
- Never introduce new platform capabilities not defined in `CAPABILITIES.md`
- Never implement more than one story per execution
- Never provision infrastructure not required by the current story's AC
- Never generate placeholder code or leave `TODO` comments in production paths
- Never hardcode business logic — use configuration, metadata, and Platform Objects
- Always read Architecture v2.0 platform constitution (Step 1) before PI context
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
- Modify a contract schema without an ADR in `docs/architecture/ADR/DECISIONS.md`
- Omit type hints or use `any` in TypeScript
- Skip Step 9 inline reviews or Step 10 documentation updates
- Invoke `/release-story` during this skill — run after PR is opened
- Sprint planning, velocity tracking, risk register management, or PI objectives review
  are not part of this skill (except reading `STATUS.md` for story resolution)
