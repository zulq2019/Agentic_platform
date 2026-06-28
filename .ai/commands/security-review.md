# security-review.md

**Command:** `security-review`  
**Version:** 1.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs, all sprints — mandatory on stories touching auth, data, secrets, or tenant isolation

---

## Purpose

Use this command to perform a focused security review of a completed implementation.

This command is narrower and deeper than `review-story.md`. It specialises in six security domains: credential management, tenant isolation, input validation, network boundaries, audit trail completeness, and dependency vulnerabilities.

Run this command on every story that touches authentication, secrets, database access, tool integration, or multi-tenant data.

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Constitution — Security principles | `CONSTITUTION.md` (S-series principles) | Mandatory |
| Architecture — Security section | `docs/artifacts/TECHNICAL_ARCHITECTURE.md` (Section 14) | Mandatory |
| Architecture — Multi-tenancy | `docs/artifacts/TECHNICAL_ARCHITECTURE.md` (Section 20) | If story touches data |
| AI implementation rules | `CLAUDE.md` (Security Rules section) | Mandatory |
| ADRs — Security decisions | `DECISIONS.md` | Mandatory |
| Changed files | `git diff main` | Mandatory |
| Container scan results | `trivy image {image}` output | If Dockerfile changed |
| Dependency audit | `pip-audit` or `npm audit` output | Mandatory |
| Secrets scan | `detect-secrets scan` output | Mandatory |

**Substitutions required:**

```
{service_name}   = service under review
{target_folder}  = src/{location}
{tenant_id_var}  = the variable name used for tenant isolation
```

---

## Preconditions

- [ ] Implementation is complete
- [ ] `detect-secrets scan` output is available
- [ ] `pip-audit` output is available
- [ ] `trivy image` output available if Dockerfile was changed
- [ ] Database migration files available if story touches schema

---

## Execution Steps

### Step 1 — Credential scan

Read every changed file. Search for:

| Pattern | Severity |
|---------|---------|
| Strings matching API key patterns: `sk-`, `Bearer `, `token=`, `password=` | BLOCKER |
| Hardcoded hostnames or IP addresses | BLOCKER |
| Hardcoded database connection strings | BLOCKER |
| Any value that should come from environment variables | BLOCKER |
| `os.environ.get("KEY", "default-secret")` — default is a secret | BLOCKER |

For every finding, record:
```
CREDENTIAL FINDING
File: {filename}:{line}
Pattern: {what was found}
Severity: BLOCKER
Required action: Move to environment variable. Reference via Pydantic Settings.
```

Confirm that `detect-secrets scan` reports zero findings.

### Step 2 — Tenant isolation audit

For every database query in changed files:

- [ ] Does the query include `tenant_id` in the `WHERE` clause or rely on RLS policy?
- [ ] Is `current_setting('app.current_tenant_id')` set before the query?
- [ ] Are there any raw SQL strings that bypass the ORM and might miss the RLS context?
- [ ] Is there any aggregation that spans multiple tenants?

For every Kafka message produced:
- [ ] Does the `EventEnvelope` include `tenant_id`?

For every Redis key used:
- [ ] Does the key follow the pattern `aep:{tenant_id}:*`?

For every pgvector query:
- [ ] Does the query include a `tenant_id` metadata filter alongside the vector similarity search?

Record all violations as BLOCKER.

### Step 3 — Input validation audit

For every API endpoint and Kafka consumer in changed files:

- [ ] Is input validated against a schema before processing?
- [ ] Are Pydantic models used for all request bodies?
- [ ] Are `task_id`, `workflow_run_id`, and `tenant_id` validated as UUIDs, not plain strings?
- [ ] Is there protection against excessively large payloads?
- [ ] Are SQL injection vectors eliminated by ORM usage?
- [ ] Is there no string interpolation in SQL queries?

### Step 4 — Network boundary check

Cross-reference changed files against the Network Policy Matrix in `docs/artifacts/TECHNICAL_ARCHITECTURE.md` (Section 10):

- [ ] Does the code introduce any direct HTTP calls between services that are marked DENY?
- [ ] Specifically: does `agent-runtime` call `orchestrator-service` directly?
- [ ] Specifically: does `agent-runtime` call another `agent-runtime` instance?
- [ ] Does any service access Vault directly instead of through `secrets-service`?
- [ ] Are all new Kafka producers using SASL credentials from environment variables?

### Step 5 — Secrets management audit

For every place a credential or token is used:

- [ ] Is the token fetched from `secrets-service` at invocation time (not cached permanently)?
- [ ] Is the token TTL ≤ 15 minutes for tool invocations?
- [ ] Is the token scope limited to the minimum required (read vs write vs admin)?
- [ ] Is the token never logged, even at DEBUG level?
- [ ] Is the token never included in API response bodies?

### Step 6 — Audit trail completeness

For every significant action in the changed code:

- [ ] Does the action publish an event to Kafka that will be consumed by `audit-service`?
- [ ] Does the event include enough information to reconstruct the action from the audit log alone?
- [ ] For human approval decisions: is the approver name, timestamp, and decision captured?
- [ ] Are failed authentication attempts logged?

### Step 7 — Dependency vulnerability check

Review `pip-audit` output:
- [ ] Zero critical vulnerabilities
- [ ] Zero high vulnerabilities
- [ ] All medium vulnerabilities reviewed and either accepted (with written rationale) or remediated

Review `trivy image` output (if Dockerfile changed):
- [ ] Zero critical CVEs in base image
- [ ] Zero high CVEs in base image
- [ ] Base image is the latest approved version

### Step 8 — Three-control separation check (Constitution S1)

Verify that RBAC, Policy Engine, and Secrets remain three separate services:

- [ ] No new code in `rbac-service` that performs policy evaluation
- [ ] No new code in `policy-engine` that issues credentials
- [ ] No new code in `secrets-service` that performs access control decisions
- [ ] No new shared module that merges any two of these concerns

### Step 9 — Produce security review report

```
## Security Review Report: {service_name}

### Verdict: PASS | FAIL | PASS WITH CONDITIONS

### Critical Findings (must fix before merge)
1. ...

### High Findings (must fix before merge)
1. ...

### Medium Findings (should fix, tracked in TASKS.md)
1. ...

### Domain Results
Credential scan:         PASS | FAIL
Tenant isolation:        PASS | FAIL
Input validation:        PASS | FAIL
Network boundaries:      PASS | FAIL
Secrets management:      PASS | FAIL
Audit trail:             PASS | FAIL
Dependencies:            PASS | FAIL
Three-control separation: PASS | FAIL

### Summary
{one paragraph}
```

---

## Expected Outputs

| Artifact | Description |
|----------|-------------|
| Security review report | Structured report with verdict, findings by severity, domain results |
| Remediation list | Ordered list of required fixes with file and line references |

---

## Quality Gates

- [ ] `detect-secrets scan` reports zero findings
- [ ] `pip-audit` reports zero critical/high vulnerabilities
- [ ] Every database query verified to include tenant isolation
- [ ] Every new API key or token confirmed to come from `secrets-service`
- [ ] Three-control separation (RBAC/Policy/Secrets) confirmed intact
- [ ] No direct service-to-service HTTP calls introduced for denied pairs

---

## Completion Checklist

```
[ ] Credential scan complete — zero findings
[ ] Tenant isolation audit complete — all queries verified
[ ] Input validation audit complete — all endpoints validated
[ ] Network boundary check complete — no policy violations
[ ] Secrets management audit complete — TTL + scope verified
[ ] Audit trail completeness verified
[ ] Dependency vulnerability check complete
[ ] Three-control separation verified
[ ] Security review report produced with clear verdict
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Accept a credential finding as "acceptable" without explicit written approval
- Skip the tenant isolation check because "it was checked before"
- Ignore a critical or high CVE because "it is unlikely to be exploited"
- Accept an empty `detect-secrets` allowlist without verifying each entry
- Mark the review as PASS if any BLOCKER finding is unresolved
- Merge RBAC, Policy, or Secrets logic into a single module
- Accept a Vault bypass as a "temporary" solution
- Skip the three-control separation check
- Modify the Constitution's security principles
