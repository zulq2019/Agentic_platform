# review-story.md

**Command:** `review-story`  
**Version:** 2.0 — Architecture v2.0-aware  
**Skill authority:** `.ai/skills/review-story/SKILL.md` (full pipeline)  
**Applies to:** All PIs, all sprints

---

## Purpose

Use this command to review a completed User Story implementation before raising a pull request.

This command operates as a structured peer reviewer. Before reviewing, it **automatically loads** platform constitution, repository constitution, current PI, current story, acceptance criteria, architecture contracts, platform contracts, and metadata model. It reviews against Architecture v2.0 dimensions and produces findings, risk assessment, compliance scores, and an overall recommendation.

Run this command after `implement-story.md` and before `git push`.

### Invocation (unchanged)

```
/review-story US-01.03
/review-story US-02.01
```

See `.ai/skills/review-story/SKILL.md` for the complete authoritative workflow.

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Platform primitives | `docs/architecture/PLATFORM_PRIMITIVES.md` | Mandatory (v2) |
| Platform contracts | `docs/architecture/PLATFORM_CONTRACTS.md` | Mandatory (v2) |
| Meta model | `docs/architecture/PLATFORM_META_MODEL.md` | Mandatory (v2) |
| Metadata-driven architecture | `docs/architecture/METADATA_DRIVEN_ENTERPRISE_PLATFORM.md` | Mandatory (v2) |
| Architecture baseline v2 | `docs/architecture/ARCHITECTURE_BASELINE_V2.md` | Mandatory (v2) |
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture | `ARCHITECTURE.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| ADRs | `docs/architecture/ADR/DECISIONS.md` | Mandatory |
| User Story | `docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md` | Mandatory |
| Acceptance Criteria | `docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md` | Mandatory |
| Definition of Done | `docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md` | Mandatory |
| Review Checklist | `docs/engineering/implementation-roadmap/{PI}/REVIEW_CHECKLIST.md` | Mandatory |
| Implementation Guide | `docs/engineering/implementation-roadmap/{PI}/IMPLEMENTATION.md` | Mandatory |
| Contract schemas | `contracts/` | Mandatory |
| Changed files | Output of `git diff master` | Mandatory |
| Test output | Output of `pytest` or equivalent | Mandatory |
| Lint output | Output of `ruff check` + `black --check` + `mypy --strict` | Mandatory |

**Substitutions required:**

```
{PI}          = e.g. PI-03-Provider-Framework
{story_id}    = e.g. US-PI-03-01
{pr_branch}   = the branch under review
```

---

## Preconditions

- [ ] Implementation is complete — all files written, no `# TODO` in production paths
- [ ] Tests have been executed and results are available
- [ ] Lint and type check have been run and results are available
- [ ] `git diff main` output is available for review

---

## Execution Steps

### Step 1 — Read all changed files

Read every file in `git diff main`. Build a complete picture of what was changed, added, and deleted.

Produce a change summary:
```
Files added:    list
Files modified: list
Files deleted:  list
Lines added:    N
Lines removed:  N
```

### Step 2 — Constitutional compliance check

For every changed file, check against `CONSTITUTION.md`. Work through each principle in this priority order:

**Architecture principles (A-series):**
- A1: Does any changed code call another agent's module or API directly?
- A2: Does `orchestrator-service` now contain specialist logic (LLM calls, code generation)?
- A3: Was a new agent added by modifying the orchestrator instead of the registry?
- A4: Does any service make a direct HTTP call to another service for business logic?
- A5: Does any service read or write another service's data store directly?

**Human oversight principles (H-series):**
- H2: Is there any flag, timeout, or condition that can auto-approve a gate without a human decision?

**Security principles (S-series):**
- SR1: Are any credentials, API keys, or tokens hardcoded?
- SR3: Does every database query include `tenant_id`?

**Agent principles (AG-series):**
- AG4: Do agents request tools by capability tag, not by tool ID?

For each violation found, record:
```
VIOLATION: {principle_id}
File: {filename}:{line_number}
Finding: {description}
Severity: BLOCKER | WARNING
Required action: {what must change}
```

### Step 3 — Architectural boundary check

Compare changed files against `ARCHITECTURE.md` service boundaries:
- Does the code belong in the service directory it is placed in?
- Are all new dependencies declared in `pyproject.toml`?
- Are any new inter-service calls introduced? (Only registry lookups and Kafka are permitted)
- Do new Kafka messages use the `EventEnvelope` schema from `contracts/event-envelope.schema.json`?

### Step 4 — Code quality check

Review each changed file for:

| Issue | Severity |
|-------|---------|
| `any` type in TypeScript | BLOCKER |
| Missing type hints in Python | BLOCKER |
| Silent `except:` or `except Exception: pass` | BLOCKER |
| `print()` statements in production code | BLOCKER |
| Hardcoded string that should be config | BLOCKER |
| Missing structured logging | WARNING |
| Missing docstring on public method | WARNING |
| Function longer than 50 lines | WARNING |
| Test file missing for new module | BLOCKER |
| Coverage below 80% on new code | BLOCKER |

### Step 5 — Acceptance criteria verification

For each acceptance criterion in `ACCEPTANCE_CRITERIA.md` for `{story_id}`:
- Does a test exist that directly tests this criterion?
- Does the test name match the criterion?
- Does the test actually fail when the criterion is not met (not a vacuous pass)?

Mark each criterion:
```
AC: {criterion_id} — COVERED | NOT COVERED | PARTIALLY COVERED
Test: {test_file}:{test_name}
```

### Step 6 — Observability check

- [ ] Every new public domain method has OTEL trace instrumentation
- [ ] Every new service endpoint increments a Prometheus counter
- [ ] Every error path logs with `logger.error(...)` including `task_id` and `tenant_id`
- [ ] No log line uses `print()` or Python's built-in `logging` directly — only `aep_common.logging`

### Step 7 — Definition of Done check

Work through `docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md`. Mark each criterion as met or unmet.

### Step 8 — Produce the review report

Structure the report as (see skill for full v2.0 template with scores):

```
## Review Report: {story_id} — {story_title}
Branch: {pr_branch}

### Verdict: PASS | PASS WITH WARNINGS | FAIL

### Findings (Critical / Warnings / Minor)

### Risk Assessment

### Compliance Scores
| Architecture | Maintainability | Performance | Security | Overall |
|--------------|-----------------|-------------|----------|---------|
| {N}/100      | {N}/100         | {N}/100     | {N}/100  | {N}/100 |

### Architecture v2.0 Dimension Summary
(Architecture, DDD, SOLID, Platform Contracts, Metadata Driven, Security,
 Performance, Extensibility, Config over Customization, Composition over Hardcoding,
 Platform Object, Execution Profile, Provider Model, Workflow, Observability,
 Governance, Versioning, Audit)

### Overall Recommendation
{merge readiness and required fixes}
```

---

## Expected Outputs

| Artifact | Format | Description |
|----------|--------|-------------|
| Review report | Markdown | Structured report with verdict, blockers, warnings, AC coverage, DoD |
| Blocker list | Ordered list | Every finding that must be resolved before merge |
| Warning list | Ordered list | Every finding that should be resolved but is not blocking |

---

## Quality Gates

The review is complete when:

- [ ] Every changed file has been read and evaluated
- [ ] Every CONSTITUTION.md principle has been checked
- [ ] Every acceptance criterion has a coverage verdict
- [ ] Every Definition of Done item has a met/not-met verdict
- [ ] Verdict is clearly stated: PASS, PASS WITH WARNINGS, or FAIL
- [ ] Every blocker has a specific required action

---

## Completion Checklist

```
[ ] All changed files read
[ ] Constitutional compliance checked — all A, H, S, AG principles
[ ] Architectural boundaries verified
[ ] Code quality checked — types, logging, error handling
[ ] Acceptance criteria coverage verified
[ ] Observability coverage verified
[ ] Definition of Done checked
[ ] Review report produced with clear verdict
[ ] Blockers listed with required actions
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Approve a story with unresolved BLOCKER findings
- Modify the implementation files during review (review only — no edits)
- Accept "it will be fixed later" as resolution for a blocker
- Skip checking the Constitution
- Skip checking acceptance criteria coverage
- Produce a review that only says "looks good" without evidence
- Change or relax the acceptance criteria to match the implementation
- Introduce new features while reviewing
- Modify PI documentation
- Alter the Definition of Done to make the story pass
