# release-story.md

**Command:** `release-story`  
**Version:** 2.0 — Architecture v2.0-aware  
**Skill authority:** `.ai/skills/release-story/SKILL.md` (full pipeline)  
**Applies to:** All PIs — run when a story is complete and ready for merge and deployment to a target environment

---

## Purpose

Use this command to prepare a completed User Story for release: verify all quality gates are met, run Pre-Release Verification against Architecture v2.0 dimensions, execute 11 release lenses, produce release artefacts, update the changelog, and ensure the deployment is safe and observable.

This command is the final checkpoint before merge. It does not merge or deploy — it validates that the implementation is ready for a human to approve and merge.

Before reviewing, this command **automatically loads** platform constitution, repository constitution, PI context (including `STATUS.md` and `METRICS.md`), and contract schemas. See `.ai/skills/release-story/SKILL.md` for the complete authoritative workflow.

### Invocation (unchanged)

```
/release-story 42
/release-story https://github.com/org/Agentic_platform/pull/42
```

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Platform primitives | `docs/architecture/PLATFORM_PRIMITIVES.md` | Mandatory (v2) |
| Platform contracts | `docs/architecture/PLATFORM_CONTRACTS.md` | Mandatory (v2) |
| Meta model | `docs/architecture/PLATFORM_META_MODEL.md` | Mandatory (v2) |
| UX model | `docs/architecture/PLATFORM_UX_MODEL.md` | Mandatory (v2) |
| Glossary | `docs/architecture/PLATFORM_GLOSSARY.md` | Mandatory (v2) |
| Metadata-driven architecture | `docs/architecture/METADATA_DRIVEN_ENTERPRISE_PLATFORM.md` | Mandatory (v2) |
| Architecture baseline v2 | `docs/architecture/ARCHITECTURE_BASELINE_V2.md` | Mandatory (v2) |
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture | `ARCHITECTURE.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| ADRs | `docs/architecture/ADR/DECISIONS.md` | Mandatory |
| Definition of Done | `docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md` | Mandatory |
| Review Checklist | `docs/engineering/implementation-roadmap/{PI}/REVIEW_CHECKLIST.md` | Mandatory |
| User Story | `docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md` — implemented story | Mandatory |
| Acceptance Criteria | `docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md` | Mandatory |
| PI status | `docs/engineering/implementation-roadmap/{PI}/STATUS.md` | Mandatory (v2) |
| PI metrics | `docs/engineering/implementation-roadmap/{PI}/METRICS.md` | Mandatory (v2) |
| Review report | Output of `review-story.md` — must be PASS | Mandatory |
| Security review report | Output of `security-review.md` | If story touches auth/data/secrets |
| Performance review report | Output of `performance-review.md` | If story has latency SLOs |
| Regression review report | Output of `regression-review.md` | If PR touches shared zones |
| Test output | `pytest` run — all tests passing | Mandatory |
| Lint output | `ruff check` + `black --check` + `mypy --strict` | Mandatory |
| PR diff | `gh pr diff <NUMBER>` | Mandatory |
| Changelog | `CHANGELOG.md` (repo) and PI release notes if applicable | Mandatory |

**Substitutions required:**

```
{PI}              = e.g. PI-05-Execution-Framework
{story_id}        = e.g. US-PI-05-03
{story_title}     = e.g. Tool Capability Discovery
{service_name}    = e.g. tool-registry-service
{target_version}  = e.g. 1.2.0 (semver)
{target_env}      = dev | staging | production
{pr_branch}       = feature/PI-05-US-03-tool-capability-discovery
{pr_number}       = GitHub pull request number
```

---

## Preconditions

- [ ] `review-story.md` has been executed and result is PASS or PASS WITH WARNINGS (no BLOCKERs)
- [ ] All tests pass: `pytest src/tests/ -v` exits 0
- [ ] Lint clean: `ruff check src/` exits 0
- [ ] Type check clean: `mypy --strict src/{target_folder}/` exits 0
- [ ] Security review complete (if required)
- [ ] Performance review complete (if required)
- [ ] Regression review complete (if required)
- [ ] No unresolved BLOCKER findings from any review
- [ ] Branch is up to date with `main`
- [ ] PR is open and fetchable via `gh pr view` / `gh pr diff`

---

## Execution Steps

### Step 1 — Fetch PR metadata and CI status

See `.ai/skills/release-story/SKILL.md` Step 1. Parse story ID, PI, and CI rollup before proceeding.

### Step 2 — Load platform and repository constitution (automatic)

Load all platform constitution docs, repository constitution, PI context (`STATUS.md`, `METRICS.md`), and contract schemas. See skill Step 2.

### Step 2b — Pre-Release Verification gate

Assess all 13 Architecture v2.0 release dimensions before executing lenses:

| Dimension | Mandatory |
|-----------|-----------|
| Architecture Compliance | Yes |
| Platform Contracts | Yes |
| Documentation | Yes |
| Tests | Yes |
| Security | Yes (if high-risk PR) |
| Performance | Yes (if SLOs defined) |
| Observability | Yes |
| Metrics | Yes |
| Audit | Yes |
| Version | Yes |
| CHANGELOG | Yes |
| STATUS | Yes |
| METRICS (PI) | Yes |

Any mandatory FAIL blocks READY FOR RELEASE. See skill Step 2b for evidence requirements.

### Step 3 — Final Definition of Done sweep

Work through every item in `docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md`. For each item:
- Mark as MET with evidence, or
- Mark as NOT MET with the blocking issue

```
DoD Check: {story_id}
[ ] Code complete and reviewed              — REVIEW PASSED: {review_date}
[ ] All acceptance criteria tested          — COVERAGE: {N}/{N} AC criteria
[ ] Unit test coverage ≥ 80%               — COVERAGE: {N}%
[ ] Integration tests pass                 — RESULT: {N}/{N} passing
[ ] No lint warnings                       — ruff: CLEAN, black: CLEAN, mypy: CLEAN
[ ] Security review complete               — RESULT: {PASS|SKIPPED — reason}
[ ] Performance review complete            — RESULT: {PASS|SKIPPED — reason}
[ ] Documentation updated                  — update-documentation.md: COMPLETE
[ ] Observability wired                    — traces: YES, metrics: YES, logs: YES
[ ] Changelog updated                      — see Step 4
[ ] STATUS.md updated                      — story marked complete
[ ] METRICS.md updated                     — measurable outcomes recorded
[ ] .env.example updated                   — YES | NO change needed
[ ] PR description written                 — see Step 5
[ ] No TODO/FIXME in production paths      — grep: CLEAN
[ ] No hardcoded secrets                   — detect-secrets: CLEAN
```

If any mandatory DoD item is NOT MET, STOP. Resolve the item before proceeding.

### Step 4 — Update the changelog

Update `CHANGELOG.md` at the repository root:

```markdown
## [Unreleased]

### Added
- {story_id}: {story_title} — {one sentence description of what was added}
  Service: {service_name}
  PI: {PI}
  Tests: {N} unit, {N} integration, {N} acceptance

### Changed
- {story_id}: {what changed and why — if any breaking change, mark BREAKING}

### Fixed
- {story_id}: {bug fixed if applicable}
```

If `CHANGELOG.md` does not exist, create it with the standard Keep a Changelog format.

Update PI `STATUS.md` and `METRICS.md` when this story completes a deliverable or changes measurable PI outcomes.

### Step 5 — Write the pull request description

Produce a PR description in this format:

```markdown
## {story_id}: {story_title}

**PI:** {PI}  
**Service:** {service_name}  
**Branch:** `{pr_branch}`  
**Target:** `main`

### What was implemented

{2-3 sentences describing what this story delivers and why it matters to the platform}

### Acceptance criteria coverage

| Criterion | Test | Status |
|-----------|------|--------|
| AC-{N}: {description} | `test_file.py::test_name` | COVERED |

### Constitutional compliance

All applicable CONSTITUTION.md principles verified:
- {principle_id}: {one line on how compliance is demonstrated}

### Changes

| File | Change type | Description |
|------|------------|-------------|
| `src/{path}` | Added | {description} |
| `src/{path}` | Modified | {description} |

### Tests

- Unit tests: N added, all pass, coverage N%
- Integration tests: N added, all pass
- Acceptance tests: N added, all pass (one per AC criterion)

### Observability

- Traces: [x] OTEL spans on all domain methods
- Metrics: [x] Prometheus counters and histograms
- Logs: [x] Structured JSON with task_id, tenant_id

### Review reports

- Code review: PASS — {reviewer or self-review}
- Security review: {PASS | N/A — reason}
- Performance review: {PASS | N/A — reason}
- Regression review: {PASS | N/A — reason}

### Deployment notes

{Any migration steps, feature flag requirements, or environment variables required before deployment}
{If none: "No special deployment steps required."}
```

### Step 6 — Execute 11 release lenses

See `.ai/skills/release-story/SKILL.md` Step 3. Lenses 1–11 are preserved unchanged:
Test Completeness → CI Pipeline → Docker Readiness → Migration Safety → Rollback Strategy →
Release Notes → Versioning → Contract Integrity → Documentation → Definition of Done → Deployment Safety.

### Step 7 — Final secrets check

Run and verify:
```
detect-secrets scan src/{target_folder}/ --baseline .secrets.baseline
```

Confirm: zero new findings.

### Step 8 — Final dependency check

```
pip-audit --requirement requirements.txt
```

Confirm: zero critical or high vulnerabilities.

### Step 9 — Verify migration safety

If the story includes a database migration:
- [ ] Migration is reversible (`downgrade` function present)
- [ ] Migration runs on an empty database without error
- [ ] Migration runs on a database with existing data without error
- [ ] Migration does not lock tables for longer than 1 second
- [ ] Column additions use `nullable=True` or have a safe `server_default`

### Step 10 — Verify observability completeness

Confirm the following metrics are present in Prometheus scrape output (or code):
- `aep_{service_name}_requests_total` — counter by status
- `aep_{service_name}_request_duration_seconds` — histogram
- `aep_{service_name}_errors_total` — counter by error type

Confirm the following log events are emitted:
- Service startup: `{service_name}.started`
- Request processed: `{operation}.succeeded` or `{operation}.failed`
- Kafka event published: `event.published`
- Kafka event consumed: `event.processed` or `event.processing_failed`

### Step 11 — Produce release readiness report

```
## Release Story Review: PR #{N} — {title}
Story: {story_id} | PI: {PI}

### Pre-Release Verification
{13-dimension table from Step 2b}

### Verdict: APPROVE | REQUEST CHANGES | READY FOR RELEASE

### Definition of Done
All {N} items: MET | {N} NOT MET (list blocking items)

### Quality Summary
Tests:       N unit passing, N integration passing, N acceptance passing
Coverage:    N% (≥ 80% required)
Lint:        CLEAN
Type check:  CLEAN
Secrets:     CLEAN
Deps audit:  CLEAN (zero critical/high CVEs)

### Reviews
Code review:        PASS
Security review:    PASS | N/A
Performance review: PASS | N/A
Regression review:  PASS | N/A

### Release Readiness Matrix
{11-lens status table — see skill Step 5}

### Release Notes
{human-readable notes for CHANGELOG and team communication}

### Deployment Checklist
{ordered deployment steps}

### Rollback Plan
{risk level + numbered procedure}

### Known Risks
{residual risks or "None identified"}

### Next Story Recommendation
{next story ID from USER_STORIES.md with rationale}

### Final Merge Checklist
{full checklist from skill Step 4}
```

---

## Expected Outputs

| Artifact | Description |
|----------|-------------|
| Pre-Release Verification table | 13-dimension Architecture v2.0 gate with evidence |
| Definition of Done sweep | Completed DoD checklist with evidence for every item |
| Updated `CHANGELOG.md` | Story entry under `[Unreleased]` |
| Updated `STATUS.md` / `METRICS.md` | PI progress and measurable outcomes (when applicable) |
| PR description | Complete PR description ready to paste |
| Release Notes | Human-readable summary for team and changelog |
| Deployment Checklist | Ordered, executable deployment steps |
| Rollback Plan | Risk classification and rollback procedure |
| Known Risks | Residual risks and monitoring watch items |
| Next Story recommendation | Suggested next story ID with rationale |
| Release readiness report | Verdict with 11-lens matrix and merge checklist |

---

## Quality Gates

- [ ] Platform constitution loaded before review (Step 2)
- [ ] Pre-Release Verification complete — all mandatory dimensions PASS
- [ ] Every DoD item is MET or has a documented exception
- [ ] No unresolved BLOCKER from any review
- [ ] `detect-secrets` is clean
- [ ] `pip-audit` is clean (zero critical/high)
- [ ] Migration is reversible (if applicable)
- [ ] PR description is complete and accurate
- [ ] Observability metrics and logs confirmed present
- [ ] All 11 release lenses executed (see skill)

---

## Completion Checklist

```
[ ] Platform constitution loaded
[ ] Pre-Release Verification complete — mandatory dimensions PASS
[ ] PR metadata and CI status parsed
[ ] Definition of Done sweep complete — all items MET
[ ] Changelog updated under [Unreleased]
[ ] STATUS.md and METRICS.md updated (if applicable)
[ ] PR description written — all sections complete
[ ] 11 release lenses executed — matrix produced
[ ] Final secrets check — zero findings
[ ] Final dependency audit — zero critical/high CVEs
[ ] Migration safety verified (if applicable)
[ ] Observability confirmed — metrics, traces, logs
[ ] Release Notes, Deployment Checklist, Rollback Plan, Known Risks, Next Story produced
[ ] Release readiness report produced with verdict
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Skip platform constitution loading (Step 2) or Pre-Release Verification (Step 2b)
- Declare a story READY FOR RELEASE with unresolved BLOCKERs or Pre-Release FAILs
- Skip the Definition of Done sweep
- Write a PR description that does not reference acceptance criteria
- Accept "tests will be added in the next sprint" as meeting DoD
- Produce a changelog entry for features not in this story
- Skip the secrets scan or the dependency audit
- Mark a migration as safe without verifying reversibility
- Merge the PR directly — this command produces artefacts for human review and approval only
- Approve a story that has a gate bypass mechanism (Constitution H2 violation)
- Mark performance or security review as N/A without a written justification
- Issue READY FOR RELEASE when any mandatory Pre-Release dimension FAILs
- Skip any of the 11 release lenses (see skill Forbidden Actions)
