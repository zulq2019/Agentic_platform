# implement-story.md

**Command:** `implement-story`  
**Version:** 2.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs, all sprints

---

## Purpose

Use this command to implement a single User Story from specification to production-ready code.

Read the required context. Verify dependencies. Plan. Code. Self-check. Stop.

Review, security review, performance review, and release activities are separate commands with their own entry points. This command does not invoke them.

One execution = one User Story. Never more.

---

## Inputs

Read all of the following before writing a single line of code. Do not proceed if any mandatory input is missing.

| Input | Location | Required |
|-------|----------|----------|
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture | `ARCHITECTURE.md` | Mandatory |
| PI README | `docs/04-program/{PI}/README.md` | Mandatory |
| Capabilities | `docs/04-program/{PI}/CAPABILITIES.md` — capability for this story | Mandatory |
| User Story | `docs/04-program/{PI}/USER_STORIES.md` — target story only | Mandatory |
| Acceptance Criteria | `docs/04-program/{PI}/ACCEPTANCE_CRITERIA.md` — target story only | Mandatory |
| Implementation Guide | `docs/04-program/{PI}/IMPLEMENTATION.md` | Mandatory |
| Contract Schemas | `contracts/` — schemas relevant to this story | If story produces/consumes events or registers an agent or tool |
| ADRs | `DECISIONS.md` — decisions applicable to this story | If available |

**Substitutions required:**

```
{PI}            = e.g. PI-01-Platform-Spine
{story_id}      = e.g. US-01.03
{service_name}  = e.g. orchestrator-service
{target_folder} = e.g. src/platform/orchestrator/
```

---

## Preconditions

Verify these before proceeding:

- [ ] The PI this story belongs to has status `IN PROGRESS`
- [ ] All stories this story depends on are marked complete in `SPRINT_PLAN.md`
- [ ] The target folder exists in `src/`
- [ ] No other story is in progress in this session

---

## Execution Steps

Execute in this exact order. Do not skip. Do not reorder.

### Step 1 — Read and identify constitutional constraints

Read `CONSTITUTION.md`. List every principle that applies to this story before touching code.

Common constraints to check:

| Principle | Rule |
|-----------|------|
| A1 | Agents never call agents directly |
| A2 | Orchestrator plans only — no specialist logic |
| A4 | Event bus is the only inter-container communication path |
| S1 | RBAC, Policy, Secrets are three separate services |
| SR1 | No credentials in code — always environment variables |
| SR3 | Tenant ID in every data query |
| H2 | No gate bypass mechanism |

### Step 2 — Read architecture and locate the service boundary

Read `ARCHITECTURE.md`. Confirm:
- Which service owns this story
- Which Kafka topics this service produces and consumes
- Which registries this service calls (agent registry, tool registry — lookup only, no direct business calls)

### Step 3 — Read the capability

Read the capability section in `CAPABILITIES.md` that this story belongs to. The capability defines the technical contracts, schemas, and sequences the implementation must satisfy.

### Step 4 — Read the acceptance criteria

Read the acceptance criteria for `{story_id}` in `ACCEPTANCE_CRITERIA.md`. Write out each Given/When/Then criterion. Every criterion needs a corresponding test.

### Step 5 — Read the implementation guide

Read `IMPLEMENTATION.md`. Use the patterns it defines exactly — directory layout, dependency injection, error handling, logging, configuration. Do not invent new patterns.

### Step 6 — Produce a short implementation plan

Before writing code, state:

```
Story:          {story_id} — {story_title}
Service:        {service_name}
Target folder:  {target_folder}

Files to create:
  - {path}: {purpose}

Files to modify:
  - {path}: {what changes}

Constitutional constraints that apply:
  - {principle_id}: {how it is enforced}

Acceptance criteria to satisfy:
  - AC-{n}: {how the implementation satisfies it}
  - AC-{n}: ...
```

Do not proceed to Step 7 until this plan is confirmed correct.

### Step 7 — Implement

Write production code in `{target_folder}` following the patterns from `IMPLEMENTATION.md`.

Non-negotiable rules:

- All configuration from environment variables via Pydantic Settings
- All inter-service communication via Kafka using `aep_common.kafka`
- All database queries include `tenant_id`
- All log lines include `task_id`, `workflow_run_id`, `tenant_id` via `aep_common.logging`
- No vendor SDK imports in agent or tool code
- No hardcoded strings that should be configuration
- No silent exception handling — all errors typed and logged
- Type hints on every function signature
- Docstrings on public methods explain intent, not mechanics

Wire observability on every new public domain method:

```python
from aep_common.tracing import get_tracer
tracer = get_tracer(__name__)

with tracer.start_as_current_span("method_name") as span:
    span.set_attribute("task_id", str(task_id))
    span.set_attribute("tenant_id", tenant_id)
```

Every new service emits at minimum: request count counter, request duration histogram, error rate counter.

### Step 8 — Write tests

Write tests alongside the implementation — not after:

- Unit test for every public method in `domain/` — happy path and at least two edge cases
- Integration test for the primary event flow
- One acceptance test per Given/When/Then criterion — test name must reference the criterion ID
- Cross-tenant isolation test if the story touches data

Tests must actually fail when the code they test is removed. No vacuous assertions.

### Step 9 — Self-check against acceptance criteria

For each acceptance criterion defined in Step 4:

```
AC-{n}: {criterion text}
  Implementation: {which file/method satisfies it}
  Test:           {which test file and test name covers it}
  Status:         SATISFIED | NOT SATISFIED
```

If any criterion is NOT SATISFIED, return to Step 7. Do not mark the story complete.

**Stop here.** The story is complete when all acceptance criteria are satisfied and all tests pass.

---

## Expected Outputs

| Artifact | Location |
|----------|----------|
| Production code | `src/{target_folder}/` |
| Unit tests | `src/tests/unit/{service_name}/` |
| Integration test | `src/tests/integration/{service_name}/` |
| Acceptance tests | `src/tests/integration/{service_name}/` |
| Updated `.env.example` | Service root — any new environment variables |

---

## Quality Gates

Before declaring the story complete, verify:

**Constitutional:**
- [ ] No agent calls another agent directly
- [ ] No business logic added to the orchestrator
- [ ] No credentials hardcoded
- [ ] All database queries include `tenant_id`
- [ ] No gate bypass mechanism introduced
- [ ] All Kafka messages validate against `contracts/event-envelope.schema.json`

**Code:**
- [ ] `ruff check src/` exits 0
- [ ] `black --check src/` exits 0
- [ ] `mypy --strict src/{target_folder}/` exits 0
- [ ] No `TODO`, `FIXME`, or `print()` in production code

**Tests:**
- [ ] Every acceptance criterion has a corresponding test
- [ ] Unit test coverage ≥ 80% on new code
- [ ] Cross-tenant isolation test present if story touches data

**Observability:**
- [ ] OTEL trace spans on new domain methods
- [ ] Prometheus metrics emitted
- [ ] Structured logs include `task_id`, `workflow_run_id`, `tenant_id`

---

## Completion Checklist

```
[ ] Constitution read — applicable principles listed
[ ] Architecture read — service boundary confirmed
[ ] Capability read — technical contracts understood
[ ] Acceptance criteria read — all criteria documented
[ ] Implementation guide read — patterns understood
[ ] Implementation plan produced and confirmed
[ ] Production code written
[ ] Observability wired
[ ] Tests written — unit, integration, acceptance
[ ] Self-check complete — all AC criteria satisfied
[ ] No unrelated files modified
```

---

## Forbidden Actions

- Implement more than one User Story per execution
- Redesign the architecture or change service boundaries
- Modify `CONSTITUTION.md`, `ARCHITECTURE.md`, `CLAUDE.md`, or any PI documentation
- Add a bypass mechanism for any human gate
- Import vendor SDKs in agent or tool code
- Hardcode credentials, URLs, or tenant IDs
- Generate placeholder code or `# TODO: implement` in production paths
- Silently catch exceptions
- Skip tests
- Add a new inter-service HTTP call
- Modify a contract schema without creating an ADR
- Invoke `review-story.md`, `security-review.md`, `performance-review.md`, or `release-story.md` — those are separate commands
