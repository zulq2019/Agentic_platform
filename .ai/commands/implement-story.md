# implement-story.md

**Command:** `implement-story`  
**Version:** 3.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs, all sprints

---

## Purpose

Use this command to implement a single User Story from specification to production-ready code.

This command is the standard implementation workflow for every engineer and every AI coding agent working on the Agentic Engineering Platform. It is capability-driven, infrastructure-aware, and implementation-focused.

Execute every phase in order. Do not skip phases. Do not combine phases.

One execution = one User Story. Never more.

---

## Phase 1 — Read Context

Read every item in this list before doing anything else. Stop and report what is missing if any mandatory input cannot be found.

| Input | Location | Required |
|-------|----------|----------|
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture | `ARCHITECTURE.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| PI README | `docs/04-program/{PI}/README.md` | Mandatory |
| Capabilities | `docs/04-program/{PI}/CAPABILITIES.md` | Mandatory |
| User Stories | `docs/04-program/{PI}/USER_STORIES.md` | Mandatory |
| Acceptance Criteria | `docs/04-program/{PI}/ACCEPTANCE_CRITERIA.md` | Mandatory |
| Implementation Guide | `docs/04-program/{PI}/IMPLEMENTATION.md` | Mandatory |
| Prompt Mapping | `docs/04-program/{PI}/PROMPT_MAPPING.md` | Mandatory |
| Contract schemas | `contracts/` — schemas relevant to this story | If story produces or consumes events, registers an agent or tool |
| Existing implementation | `src/{target_folder}/` — code already written for this service | If the service has been started in a prior story |

**Substitutions required before executing:**

```
{PI}            = e.g. PI-02-Agent-Runtime
{story_id}      = e.g. US-02.03
{service_name}  = e.g. agent-registry-service
{target_folder} = e.g. src/platform/registry/
```

**Stop condition:** If any mandatory input is missing, report exactly which document is missing and why it is needed. Do not proceed.

---

## Phase 2 — Understand the Story

Extract and state the following before any planning or coding begins:

```
Story ID:           {story_id}
Story title:        {story_title}
Capability:         {CAP-XX} — {capability_name}
Sprint:             Sprint {N}
PI:                 {PI}

Dependencies:
  Stories:          {list of story IDs that must be complete first, or NONE}
  Infrastructure:   {list of infrastructure components this story assumes exist}

Acceptance Criteria:
  AC-{n}: {Given / When / Then}
  AC-{n}: ...

Definition of Done:
  → docs/04-program/{PI}/DEFINITION_OF_DONE.md — Story-Level Gate
```

**Confirm:** Only one User Story is being implemented. If the scope covers more than one story, stop and state which story to implement first.

**Verify dependencies:** Check `SPRINT_PLAN.md`. If any story listed as a dependency is not complete, stop and report the blocking dependency.

---

## Phase 3 — Infrastructure Assessment

Before writing any code, determine which infrastructure components are required by this story specifically. Write the result to `docs/04-program/{PI}/INFRASTRUCTURE.md` under a section for `{story_id}`.

### Assessment table

Evaluate each component:

| Component | Required for this story | Already Exists | Action |
|-----------|------------------------|----------------|--------|
| Docker Compose | Yes / No | Yes / No / N/A | Use existing / Configure / Add service / Defer |
| PostgreSQL | Yes / No | Yes / No / N/A | Use existing / Add migration / Defer |
| Kafka | Yes / No | Yes / No / N/A | Use existing / Add topic / Defer |
| Redis | Yes / No | Yes / No / N/A | Use existing / Add key schema / Defer |
| OpenTelemetry | Yes / No | Yes / No / N/A | Use existing / Wire to service / Defer |
| Prometheus | Yes / No | Yes / No / N/A | Use existing / Add scrape config / Defer |
| Grafana | Yes / No | Yes / No / N/A | Use existing / Add dashboard / Defer |
| GitHub Actions | Yes / No | Yes / No / N/A | Use existing / Add step / Defer |
| Vault | Yes / No | Yes / No / N/A | Use existing / Register secret / Defer |
| Kubernetes | Yes / No | Yes / No / N/A | Use existing / Add manifest / Defer |

### Infrastructure rules

- **Only provision or configure infrastructure required for the current story.** If a component is not needed to satisfy the acceptance criteria, mark it Defer.
- **Do not introduce infrastructure because it may be needed later.** Future stories will assess their own infrastructure needs.
- **Do not remove existing infrastructure.** Mark it as already existing and used, or note it is not needed for this story.
- If a required component does not yet exist, add only the minimum configuration needed for this story to pass its acceptance criteria.

**Stop condition:** If the required infrastructure cannot be determined from the story's acceptance criteria and capability definition, clarify before proceeding.

---

## Phase 4 — Implementation Plan

Produce a short, focused plan. Do not over-design. Every item in the plan must be traceable to a specific acceptance criterion or infrastructure requirement.

```
## Implementation Plan: {story_id} — {story_title}

### Files to create
- {path}: {purpose and which AC it serves}

### Files to modify
- {path}: {what changes and why}

### Package structure
{only if new packages or modules are introduced}

### APIs
{list any new HTTP endpoints — method, path, purpose}
{NONE if story produces no endpoints}

### Events
{list any new Kafka topics or event types — topic name, producer, consumer}
{NONE if story produces no events}

### Infrastructure changes
{reference the Infrastructure Assessment table — what is being added or configured}

### External dependencies
{any new pyproject.toml or go.mod entries required}

### Constitutional constraints that apply
- {principle_id}: {how compliance is enforced in this implementation}
```

Do not proceed to Phase 5 until this plan is confirmed correct.

---

## Phase 5 — Production Implementation

Implement exactly what is in the approved plan. Nothing more.

### Code standards (non-negotiable)

**Architecture:**
- All inter-service communication via Kafka using `aep_common.kafka` — no direct HTTP calls between services
- All database queries include `tenant_id` — RLS enforced at the storage layer
- No vendor SDK imports in agent or tool code — all external tools accessed via Tool Registry

**Configuration:**
- All configuration from environment variables via Pydantic Settings
- No hardcoded values — credentials, URLs, tenant IDs, topic names

**Error handling:**
- All exceptions are typed — no bare `except:` or `except Exception: pass`
- All errors are logged with structured context before re-raising or returning
- Agent and tool failures publish `AgentFailed` or `ToolFailed` events — no silent failures

**Logging:**
- All log lines use `aep_common.logging`
- Every log line in task context includes `task_id`, `workflow_run_id`, `tenant_id`
- No `print()` statements in production code

**Observability:**
- Every new public method in `domain/` is wrapped in an OTEL trace span:
  ```python
  from aep_common.tracing import get_tracer
  tracer = get_tracer(__name__)

  with tracer.start_as_current_span("method_name") as span:
      span.set_attribute("task_id", str(task_id))
      span.set_attribute("tenant_id", tenant_id)
  ```
- Every new service exposes: request count counter, request duration histogram, error rate counter

**Code quality:**
- Type hints on every function signature
- Docstrings on public methods describe intent — not mechanics
- No `TODO`, `FIXME`, or `HACK` in production code paths
- No placeholder implementations

### Tests

Write tests alongside the implementation:

- **Unit tests** — one test file per `domain/` module, happy path and at least two edge cases per method
- **Integration test** — end-to-end test for the primary flow through this story
- **Acceptance tests** — one test per Given/When/Then criterion, named `test_ac_{criterion_id}_{description}`
- **Isolation test** — cross-tenant query returns 0 rows, if the story touches data

Every test must fail when the code it tests is removed. No vacuous assertions.

---

## Phase 6 — Self Validation

Work through each validation category before declaring the story complete.

### Acceptance criteria

For each criterion defined in Phase 2:

```
AC-{n}: {criterion text}
  Satisfied by: {file and method}
  Tested by:    {test file and test function name}
  Status:       SATISFIED | NOT SATISFIED
```

If any criterion is NOT SATISFIED, return to Phase 5.

### Definition of Done — Story-Level Gate

Work through every item in the Story-Level Gate section of `docs/04-program/{PI}/DEFINITION_OF_DONE.md`:

```
[ ] Architecture — no direct HTTP calls between services
[ ] Architecture — config from environment variables only
[ ] Architecture — no hardcoded credentials
[ ] Database — tenant_id in every query (if applicable)
[ ] Database — RLS policy on every new table (if applicable)
[ ] Database — migration has downgrade() (if applicable)
[ ] Kafka — offset committed after successful processing (if applicable)
[ ] Kafka — failed messages routed to DLQ (if applicable)
[ ] Code quality — ruff check exits 0
[ ] Code quality — black --check exits 0
[ ] Code quality — mypy --strict exits 0
[ ] Code quality — no TODO/FIXME in production paths
[ ] Testing — unit coverage >= 80% on new code
[ ] Testing — acceptance test for every AC criterion
[ ] Security — detect-secrets finds zero new secrets
[ ] Security — non-root user in Dockerfile (if applicable)
[ ] Documentation — .env.example updated for new variables
```

### Contract compliance

If the story produces or consumes events:
- [ ] Every published message validates against `contracts/event-envelope.schema.json`
- [ ] Event type follows PascalCase convention
- [ ] Topic name follows `aep.{domain}.{event-type-kebab}` convention

If the story registers an agent or tool:
- [ ] Registration validates against the relevant contract schema in `contracts/`

### Architecture compliance

- [ ] No agent calls another agent directly (Constitution A1)
- [ ] No specialist logic added to `orchestrator-service` (Constitution A2)
- [ ] No gate bypass mechanism introduced (Constitution H2)
- [ ] `tenant_id` present in all data queries and Kafka messages (Constitution SR3)

**Stop condition:** Report every unmet criterion with the specific file and line that needs to change. Do not declare complete with unmet criteria.

---

## Phase 7 — Handoff

Produce this summary when all Phase 6 checks pass:

```
## Implementation Summary: {story_id} — {story_title}

### Files created
- {path}: {one-line description}

### Files modified
- {path}: {what changed}

### Infrastructure added
- {component}: {what was configured and why}

### Infrastructure deferred
- {component}: {why it was not needed for this story}

### Commands to run
  # Install / build
  {command}

  # Run migrations (if applicable)
  {command}

  # Run tests
  pytest src/tests/unit/{service_name}/ -v --cov={target_folder}
  pytest src/tests/integration/{service_name}/ -v

  # Lint and type check
  ruff check src/{target_folder}/
  black --check src/{target_folder}/
  mypy --strict src/{target_folder}/

### Known limitations
{anything the implementation does not cover that a reviewer should know}
{NONE if there are no limitations}

### Recommended next story
{story_id from SPRINT_PLAN.md that logically follows this one}
```

---

## Engineering Rules

- Never redesign the architecture
- Never modify `CONSTITUTION.md`, `ARCHITECTURE.md`, `CLAUDE.md`, or any PI document
- Never introduce new platform capabilities not defined in `CAPABILITIES.md`
- Never implement more than one story per execution
- Never provision infrastructure not required by the current story's acceptance criteria
- Never generate placeholder code or leave `TODO` comments in production paths
- Always produce production-ready code — assume Principal Engineer review
- Always optimise for maintainability over speed
- Always stop and report when a required input is missing or a dependency is unmet

---

## Forbidden Actions

- Implement more than one User Story
- Skip any phase
- Proceed past a Stop condition without resolving it
- Add infrastructure "for later" — every infrastructure decision must trace to an acceptance criterion
- Import vendor SDKs in agent or tool code
- Hardcode credentials, URLs, topic names, or tenant IDs
- Silent exception handling
- Placeholder implementations or stubs
- Add a new direct HTTP call between services
- Modify a contract schema without an ADR
- Omit type hints or use `any` in TypeScript
- Invoke `review-story.md`, `security-review.md`, `performance-review.md`, or `release-story.md` — those are separate commands run after this one completes
