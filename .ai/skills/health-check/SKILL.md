---
name: health-check
description: |
  When the engineer types /health-check, /health-check <PI-ID>, or /health-check --quick,
  perform a read-only Engineering Governance Audit of the entire repository. Auto-discovers
  architecture documents, engineering docs, tests, CI/CD, skills, contracts, and repository
  structure via glob/search with graceful degradation. Evaluates 35 governance dimensions
  (Architecture, Repository Structure, Documentation, PI Progress, Story Completion,
  Dependencies, Architecture Compliance, Platform Contract Compliance, Code Quality, DDD,
  SOLID, Hexagonal Architecture, Security, Performance, Regression Coverage, Test Coverage,
  Observability, Governance, Audit, Versioning, Configuration, Metadata, Marketplace,
  Provider Model, Execution Profiles, Workflow Consistency, Prompt Library, Skill Library,
  README consistency, Broken Links, Dead Documents, Technical Debt, Duplicate Documents,
  Repository Hygiene). Produces scored reports (0–100), risk tiers, and seven deliverables:
  Engineering Health Report, Risk Matrix, Repository Scorecard, Architecture Drift Report,
  Missing Documentation Report, Implementation Readiness, and Release Readiness. Never
  modifies files — analysis only.
allowed-tools: |
  read, bash, grep, rg, git, find
---

# Health Check — Engineering Governance Auditor

**Version:** 1.0  
**Mode:** Read-only — never create, edit, or delete files  
**Scope:** Repository-agnostic with architecture-aware evaluation when v2 docs exist

<purpose>
`/health-check` is the Engineering Quality Gate for any repository. It evaluates overall
engineering health across architecture, implementation, documentation, testing, security,
performance, governance, and repository hygiene. Unlike PR-scoped review skills
(`aep-review`, `security-review`, `performance-review`, `regression-review`), this skill
audits the **entire repository state** — not a single diff.

This skill never changes code. It discovers what exists, evaluates what is missing or
degraded, scores each dimension, and produces actionable reports with prioritised
recommendations. Missing documents are reported — the skill never fails because a
document is absent.
</purpose>

---

## When To Activate

```
/health-check
/health-check PI-02
/health-check PI-02-Platform-Core
/health-check --quick
```

| Invocation | Behaviour |
|------------|-----------|
| `/health-check` | Full audit — all 35 checks, all seven reports, all scores |
| `/health-check <PI-ID>` | Full audit scoped to one PI (e.g. `PI-02`, `PI-02-Platform-Core`) |
| `/health-check --quick` | Abbreviated audit — top-level scores, Critical/High risks only, summary reports |

**Use this skill when:**
- Starting a new sprint or PI — baseline engineering health
- Before a release — release readiness gate
- After major refactors — detect architecture drift and documentation gaps
- Onboarding — understand repository maturity and gaps
- Quarterly governance review — track improvement over time

---

## Step 1 — Automatic Repository Discovery

**Never hardcode project names.** Discover everything via search with graceful degradation.

### 1.1 — Repository root and structure

```bash
git rev-parse --show-toplevel
git branch --show-current
git log -1 --format='%H %s %ci'
find . -maxdepth 3 -type d ! -path '*/node_modules/*' ! -path '*/.git/*' 2>/dev/null | head -80
```

Record: repo name (from directory), current branch, last commit, top-level folder layout.

### 1.2 — Architecture documents

```bash
# Platform constitution (v2 — glob, do not assume paths)
find . -iname 'PLATFORM_*.md' 2>/dev/null
find . -iname 'ARCHITECTURE_BASELINE_V2.md' 2>/dev/null
find . -iname 'CONSTITUTION.md' -o -iname 'ARCHITECTURE.md' -o -iname 'CLAUDE.md' 2>/dev/null
find . -path '*/docs/architecture/*' -name '*.md' 2>/dev/null | head -40
find . -path '*/ADR/*' -name '*.md' -o -path '*/adr/*' -name '*.md' 2>/dev/null
```

### 1.3 — Engineering documentation, roadmap, stories

```bash
find . -path '*/implementation-roadmap/*' -name '*.md' 2>/dev/null | head -60
find . -iname 'TASKS.md' -o -iname 'ROADMAP.md' -o -iname 'USER_STORIES.md' 2>/dev/null
find . -iname 'ACCEPTANCE_CRITERIA.md' -o -iname 'IMPLEMENTATION.md' -o -iname 'SPRINT_PLAN.md' 2>/dev/null
find . -iname 'DEFINITION_OF_DONE.md' -o -iname 'REPOSITORY_GUIDE.md' 2>/dev/null
```

### 1.4 — Tests and CI/CD

```bash
find . -path '*/.github/workflows/*' -name '*.yml' -o -path '*/.github/workflows/*' -name '*.yaml' 2>/dev/null
find . -name '*test*' -type f \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' \) 2>/dev/null | wc -l
find . -path '*/tests/*' -o -path '*/__tests__/*' -o -name '*.test.ts' -o -name '*.spec.ts' 2>/dev/null | head -30
rg -l "pytest|jest|vitest|unittest" --glob '*.{yml,yaml,json,toml}' 2>/dev/null | head -20
```

### 1.5 — Skills and prompt library

```bash
find . -path '*/.ai/skills/*' -name 'SKILL.md' 2>/dev/null
find . -path '*/.ai/commands/*' -name '*.md' 2>/dev/null
find . -path '*/.ai/templates/*' 2>/dev/null | head -20
find . -path '*/.ai/checklists/*' 2>/dev/null | head -20
```

### 1.6 — Contracts

```bash
find . -path '*/contracts/*' -name '*.json' -o -path '*/contracts/*' -name '*.schema.json' 2>/dev/null
ls contracts/ 2>/dev/null || echo "contracts/ not found"
```

### 1.7 — Dependencies and configuration

```bash
find . -maxdepth 2 \( -name 'package.json' -o -name 'pyproject.toml' -o -name 'requirements.txt' -o -name 'go.mod' -o -name 'Cargo.toml' \) 2>/dev/null
find . -name '.env.example' -o -name '.env.sample' -o -name 'docker-compose*.yml' 2>/dev/null
```

### 1.8 — Discovery inventory

Produce a **Discovery Inventory** table:

| Category | Found | Path(s) | Status |
|----------|-------|---------|--------|
| Platform constitution | YES/NO | {paths or "missing"} | OK / GAP |
| Repository constitution | YES/NO | {paths} | OK / GAP |
| Architecture baseline v2 | YES/NO | {paths} | OK / GAP |
| PI folders | N | {paths} | OK / GAP |
| Contract schemas | N | {paths} | OK / GAP |
| CI workflows | N | {paths} | OK / GAP |
| Test files | N | {summary} | OK / GAP |
| Skills | N | {paths} | OK / GAP |
| Commands | N | {paths} | OK / GAP |

**Rule:** If any category is missing, record it in Missing Documentation Report — do not abort.

---

## Step 2 — Scope Resolution

### Full audit (`/health-check`)

Evaluate all 35 checks across the entire repository.

### PI-scoped audit (`/health-check PI-02`)

1. Resolve PI folder: search `**/implementation-roadmap/*PI-02*/` or match `PI-02` in folder names.
2. Read PI-specific: `USER_STORIES.md`, `ACCEPTANCE_CRITERIA.md`, `IMPLEMENTATION.md`, `SPRINT_PLAN.md`, `CAPABILITIES.md`, `PROMPT_MAPPING.md` if present.
3. Scope story completion and PI progress to that PI; all other checks remain repository-wide.

### Quick audit (`/health-check --quick`)

- Run discovery (Step 1) in abbreviated form
- Evaluate checks at summary level only (no deep file reads beyond top-level docs)
- Produce: Overall Health Score + 8 dimension scores, Critical/High risks only, one-page Engineering Health Report
- Skip: Architecture Drift deep analysis, broken-link crawl, duplicate-document deep scan

---

## Step 3 — Execute 35 Governance Checks

For each check, assign status: **PASS** | **WARN** | **FAIL** | **N/A**

Scoring guidance per check:
- **PASS** — meets or exceeds expected standard
- **WARN** — partially met, gaps that should be addressed soon
- **FAIL** — materially missing or violated
- **N/A** — not applicable to this repository type (document why)

---

### Check 1 — Architecture

**Evaluate:** Presence and coherence of architecture docs; service boundaries documented; event-driven patterns described; deployment model clear.

**Signals:**
- `ARCHITECTURE.md`, `REFERENCE_ARCHITECTURE.md`, ADRs exist and cross-reference
- Diagrams or mermaid flows for multi-step processes
- Clear container/service boundaries

**If v2 docs present:** Cross-check against `ARCHITECTURE_BASELINE_V2.md` and `PLATFORM_PRIMITIVES.md`.

---

### Check 2 — Repository Structure

**Evaluate:** Folder layout matches documented conventions; separation of concerns (agents, tools, contracts, infra, docs); no orphan directories.

**Signals:**
```bash
find . -maxdepth 2 -type d ! -path '*/.git/*' 2>/dev/null
rg -l "platform/|containers/|agents/|tools/|contracts/" --glob 'README.md' 2>/dev/null
```

Compare actual structure to what `ARCHITECTURE.md` or `REPOSITORY_GUIDE.md` describes.

---

### Check 3 — Documentation

**Evaluate:** README at root and key folders; API docs; onboarding guides; inline doc coverage on public interfaces.

**Signals:** Root `README.md`, per-service READMEs, `docs/` tree depth, stale dates in headers.

---

### Check 4 — PI Progress

**Evaluate:** Implementation roadmap exists; PI folders have sprint plans; milestones trackable.

**Signals:**
```bash
find . -path '*/implementation-roadmap/*' -name 'SPRINT_PLAN.md' 2>/dev/null
find . -path '*/implementation-roadmap/*' -name 'IMPLEMENTATION_STATUS.md' -o -name 'STATUS.md' 2>/dev/null
```

For PI-scoped runs: assess that PI's sprint completion vs plan.

---

### Check 5 — Story Completion

**Evaluate:** User stories defined with acceptance criteria; story status trackable; DoD referenced.

**Signals:** `USER_STORIES.md` story states (TODO/IN PROGRESS/DONE), linkage to `ACCEPTANCE_CRITERIA.md`.

---

### Check 6 — Dependencies

**Evaluate:** Lock files present; dependency manifests documented; known vulnerable patterns absent; version pinning strategy.

**Signals:**
```bash
find . -maxdepth 3 \( -name 'package-lock.json' -o -name 'poetry.lock' -o -name 'uv.lock' \) 2>/dev/null
rg "latest|\*" --glob 'requirements.txt' 2>/dev/null | head -10
```

---

### Check 7 — Architecture Compliance

**Evaluate:** Code and docs align with constitutional principles (agent-to-agent calls forbidden, orchestrator plans-only, event bus IPC, registry plug-in).

**Signals:** Search forbidden patterns from `CLAUDE.md` / `CONSTITUTION.md`:
```bash
rg "EMERGENCY_BYPASS|skip_gate|auto_approve|bypass.*gate" --glob '*.{py,ts,tsx}' 2>/dev/null | head -10
rg "orchestrator.*generateCode|agent.*\.run\(" --glob '*.{py,ts}' 2>/dev/null | head -10
```

---

### Check 8 — Platform Contract Compliance

**Evaluate:** Contract schemas exist; agents/tools validate against contracts; event envelope standard.

**Signals:**
```bash
ls contracts/ 2>/dev/null
find . -name 'validate_contract*' -o -name '*contract*test*' 2>/dev/null | head -10
```

---

### Check 9 — Code Quality

**Evaluate:** Linting config present; formatting enforced; TypeScript strict / Python type hints; CI lint stage.

**Signals:**
```bash
find . -maxdepth 3 \( -name 'eslint.config.*' -o -name '.eslintrc*' -o -name 'ruff.toml' -o -name 'pyproject.toml' \) 2>/dev/null
rg '"strict":\s*true' --glob 'tsconfig*.json' 2>/dev/null
```

---

### Check 10 — DDD Compliance

**Evaluate:** Bounded contexts identifiable; domain language consistent with glossary; aggregates and entities separated from infrastructure.

**Signals:** `PLATFORM_GLOSSARY.md`, domain folder naming, absence of infrastructure imports in domain layer (sample grep).

---

### Check 11 — SOLID Compliance

**Evaluate:** Single-responsibility modules; dependency injection patterns; interface segregation in SDKs.

**Signals:** Spot-check largest modules for god-class anti-patterns; SDK abstract interfaces vs concrete vendors.

---

### Check 12 — Hexagonal Architecture

**Evaluate:** Ports and adapters pattern; vendor SDKs in tools/ not agents/; domain core independent of frameworks.

**Signals:**
```bash
rg "import (openai|anthropic|boto3|@octokit)" --glob '**/agents/**' 2>/dev/null | head -10
```

---

### Check 13 — Security

**Evaluate:** No hardcoded secrets; RLS/tenant isolation documented; secrets vault pattern; security review skill present.

**Signals:**
```bash
rg "(api[_-]?key|password|secret)\s*=\s*['\"][^'\"]+['\"]" --glob '*.{py,ts,tsx,js}' 2>/dev/null | head -10
find . -path '*/.ai/skills/security-review/*' 2>/dev/null
```

---

### Check 14 — Performance

**Evaluate:** NFRs documented; performance review skill present; observability for latency; SLO references in acceptance criteria.

**Signals:** `performance-review` skill/command exists; SLO mentions in `ACCEPTANCE_CRITERIA.md` or `ARCHITECTURE.md`.

---

### Check 15 — Regression Coverage

**Evaluate:** Regression review skill present; contract validation in CI; backward-compatibility tests for shared zones.

**Signals:** `regression-review` skill; CI jobs running contract validation or integration tests.

---

### Check 16 — Test Coverage

**Evaluate:** Test pyramid present (unit, integration, contract); CI runs tests; coverage thresholds if configured.

**Signals:**
```bash
find . -path '*/.github/workflows/*' -exec rg -l "pytest|jest|test" {} \; 2>/dev/null
find . -name 'coverage.*' -o -name '.coveragerc' -o -name 'jest.config.*' 2>/dev/null
```

---

### Check 17 — Observability

**Evaluate:** Structured logging documented; metrics naming conventions; tracing (OTEL) references; health endpoints.

**Signals:** `rg "opentelemetry|prometheus|structured.*log|health" --glob '*.md' -i` ; health check routes in code.

---

### Check 18 — Governance

**Evaluate:** Constitution exists; ADR process documented; PR checklist; constitutional compliance checks in CI.

**Signals:** `CONSTITUTION.md`, `docs/architecture/ADR/`, PR template with compliance checklist.

---

### Check 19 — Audit

**Evaluate:** Audit trail requirements documented; auditable events defined; no silent operations pattern.

**Signals:** Audit store references in architecture; `AgentCompleted`/`AgentFailed` event patterns.

---

### Check 20 — Versioning

**Evaluate:** Semantic versioning for APIs/contracts/workflows; changelog or release notes; workflow template versioning.

**Signals:** `contracts/` version fields; `workflows/*-v*.json`; `CHANGELOG.md` or release tags.

---

### Check 21 — Configuration

**Evaluate:** Environment variables documented; `.env.example` present; no secrets in config files; config layering documented.

**Signals:**
```bash
find . -name '.env.example' -o -name '.env.sample' 2>/dev/null
rg "process\.env\.|os\.environ" --glob '*.{ts,py}' 2>/dev/null | wc -l
```

---

### Check 22 — Metadata

**Evaluate:** Metadata-driven architecture docs; Platform Object schema; `aep_meta` or equivalent patterns.

**Signals:** `METADATA_DRIVEN_ENTERPRISE_PLATFORM.md`, `platform-object.schema.json`, metadata engine paths.

---

### Check 23 — Marketplace

**Evaluate:** Marketplace/solution pack concepts documented if in scope; install flows defined.

**N/A** if repository has no marketplace scope — document why.

---

### Check 24 — Provider Model

**Evaluate:** Provider framework documented; capability-based resolution; no hardcoded provider names in agents.

**Signals:** Provider references in `ARCHITECTURE_BASELINE_V2.md`; provider registry paths.

---

### Check 25 — Execution Profiles

**Evaluate:** Execution profile concept documented; profile schema if applicable.

**N/A** if not in repository scope.

---

### Check 26 — Workflow Consistency

**Evaluate:** Workflow templates exist; state machines documented; gate enforcement described; versioned templates.

**Signals:**
```bash
find . -path '*/workflows/*' -name '*.json' 2>/dev/null
rg "gate|state.*machine|workflow" --glob 'ARCHITECTURE*.md' -i 2>/dev/null | head -5
```

---

### Check 27 — Prompt Library

**Evaluate:** `.ai/commands/` populated; commands documented in `.ai/README.md`; PROMPT_MAPPING in PI folders.

**Signals:** Command count, README listing completeness, deprecated commands marked.

---

### Check 28 — Skill Library

**Evaluate:** `.ai/skills/` populated; skills have YAML frontmatter; skills match commands; version declared.

**Signals:**
```bash
find . -path '*/.ai/skills/*' -name 'SKILL.md' -exec head -5 {} \; 2>/dev/null
```

---

### Check 29 — README Consistency

**Evaluate:** Root README matches actual structure; `.ai/README.md` lists all commands; PI READMEs consistent with parent docs.

**Signals:** Cross-check command table in `.ai/README.md` vs actual files in `.ai/commands/`.

---

### Check 30 — Broken Links

**Evaluate:** Internal markdown links resolve to existing files (sample-based for large repos).

**Signals:**
```bash
rg "\]\([^)]+\.md\)" --glob '*.md' 2>/dev/null | head -30
# For each link target, verify file exists (sample 20 links minimum in full audit)
```

---

### Check 31 — Dead Documents

**Evaluate:** Docs referencing removed features; DEPRECATED headers without replacement; orphan docs not linked from anywhere.

**Signals:** Files with `DEPRECATED` header; docs with no inbound links from README or index.

---

### Check 32 — Technical Debt

**Evaluate:** TODO/FIXME density; HACK comments; debt tracking in TASKS.md or issues.

**Signals:**
```bash
rg "TODO|FIXME|HACK|XXX" --glob '*.{py,ts,tsx,md}' 2>/dev/null | wc -l
find . -iname 'TECHNICAL_DEBT.md' -o -iname 'DEBT.md' 2>/dev/null
```

---

### Check 33 — Duplicate Documents

**Evaluate:** Same content in multiple locations; overlapping architecture docs; redundant READMEs.

**Signals:** Similar filenames (`ARCHITECTURE.md` in multiple places — check if intentional); near-duplicate section headers.

---

### Check 34 — Repository Hygiene

**Evaluate:** `.gitignore` coverage; no committed secrets; no large binaries; clean untracked state; branch protection docs.

**Signals:**
```bash
git status --short 2>/dev/null | head -20
find . -size +5M ! -path '*/.git/*' 2>/dev/null | head -10
```

---

### Check 35 — (Reserved for composite Governance Audit)

**Evaluate:** Overall governance maturity — synthesis of checks 18, 27, 28, 29. Are governance artefacts complete, current, and used?

---

## Step 4 — Score Calculation (0–100)

Compute each score from check results. Use weighted averages; **N/A checks are excluded** from that score's denominator.

### Score weights

| Score | Contributing checks | Weight emphasis |
|-------|---------------------|-----------------|
| **Overall Health Score** | All applicable checks | Equal weight across categories |
| **Architecture Score** | 1, 7, 10, 11, 12, 22, 24, 25, 26 | Architecture + patterns |
| **Implementation Score** | 4, 5, 9, 21, 20 | Delivery + code quality |
| **Documentation Score** | 3, 29, 30, 31, 33 | Docs completeness |
| **Testing Score** | 15, 16 | Test + regression |
| **Security Score** | 13, 19, 34 | Security + audit + hygiene |
| **Performance Score** | 14, 17 | Performance + observability |
| **Repository Quality Score** | 2, 6, 28, 32, 34 | Structure + deps + hygiene |

### Points per check status

| Status | Points |
|--------|--------|
| PASS | 100 |
| WARN | 60 |
| FAIL | 20 |
| N/A | excluded |

**Formula:** `Score = round(sum(points) / count(applicable_checks))`

### Score interpretation

| Range | Rating |
|-------|--------|
| 90–100 | Excellent — release-ready governance |
| 75–89 | Good — minor gaps to address |
| 60–74 | Fair — targeted remediation needed |
| 40–59 | Poor — significant governance debt |
| 0–39 | Critical — not release-ready |

---

## Step 5 — Risk Classification

Classify findings into four tiers. Every FAIL → at least Medium; constitutional violations → Critical.

### Critical Risks
- Missing `CONSTITUTION.md` or core architecture docs in an architecture-governed repo
- Hardcoded secrets detected in source
- Forbidden constitutional patterns in code (`EMERGENCY_BYPASS`, agent-to-agent calls)
- Zero test infrastructure in a production-bound codebase
- Broken contract schemas with no validation

### High Risks
- Missing contract schemas when agents/tools exist
- No CI pipeline
- PI stories without acceptance criteria
- Security review skill missing when auth/secrets code exists
- Architecture drift from v2 baseline (when v2 docs present)

### Medium Risks
- Stale or incomplete documentation
- Low test file count relative to source files
- TODO/FIXME density above threshold (>50 per 10k LOC)
- Broken internal links in key docs
- README/command table out of sync

### Low Risks
- Minor README inconsistencies
- Missing optional templates
- N/A checks that could be documented
- Cosmetic documentation gaps

For each risk, provide: **ID**, **Tier**, **Check**, **Evidence**, **Impact**, **Recommendation**.

---

## Step 6 — Produce Seven Reports

---

### Report 1 — Engineering Health Report (main output)

```
# Engineering Health Report
Repository: {name}
Branch: {branch}
Commit: {sha}
Audit mode: FULL | PI-SCOPED ({PI-ID}) | QUICK
Date: {date}
Version: health-check v1.0

## Executive Summary
{2-3 sentences on overall health and top blockers}

## Scores
| Score | Value | Rating |
|-------|-------|--------|
| Overall Health | {0-100} | {rating} |
| Architecture | {0-100} | {rating} |
| Implementation | {0-100} | {rating} |
| Documentation | {0-100} | {rating} |
| Testing | {0-100} | {rating} |
| Security | {0-100} | {rating} |
| Performance | {0-100} | {rating} |
| Repository Quality | {0-100} | {rating} |

## Check Summary (35 checks)
| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Architecture | PASS/WARN/FAIL/N/A | {one line} |
...
| 35 | Governance Audit | ... | ... |

## Discovery Inventory
{Step 1.8 table}

## Top Recommendations
1. {priority 1}
2. {priority 2}
3. {priority 3}

## Next Priorities
- {immediate action}
- {this sprint}
- {this PI}
```

---

### Report 2 — Risk Matrix

```
# Risk Matrix

| ID | Tier | Check | Finding | Impact | Recommendation |
|----|------|-------|---------|--------|----------------|
| R-001 | CRITICAL | Security | {evidence} | {impact} | {fix} |
...

## Risk Counts
| Tier | Count |
|------|-------|
| Critical | {n} |
| High | {n} |
| Medium | {n} |
| Low | {n} |
```

---

### Report 3 — Repository Scorecard

```
# Repository Scorecard

## Maturity Dimensions
| Dimension | Score | Status | Trend hint |
|-----------|-------|--------|------------|
| Architecture | {n} | 🟢/🟡/🔴 | {note} |
| Implementation | {n} | ... | ... |
| Documentation | {n} | ... | ... |
| Testing | {n} | ... | ... |
| Security | {n} | ... | ... |
| Performance | {n} | ... | ... |
| Governance | {n} | ... | ... |
| Repository Hygiene | {n} | ... | ... |

## Strengths
- {strength 1}

## Weaknesses
- {weakness 1}

## Release Readiness Indicator
{READY | NOT READY | CONDITIONAL} — {one sentence}
```

---

### Report 4 — Architecture Drift Report

**Skip in `--quick` mode.**

```
# Architecture Drift Report

## Baseline
{ARCHITECTURE_BASELINE_V2.md or ARCHITECTURE.md — which was used}

## Documented vs Actual
| Aspect | Documented | Actual | Drift |
|--------|------------|--------|-------|
| Service boundaries | {doc} | {actual} | NONE/MINOR/MAJOR |
| Folder structure | ... | ... | ... |
| Event patterns | ... | ... | ... |
| Contract set | ... | ... | ... |

## Constitutional Violations Detected
{list or "None detected"}

## ADR Coverage Gaps
{decisions made in code but not in ADRs}
```

---

### Report 5 — Missing Documentation Report

```
# Missing Documentation Report

| Document | Expected location | Priority | Notes |
|----------|-------------------|----------|-------|
| {name} | {path} | HIGH/MED/LOW | {why needed} |

## PI-Scoped Gaps (if applicable)
{PI-specific missing docs}

## Recommended Creation Order
1. {doc}
2. {doc}
```

---

### Report 6 — Implementation Readiness

```
# Implementation Readiness

## PI Status (if PI-scoped or PI folders found)
| PI | Stories defined | AC present | Sprint plan | Implementation status | Ready |
|----|-----------------|------------|-------------|----------------------|-------|
| {PI} | {n} | YES/NO | YES/NO | {%} | YES/NO |

## Blockers to Implementation
1. {blocker}

## Enablers Present
- {enabler}
```

---

### Report 7 — Release Readiness

```
# Release Readiness

## Gate Checklist
| Gate | Status | Evidence |
|------|--------|----------|
| Constitution compliance | PASS/FAIL | {evidence} |
| Contract validation | PASS/FAIL/N/A | {evidence} |
| Test suite in CI | PASS/FAIL | {evidence} |
| Security review skill | PASS/FAIL | {evidence} |
| Documentation current | PASS/FAIL | {evidence} |
| No Critical risks open | PASS/FAIL | {count} |
| Performance NFRs defined | PASS/FAIL/N/A | {evidence} |

## Verdict
RELEASE READY | NOT RELEASE READY | CONDITIONAL RELEASE

## Conditions (if conditional)
- {condition}
```

---

## Step 7 — Final Output Order

Present reports in this order:

1. **Engineering Health Report** (always — main deliverable)
2. **Risk Matrix**
3. **Repository Scorecard**
4. **Architecture Drift Report** (skip if `--quick`)
5. **Missing Documentation Report**
6. **Implementation Readiness**
7. **Release Readiness**

End with **Next Priorities** (max 5 items, ordered by impact).

---

## Completion Checklist

Before declaring the audit complete:

- [ ] Repository discovery completed with inventory table
- [ ] Scope resolved (full / PI-scoped / quick)
- [ ] All 35 checks evaluated with PASS/WARN/FAIL/N/A
- [ ] All 8 scores calculated (0–100)
- [ ] Risks classified into four tiers with recommendations
- [ ] All seven reports produced (or abbreviated set for `--quick`)
- [ ] Missing documents reported, not treated as fatal errors
- [ ] No files were created, edited, or deleted

---

## Review Rules

1. **Read-only** — never modify repository files
2. **Repository agnostic** — discover via glob/search; never assume fixed paths
3. **Graceful degradation** — missing docs → report in Missing Documentation Report
4. **Evidence-based** — every FAIL/WARN cites specific paths, counts, or grep results
5. **Architecture-aware** — when v2 docs exist, evaluate against them; when absent, use available docs
6. **Technology agnostic** — adapt checks to detected stack (Python, TypeScript, Go, etc.)
7. **No false precision** — scores are estimates from available signals; state confidence level
8. **PI scoping** — when PI specified, emphasise that PI's progress without ignoring repo-wide risks

---

## Forbidden Actions

- **Never** create, edit, or delete any file
- **Never** run destructive git commands (`reset --hard`, `clean -fd`, force push)
- **Never** hardcode project-specific paths that bypass discovery
- **Never** fail the audit because a document is missing — report it instead
- **Never** invent findings without evidence from discovery or search
- **Never** conflate this audit with PR review — health-check is repository-wide
- **Never** skip risk classification — every FAIL must appear in Risk Matrix
- **Never** approve RELEASE READY with open Critical risks
