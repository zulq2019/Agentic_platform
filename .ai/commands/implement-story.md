# implement-story.md

**Command:** `implement-story`  
**Version:** 1.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs, all sprints

---

## Purpose

Use this command to implement a single User Story from specification to production-ready code.

This command is the primary engineering entry point. It ensures the AI assistant reads all required context before writing a single line, follows the constitutional constraints that apply to the story, and produces code that is testable, observable, and deployable from day one.

One execution of this command = one User Story. Never more.

---

## Inputs

Gather these documents before executing. Do not proceed without them.

| Input | Location | Required |
|-------|----------|----------|
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture | `ARCHITECTURE.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| PI README | `docs/04-program/{PI}/README.md` | Mandatory |
| User Story | `docs/04-program/{PI}/USER_STORIES.md` — target story | Mandatory |
| Acceptance Criteria | `docs/04-program/{PI}/ACCEPTANCE_CRITERIA.md` — target story | Mandatory |
| Implementation Guide | `docs/04-program/{PI}/IMPLEMENTATION.md` | Mandatory |
| Sprint Plan | `docs/04-program/{PI}/SPRINT_PLAN.md` — target sprint | Mandatory |
| Data Model | `docs/04-program/{PI}/DATA_MODEL.md` | If story touches data |
| API Spec | `docs/04-program/{PI}/API_SPEC.md` | If story produces an endpoint |
| Architecture Diagrams | `docs/artifacts/TECHNICAL_ARCHITECTURE.md` | For service boundary decisions |
| Relevant ADRs | `DECISIONS.md` — decisions applicable to this story | If available |
| Relevant Contract Schemas | `contracts/` | If story produces or consumes events or registers an agent/tool |

**Substitutions required:**

```
{PI}              = e.g. PI-01-Platform-Spine
{story_id}        = e.g. US-01.03
{story_title}     = e.g. Event Bus Ready
{service_name}    = e.g. orchestrator-service
{target_folder}   = e.g. src/platform/orchestrator/
```

---

## Preconditions

Before executing, verify all of the following are true:

- [ ] The PI this story belongs to has status `IN PROGRESS` (check PI README)
- [ ] All stories this story depends on are complete (check SPRINT_PLAN.md)
- [ ] The target folder in `src/` exists (check repository root)
- [ ] No other story is `IN PROGRESS` in this session
- [ ] The relevant contract schemas have been read and understood
- [ ] The `aep-common` shared library is available (for PI-02+)

---

## Execution Steps

Execute in this exact order. Do not skip or reorder.

### Step 1 — Understand the constitutional constraints

Read `CONSTITUTION.md`. Identify every principle that applies to this story. Write them down before touching any code. Common applicable principles:

- **A1** — Agents never call agents directly
- **A2** — Orchestrator plans, never executes
- **A4** — Event bus is the only inter-container communication path
- **S1** — RBAC, Policy, and Secrets are three separate services
- **SR1** — No credentials in code — always environment variables
- **SR3** — Tenant ID in every data query
- **H2** — No gate bypass mechanism

### Step 2 — Understand the architectural boundaries

Read `ARCHITECTURE.md` and `docs/artifacts/TECHNICAL_ARCHITECTURE.md`. Confirm:
- Which service owns this story
- Which Kafka topics this service produces and consumes
- Which other services this service calls (registry lookups only — no direct business calls)
- What the data model looks like for this service

### Step 3 — Read the implementation pattern

Read `docs/04-program/{PI}/IMPLEMENTATION.md`. Use the established patterns exactly. Do not invent new patterns. The implementation guide defines:
- Service directory layout
- Dependency injection pattern
- Error handling conventions
- Logging conventions (always use `aep_common.logging`)
- Configuration conventions (always Pydantic Settings)

### Step 4 — Understand the acceptance criteria

Read `docs/04-program/{PI}/ACCEPTANCE_CRITERIA.md` for `{story_id}`. Write down the exact Given/When/Then criteria. Every criterion must have a corresponding test.

### Step 5 — Plan before coding

Before writing code, produce a brief implementation plan:
- What files will be created
- What files will be modified
- What tests will be written
- Which constitutional constraints apply and how they are enforced

Present this plan. Do not proceed to Step 6 without confirming it is correct.

### Step 6 — Implement the story

Write production code in `{target_folder}` following the patterns from Step 3.

Implementation rules (non-negotiable):
- All configuration from environment variables via Pydantic Settings
- All inter-service communication via Kafka using `aep_common.kafka`
- All database queries include `tenant_id` (RLS enforced at storage layer)
- All log lines include `task_id`, `workflow_run_id`, `tenant_id` via `aep_common.logging`
- No vendor SDK imports in agent or tool code
- No hardcoded strings that should be configuration
- No silent exception handling — all errors typed and logged
- Type hints on every function signature
- Docstring on every public method explaining intent, not what the code does

### Step 7 — Wire observability

Every new public method in the `domain/` layer must be traced:
```python
from aep_common.tracing import get_tracer
tracer = get_tracer(__name__)

with tracer.start_as_current_span("method_name") as span:
    span.set_attribute("task_id", str(task_id))
    span.set_attribute("tenant_id", tenant_id)
```

Every new service must emit at least:
- Request count counter
- Request duration histogram
- Error rate counter

### Step 8 — Write tests

Using `generate-tests.md` command, write:
- Unit tests for every function in `domain/`
- Integration test for the primary event flow
- Acceptance test mapping directly to each Given/When/Then criterion
- Cross-tenant isolation test if story touches data

### Step 9 — Self-review

Before declaring done, execute `review-story.md` command against your own output.

---

## Expected Outputs

| Artifact | Location | Description |
|----------|----------|-------------|
| Service code | `src/{target_folder}/` | Production implementation following IMPLEMENTATION.md patterns |
| Unit tests | `src/tests/unit/` | One test file per domain module, ≥ 80% coverage |
| Integration test | `src/tests/integration/` | End-to-end event flow test |
| Acceptance tests | `src/tests/integration/` | One test per AC criterion |
| Updated `.env.example` | Service root | Any new environment variables documented |
| Linting clean | CI | `ruff check` and `black --check` exit 0 |
| Type check clean | CI | `mypy --strict` exits 0 |

---

## Quality Gates

The AI must verify all of the following before declaring the story complete:

**Constitutional compliance:**
- [ ] No agent calls another agent directly
- [ ] No business logic in `orchestrator-service`
- [ ] No credentials hardcoded anywhere
- [ ] All database queries include `tenant_id`
- [ ] No gate bypass mechanism introduced
- [ ] All Kafka messages validate against `contracts/event-envelope.schema.json`

**Code quality:**
- [ ] `ruff check src/` exits 0
- [ ] `black --check src/` exits 0
- [ ] `mypy --strict src/{target_folder}/` exits 0
- [ ] No `TODO`, `FIXME`, or `HACK` comments in production code paths
- [ ] No `print()` statements — only structured logger

**Testing:**
- [ ] All acceptance criteria have corresponding tests
- [ ] Unit test coverage ≥ 80% on new code
- [ ] Cross-tenant isolation test passes if story touches data

**Observability:**
- [ ] OTEL traces flow from new code
- [ ] Prometheus metrics emitted from new code
- [ ] Structured logs include all correlation IDs

---

## Completion Checklist

```
[ ] Step 1: Constitutional constraints identified and documented
[ ] Step 2: Service boundary confirmed — no violations
[ ] Step 3: Implementation pattern followed exactly
[ ] Step 4: All acceptance criteria understood
[ ] Step 5: Implementation plan reviewed and confirmed
[ ] Step 6: Production code written — no shortcuts
[ ] Step 7: Observability wired — traces, metrics, logs
[ ] Step 8: Tests written — unit + integration + acceptance
[ ] Step 9: Self-review passed using review-story.md
[ ] No unrelated files modified
[ ] PR description written explaining what changed and why
[ ] DEFINITION_OF_DONE.md criteria checked for this PI
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Implement more than one User Story in a single execution
- Redesign the architecture or change service boundaries
- Modify `CONSTITUTION.md`, `ARCHITECTURE.md`, or `CLAUDE.md`
- Modify any PI documentation
- Add a bypass mechanism for any human gate
- Import vendor SDKs in agent or tool code
- Hardcode credentials, URLs, or tenant IDs
- Generate placeholder code, stubs, or `# TODO: implement` comments in production code paths
- Silently catch exceptions
- Skip writing tests because "it will be done later"
- Change the Kafka topic naming convention
- Add a new inter-service HTTP call
- Modify a contract schema without creating an ADR
- Use `any` in TypeScript or omit type hints in Python
