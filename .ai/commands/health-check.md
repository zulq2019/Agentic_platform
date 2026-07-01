# health-check.md

**Command:** `health-check`  
**Version:** 1.0 — Engineering Governance Auditor  
**Skill authority:** `.ai/skills/health-check/SKILL.md` (full pipeline)  
**Applies to:** All repositories — mandatory before release gates, PI kickoff, and quarterly governance reviews

---

## Purpose

Use this command to evaluate **overall repository engineering health**. Acts as the Engineering Quality Gate.

`/health-check` is a **read-only** governance audit. It never creates, edits, or deletes files. It auto-discovers architecture documents, engineering docs, tests, skills, CI/CD, contracts, and repository structure via glob/search with graceful degradation. Missing documents are reported — the audit never fails because a document is absent.

Evaluates **35 governance checks** across architecture, implementation, documentation, testing, security, performance, governance, and repository hygiene. Produces **8 scores (0–100)**, **four risk tiers**, and **seven reports**.

### Invocation

```
/health-check
/health-check PI-02
/health-check PI-02-Platform-Core
/health-check --quick
```

| Mode | Behaviour |
|------|-----------|
| `/health-check` | Full audit — all checks, all reports, all scores |
| `/health-check <PI-ID>` | Full audit with PI-scoped progress and story completion |
| `/health-check --quick` | Abbreviated — top scores, Critical/High risks, summary report only |

See `.ai/skills/health-check/SKILL.md` for the complete authoritative workflow.

---

## Inputs

All inputs are **auto-discovered**. No manual path substitution required.

| Category | Discovery method | Required |
|----------|------------------|----------|
| Architecture documents | `find` / `rg` for `CONSTITUTION.md`, `ARCHITECTURE.md`, `PLATFORM_*.md`, `ARCHITECTURE_BASELINE_V2.md` | Auto — report if missing |
| Engineering roadmap | `find` under `implementation-roadmap/` | Auto — report if missing |
| Contract schemas | `find` under `contracts/` | Auto — report if missing |
| Tests | `find` test files and test directories | Auto |
| CI/CD | `.github/workflows/` | Auto — report if missing |
| Skills & commands | `.ai/skills/`, `.ai/commands/` | Auto |
| Repository structure | `find` top-level directories | Auto |
| Dependencies | `package.json`, `pyproject.toml`, lock files | Auto |

**Optional scope input:**

```
{pi_id} = e.g. PI-02 or PI-02-Platform-Core (scopes story completion and PI progress)
```

---

## Preconditions

- [ ] Repository is readable (git or filesystem access)
- [ ] Read-only tools available: `read`, `bash`, `grep`, `rg`, `git`, `find`
- [ ] No write permissions required or used

---

## Execution Steps

### Step 1 — Automatic repository discovery

See `.ai/skills/health-check/SKILL.md` Step 1. Produce Discovery Inventory table. Report gaps — do not abort.

### Step 2 — Resolve audit scope

- **Full:** all 35 checks, entire repository
- **PI-scoped:** resolve PI folder from `{pi_id}`, scope checks 4–5 to that PI
- **Quick:** abbreviated discovery, summary checks, Critical/High risks only

### Step 3 — Execute 35 governance checks

Evaluate each check; mark **PASS / WARN / FAIL / N/A**:

| # | Check |
|---|-------|
| 1 | Architecture |
| 2 | Repository Structure |
| 3 | Documentation |
| 4 | PI Progress |
| 5 | Story Completion |
| 6 | Dependencies |
| 7 | Architecture Compliance |
| 8 | Platform Contract Compliance |
| 9 | Code Quality |
| 10 | DDD Compliance |
| 11 | SOLID Compliance |
| 12 | Hexagonal Architecture |
| 13 | Security |
| 14 | Performance |
| 15 | Regression Coverage |
| 16 | Test Coverage |
| 17 | Observability |
| 18 | Governance |
| 19 | Audit |
| 20 | Versioning |
| 21 | Configuration |
| 22 | Metadata |
| 23 | Marketplace |
| 24 | Provider Model |
| 25 | Execution Profiles |
| 26 | Workflow Consistency |
| 27 | Prompt Library |
| 28 | Skill Library |
| 29 | README Consistency |
| 30 | Broken Links |
| 31 | Dead Documents |
| 32 | Technical Debt |
| 33 | Duplicate Documents |
| 34 | Repository Hygiene |
| 35 | Governance Audit (composite) |

### Step 4 — Calculate scores (0–100)

| Score | Primary inputs |
|-------|----------------|
| Overall Health Score | All applicable checks |
| Architecture Score | Checks 1, 7, 10–12, 22, 24–26 |
| Implementation Score | Checks 4, 5, 9, 20–21 |
| Documentation Score | Checks 3, 29–31, 33 |
| Testing Score | Checks 15–16 |
| Security Score | Checks 13, 19, 34 |
| Performance Score | Checks 14, 17 |
| Repository Quality Score | Checks 2, 6, 28, 32, 34 |

### Step 5 — Classify risks

Produce **Critical / High / Medium / Low** risk tiers with evidence, impact, and recommendations.

### Step 6 — Produce seven reports

1. Engineering Health Report (main output)
2. Risk Matrix
3. Repository Scorecard
4. Architecture Drift Report (skip in `--quick`)
5. Missing Documentation Report
6. Implementation Readiness
7. Release Readiness

---

## Expected Outputs

| Artifact | Description |
|----------|-------------|
| Engineering Health Report | Executive summary, scores, 35-check table, recommendations |
| Risk Matrix | Tiered risks with evidence and remediation |
| Repository Scorecard | Maturity dimensions, strengths, weaknesses |
| Architecture Drift Report | Documented vs actual structure and patterns |
| Missing Documentation Report | Gap list with priority and recommended creation order |
| Implementation Readiness | PI status, blockers, enablers |
| Release Readiness | Gate checklist and verdict |

---

## Quality Gates

- [ ] Discovery inventory completed with graceful degradation
- [ ] All 35 checks evaluated (or N/A documented with reason)
- [ ] All 8 scores calculated
- [ ] Risk matrix includes every FAIL and significant WARN
- [ ] Missing documents listed — audit did not abort on gaps
- [ ] Release Readiness verdict consistent with Critical risk count
- [ ] No files were modified

---

## Completion Checklist

```
[ ] Repository discovery completed
[ ] Audit scope resolved (full / PI-scoped / quick)
[ ] 35 checks evaluated with PASS/WARN/FAIL/N/A
[ ] 8 scores calculated (0–100)
[ ] Risk tiers populated with recommendations
[ ] Engineering Health Report produced
[ ] Risk Matrix produced
[ ] Repository Scorecard produced
[ ] Architecture Drift Report produced (or skipped for --quick)
[ ] Missing Documentation Report produced
[ ] Implementation Readiness produced
[ ] Release Readiness produced with verdict
[ ] Next Priorities listed (max 5)
[ ] Confirmed: no files created, edited, or deleted
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Create, edit, or delete any repository file
- Run destructive git commands
- Hardcode project-specific paths instead of using discovery
- Fail the audit because a document is missing — report it instead
- Invent findings without evidence from search or file reads
- Conflate this with PR-scoped review (`aep-review`, `security-review`, etc.)
- Mark RELEASE READY when Critical risks remain open
- Skip risk classification for any FAIL result
