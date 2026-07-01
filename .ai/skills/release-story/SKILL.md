---
name: release-story
description: |
  When the engineer types /release-story <PR_NUMBER> or /release-story <GitHub PR URL>,
  fetch the PR diff and execute the final release gate before merge. This is not a
  correctness review (aep-review) nor a security review (security-review) nor a
  regression review (regression-review) — it is a ship-readiness gate. Executes 11
  release lenses in sequence: Test Completeness → CI Pipeline → Docker Readiness →
  Migration Safety → Rollback Strategy → Release Notes → Versioning → Contract Integrity
  → Documentation → Definition of Done → Deployment Safety. Produces a Final Merge
  Checklist with ordered deployment steps and rollback procedure. Verdicts are
  APPROVE, REQUEST CHANGES, or READY FOR RELEASE. Never approve a PR with failing CI,
  an unresolved Critical finding, or an acceptance criterion without a corresponding test.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq
  file: read
---

# Release Story — Final Release Gate

<purpose>
This is the final human gate before a story is merged and deployed. Its job is not to
re-check correctness or security — those gates ran earlier in the pipeline. Its job is
to answer one question: **Is this safe to deploy, reversible if it fails, and understood
by every stakeholder?**

Correct pipeline order:
implement-story → aep-review → security-review → performance-review → regression-review → **release-story**

Every PR that reaches release-story has already passed technical correctness and security
checks. release-story checks ship-readiness: CI is green, tests cover every acceptance
criterion, the deployment can be rolled back, release notes inform the team, contracts
are intact, and the deployment sequence is documented.
</purpose>

---

## When To Activate

Trigger when the engineer types `/release-story` followed by a PR number or GitHub PR URL.
This skill runs after all other review skills have passed. It is the last command before
a human clicks "Merge".

```
/release-story 42
/release-story https://github.com/org/Agentic_platform/pull/42
```

---

## Step 1 — Fetch PR Metadata

```bash
# Full PR metadata including CI check rollup and review statuses
gh pr view <NUMBER> --json \
  title,body,author,baseRefName,headRefName,additions,deletions,changedFiles,\
  reviews,statusCheckRollup,labels,milestone,createdAt,updatedAt

# File-level change summary (status + name)
gh pr diff <NUMBER> --name-status

# Full CI check status
gh pr checks <NUMBER>
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
Story ID:       {US-XX.XX}  (from PR body)
PI:             {PI-XX-...} (from PR body or head branch name)
```

Parse PR body to extract Story ID (e.g. `US-01.03`) and PI (e.g. `PI-01-Platform-Core`).
If either is absent, flag as **Major** — PR description does not link to a User Story.

**Parse and report CI status immediately:**

```
CI Lint:               ✅ PASS / ❌ FAIL / ⏳ PENDING
CI Unit Tests:         ✅ PASS / ❌ FAIL / ⏳ PENDING
CI Contract Validation: ✅ PASS / ❌ FAIL / ⏳ PENDING
CI Build:              ✅ PASS / ❌ FAIL / ⏳ PENDING
CI Security Scan:      ✅ PASS / ❌ FAIL / ⏳ PENDING
Overall CI:            🟢 GREEN / 🔴 RED / 🟡 PENDING
```

**Stop condition:** If Overall CI is RED or PENDING, flag all failing/pending checks as
Critical and proceed with lenses for completeness, but the Verdict MUST be REQUEST CHANGES.

---

## Step 2 — Load Reference Documents

Read these documents as release context. Do not re-output their contents. They are the
standards against which release readiness is measured.

```bash
# Platform authorities
cat CONSTITUTION.md
cat ARCHITECTURE.md
cat CHANGELOG.md

# PI context (substitute {PI} from Step 1)
cat docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md
cat docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md
cat docs/engineering/implementation-roadmap/{PI}/TESTING.md

# Contract schemas
ls contracts/
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
cat contracts/tool-contract.schema.json
cat contracts/task-schema.schema.json
cat contracts/memory-schema.schema.json

# Environment baseline
cat .env.example 2>/dev/null || echo ".env.example not found"
```

**Stop condition:** If `DEFINITION_OF_DONE.md` or `ACCEPTANCE_CRITERIA.md` cannot be read,
flag as Critical — release gate cannot execute without DoD and AC documents.

---

## Step 3 — Execute 11 Release Lenses

Execute every lens in this exact order. A Critical finding in Lens 1 is not superseded by
a clean result in Lens 11. Report findings from all lenses before producing the verdict.

---

### Lens 1 — Test Completeness and Coverage

**Every changed source file must have a corresponding test file. Every acceptance criterion
must have a named test. No exceptions.**

```bash
# Get all added/modified Python source files
gh pr diff <NUMBER> --name-status | grep -E "^[AM].*src.*\.py$"

# For each changed source file: verify corresponding test file exists
# e.g. src/platform/agent_registry/domain/registry_service.py
#      → tests/platform/agent_registry/domain/test_registry_service.py

# Check acceptance criterion test naming convention
rg "test_ac_" --include="*.py" -l

# Check for vacuous tests
rg "assert True\b|assert 1 == 1|assert False\b|^\s+pass$" --include="*.py" -- <test_files>

# Check cross-tenant isolation tests if data layer touched
rg "tenant_id.*isolation|cross_tenant|test_tenant" --include="*.py"

# Check integration test for primary event flow
rg "test.*integration\|integration.*test" --include="*.py" -l
```

**Checks:**

- Every changed source file has a corresponding test file at the mirrored path under `tests/`
- Unit test coverage ≥ 80% on all new code — evidence required from CI coverage report or
  coverage badge in the PR. If no coverage evidence is present, flag as Major.
- One test per Given/When/Then acceptance criterion in `ACCEPTANCE_CRITERIA.md` for this story,
  named `test_ac_{criterion_id}_{description}` (e.g. `test_ac_01_topic_provisioned_on_task_created`)
- Integration test present covering the primary event flow introduced by this story
- Cross-tenant isolation test present if the story touches any database table, Redis key,
  or Kafka topic (verifying tenant A cannot read or affect tenant B's data)
- No vacuous assertions (`assert True`, `assert 1 == 1`, lone `pass` in test body)
- Tests are structured: arrange-act-assert — not a single monolithic assertion block

**Why it matters:** Shipping code without AC-mapped tests means the next PR can silently
break this story's behaviour with no automated signal. Cross-tenant isolation tests are the
only automated proof that multi-tenancy is correctly enforced.

**Flag as Critical:** Acceptance criterion with no corresponding test, missing cross-tenant
isolation test when data layer is touched

**Flag as Major:** Coverage below 80% on new code, missing integration test for primary
event flow, test file missing for a changed source file

**Flag as Minor:** Test file exists but does not cover an edge case visible in the diff,
vacuous assertion in a non-critical test

---

### Lens 2 — CI Pipeline Status

**All CI checks must be GREEN. A single failing or pending check blocks merge.**

```bash
gh pr checks <NUMBER>
```

**Checks:**

- **ALL** CI checks are GREEN — no pending steps, no failing steps, no skipped steps
- Lint step (Ruff, Black, ESLint, Prettier) passed — zero warnings
- Type check step (`mypy --strict`) passed — no type errors
- Unit tests passed — all pass, no skipped tests without documented reason
- Contract validation step (`python scripts/validate_contract.py contracts/`) passed — exits 0
- Container build passed — all service images build successfully
- Security scan passed:
  - Trivy: zero critical, zero high CVEs in the final image
  - `detect-secrets scan` clean — no new findings
  - `pip-audit` clean — no packages with known vulnerabilities
- No CI step was skipped with `continue-on-error: true` or equivalent bypass

```bash
# Verify no bypass flags in CI config
rg "continue-on-error|allow_failure|--no-verify" .github/workflows/ 2>/dev/null
```

**Why it matters:** A PR merged with a failing CI step leaves the main branch broken for
every developer who pulls after this merge. A bypassed security scan leaves CVEs in production.

**Flag as Critical:** Any CI check is not GREEN (failing, pending, skipped, or bypassed)

---

### Lens 3 — Docker and Container Readiness

**Apply this lens to every Dockerfile and docker-compose file in the diff.**

```bash
# Find changed Dockerfiles
gh pr diff <NUMBER> --name-status | grep -iE "^[AM].*Dockerfile"

# For each changed Dockerfile, inspect:
rg "^FROM|^USER|^HEALTHCHECK|^EXPOSE|^COPY|^RUN|^ENV|^ARG" -- <changed_dockerfiles>

# Detect secrets in Dockerfile
rg "(ENV|ARG)\s+(PASSWORD|SECRET|TOKEN|API_KEY|KEY)\s*=" -- <changed_dockerfiles> -i
```

**Checks:**

- **Multi-stage build:** final image stage does not `COPY --from=builder` build tools,
  dev dependencies, test files, or source code beyond what the runtime requires
- **Non-root user:** `USER` instruction present in the final stage, setting a non-root UID
  (e.g. `USER 1000:1000` or a named service account — never `USER root`)
- **HEALTHCHECK:** `HEALTHCHECK` instruction present and pointing to `/health/live` with
  an appropriate interval (`--interval=30s`) and timeout (`--timeout=10s`)
- **Pinned base image:** base image uses a specific version tag — not `:latest`, not `:stable`
  (e.g. `python:3.12.4-slim-bookworm` is correct; `python:3.12-slim` is a Major flag)
- **No credentials:** no `ENV` or `ARG` instruction that assigns a credential value inline
- **Image builds:** confirmed GREEN in CI build step (see Lens 2)
- **No unnecessary files:** `.dockerignore` prevents `.git`, `tests/`, `*.pyc`, `__pycache__`,
  `node_modules/`, local env files from being copied into the image

**Why it matters:** A container running as root means a process escape gives an attacker
full host access. A missing HEALTHCHECK means Kubernetes cannot detect a crashed service
and will continue routing traffic to it. Pinned base images prevent silent upstream changes
from breaking builds or introducing CVEs.

**Flag as Critical:** Root user in final image stage, credential value in `ENV`/`ARG`

**Flag as Major:** `HEALTHCHECK` missing, base image uses `:latest` or unpinned tag,
multi-stage build not used for a new service Dockerfile

**Flag as Minor:** `.dockerignore` missing or incomplete, overly generous `COPY . .`
without exclusions

---

### Lens 4 — Database Migration Safety

**Apply this lens when the diff contains any Alembic migration file.**

```bash
# Find new or modified migration files
gh pr diff <NUMBER> --name-status | grep -E "^[AM].*alembic/versions/.*\.py$"

# For each migration file, read its contents
# Check downgrade function
rg "def downgrade" -- <migration_files>

# Check for NOT NULL additions without defaults
rg "nullable=False|NOT NULL" -- <migration_files>

# Check for column removals and live code references
gh pr diff <NUMBER> --name-status | grep -E "^D.*alembic" 2>/dev/null
# If columns removed: verify no source references remain
rg "{removed_column_name}" src/ --include="*.py"

# Check RLS on new tables
rg "CREATE TABLE|op\.create_table" -- <migration_files>
rg "ROW LEVEL SECURITY|ENABLE ROW" -- <migration_files>

# Check migration test evidence
rg "test_migrations|test_migration_idempotency" --include="*.py" -l
```

**Checks:**

- **Downgrade function:** every migration has a `downgrade()` function that exactly reverses
  the `upgrade()` — not a `pass` stub, a real reverse operation
- **Idempotency:** migration uses `checkfirst=True` on index/constraint creation,
  or guards column additions with `IF NOT EXISTS` where applicable
- **NOT NULL safety:** no column added as `NOT NULL` without either a `server_default`
  value or an explicit backfill of existing rows before the constraint is applied
- **Column removal:** no column removed that has any reference in application source code
  (verified with `rg` search returning 0 results for the column name across `src/`)
- **No table locks:** migration does not perform a full table rewrite on a table with
  existing production data (e.g. changing column type on a large table without CONCURRENTLY)
- **RLS applied:** every new table created in `upgrade()` has `ALTER TABLE ... ENABLE ROW
  LEVEL SECURITY` and at least a deny-all policy in the same migration
- **Migration filename:** follows the convention `{revision_id}_{description}.py` — no
  auto-generated names like `a3f1b2c4d5e6_.py`
- **Migration tests passing:** `pytest tests/db/test_migrations.py` GREEN (idempotency),
  `pytest tests/db/test_rls_isolation.py` GREEN (if new table added)

**Why it matters:** A migration with no `downgrade()` function means a bad deployment
cannot be rolled back without manual database surgery. A `NOT NULL` column without a
default will crash every existing row read during the migration, taking the service down.
Missing RLS on a new table is a tenant data isolation breach.

**Flag as Critical:** No `downgrade()` function or `downgrade()` is a stub `pass`,
`NOT NULL` column addition without `server_default` or explicit backfill, column removal
with live application code references

**Flag as Major:** Missing RLS policy on new table, migration without idempotency
safeguards, migration file with auto-generated opaque name

**Flag as Minor:** Missing index that will be required for a query that exists in the
application code, migration comment describing intent absent

---

### Lens 5 — Rollback Strategy

**Assess the rollback story for this PR. Classify rollback risk. Document the procedure.**

```bash
# Check PR description for rollback documentation
gh pr view <NUMBER> --json body | jq -r '.body' | rg -i "rollback|revert|downgrade"

# Identify change categories
gh pr diff <NUMBER> --name-status | grep -E "^[AM]" | awk '{print $2}' | \
  grep -E "(Dockerfile|migration|schema|kafka|contracts/)" | sort -u
```

**Checks:**

**Code-only changes (no migration, no contract change, no new Kafka topic):**
- Rollback = redeploy previous image tag — always safe
- Rollback risk: **LOW**

**Migration present:**
- Is `alembic downgrade -1` safe? The downgrade must not destroy data the new code created
- Will rolling back the image (before downgrading) leave the schema in a state the old
  code can run against? (Schema forward + old code must be compatible for the window
  between deployment and rollback decision)
- Rollback risk: **MEDIUM** if downgrade is safe, **HIGH** if downgrade destroys data

**New Kafka topic introduced:**
- Rolling back the consumer: topic persists, new messages accumulate, old consumer
  ignores them — acceptable provided the topic has a retention policy
- Rolling back the producer: topic exists but no new messages — acceptable
- Rollback risk: **LOW** to **MEDIUM** depending on consumer coupling

**Contract schema changed:**
- Is the change backward compatible? (Consumers of old schema version still process new messages?)
- If backward incompatible: what is the cutover plan and can it be reversed?
- Rollback risk: **HIGH** if breaking change, **MEDIUM** if additive only

**API endpoint changed:**
- Can old callers still use the new endpoint (backward compatible)?
- If new required field added to request: old callers will fail — HIGH risk
- Rollback risk: assessed per case

**Checks for all risk levels:**
- Is the rollback strategy documented in the PR description?
  (For MEDIUM: procedure must be present; for HIGH: procedure is mandatory and blocking)
- For HIGH rollback risk: is there an explicit "go/no-go" rollback decision point
  documented (e.g. time window before migration is considered permanent)?

**Why it matters:** Deployments fail. Without a documented rollback plan, a bad deployment
requires emergency manual intervention at 3am by an engineer who was not on-call, working
from first principles with no documented procedure.

**Flag as Critical:** No rollback path exists and the deployment cannot be reverted
without data loss or manual schema surgery, with no documented plan

**Flag as Major:** HIGH rollback risk without explicit rollback procedure in PR description,
MEDIUM rollback risk without at least a one-line procedure

---

### Lens 6 — Release Notes and Changelog

**Release notes are the social contract between the PR author and every engineer who
integrates this change.**

```bash
# Read the top of the changelog
head -80 CHANGELOG.md

# Verify story ID is referenced
rg "{story_id}" CHANGELOG.md

# Check for breaking change marker
rg "BREAKING" CHANGELOG.md | head -20

# Check for environment variable documentation
gh pr diff <NUMBER> | rg "^\+.*os\.environ|^\+.*getenv|^\+.*ENV\[" 2>/dev/null
```

**Checks:**

- `CHANGELOG.md` has been updated — there is an entry under `[Unreleased]` or a new
  version heading added in this PR
- The entry references the Story ID (e.g. `US-01.03`) so it is traceable
- The entry is placed under the correct section:
  - `### Added` — new capability introduced
  - `### Changed` — existing behaviour modified
  - `### Fixed` — defect corrected
  - `### Deprecated` — capability scheduled for removal
  - `### Removed` — capability removed
  - `### Security` — security-relevant change
- The entry is written for a human reader — full sentence, past tense, describes what
  changed and why it matters: _"Added Kafka topic provisioning for TaskCreated events,
  enabling agent-runtime to consume work items without polling."_
  NOT a raw commit message: _"feat(kafka): add topic"_
- **Breaking changes** are marked `**BREAKING**` at the start of the entry and also
  appear under a `### Breaking Changes` section if one exists
- Every new environment variable introduced by this PR is listed in the changelog entry
  (name and purpose — not the value)
- Every new API endpoint is listed in the changelog entry (method + path)
- If a new service or major feature was added: `ARCHITECTURE.md` or the relevant
  `docs/engineering/implementation-roadmap/{PI}/` document has been updated

**Why it matters:** The changelog is the primary communication channel to other engineers,
QA, and operations about what shipped in each release. An undocumented breaking change
causes multi-hour debugging sessions for downstream teams who integrate after this release.

**Flag as Major:** `CHANGELOG.md` not updated at all, breaking change not marked as
`**BREAKING**`, new environment variable not documented

**Flag as Minor:** Changelog entry written as commit message rather than human prose,
entry placed under wrong section, new API endpoint not listed

---

### Lens 7 — Versioning

**Version numbers are the contract between publisher and consumer. Breaking a contract
without incrementing the version causes silent failures.**

```bash
# Check service version
rg "^version\s*=" pyproject.toml 2>/dev/null
rg "\"version\"\s*:" package.json 2>/dev/null

# Check contract schema versions
rg "schema_version" contracts/ --include="*.json"

# Check agent contract version in registration files
rg "contract_version" -- <changed_registration_files>

# Check API version in routes
rg "/api/v[0-9]+" -- <changed_files>
```

**Checks:**

**Semantic versioning (applies to packages, services, and SDKs):**
- `MAJOR.MINOR.PATCH` — `MAJOR` for breaking changes, `MINOR` for new backward-compatible
  features, `PATCH` for backward-compatible bug fixes
- The new version number is higher than the version on `main` — no version downgrade
- If a dependency (`aep-common`, `agent-sdk`, `tool-sdk`) was changed in a breaking way:
  its package version must be incremented and consuming services updated

**API versioning:**
- If an existing endpoint's request or response contract changed in a breaking way:
  the endpoint must move to a new version (`/api/v2/`) — not silently modify `/api/v1/`
- New endpoints introduced in this PR use the current API version prefix

**Contract schema versioning:**
- If any file in `contracts/` was modified: `schema_version` field in that schema must
  be incremented
- All existing examples in `contracts/examples/*.json` must still validate against the
  updated schema
- If a breaking schema change: ADR must exist in `DECISIONS.md` (see Lens 8)

**Agent/Tool contract versioning:**
- If an agent's `input_schema` or `output_schema` changed: `contract_version` in the
  agent registration file must be incremented
- Consumers of this agent's output must be assessed for compatibility

**Why it matters:** A breaking API or contract change without a version increment causes
consumers to receive data they cannot parse, silently deserialising to zero or crashing.
These failures are difficult to trace because the producer appears healthy.

**Flag as Major:** Breaking API change without version increment, breaking contract change
without `schema_version` bump, package version not incremented for a breaking library change

**Flag as Minor:** PATCH vs MINOR version increment choice arguable (document rationale
rather than blocking)

---

### Lens 8 — Contract Integrity

**Contract violations are Critical and block merge unconditionally. A single bad event
schema can corrupt the event log for the lifetime of the platform.**

```bash
# Run the contract validation script
python scripts/validate_contract.py contracts/

# Validate examples against schemas
python -c "
import json, jsonschema, glob, sys
errors = []
for schema_path in glob.glob('contracts/*.schema.json'):
    with open(schema_path) as f:
        schema = json.load(f)
    example_pattern = schema_path.replace('contracts/', 'contracts/examples/').replace('.schema.json', '.*.json')
    for example_path in glob.glob(example_pattern):
        with open(example_path) as f:
            instance = json.load(f)
        try:
            jsonschema.validate(instance, schema)
        except jsonschema.ValidationError as e:
            errors.append(f'{example_path}: {e.message}')
for e in errors: print(e)
sys.exit(1 if errors else 0)
"

# Verify event type strings in changed producers match schemas
rg "event_type.*=|\"event_type\":" -- <changed_files>

# Check for missing ADR on contract changes
gh pr diff <NUMBER> --name-status | grep "^[AM].*contracts/"
rg "ADR-" DECISIONS.md | tail -10
```

**Checks:**

- `python scripts/validate_contract.py contracts/` exits 0 — all schemas are valid JSON
  Schema documents and pass internal consistency checks
- Every example in `contracts/examples/` validates against its corresponding schema — no
  schema change has broken existing examples without the examples also being updated
- Event type strings in changed producer code match the `event_type` values defined in
  `contracts/event-envelope.schema.json` exactly (case-sensitive, PascalCase)
- Agent registration files in changed code validate against `contracts/agent-contract.schema.json`
- Tool registration files validate against `contracts/tool-contract.schema.json`
- No field that existing consumers depend on was removed from a schema without:
  1. A deprecation period in the previous release
  2. An ADR documenting the removal decision
- If any contract schema was modified: an ADR exists in `DECISIONS.md` documenting the
  decision (title, date, context, decision, consequences)
- Contract examples cover the happy path AND at least one error/edge-case variant

**Why it matters:** A contract mismatch between producer and consumer causes silent
deserialization failures in production. Because events are asynchronous, the failure
surface can appear in a completely different service from where the bug was introduced,
making them extremely hard to debug under pressure.

**Flag as Critical:** Contract validation script fails, producer publishes event type
not matching schema, agent registration fails contract validation, contract field removed
without ADR

**Flag as Major:** Breaking contract change without ADR, contract examples not updated
to reflect schema change, event type string does not match schema definition (PascalCase
violation, typo, extra suffix)

---

### Lens 9 — Documentation Completeness

**Every public surface introduced by this story — API endpoints, environment variables,
Kafka topics, services — must be documented before the story can ship.**

```bash
# Check API spec for new endpoints
gh pr diff <NUMBER> | rg "^\+.*@router\.(get|post|put|patch|delete)" 2>/dev/null
# For each new endpoint, verify it appears in API_SPEC.md
rg "{endpoint_path}" docs/engineering/implementation-roadmap/{PI}/API_SPEC.md 2>/dev/null || echo "Check API_SPEC.md"

# Check .env.example for new environment variables
gh pr diff <NUMBER> | rg "^\+.*os\.getenv|^\+.*os\.environ\[" | grep -v "test"
# For each new env var, verify .env.example has it
rg "{ENV_VAR_NAME}" .env.example 2>/dev/null || echo "Missing from .env.example"

# Check REFERENCE_ARCHITECTURE.md event catalogue for new topics
gh pr diff <NUMBER> | rg "^\+.*topic.*=|^\+.*TOPIC" 2>/dev/null
rg "{topic_name}" ARCHITECTURE.md 2>/dev/null || echo "Check event catalogue"

# Check for undocumented public methods
gh pr diff <NUMBER> --name-status | grep -E "^[AM].*src.*\.py$" | awk '{print $2}'
# For each changed file: check docstrings on new public methods
rg "^def [a-z]" -- <changed_source_files> -A 1 | rg -v '"""'

# Check ARCHITECTURE.md for new services
gh pr diff <NUMBER> --name-status | grep -E "^A.*src/platform/[^/]+/__init__" 2>/dev/null
```

**Checks:**

- Every new HTTP endpoint documented in `docs/engineering/implementation-roadmap/{PI}/API_SPEC.md` with:
  method, path, request body schema, response schema, authentication requirement, status codes
- Every new environment variable documented in `.env.example` for its service with:
  variable name, example value (not a real credential), and a comment describing its purpose
- Every new Kafka topic documented in `ARCHITECTURE.md` event catalogue (Section 8) with:
  topic name, schema reference, producer service, consumer service(s), retention policy
- If a new platform service was introduced: `ARCHITECTURE.md` updated with service name,
  responsibility, owned database schema, owned Kafka topics, and API surface
- If an architectural decision was made (e.g. choosing one approach over alternatives):
  an ADR created in `DECISIONS.md`
- PR description contains deployment notes for any migration step, environment variable
  addition, or infrastructure change that the deployer must perform manually
- All new `public` methods in `domain/` layer have docstrings explaining the operation,
  parameters, and return value (not auto-generated one-liners)

**Why it matters:** An undocumented environment variable means the next deployment
environment starts up with a missing config and an opaque startup failure. An undocumented
API endpoint is invisible to the team and will be reimplemented or called incorrectly.

**Flag as Major:** New endpoint not in API spec, new environment variable not in
`.env.example`, new Kafka topic not in event catalogue, new service not in `ARCHITECTURE.md`

**Flag as Minor:** Public method missing docstring, docstring is a one-liner that just
restates the method name, deployment notes absent from PR description

---

### Lens 10 — Definition of Done Sweep

**The DoD is the team's explicit agreement on what "done" means. This lens performs an
exhaustive pass through every item.**

Read `docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md` in full.

For every item in the **Story-Level Gate** section, determine:

- **MET** — evidence found in the diff, CI results, or linked review verdicts
- **NOT MET** — evidence shows the criterion is not satisfied
- **N/A** — criterion does not apply to this story; explain why in one sentence

```
Story-Level Gate Results:
  [ MET ] {DoD item text} — evidence: {where/how it is satisfied}
  [ NOT MET ] {DoD item text} — gap: {what is missing}
  [ N/A ] {DoD item text} — reason: {why it does not apply}

Story-Level Gate: {N}/{N} items MET, {N} N/A, {N} NOT MET
```

If this PR closes out an entire PI (PI-Level PR):

```
PI-Level Gate Results:
  [ MET ] ...
  [ NOT MET ] ...
  [ N/A ] ...

PI-Level Gate: {N}/{N} items MET
```

**Cross-check with previous review verdicts:**

```bash
# Check that prior reviews have been completed
gh pr view <NUMBER> --json reviews | jq '.reviews[] | {author: .author.login, state: .state, body: (.body | .[0:100])}'
```

Verify:
- At minimum, `aep-review` verdict was APPROVE or READY FOR RELEASE (check PR comments
  or review approvals for evidence of the review having been run)
- For high-risk PRs: `security-review` and `regression-review` verdicts are present
- No prior review issued a REQUEST CHANGES verdict that was not subsequently resolved
  with a follow-up APPROVE comment

**Why it matters:** The DoD is a team-level social contract. Shipping something that does
not meet DoD sets a precedent that the quality bar is negotiable. Once the bar slips, it
continues slipping with each subsequent story.

**Flag as Critical:** Any mandatory DoD item is NOT MET with no N/A justification,
prior review issued REQUEST CHANGES with no documented resolution

**Flag as Major:** N/A justification is absent or insufficient (e.g. "not applicable"
with no reason), PI-Level Gate item NOT MET on a PI-closing PR

---

### Lens 11 — Deployment Safety

**Assess what happens the moment this PR is deployed to the dev cluster. Identify any
scenario where the service fails to start, fails health checks, or enters an inconsistent
state.**

```bash
# Check for new Kubernetes manifests
gh pr diff <NUMBER> --name-status | grep -E "^[AM].*infra/k8s/.*\.ya?ml$"

# Check for new GitHub Actions workflow changes
gh pr diff <NUMBER> --name-status | grep -E "^[AM].*\.github/workflows/"

# Check environment variable startup dependencies
gh pr diff <NUMBER> | rg "^\+.*os\.getenv|^\+.*os\.environ" | grep -v "test" | grep -v "default="

# Check for init container pattern on migration
rg "initContainers|alembic upgrade" infra/k8s/ --include="*.yaml" 2>/dev/null

# Check health check configuration
rg "livenessProbe|readinessProbe|HEALTHCHECK" infra/k8s/ --include="*.yaml" 2>/dev/null

# Check resource limits
rg "resources:|limits:|requests:" infra/k8s/ --include="*.yaml" 2>/dev/null
```

**Checks:**

**Environment variable readiness:**
- Every new `os.getenv("NEW_VAR")` call without a default value is a startup dependency
- Is `NEW_VAR` already set in the deployment environment, or must it be added before
  this service version is deployed?
- Startup order: env var must exist **before** the new service version starts

**Migration ordering:**
- If the PR includes an Alembic migration: does the migration run before the new service
  version starts? (init container pattern or pre-deploy migration hook in CI/CD)
- A service that requires a new column must not start until the migration applying that
  column is complete

**Kafka topic ordering:**
- If a new Kafka topic is introduced: is there a topic provisioning step before producers
  start? (missing topic causes producer errors at startup)
- Verify topic is created in the `docker-compose.yml` init or the K8s init container

**Health check success:**
- Does the new or modified service start cleanly within 60 seconds (platform SLO from
  `ARCHITECTURE.md`) against an existing, already-migrated database?
- `/health/live` and `/health/ready` endpoints respond 200 after startup

**Kubernetes resource configuration (for new service deployments):**
- `resources.requests` and `resources.limits` set for CPU and memory on new Deployments
- `livenessProbe` configured (checks `/health/live`)
- `readinessProbe` configured (checks `/health/ready`, prevents traffic before service is ready)
- `replicas` set to at least 2 for any service on a critical path

**Circular startup dependencies:**
- Does any new service wait for another service that in turn waits for the first?
  (Service A: `waitFor: service-b`, Service B: `waitFor: service-a`)
- This would cause both services to never reach READY state

**Deployment sequence documentation:**
- PR description includes ordered deployment steps for any non-trivial deployment
  (anything beyond "deploy the image")

**Why it matters:** A service that fails to start in production creates an alert at
deployment time. A missing environment variable or an unrun migration produces opaque
startup errors that take time to diagnose under deployment pressure.

**Flag as Critical:** Service will fail to start due to a missing required environment
variable that is not yet deployed, migration not ordered before service start when the
new code depends on a schema change

**Flag as Major:** Missing `resources.limits` on new K8s Deployment, missing
`livenessProbe` or `readinessProbe`, new Kafka topic not provisioned before producer starts,
circular startup dependency introduced

**Flag as Minor:** Single replica for a non-critical service, deployment notes absent
from PR description for a multi-step deployment

---

## Step 4 — Generate Final Merge Checklist

After completing all 11 lenses, produce this checklist in full. It must be actionable
without additional context — the engineer who clicks "Merge" must be able to follow it.

```markdown
## Final Merge Checklist: PR #{N} — {story_id} {story_title}

### Must be TRUE before merge (BLOCKING — do not merge if any box is unchecked)
- [ ] All CI checks are GREEN (lint, type check, unit tests, contract validation, build, security scan)
- [ ] No Critical findings from aep-review (or APPROVE / READY FOR RELEASE verdict documented)
- [ ] No Critical findings from security-review (if run for this PR)
- [ ] No Critical findings from regression-review (if run for this PR)
- [ ] No Critical findings from release-story (this review)
- [ ] All acceptance criteria have a corresponding named test (test_ac_{id}_*)
- [ ] Definition of Done Story-Level Gate: {N}/{N} items MET or N/A with justification
- [ ] CHANGELOG.md updated under [Unreleased] with human-readable entry referencing {story_id}
- [ ] No hardcoded credentials anywhere in the diff (detect-secrets clean)
- [ ] Database migration has a real downgrade() function (not a pass stub) — if applicable
- [ ] All contracts validate: python scripts/validate_contract.py contracts/ exits 0
- [ ] PR description includes story ID, deployment notes, and rollback procedure

### Should be TRUE before merge (MAJOR — resolve or formally defer with TASKS.md entry)
- [ ] Unit test coverage ≥ 80% on all new code (evidence from CI coverage report)
- [ ] All new environment variables documented in .env.example
- [ ] API spec updated for all new endpoints — docs/engineering/implementation-roadmap/{PI}/API_SPEC.md
- [ ] All Major findings from any review resolved or formally deferred to TASKS.md
- [ ] Rollback procedure documented in PR description (if rollback risk is MEDIUM or HIGH)
- [ ] ARCHITECTURE.md updated if a new service, topic, or service boundary changed

### Address before or shortly after merge (MINOR — track in TASKS.md)
- [ ] All Minor findings acknowledged and tracked in TASKS.md
- [ ] Performance baseline recorded if story has a latency or throughput SLO
- [ ] Docstrings on all new public domain methods

### Deployment steps (execute in this exact order)
1. {e.g. "Confirm NEW_ENV_VAR is set in dev cluster secrets before proceeding"}
2. {e.g. "Run: alembic upgrade head — verify: 'Running upgrade -> {revision_id}' in output"}
3. {e.g. "Provision Kafka topic: aep.task.created — verify topic exists before deploying producer"}
4. {e.g. "Deploy service image — rolling update: kubectl rollout status deployment/{service-name}"}
5. {e.g. "Verify: curl https://{host}/health/ready returns HTTP 200 on all replicas"}
6. {e.g. "Run smoke tests: pytest tests/smoke/ -v — all must pass"}

### Rollback procedure (execute if deployment fails or health check does not pass within 5 minutes)
1. {e.g. "Redeploy previous image tag: kubectl rollout undo deployment/{service-name}"}
2. {e.g. "Verify rollback: kubectl rollout status deployment/{service-name} shows previous revision"}
3. {e.g. "Run migration downgrade if migration was applied: alembic downgrade -1"}
4. {e.g. "Verify: curl https://{host}/health/ready returns HTTP 200 on all replicas"}
5. {e.g. "Notify #platform-alerts with incident summary and root cause"}
```

---

## Step 5 — Produce the Review Output

```
## Release Story Review: PR #{N} — {title}
Story: {story_id} | PI: {PI} | Author: {author}
Rollback Risk: LOW / MEDIUM / HIGH

### CI Status
Lint:                ✅ PASS / ❌ FAIL / ⏳ PENDING
Type Check:          ✅ PASS / ❌ FAIL / ⏳ PENDING
Unit Tests:          ✅ PASS / ❌ FAIL / ⏳ PENDING
Contract Validation: ✅ PASS / ❌ FAIL / ⏳ PENDING
Container Build:     ✅ PASS / ❌ FAIL / ⏳ PENDING
Security Scan:       ✅ PASS / ❌ FAIL / ⏳ PENDING
Overall:             🟢 GREEN / 🔴 RED / 🟡 PENDING

---

### Critical 🔴
{file/path.py}:{line} or {lens name} — {what is wrong}
  Why it blocks release: {concrete failure scenario in production}
  Fix: {specific action the author must take before merge}

---

### Major 🟠
{file/path.py}:{line} or {lens name} — {what is wrong}
  Risk: {impact if shipped without addressing}
  Fix: {specific action required, or "track in TASKS.md with priority HIGH"}

---

### Minor 🟡
{file/path.py}:{line} or {lens name} — {what is wrong}
  Fix: {specific action, or "track in TASKS.md"}

---

### Release Readiness Matrix
| Lens | Status | Notes |
|------|--------|-------|
| 1 Tests & Coverage | ✅ / ⚠️ / ❌ | AC coverage: {N}/{N}, coverage: {N}% on new code |
| 2 CI Pipeline | ✅ / ⚠️ / ❌ | All green / {failing step names} |
| 3 Docker | ✅ / ⚠️ / ❌ / N/A | {multi-stage ✅, non-root ✅, HEALTHCHECK ✅} |
| 4 Migration Safety | ✅ / ⚠️ / ❌ / N/A | {downgrade ✅, RLS ✅} or N/A — no migrations |
| 5 Rollback Strategy | LOW / MEDIUM / HIGH | {what makes it rollable, or what the risk is} |
| 6 Release Notes | ✅ / ⚠️ / ❌ | CHANGELOG updated ✅ / not updated ❌ |
| 7 Versioning | ✅ / ⚠️ / ❌ / N/A | {schema_version bumped ✅} or N/A — no contract change |
| 8 Contract Integrity | ✅ / ⚠️ / ❌ | validate_contract.py exits 0 ✅ / fails ❌ |
| 9 Documentation | ✅ / ⚠️ / ❌ | API spec ✅, .env.example ✅, event catalogue ✅ |
| 10 Definition of Done | {N}/{N} MET | {N} N/A with justification, {N} NOT MET |
| 11 Deployment Safety | ✅ / ⚠️ / ❌ | {env vars ✅, migration order ✅, probes ✅} |

---

{FINAL MERGE CHECKLIST — paste the full checklist generated in Step 4 here}

---

### Merge Recommendation
{1-3 sentences stating what must be resolved before merge, or confirming the story
meets every release gate and is ready to ship. Name specific findings that block merge
if any. Do not be vague.}

### Verdict
APPROVE — story is release-ready; merge when the team is ready to deploy
REQUEST CHANGES — {N} blocking issue(s) must be resolved; re-run release-story after fixes
READY FOR RELEASE — all 11 lenses pass, no Critical or Major findings, full merge checklist
                    complete, deployment and rollback procedures documented; approved for
                    immediate merge and deployment
```

---

## Mandatory Verdict Rules

**`REQUEST CHANGES`** — required when any of the following are present, regardless of other lens results:

- Any Critical finding in any lens
- Overall CI is RED or PENDING (any check not GREEN)
- Any acceptance criterion has no corresponding test
- Any mandatory DoD Story-Level Gate item is NOT MET with no N/A justification
- Contract validation script (`validate_contract.py`) fails or exits non-zero
- Database migration has no real `downgrade()` function
- No rollback path exists for a HIGH-risk deployment

**`APPROVE`** — when all of the following hold:

- All Critical findings are absent
- All Major findings are either resolved or explicitly deferred to `TASKS.md` with a
  priority and owner (the deferred item must be acknowledged in the checklist)
- Overall CI is GREEN
- DoD Story-Level Gate is fully met or N/A with justification for every item
- Contract integrity check passes
- Deployment steps and rollback procedure documented (even if brief)

**`READY FOR RELEASE`** — the highest verdict; only when:

- All 11 lenses produce ✅ PASS or documented N/A
- Zero Critical findings
- Zero Major findings (all resolved — not deferred)
- Full merge checklist produced with all boxes checkable
- Deployment steps ordered and complete
- Rollback procedure documented and executable
- All prior review verdicts (aep-review, security-review, regression-review) are APPROVE
  or READY FOR RELEASE

---

## Forbidden Actions

The following actions are **absolutely prohibited** regardless of circumstance:

1. **Never approve a PR with any failing or pending CI check.** A yellow or red CI status
   is a merge blocker without exception.
2. **Never approve a PR with an unresolved Critical finding.** Critical findings are not
   negotiable — the deployment will fail, lose data, or breach security.
3. **Never skip the DoD sweep.** Every item must be assessed. Skipping items means the
   gate did not run.
4. **Never approve a migration PR without verifying `downgrade()` exists and is a real
   reversal** — not a `pass` stub, not `raise NotImplementedError`.
5. **Never approve a PR with HIGH rollback risk and no documented rollback procedure.**
   HIGH risk means data loss is possible on rollback without a procedure.
6. **Never skip the contract integrity check.** A bad event schema corrupts the event
   log and breaks all consumers. It takes minutes to introduce and hours to diagnose.
7. **Never issue READY FOR RELEASE when any Major finding is unresolved.**
   READY FOR RELEASE means the PR is safe to merge and deploy immediately.
8. **Never produce a merge checklist with steps out of order.** Migrations must come
   before service deployments. Environment variables must be set before service start.
   Out-of-order steps cause the deployment to fail.

---

## Completion Checklist (internal — verify before issuing verdict)

Before stating the Verdict, confirm:

- [ ] CI status parsed and reported (all checks enumerated)
- [ ] All 11 lenses executed (no lens skipped)
- [ ] Rollback risk classified: LOW / MEDIUM / HIGH
- [ ] Final Merge Checklist produced (BLOCKING, MAJOR, MINOR, deployment steps, rollback)
- [ ] Deployment steps are in dependency order (env vars → migration → topic → service → healthcheck → smoke)
- [ ] Rollback procedure is actionable without additional context
- [ ] Verdict stated as exactly one of: APPROVE / REQUEST CHANGES / READY FOR RELEASE
- [ ] If REQUEST CHANGES: every Critical and blocking Major finding is named in the Merge Recommendation

---

## Review Rules

1. Review only the diff and CI results — do not invent findings not present in the evidence
2. This is a release gate, not a second correctness review — do not re-litigate findings
   that aep-review already approved; focus on ship-readiness
3. Every Critical finding must name the deployment risk in concrete terms — not "this is bad"
   but "this migration will drop the `tenant_id` column that 3 active consumers depend on"
4. Every finding must have a concrete fix — not "add tests" but "add `test_ac_03_topic_created`
   to `tests/platform/kafka/test_topic_provisioner.py`"
5. Cite the lens name or `file:line` from the diff for every finding
6. If a lens produces no findings, omit it from the findings sections (show in the matrix as ✅)
7. Deployment steps must be ordered — step 2 may not depend on step 4
8. The rollback procedure must work even if the engineer executing it did not write the PR
9. Maximum 15 findings total — prioritise by deployment risk, then data risk, then operational risk
10. The merge checklist is the single source of truth for the merge decision — it must be
    self-contained and executable by the engineer who clicks "Merge"
