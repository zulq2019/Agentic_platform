---
name: review-story
description: |
  When the engineer types /review-story <story_id>, perform an Architecture v2.0-aware
  structured review of a completed User Story implementation before raising a PR.
  Automatically loads platform constitution, repository constitution, PI context,
  acceptance criteria, and contracts. Produces findings, risk assessment, compliance
  scores, and an overall recommendation. Review only — never modifies implementation.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq, pytest
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


# review-story

**Version:** 2.0 — Architecture v2.0-aware story review  
**Backward compatible:** `/review-story US-01.03` works exactly as before.

<purpose>
Structured peer review for a completed User Story on the Agentic Engineering Platform.
Before reviewing any implementation, automatically builds complete execution context
from the platform constitution, repository constitution, current PI, current story,
acceptance criteria, architecture contracts, platform contracts, and metadata model.
Reviews against Architecture v2.0 dimensions and produces scored findings with an
overall recommendation. Operates in read-only mode on implementation files.
</purpose>

---

## When To Activate

Trigger when the engineer types `/review-story` followed by a User Story ID.

```
/review-story US-01.03
/review-story US-02.01
```

The story ID must exist in `docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md`.

Run after `implement-story` and before `git push`.

---

## Workflow Position

```
implement-story → review-story → generate-tests → regression-review → aep-review
    → security-review (optional) → performance-review (optional) → release-story
```

---

## Substitutions Required

```
{story_id}      = the story ID passed by the engineer, e.g. US-02.01
{story_title}   = human-readable title from USER_STORIES.md
{PI}            = the PI folder, e.g. PI-02-Metadata-Engine
{pr_branch}     = the branch under review (current branch)
```

---

## Phase 1 — Load Review Context (automatic)

**Read ALL of the following before reviewing any changed file. No exceptions.**

### Platform Constitution

```bash
cat docs/architecture/PLATFORM_PRIMITIVES.md
cat docs/architecture/PLATFORM_CONTRACTS.md
cat docs/architecture/PLATFORM_META_MODEL.md
cat docs/architecture/PLATFORM_UX_MODEL.md
cat docs/architecture/PLATFORM_GLOSSARY.md
cat docs/architecture/METADATA_DRIVEN_ENTERPRISE_PLATFORM.md
cat docs/architecture/ARCHITECTURE_BASELINE_V2.md
```

### Repository Constitution

```bash
cat CONSTITUTION.md
cat ARCHITECTURE.md
cat CLAUDE.md
cat docs/architecture/ADR/DECISIONS.md
```

### Current PI and Story

```bash
PI_DIR=$(ls docs/engineering/implementation-roadmap/ | rg "PI-$(echo {story_id} | cut -d- -f2 | cut -d. -f1)")

cat docs/engineering/implementation-roadmap/${PI_DIR}/README.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/OBJECTIVES.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/CAPABILITIES.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/USER_STORIES.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/ACCEPTANCE_CRITERIA.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/IMPLEMENTATION.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/API_SPEC.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/DATA_MODEL.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/TESTING.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/DEFINITION_OF_DONE.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/REVIEW_CHECKLIST.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/STATUS.md
```

### Architecture Contracts and Platform Contracts

```bash
ls contracts/
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
cat contracts/tool-contract.schema.json
cat contracts/task-schema.schema.json
cat contracts/memory-schema.schema.json
cat contracts/platform-object.schema.json
```

### Metadata Model

Cross-reference `PLATFORM_META_MODEL.md`, `PLATFORM_PRIMITIVES.md` §3, and PI `DATA_MODEL.md`
for Platform Object envelope, lifecycle FSM, relationships, and versioning rules.

### Implementation diff

```bash
git diff master...HEAD --stat
git diff master...HEAD
pytest -m "story_{story_id}" -v 2>/dev/null || pytest src/tests -v
ruff check src/ 2>/dev/null
```

**Stop condition:** If constitution docs, acceptance criteria, or `git diff` cannot be
read, stop and report what is missing. Review cannot proceed without context.

---

## Phase 2 — Preconditions

Verify before proceeding:

- [ ] Implementation is complete — no `# TODO` in production paths
- [ ] Tests have been executed and results are available
- [ ] Lint and type check have been run (or run now)
- [ ] `git diff master` (or base branch) output is available

**STOP if implementation is incomplete or tests were not run.**

---

## Phase 3 — Read Changed Files

Read every file in the diff. Produce a change summary:

```
Files added:    {list}
Files modified: {list}
Files deleted:  {list}
Lines added:    {N}
Lines removed:  {N}
```

---

## Phase 4 — Architecture v2.0 Review Dimensions

Review the implementation against **every applicable dimension** below. Record
findings with `file:line`, severity, and required action. Dimensions with no
applicable code record **N/A**.

| Dimension | What to verify |
|-----------|----------------|
| **Architecture** | Service boundaries, hexagonal layers, event-mediated IPC (A1–A5) |
| **DDD** | Bounded contexts, aggregates, domain rules in `domain/` only |
| **SOLID** | Single responsibility, dependency inversion via ports |
| **Platform Contracts** | JSON Schema validation at boundaries; correct contract version |
| **Metadata Driven Architecture** | Objects use Platform Object envelope; no hardcoded metadata |
| **Security** | SR1–SR6; tenant_id everywhere; no credentials in code |
| **Performance** | No unbounded queries; indexes on tenant-scoped columns |
| **Extensibility** | Extension points used; no closed-for-modification core |
| **Configuration over Customization** | Business rules from config/metadata, not code branches |
| **Composition over Hardcoding** | Primitives composed; no tenant-specific code forks |
| **Platform Object compliance** | Identity, lifecycle, versioning, audit per `PLATFORM_PRIMITIVES.md` §3 |
| **Execution Profile compliance** | Profile schema/runtime hooks per ADR-012/027 |
| **Provider Model compliance** | Provider discovery by capability; no vendor SDKs in agents |
| **Workflow compliance** | State machine transitions; gate enforcement (H2) |
| **Observability** | OTEL traces, Prometheus metrics, structured logs |
| **Governance** | Audit events; human gates not bypassable |
| **Versioning** | Semantic versioning on contracts, APIs, Platform Objects |
| **Audit** | Every state change and human decision produces auditable event |

### Constitutional compliance (mandatory — existing checks preserved)

**Architecture principles (A-series):**
- A1: No agent calls another agent directly
- A2: No specialist logic in orchestrator
- A3: New agents via registry only
- A4: No direct HTTP between services for business logic
- A5: No cross-service data store access

**Human oversight (H-series):**
- H2: No auto-approve gate bypass

**Security (S-series):**
- SR1: No hardcoded credentials
- SR3: `tenant_id` in every data query

**Agent (AG-series):**
- AG4: Tools resolved by capability tag

For each violation:

```
VIOLATION: {principle_id}
File: {filename}:{line_number}
Finding: {description}
Severity: BLOCKER | WARNING
Required action: {specific fix}
```

### Architectural boundary check (existing — preserved)

- Code belongs in the correct service directory
- New dependencies declared in `pyproject.toml`
- No new direct inter-service HTTP calls
- Kafka messages use `event-envelope.schema.json`

### Code quality check (existing — preserved)

| Issue | Severity |
|-------|---------|
| `any` type in TypeScript | BLOCKER |
| Missing type hints in Python | BLOCKER |
| Silent `except:` or `except Exception: pass` | BLOCKER |
| `print()` in production code | BLOCKER |
| Hardcoded string that should be config | BLOCKER |
| Missing structured logging | WARNING |
| Missing docstring on public method | WARNING |
| Function longer than 50 lines | WARNING |
| Test file missing for new module | BLOCKER |
| Coverage below 80% on new code | BLOCKER |

### Acceptance criteria verification (existing — preserved)

For each criterion in `ACCEPTANCE_CRITERIA.md` for `{story_id}`:

```
AC: {criterion_id} — COVERED | NOT COVERED | PARTIALLY COVERED
Test: {test_file}:{test_name}
```

### Observability check (existing — preserved)

- [ ] OTEL traces on new public domain methods
- [ ] Prometheus counters on new endpoints
- [ ] Errors logged with `task_id` and `tenant_id`
- [ ] Uses `aep_common.logging` only

### Definition of Done check (existing — preserved)

Work through `DEFINITION_OF_DONE.md` Story-Level Gate. Mark each item met or unmet.

---

## Phase 5 — Scoring

Score each dimension 0–100 based on findings. Weight blockers heavily (cap at 40 if
any BLOCKER unresolved).

| Score | Dimension |
|-------|-----------|
| Architecture Compliance Score | Boundaries, constitution, hexagonal, contracts |
| Maintainability Score | DDD, SOLID, clarity, testability, no duplication |
| Performance Score | Query patterns, indexes, hot-path efficiency |
| Security Score | Credentials, tenancy, RBAC/policy/secrets separation |
| **Overall** | Weighted average; BLOCKER caps overall at 40 |

Scoring guide:
- **90–100:** No blockers; minor warnings only
- **70–89:** Warnings present; no blockers
- **40–69:** Blockers present or significant gaps
- **0–39:** Critical constitutional or security violations

---

## Phase 6 — Produce Review Report

```
## Review Report: {story_id} — {story_title}
Branch: {pr_branch}
Reviewed by: review-story skill (Architecture v2.0)

### Verdict: PASS | PASS WITH WARNINGS | FAIL

### Findings

#### Critical / Blockers
{file:line} — {finding}
  Why it matters: {runtime failure scenario}
  Fix: {specific action}

#### Warnings
{file:line} — {finding}
  Fix: {specific action}

#### Minor
{file:line} — {note}

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {risk} | Low/Med/High | Low/Med/High | {action} |

### Compliance Scores

| Dimension | Score |
|-----------|-------|
| Architecture Compliance | {N}/100 |
| Maintainability | {N}/100 |
| Performance | {N}/100 |
| Security | {N}/100 |
| **Overall** | **{N}/100** |

### Architecture v2.0 Dimension Summary

| Dimension | Status | Notes |
|-----------|--------|-------|
| Architecture | PASS/WARN/FAIL/N/A | {summary} |
| DDD | PASS/WARN/FAIL/N/A | {summary} |
| SOLID | PASS/WARN/FAIL/N/A | {summary} |
| Platform Contracts | PASS/WARN/FAIL/N/A | {summary} |
| Metadata Driven | PASS/WARN/FAIL/N/A | {summary} |
| Security | PASS/WARN/FAIL/N/A | {summary} |
| Performance | PASS/WARN/FAIL/N/A | {summary} |
| Extensibility | PASS/WARN/FAIL/N/A | {summary} |
| Config over Customization | PASS/WARN/FAIL/N/A | {summary} |
| Composition over Hardcoding | PASS/WARN/FAIL/N/A | {summary} |
| Platform Object | PASS/WARN/FAIL/N/A | {summary} |
| Execution Profile | PASS/WARN/FAIL/N/A | {summary} |
| Provider Model | PASS/WARN/FAIL/N/A | {summary} |
| Workflow | PASS/WARN/FAIL/N/A | {summary} |
| Observability | PASS/WARN/FAIL/N/A | {summary} |
| Governance | PASS/WARN/FAIL/N/A | {summary} |
| Versioning | PASS/WARN/FAIL/N/A | {summary} |
| Audit | PASS/WARN/FAIL/N/A | {summary} |

### Constitutional Compliance
All principles: PASS | VIOLATIONS FOUND (list)

### Acceptance Criteria Coverage
AC-01: COVERED — test_file.py::test_name
AC-02: NOT COVERED — no test found
...

### Definition of Done
[ ] criterion 1 — MET | NOT MET
...

### Overall Recommendation

{1–3 sentences: merge readiness, required fixes before PR, suggested next step}

Recommended next workflow:
  /generate-tests {story_id}     # if test gaps found
  /regression-review <PR_NUMBER>  # after PR opened
  /aep-review <PR_NUMBER>
```

---

## Engineering Rules

- Never modify implementation files during review
- Never approve a story with unresolved BLOCKER findings
- Never relax acceptance criteria to match implementation
- Never skip platform constitution loading (Phase 1)
- Every finding must cite `file:line` from the diff
- Every finding must explain concrete runtime impact

---

## Forbidden Actions

- Approve with unresolved BLOCKER findings
- Modify implementation or PI planning documents
- Skip Constitution or Architecture v2.0 dimension checks
- Produce "looks good" without evidence and scores
- Change or relax acceptance criteria
- Introduce new features while reviewing
- Alter Definition of Done to make the story pass
