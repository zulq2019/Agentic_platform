# security-review.md

**Command:** `security-review`  
**Version:** 2.0 — Architecture v2.0-aware  
**Skill authority:** `.ai/skills/security-review/SKILL.md` (full pipeline)  
**Applies to:** All PIs, all sprints — mandatory on stories touching auth, data, secrets, or tenant isolation

---

## Purpose

Use this command to perform a Principal Security Engineer level security audit of a pull request.

Before reviewing, this command **automatically loads** platform constitution, repository constitution, and contract schemas. It executes 20 security lenses (13 original + 7 Architecture v2.0 extensions) covering credentials, tenant isolation, metadata security, configuration security, execution profiles, provider isolation, plugin/marketplace security, compliance, OWASP, and supply chain. Produces findings, remediation plan, and merge recommendation.

Run this command on every PR touching authentication, secrets, database access, tool integration, multi-tenant data, Platform Objects, providers, plugins, or marketplace packages.

### Invocation (unchanged)

```
/security-review 42
/security-review https://github.com/org/Agentic_platform/pull/42
```

See `.ai/skills/security-review/SKILL.md` for the complete authoritative workflow.

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
| Constitution — Security principles | `CONSTITUTION.md` (S-series, H-series) | Mandatory |
| Architecture | `ARCHITECTURE.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| ADRs — Security decisions | `docs/architecture/ADR/DECISIONS.md` | Mandatory |
| Contract schemas | `contracts/` (including `platform-object.schema.json`) | Mandatory |
| PR diff | `gh pr diff <NUMBER>` | Mandatory |
| Container scan results | `trivy image {image}` output | If Dockerfile changed |
| Dependency audit | `pip-audit` or `npm audit` output | Mandatory |
| Secrets scan | `detect-secrets scan` output | Mandatory |

**Substitutions required:**

```
{pr_number}      = GitHub pull request number
{service_name}   = service under review
{target_folder}  = src/{location}
{tenant_id_var}  = the variable name used for tenant isolation
```

---

## Preconditions

- [ ] PR is open and diff is fetchable via `gh pr diff`
- [ ] `detect-secrets scan` output is available
- [ ] `pip-audit` output is available
- [ ] `trivy image` output available if Dockerfile was changed
- [ ] Database migration files available if PR touches schema

---

## Execution Steps

### Step 1 — Fetch PR metadata and classify security zones

See `.ai/skills/security-review/SKILL.md` Step 1. Classify every changed file into security zones (AUTH, RBAC, POLICY, SECRETS, TENANT, AGENT, TOOL, INFRA, DEPS).

### Step 2 — Load platform and repository constitution (automatic)

Load all platform constitution docs and repository constitution before reviewing any changed file. See skill Step 2.

### Step 3 — Run automated pre-checks

Execute `detect-secrets`, `pip-audit`, credential patterns, gate bypass scan, dangerous functions, and SQL injection vectors against changed files only.

### Step 4 — Execute 20 security lenses

**Lenses 1–13 (preserved):** Authentication, Authorisation/RBAC, Secrets, RBAC/Policy/Secrets Separation, Tenant Isolation, Input Validation, Output Encoding, API Security, Container Security, Dependencies, Least Privilege, Auditability, Human Gate Integrity.

**Lenses 14–20 (Architecture v2.0):** Metadata Security, Configuration Security, Execution Profile Security, Provider Isolation, Compliance, Plugin Security, Marketplace Security.

### Step 5 — Produce security review report

```
## Security Review: PR #{N} — {title}

### Pre-check Results
{automated scan summary}

### Security Zone Classification
{zone table}

### Critical / Major / Minor Findings
{file:line findings with attack scenario and specific fix}

### Security Findings Summary
{20-lens status table}

### Architecture v2.0 Dimension Summary
{17-dimension status table}

### Remediation Plan
Priority 1 — Critical (must resolve before merge)
Priority 2 — Major (resolve before or immediately after merge)
Priority 3 — Minor (track in TASKS.md)

### Merge Recommendation
{1-2 sentences}

### Verdict
APPROVE | REQUEST CHANGES | NEEDS DISCUSSION
```

---

## Architecture v2.0 Review Dimensions

| Dimension | Primary lens |
|-----------|--------------|
| Platform Contracts | 6, 14 |
| RBAC | 2, 4 |
| Least Privilege | 11 |
| Secrets | 3, 4 |
| Authentication | 1 |
| Authorization | 2 |
| Metadata Security | 14 |
| Configuration Security | 15 |
| Execution Profiles | 16 |
| Provider Isolation | 17 |
| Tenant Isolation | 5 |
| Audit | 12 |
| Compliance | 18 |
| OWASP | 1–13 |
| Supply Chain | 9, 10 |
| Plugin Security | 19 |
| Marketplace Security | 20 |

---

## Expected Outputs

| Artifact | Description |
|----------|-------------|
| Security review report | Structured report with verdict, 20-lens summary, v2.0 dimension summary |
| Remediation plan | Ordered Priority 1–3 fixes with file and line references |

---

## Quality Gates

- [ ] Platform constitution loaded before review (Step 2)
- [ ] `detect-secrets scan` reports zero findings
- [ ] `pip-audit` reports zero critical/high vulnerabilities
- [ ] Every database query verified to include tenant isolation
- [ ] Every new API key or token confirmed to come from `secrets-service`
- [ ] Three-control separation (RBAC/Policy/Secrets) confirmed intact
- [ ] No direct service-to-service HTTP calls introduced for denied pairs
- [ ] All applicable Architecture v2.0 dimensions reviewed

---

## Completion Checklist

```
[ ] Platform constitution loaded
[ ] PR diff fetched and security zones classified
[ ] Automated pre-checks complete
[ ] Lenses 1–13 executed (or N/A documented)
[ ] Lenses 14–20 executed (or N/A documented)
[ ] Architecture v2.0 dimension summary produced
[ ] Remediation plan produced with Priority 1–3
[ ] Verdict issued (APPROVE | REQUEST CHANGES | NEEDS DISCUSSION)
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Skip platform constitution loading (Step 2)
- Accept a credential finding as "acceptable" without explicit written approval
- Skip the tenant isolation check because "it was checked before"
- Ignore a critical or high CVE because "it is unlikely to be exploited"
- Accept an empty `detect-secrets` allowlist without verifying each entry
- Mark the review as PASS if any BLOCKER finding is unresolved
- Merge RBAC, Policy, or Secrets logic into a single module
- Accept a Vault bypass as a "temporary" solution
- Skip the three-control separation check
- Approve a gate bypass under any circumstances
- Modify the Constitution's security principles
