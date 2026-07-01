# release-story.md

**Command:** `release-story`  
**Version:** 1.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs — run when a story is complete and ready for merge and deployment to a target environment

---

## Purpose

Use this command to prepare a completed User Story for release: verify all quality gates are met, produce the release artefacts, update the changelog, and ensure the deployment is safe and observable.

This command is the final checkpoint before merge. It does not merge or deploy — it validates that the implementation is ready for a human to approve and merge.

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Constitution | `CONSTITUTION.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| Definition of Done | `docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md` | Mandatory |
| Review Checklist | `docs/engineering/implementation-roadmap/{PI}/REVIEW_CHECKLIST.md` | Mandatory |
| User Story | `docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md` — implemented story | Mandatory |
| Acceptance Criteria | `docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md` | Mandatory |
| Review report | Output of `review-story.md` — must be PASS | Mandatory |
| Security review report | Output of `security-review.md` | If story touches auth/data/secrets |
| Performance review report | Output of `performance-review.md` | If story has latency SLOs |
| Test output | `pytest` run — all tests passing | Mandatory |
| Lint output | `ruff check` + `black --check` + `mypy --strict` | Mandatory |
| `git diff main` | All changes since branching from main | Mandatory |

**Substitutions required:**

```
{PI}              = e.g. PI-05-Execution-Framework
{story_id}        = e.g. US-PI-05-03
{story_title}     = e.g. Tool Capability Discovery
{service_name}    = e.g. tool-registry-service
{target_version}  = e.g. 1.2.0 (semver)
{target_env}      = dev | staging | production
{pr_branch}       = feature/PI-05-US-03-tool-capability-discovery
```

---

## Preconditions

- [ ] `review-story.md` has been executed and result is PASS or PASS WITH WARNINGS (no BLOCKERs)
- [ ] All tests pass: `pytest src/tests/ -v` exits 0
- [ ] Lint clean: `ruff check src/` exits 0
- [ ] Type check clean: `mypy --strict src/{target_folder}/` exits 0
- [ ] Security review complete (if required)
- [ ] Performance review complete (if required)
- [ ] No unresolved BLOCKER findings from any review
- [ ] Branch is up to date with `main`

---

## Execution Steps

### Step 1 — Final Definition of Done sweep

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
[ ] Changelog updated                      — see Step 2
[ ] .env.example updated                   — YES | NO change needed
[ ] PR description written                 — see Step 3
[ ] No TODO/FIXME in production paths      — grep: CLEAN
[ ] No hardcoded secrets                   — detect-secrets: CLEAN
```

If any mandatory DoD item is NOT MET, STOP. Resolve the item before proceeding.

### Step 2 — Update the changelog

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

### Step 3 — Write the pull request description

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

### Deployment notes

{Any migration steps, feature flag requirements, or environment variables required before deployment}
{If none: "No special deployment steps required."}
```

### Step 4 — Final secrets check

Run and verify:
```
detect-secrets scan src/{target_folder}/ --baseline .secrets.baseline
```

Confirm: zero new findings.

### Step 5 — Final dependency check

```
pip-audit --requirement requirements.txt
```

Confirm: zero critical or high vulnerabilities.

### Step 6 — Verify migration safety

If the story includes a database migration:
- [ ] Migration is reversible (`downgrade` function present)
- [ ] Migration runs on an empty database without error
- [ ] Migration runs on a database with existing data without error
- [ ] Migration does not lock tables for longer than 1 second
- [ ] Column additions use `nullable=True` or have a safe `server_default`

### Step 7 — Verify observability completeness

Confirm the following metrics are present in Prometheus scrape output (or code):
- `aep_{service_name}_requests_total` — counter by status
- `aep_{service_name}_request_duration_seconds` — histogram
- `aep_{service_name}_errors_total` — counter by error type

Confirm the following log events are emitted:
- Service startup: `{service_name}.started`
- Request processed: `{operation}.succeeded` or `{operation}.failed`
- Kafka event published: `event.published`
- Kafka event consumed: `event.processed` or `event.processing_failed`

### Step 8 — Produce release readiness report

```
## Release Readiness Report: {story_id} — {story_title}

### Verdict: READY FOR MERGE | NOT READY

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

### Migration safety
Database migration: SAFE | N/A
Feature flags:      REQUIRED ({flag_name}) | NOT REQUIRED

### Deployment environment
Target environment: {target_env}
Deployment order:   {if migration: "Run migration before deploying service"}
Rollback plan:      {run downgrade migration and redeploy previous version}

### PR description
{paste the full PR description from Step 3}
```

---

## Expected Outputs

| Artifact | Description |
|----------|-------------|
| Definition of Done sweep | Completed DoD checklist with evidence for every item |
| Updated `CHANGELOG.md` | Story entry under `[Unreleased]` |
| PR description | Complete PR description ready to paste |
| Release readiness report | Verdict with evidence |

---

## Quality Gates

- [ ] Every DoD item is MET or has a documented exception
- [ ] No unresolved BLOCKER from any review
- [ ] `detect-secrets` is clean
- [ ] `pip-audit` is clean (zero critical/high)
- [ ] Migration is reversible (if applicable)
- [ ] PR description is complete and accurate
- [ ] Observability metrics and logs confirmed present

---

## Completion Checklist

```
[ ] Definition of Done sweep complete — all items MET
[ ] Changelog updated under [Unreleased]
[ ] PR description written — all sections complete
[ ] Final secrets check — zero findings
[ ] Final dependency audit — zero critical/high CVEs
[ ] Migration safety verified (if applicable)
[ ] Observability confirmed — metrics, traces, logs
[ ] Release readiness report produced with READY FOR MERGE verdict
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Declare a story READY FOR MERGE with unresolved BLOCKERs
- Skip the Definition of Done sweep
- Write a PR description that does not reference acceptance criteria
- Accept "tests will be added in the next sprint" as meeting DoD
- Produce a changelog entry for features not in this story
- Skip the secrets scan or the dependency audit
- Mark a migration as safe without verifying reversibility
- Merge the PR directly — this command produces artefacts for human review and approval only
- Approve a story that has a gate bypass mechanism (Constitution H2 violation)
- Mark performance or security review as N/A without a written justification
