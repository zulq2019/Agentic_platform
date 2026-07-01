---
name: implement-story
description: |
  When the engineer types /implement-story <story_ref>, execute the complete
  enterprise Principal Engineer implementation workflow for a single User Story.
  Automatically discovers repository context, analyses architecture impact,
  applies risk-based approval gates, runs mandatory Architecture Decision Engine (ADE)
  (reuse-before-build), then implements with DDD, hexagonal architecture, and
  metadata-driven patterns. One execution = one story.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq, pytest
  file: read, write
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


# implement-story

**Version:** 6.0 — Enterprise Principal Engineer implementation engine  
**Backward compatible:** All invocation forms unchanged from v4.0, v5.0, and v5.1.

<purpose>
Complete implementation workflow for a single User Story on the Agentic Engineering
Platform. Before writing production code, behave like a Principal Engineer and
Technical Lead — understand the repository, architecture, implementation context,
and engineering impact. Automatically discovers repository context, loads
architecture authorities, resolves the story, classifies risk, applies approval
gates, validates readiness, capability integrity, dependency satisfaction,
infrastructure requirements, and constitutional compliance. Engineers who skip
phases ship to an unvalidated foundation. One activation = one User Story. Never more.
</purpose>

---

## When To Activate

Trigger when the engineer types `/implement-story` followed by any story reference.
The invocation format is **unchanged** for existing users.

```
/implement-story US-01.03
/implement-story PI-02 US-02.01
/implement-story US-02.01
/implement-story Platform Object Framework
/implement-story current story
/implement-story next story
```

| Input form | Resolution behaviour |
|------------|---------------------|
| Story ID only (`US-02.01`) | Search all `docs/engineering/implementation-roadmap/*/USER_STORIES.md` |
| PI + Story ID (`PI-02 US-02.01`) | Resolve PI folder, then locate story within that PI |
| Story name (`Platform Object Framework`) | Case-insensitive title match across all PI `USER_STORIES.md` files |
| `current story` | First story marked **In Progress** or first **Planned** in target PI `STATUS.md` |
| `next story` | First **Planned** story after the last **Complete** story in `STATUS.md` + `SPRINT_PLAN.md` |

The resolved story must exist in `docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md`.

---

## Mature Execution Pipeline (v6.0)

Execute **all phases in order**. Do not write production code until Phase 9
(Implementation Plan) is complete, Phase 10 (Approval) gates are satisfied, and the
**Architecture Decision Engine (Phases 2–3)** returns **CONTINUE**.

```
Repository Discovery (Phase 0 + Phase 1 extension)
        ↓
Architecture Discovery (Phase 1)
        ↓
ADE Mode A — "Should we build this?" (Phase 2)
        ↓
ADE Mode B — Architecture Reuse — "How?" (Phase 3)
        ↓
Story Resolution (Phase 4)
        ↓
Story Readiness & Capability (Phase 5)
        ↓
Risk Assessment (Phase 6)
        ↓
Dependencies (Phase 7) → Infrastructure (Phase 7b)
        ↓
Architecture Validation (Phase 8)
        ↓
Implementation Plan (Phase 9)
        ↓
Approval (Phase 10)
        ↓
Implementation (Phase 11) — only after ADE CONTINUE + Approval
        ↓
Testing → Reviews → Documentation → Completion (Phases 12–15)
```

### Phase mapping — v6.0 ↔ v5.1

| v6 | Name | v5.1 equivalent |
|----|------|-----------------|
| 0 | Repository Discovery (common prepend) | Phase 0 |
| 1 | Architecture Discovery | Phase 2 |
| 2 | ADE Mode A | Phase 5A (should we build) |
| 3 | ADE Mode B — Architecture Reuse | Phase 5A (how to build) |
| 4 | Story Resolution | Phase 3 |
| 5 | Story Readiness & Capability | Phase 2 preserved |
| 6 | Risk Assessment | Phase 4 |
| 7 / 7b | Dependencies / Infrastructure | Phase 6 / Phase 4 preserved |
| 8 | Architecture Validation | Phase 5 preserved |
| 9 | Implementation Plan | Phase 7 |
| 10 | Approval | Phase 5 gates (after plan, before code) |
| 11–15 | Implementation → Completion | Phases 8–12 |

### Step mapping — 11-step pipeline (unchanged identifiers)

| Step | Name | v6 Phase |
|------|------|----------|
| 1 | Read Platform Constitution | Phase 1 |
| 2 | Read Repository Constitution | Phase 1 |
| 3 | Resolve Story | Phase 4 |
| 4 | Read PI Context | Phase 4 |
| 5 | Dependency Analysis | Phase 7 |
| 6 | Generate Implementation Plan | Phase 9 |
| 7 | Implement | Phase 11 |
| 8 | Generate Tests | Phase 12 |
| 9 | Run Reviews | Phase 13 |
| 10 | Update Documentation | Phase 14 |
| 11 | Generate Summary & Handoff | Phase 15 |

---

## Output Format

Report progress concisely throughout execution. **Never overwhelm** — highlight
only these fields in each progress report:

```
Current Phase:     {phase number and name}
Progress:          {1-line status — what was completed or is in progress}
Risks:             {LOW / MEDIUM / HIGH — or NONE if not yet classified}
Approval Status:   {AUTO-CONTINUE / AWAITING CONFIRMATION / STOPPED — AWAITING APPROVAL}
ADE:        {CONTINUE / STOP — RFC / PENDING — or N/A before ADE (Phases 2–3)}
Reuse Score:       {0-100 — or N/A before ADE (Phases 2–3)}
Next Action:       {single concrete next step}
```

Do not dump full document contents, long file lists, or repeated context in
progress reports. Reserve detail for phase-specific output blocks defined below.

---

## Engineering Principles

Behave as a **Principal Engineer + Technical Lead**, never a code generator.

| Role | Behaviour |
|------|-----------|
| **Principal Engineer** | Understand blast radius before coding; challenge scope creep; enforce constitutional compliance; recommend alternatives when risk is HIGH |
| **Software Architect** | Respect bounded contexts, contracts, and event-mediated communication; validate against ADRs; produce Architecture Review for HIGH-risk stories |
| **Platform Engineer** | Prefer metadata-driven, configurable primitives over bespoke code; validate Platform Object envelope and contract schemas at boundaries |
| **Technical Lead** | Sequence work correctly; ensure tests and documentation ship with code; produce actionable handoff for reviewers |

**Mission:** Before writing production code, understand repository, architecture,
implementation context, and engineering impact. Run Architecture Decision Engine (ADE) (ADE (Phases 2–3))
to validate reuse paths. Only begin coding after ADE CONTINUE (Phases 2–3) and Phase 10
approval requirements are satisfied.

---

## Quality Gates

Every story must pass these gates before Phase 12 (Completion):

| Gate | Check |
|------|-------|
| **Architecture Compliance** | No constitutional violations (Phase 8 + Phase 13 Architecture Review) |
| **Platform Contracts** | All payloads validate against `contracts/*.schema.json` at boundaries |
| **Metadata Driven Principles** | Platform Objects use `aep_meta` envelope; no hardcoded business rules |
| **Config over Customization** | Business logic, tenant rules, workflow definitions from configuration/metadata |
| **Composition over Hardcoding** | Reuse primitives, registries, extension points — no bespoke forks |
| **Reuse before Build** | ADE (Phases 2–3) — prefer reuse, configuration, composition, metadata over new services |
| **Observability** | OTEL traces, Prometheus metrics, structured logs on all public domain methods |
| **Auditability** | All agent actions and state changes produce auditable events |
| **Security** | No credentials in code; `tenant_id` in every query; input validated at boundaries |
| **Performance** | No unbounded queries; indexes on tenant-scoped columns; Kafka offset after success |
| **Maintainability** | Type hints, no TODO/FIXME in production paths, hexagonal layers respected |
| **Extensibility** | New capabilities via registries and contracts — no orchestrator modification |

---

## Workflow Position

```
implement-story → generate-tests → regression-review → aep-review
    → security-review (optional) → performance-review (optional) → release-story
```

This skill is the **single implementation entry point**. Do not write code before
completing Phases 1–9, passing ADE CONTINUE (Phases 2–3), and satisfying
Phase 10 approval gates. Do not proceed to `generate-tests` until Phase 15 handoff
is produced.

---

## Substitutions Required

Before executing, resolve these substitutions from the story reference and context documents:

```
{story_id}      = the resolved story ID, e.g. US-02.01
{story_title}   = human-readable title from USER_STORIES.md
{PI}            = the PI folder the story belongs to, e.g. PI-02-Metadata-Engine
{PI_SHORT}      = shorthand prefix, e.g. PI-02
{service_name}  = the service this story implements, e.g. metadata-engine
{target_folder} = source path, e.g. src/shared/aep_meta/ or src/platform/services/metadata-engine/
{CAP-XX}        = the capability this story belongs to, e.g. CAP-03
```

### PI folder resolution

When the engineer supplies a PI shorthand (`PI-02`), resolve to the v2 folder name:

```bash
ls docs/engineering/implementation-roadmap/ | rg "^{PI_SHORT}"
# PI-01 → PI-01-Platform-Core
# PI-02 → PI-02-Metadata-Engine
# PI-03 → PI-03-Provider-Framework
# PI-04 → PI-04-Workflow-Framework
# PI-05 → PI-05-Execution-Framework
# PI-06 → PI-06-Studio-Framework
# PI-07 → PI-07-Platform-Services
# PI-08 → PI-08-Solution-Packs
# PI-09 → PI-09-Platform-UX
# PI-10 → PI-10-General-Availability
```

---

### Repository targets (extends Phase 0)

**Skill-specific discovery after common Phase 0. Never fail if optional docs are missing.**

### Discovery targets

| Category | Locations | Required |
|----------|-----------|----------|
| Architecture docs | `docs/architecture/`, `ARCHITECTURE.md`, `ARCHITECTURE_BASELINE_V2.md` | Mandatory core; optional extras noted |
| Repo constitution | `CONSTITUTION.md`, `CLAUDE.md` | Mandatory |
| Engineering roadmap | `docs/engineering/implementation-roadmap/`, `docs/product/ROADMAP.md` | Mandatory roadmap; ROADMAP optional |
| Current PI / sprint / story | `{PI}/STATUS.md`, `{PI}/SPRINT_PLAN.md` | After story resolution |
| Skills | `.ai/skills/` | Discover available skills |
| Prompt library | `.ai/commands/` | Discover available commands |
| Contracts | `contracts/` | If story produces/consumes events or objects |
| Blueprints | `docs/architecture/`, PI `diagrams/` | Optional |
| Repo structure | `src/`, `platform/`, `agents/`, `tools/`, `workflows/`, `infra/` | Discover layout |

```bash
# Repository structure discovery
ls -la
ls docs/architecture/ 2>/dev/null || echo "docs/architecture/ NOT FOUND (optional)"
ls docs/engineering/implementation-roadmap/ 2>/dev/null
ls .ai/skills/ .ai/commands/ 2>/dev/null
ls contracts/ 2>/dev/null
ls src/ platform/ agents/ tools/ workflows/ infra/ 2>/dev/null
```

### Discovery output

```
Repository discovery:
  Architecture docs:    {N} found, {N} optional missing
  Constitution:         FOUND / NOT FOUND
  Roadmap:              FOUND / NOT FOUND (optional)
  Skills:               {list .ai/skills/ names}
  Commands:             {list .ai/commands/ names}
  Contracts:            {N} schemas found
  Repo structure:       {top-level dirs discovered}
  Status:               READY / BLOCKED (only if mandatory constitution missing)
```

**Stop condition:** Only stop if `CONSTITUTION.md` or `ARCHITECTURE.md` cannot be
read. Optional docs (ROADMAP, blueprints, extra PLATFORM_*.md) — note and continue.

---

## Phase 1 — Architecture Discovery

**Load architecture authorities when available. Extend Steps 1–2.**

### Step 1 — Platform Constitution

Load all available `PLATFORM_*.md` and metadata-driven architecture docs:

```bash
# Platform constitution — load all PLATFORM_*.md when present
ls docs/architecture/PLATFORM_*.md 2>/dev/null
cat docs/architecture/PLATFORM_PRIMITIVES.md
cat docs/architecture/PLATFORM_CONTRACTS.md
cat docs/architecture/PLATFORM_META_MODEL.md
cat docs/architecture/PLATFORM_UX_MODEL.md
cat docs/architecture/PLATFORM_GLOSSARY.md
cat docs/architecture/METADATA_DRIVEN_ENTERPRISE_PLATFORM.md
cat docs/architecture/ARCHITECTURE_BASELINE_V2.md
```

**Stop condition:** If `ARCHITECTURE_BASELINE_V2.md` or `PLATFORM_PRIMITIVES.md`
cannot be read for Architecture v2.0 stories, stop and report which document is
missing. Other `PLATFORM_*.md` files — note if missing and continue.

### Step 2 — Repository Constitution

```bash
cat CONSTITUTION.md
cat ARCHITECTURE.md
cat CLAUDE.md
cat docs/architecture/ADR/DECISIONS.md   # ADR authority (root DECISIONS.md is a redirect stub)
cat docs/product/ROADMAP.md 2>/dev/null || echo "ROADMAP.md optional — not found"
```

**Stop condition:** If `CONSTITUTION.md` or `ARCHITECTURE.md` cannot be read,
stop immediately and report exactly which document is missing.

---

## Phase 2 — Architecture Decision Engine — Mode A ("Should we build this?")

**Mandatory for every story. Executes immediately after Phase 1 (Architecture Discovery)
and before Phase 3 (Architecture Reuse). Uses `{story_ref}` from invocation; full story
context is confirmed in Phase 4.**

### Purpose (Evaluate Requirement)

Determine whether the requested capability **should be implemented at all**, or whether
it should be realized through existing Platform Primitives, metadata, configuration,
composition, workflows, policies, providers, or plugins.

This is an **Architecture Decision** — not an AI brainstorming step. Mode A answers:
**"Should this exist as new code?"**

### Quality principle

**Prefer:** Reuse, Configuration, Composition, Metadata  
**Over:** New Services, New Frameworks, Hardcoded Logic, New Microservices

### Discovery commands

```bash
find . \( -iname 'PLATFORM_PRIMITIVES.md' -o -iname 'PLATFORM_META_MODEL.md' -o -iname 'PLATFORM_CONTRACTS.md' \) ! -path '*/.git/*' 2>/dev/null
rg -i "{story_ref keywords}" docs/ src/ contracts/ --glob "*.md" --glob "*.py" --glob "*.json" 2>/dev/null | head -40
```

### Mode A — five mandatory questions

| # | Question | Evidence required |
|---|----------|-------------------|
| A1 | Does this **capability already exist**? | Services, APIs, providers, plugins, workflows, contracts, metadata |
| A2 | Can **metadata** solve it? | Platform Object model, config surfaces, tenant metadata |
| A3 | Can **configuration** solve it? | Feature flags, policy config, env-driven behaviour |
| A4 | Can **composition** of existing primitives solve it? | Registries, extension points, composed workflows |
| A5 | Does building this **violate Platform Primitives** or contracts? | `PLATFORM_PRIMITIVES.md`, `contracts/`, constitutional principles |

Per question output:

```
A{n}: {short label}
  Answer:     YES / NO / PARTIAL
  Evidence:   {paths, object names, or NONE}
```

### Mode A decision

| Outcome | Condition | Action |
|---------|-----------|--------|
| **CONTINUE** | A1–A4 show viable reuse/config/composition path **or** net-new build is justified without primitive violation; A5 = NO | Proceed to Phase 3 (Mode B) |
| **STOP — Architecture RFC** | No justified net-new path, reuse score for Mode A < 40, or A5 = YES without approved ADR | **STOP** — Architecture RFC (template in Phase 3); **no production code** |

When **STOP**, deliver RFC per Phase 3 template. Do not proceed to Phase 4+ until
engineer reviews RFC and approves a path forward.

### Mode A summary (required)

```
Architecture Decision Engine — Mode A:
  Story ref:              {story_ref}
  Should we build this?:  YES / NO / PARTIAL — {rationale}
  Existing capability:      {found / not found}
  Metadata path:          {viable / not viable}
  Configuration path:     {viable / not viable}
  Composition path:       {viable / not viable}
  Primitive compliance:   COMPLIANT / VIOLATION RISK
  Mode A decision:        CONTINUE / STOP — ARCHITECTURE RFC
```

---

## Phase 3 — Architecture Reuse (ADE Mode B — "How should we build it?")

**Mandatory when Mode A = CONTINUE. Executes before Phase 4 (Story Resolution).**

### Purpose (Reuse Analysis → Architecture Compliance → Decision)

If the capability must be built or extended, determine **how** using existing platform
building blocks. Mode B answers: **"How should we realize this with minimum new surface area?"**

### Mode B — six mandatory questions

| # | Question | Map to |
|---|----------|--------|
| B1 | Which **Platform Objects**? | Studios, Capabilities, Resources, Artifacts, metadata envelope |
| B2 | Which **Providers**? | Provider Framework, provider registry, adapters |
| B3 | Which **Workflows**? | Workflow templates, state machines, orchestration |
| B4 | Which **Policies**? | Policy Engine, RBAC, tenant policy configuration |
| B5 | Which **Execution Profiles**? | Runtime profiles, model routing boundaries |
| B6 | Which **APIs**? | Existing HTTP/event surfaces to extend vs new endpoints |

Per question output:

```
B{n}: {short label}
  Answer:     {specific names / NONE / NEW REQUIRED}
  Evidence:   {paths, contract names, service names}
  Reuse:      {what to reuse — or justification for new}
```

### Architecture Reuse Score (0–100)

| Score | Meaning |
|-------|---------|
| 80–100 | Fully realizable via existing objects, metadata, composition |
| 50–79 | Partial reuse — bounded new code within existing boundaries |
| 20–49 | Limited reuse — RFC recommended before planning |
| 0–19 | No viable reuse — **STOP** and RFC mandatory |

Score B1–B6: full reuse = ~17 pts each; partial = ~8; new required = 0. Round average.
A5 primitive violation caps maximum at 49.

### Combined ADE decision (Mode A + Mode B)

| Outcome | Condition | Action |
|---------|-----------|--------|
| **CONTINUE** | Mode A = CONTINUE, Reuse Score ≥ 50, primitive compliance OK | Proceed to Phase 4 — list reused Platform Objects in ADE Summary |
| **STOP — Architecture RFC** | Mode A STOP, Reuse Score < 50, or unresolved primitive/contract violation | **STOP** — RFC below; no Phase 9+ planning or code |

### Architecture RFC template (when STOP)

Write to `docs/architecture/rfc/RFC-{story_id}-{slug}.md` or deliver inline:

```
## Architecture RFC: {story_id or story_ref} — {title}

### Business Requirement
### Problem Statement
### Existing Platform Capabilities
### Gap Analysis
### Alternative Solutions
### Recommended Architecture
### Affected Platform Objects
### Risks
### Migration Strategy
### Recommendation
```

### Architecture Decision Engine — Summary (required)

Produce after Phase 2 + Phase 3 for every story:

```
Architecture Decision Engine Summary:
  Story ref:                    {story_ref}
  Mode A — Should we build?:    {YES/NO/PARTIAL + decision}
  Mode B — How to build:        {reuse map from B1–B6}
  Architecture Reuse Score:     {0-100} — {justification}
  Configuration vs Code:        CONFIGURATION / CODE / HYBRID
  Composition Recommendation:   {what to compose — or NONE}
  Platform Objects Reused:      {list — or NONE}
  Architecture Compliance:      COMPLIANT / VIOLATION RISK
  Final Recommendation:         CONTINUE / STOP — ARCHITECTURE RFC REQUIRED
```

Include in progress reports:

```
ADE:               {CONTINUE / STOP — RFC}
Reuse Score:       {0-100}
```

**Only if ADE = CONTINUE** may the pipeline proceed to Story Resolution, Risk Assessment,
Dependencies, Implementation Plan, Approval, and Implementation.

---


## Phase 4 — Story Resolution (Step 3)

**Resolve `{story_id}`, `{story_title}`, and `{PI}` before story readiness validation.**

### Resolution algorithm

```bash
# 1. If engineer passed PI shorthand + story ID
#    e.g. /implement-story PI-02 US-02.01
#    → {PI} = PI-02-Metadata-Engine, {story_id} = US-02.01

# 2. If engineer passed story ID only
rg "^## {story_id}" docs/engineering/implementation-roadmap/*/USER_STORIES.md -l

# 3. If engineer passed story name (fuzzy title match)
rg -i "{story_name}" docs/engineering/implementation-roadmap/*/USER_STORIES.md -B 1

# 4. If engineer passed "current story"
cat docs/engineering/implementation-roadmap/{PI}/STATUS.md

# 5. If engineer passed "next story"
cat docs/engineering/implementation-roadmap/{PI}/STATUS.md
rg "{story_id}" docs/engineering/implementation-roadmap/{PI}/SPRINT_PLAN.md -A 5
```

### Locate all PI docs

After resolution, load the complete PI execution context (Step 4):

```bash
cat docs/engineering/implementation-roadmap/{PI}/README.md
cat docs/engineering/implementation-roadmap/{PI}/OBJECTIVES.md
cat docs/engineering/implementation-roadmap/{PI}/CAPABILITIES.md
cat docs/engineering/implementation-roadmap/{PI}/FEATURES.md
cat docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md
cat docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md
cat docs/engineering/implementation-roadmap/{PI}/IMPLEMENTATION.md
cat docs/engineering/implementation-roadmap/{PI}/API_SPEC.md
cat docs/engineering/implementation-roadmap/{PI}/DATA_MODEL.md
cat docs/engineering/implementation-roadmap/{PI}/TESTING.md
cat docs/engineering/implementation-roadmap/{PI}/PROMPT_MAPPING.md
cat docs/engineering/implementation-roadmap/{PI}/SPRINT_PLAN.md
cat docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md
cat docs/engineering/implementation-roadmap/{PI}/REVIEW_CHECKLIST.md
cat docs/engineering/implementation-roadmap/{PI}/STATUS.md
cat docs/engineering/implementation-roadmap/{PI}/CHANGELOG.md
cat docs/engineering/implementation-roadmap/{PI}/METRICS.md

ls contracts/
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
cat contracts/tool-contract.schema.json
cat contracts/task-schema.schema.json
cat contracts/memory-schema.schema.json
cat contracts/platform-object.schema.json    # v2 — Platform Object envelope

ls src/{target_folder}/ 2>/dev/null || ls src/shared/ src/platform/services/
```

### Resolution output (required before Story Readiness)

```
Story reference:   {what the engineer typed}
Story ID:          {story_id}
Story title:       {story_title}
PI:                {PI}
PI README:         docs/engineering/implementation-roadmap/{PI}/README.md
PI docs loaded:    Objectives, Capabilities, AC, Dependencies, Sprint, DoD,
                   Testing, API Spec, Data Model, Review Checklist, STATUS,
                   CHANGELOG, METRICS
Resolution:        FOUND / AMBIGUOUS / NOT FOUND
```

**STOP if Resolution = NOT FOUND or AMBIGUOUS.** List candidate matches and ask the
engineer to disambiguate. Do not guess.

**Stop condition:** If the PI's `README.md` cannot be read, stop and report.

---

## Phase 5 — Story Readiness

**Validate before ANY other work. This phase has hard STOP conditions.**

### Story Validation

Confirm all of the following in order:

1. The story ID exists in `USER_STORIES.md`
2. The story follows the `As a / I want / so that` format
3. The story references exactly one Capability (`Capability: CAP-XX`)
4. The story references exactly one Sprint (`Sprint: N`)
5. An entry for this story ID exists in `ACCEPTANCE_CRITERIA.md`
6. Every criterion in `ACCEPTANCE_CRITERIA.md` for this story is written in Given/When/Then format
7. Every "Then" clause is observable and testable — not subjective ("works correctly" = FAIL)
8. The Story-Level Gate section exists in `DEFINITION_OF_DONE.md`

Output exactly this block:

```
Story ID:        {story_id}
Story title:     {title}
Capability:      {CAP-XX} — {name}
Sprint:          {N}
AC count:        {N} criteria found
DoD gate:        EXISTS / MISSING
Status:          READY / BLOCKED
```

**STOP if Status = BLOCKED.** List every missing or invalid item before stopping.
Do not continue to Phase 6 until Status = READY.

### Capability Validation

Cross-reference `CAPABILITIES.md` for the capability this story belongs to:

1. The capability section (`## CAP-XX`) exists in `CAPABILITIES.md`
2. The capability section contains technical contract content — not a one-line description
3. Required contract schemas are identified (cross-reference `contracts/`)
4. Dependencies between capabilities are documented

```bash
rg "^## {CAP-XX}" docs/engineering/implementation-roadmap/{PI}/CAPABILITIES.md
```

**STOP if the capability section is missing or incomplete.** A story cannot be
implemented against a capability with no technical specification.

---

## Phase 6 — Risk Assessment

**Classify story risk after Story Readiness. Principal Engineer behaviour required.**


**Classify story risk before planning or coding. Principal Engineer behaviour required.**

### Risk classification

| Risk | Indicators | Examples |
|------|------------|----------|
| **LOW** | Docs, tests, internal refactor, cleanup, comments, dev tooling | README update, unit test additions, lint fixes, internal module rename |
| **MEDIUM** | New services, providers, workflow, APIs, DB, plugins, config engine | New FastAPI service, provider adapter, workflow template, Alembic migration, plugin slot |
| **HIGH** | Platform Object, contracts, metadata engine core, execution engine, security/auth/authz, multi-tenancy, public APIs, breaking schema | `platform-object.schema.json` change, new contract schema, auth middleware, tenant isolation model, breaking API version |

### Classification output

```
Architecture Impact Analysis:
  Story:             {story_id} — {story_title}
  Risk level:        LOW / MEDIUM / HIGH
  Rationale:         {1-3 sentences — which indicators triggered this level}
  Affected areas:    {list components, services, contracts, or NONE}
  Breaking changes:  YES / NO — {brief description or NONE}
```

### Architecture Review template (HIGH risk only)

When Risk level = **HIGH**, produce this review **before** any implementation code:

```
## Architecture Review: {story_id} — {story_title}

### Business Impact
{who is affected, what capability is enabled, what happens if we defer}

### Architecture Impact
{which primitives, containers, contracts, or cross-cutting concerns change}

### Affected Components
{services, agents, tools, contracts, infra — with ownership}

### Dependencies
{upstream/downstream stories, capabilities, external systems}

### Breaking Changes
{schema, API, event envelope, or behavioural breaks — or NONE}

### Migration Strategy
{how existing consumers migrate — or N/A if additive only}

### Rollback Strategy
{deployment order, feature flags, migration downgrade — or N/A}

### Risks
{technical, tenancy, performance, security risks with likelihood}

### Alternative Designs
{at least one alternative considered with trade-offs}

### Recommendation
{proceed / proceed with conditions / defer / split story — with rationale}
```

---

## Phase 10 — Approval

**Gate implementation based on Phase 6 risk classification. Executes after Phase 9 (Implementation Plan). No code until gates pass.**

| Risk | Gate behaviour |
|------|----------------|
| **LOW** | **Auto-continue** — record risk; Approval (Phase 10) auto-continues after Implementation Plan |
| **MEDIUM** | Deliver Phase 9 Implementation Plan outline → **pause** → engineer confirmation before Phase 11 |
| **HIGH** | Deliver Architecture Review (Phase 6 template) → **STOP** → explicit approval before Phase 9–11 |

### Approval output

```
Risk Based Approval:
  Risk level:        LOW / MEDIUM / HIGH
  Approval status:   AUTO-CONTINUE / AWAITING CONFIRMATION / STOPPED — AWAITING APPROVAL
  Action required:   {NONE / "Confirm plan to proceed" / "Review Architecture Review and approve"}
```

**STOP if HIGH and no explicit approval received.**  
**STOP if MEDIUM and engineer declines or requests changes.**  
Do not proceed to Phase 11 (Implementation) until approval requirements are satisfied.

---


## Phase 7 — Dependencies (Step 5)

**Extend Phase 3 (v4). Verify all dependencies before planning begins.**

### Dependency dimensions

| Dimension | Where to check | What to verify |
|-----------|----------------|----------------|
| Architecture dependencies | `ARCHITECTURE_BASELINE_V2.md`, `CAPABILITIES.md`, ADRs | Required framework/container exists or is in scope |
| Story dependencies | `SPRINT_PLAN.md`, `STATUS.md` | Prerequisite stories marked **Complete** |
| Platform Object dependencies | `PLATFORM_PRIMITIVES.md` §3, `platform-object.schema.json` | Story extends or consumes Platform Object envelope correctly |
| Provider dependencies | `PLATFORM_META_MODEL.md`, PI `DATA_MODEL.md` | Provider Contract / Provider Registry readiness |
| Workflow dependencies | `workflows/`, PI `SEQUENCE_DIAGRAMS.md` | Workflow templates or state machines this story assumes |
| Execution Profile dependencies | `ARCHITECTURE_BASELINE_V2.md`, ADRs 012/027 | Execution Profile schema or runtime hooks required |
| Configuration dependencies | PI `IMPLEMENTATION.md`, `INFRASTRUCTURE.md` | Env vars, feature flags, tenant config surfaces |
| Plugin dependencies | `PLATFORM_PRIMITIVES.md`, PI `CAPABILITIES.md` | Extension points, registries, or plugin slots required |
| Database dependencies | PI `DATA_MODEL.md`, existing migrations | Tables, RLS policies, migration order |
| Security dependencies | `CONSTITUTION.md` SR*, PI `API_SPEC.md` | Auth, authz, secrets, tenant isolation prerequisites |
| Contract dependencies | `contracts/` | Required schemas exist and version-compatible |

```bash
rg "{story_id}" docs/engineering/implementation-roadmap/{PI}/SPRINT_PLAN.md -A 10
python -c "import aep_common; print('aep_common OK')" 2>/dev/null || echo "aep_common NOT AVAILABLE"
python -c "import aep_meta; print('aep_meta OK')" 2>/dev/null || echo "aep_meta NOT AVAILABLE (OK if story does not need it)"
ls contracts/
rg "PlatformObject|aep_meta|platform-object" docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md
```

Produce this output:

```
Dependencies check:
  Architecture:        {N} required, {N} satisfied, {N} BLOCKED
  Story dependencies:  {N} required, {N} complete, {N} BLOCKED
  Platform Objects:    {required / not applicable}
  Providers:           {required / not applicable}
  Workflows:           {required / not applicable}
  Execution Profiles:  {required / not applicable}
  Configuration:       {required / not applicable}
  Plugins:             {required / not applicable}
  Database:            {required / not applicable}
  Security:            {required / not applicable}
  Contracts:           {N} required, {N} found, {N} MISSING
  Shared libraries:    aep_common EXISTS / MISSING | aep_meta EXISTS / MISSING / N/A
  Unresolved:          {list any blocking items, or NONE}
  Status:              CLEAR / BLOCKED
```

**STOP if Status = BLOCKED.** List every unresolved dependency with the action
required to clear it.

---

## Phase 7b — Infrastructure Assessment

**Determine the minimum infrastructure required by this story's acceptance criteria.**

Evaluate each component against the story's AC — not against future stories.
Write the completed table to `docs/engineering/implementation-roadmap/{PI}/INFRASTRUCTURE.md` under a
section headed `## {story_id}`.

| Component | Required for this story | Already Exists | Action |
|-----------|------------------------|----------------|--------|
| Docker Compose | Yes/No | Yes/No/N/A | Use existing / Configure / Add service / Defer |
| PostgreSQL | Yes/No | Yes/No/N/A | Use existing / Add migration / Defer |
| Kafka | Yes/No | Yes/No/N/A | Use existing / Add topic / Defer |
| Redis | Yes/No | Yes/No/N/A | Use existing / Add key schema / Defer |
| OpenTelemetry | Yes/No | Yes/No/N/A | Use existing / Wire to service / Defer |
| Prometheus | Yes/No | Yes/No/N/A | Use existing / Add scrape config / Defer |
| Grafana | Yes/No | Yes/No/N/A | Use existing / Add dashboard / Defer |
| Vault | Yes/No | Yes/No/N/A | Use existing / Register secret / Defer |
| Kubernetes | Yes/No | Yes/No/N/A | Use existing / Add manifest / Defer |

### Infrastructure Rules

- **Only provision infrastructure required by the current story.** "May be needed
  later" = Defer.
- **Do not remove existing infrastructure** — mark it as existing and used, or note
  it is not needed for this story.
- If a required component does not exist, add only the minimum configuration needed
  for this story's AC to pass.

**STOP if a required infrastructure component cannot be determined from the AC.**
Clarify the acceptance criteria before proceeding.

---

## Phase 8 — Architecture Validation

**Check ALL of the following against `CONSTITUTION.md` and `ARCHITECTURE.md`.**

### Constitution Checks

| Principle | Check |
|-----------|-------|
| **A1** | No agent invokes another agent's module, API, or class directly |
| **A2** | `orchestrator-service` contains no specialist logic (LLM calls, code generation, scoring) |
| **A3** | New agents added via Agent Registry only — no orchestrator switch/dispatch modification |
| **A4** | No direct HTTP calls between services for business logic |
| **A5** | No service reads or writes another service's owned data store directly |
| **H2** | No flag, timeout, env var, or condition that can auto-approve a human gate |
| **SR1** | No hardcoded API keys, tokens, passwords, or connection strings |
| **SR3** | `tenant_id` in every memory query, task query, and policy check |
| **S1** | RBAC, Policy Engine, and Secrets Vault remain three separate services |
| **MI3** | No model name in agent code — `cost_class` only (low/medium/high) |

```bash
rg "from agents\." src/{target_folder}/ --include="*.py"
rg "bypass|skip_gate|auto_approve|EMERGENCY" src/{target_folder}/
rg "claude-|gpt-4|gemini-" src/{target_folder}/ --include="*.py"
rg "anthropic|openai" src/platform/orchestrator/ --include="*.py"
```

### ADR Validation

Read `docs/architecture/ADR/DECISIONS.md`. If the planned implementation would
contradict any existing ADR, STOP and report the conflict with the specific ADR
number and the conflicting design choice.

### Capability Boundary Check

Confirm all planned files belong to the service owned by `{CAP-XX}`. No implementation
logic for this capability should land in a service owned by a different capability.

Output:

```
Architecture validation:
  Constitution:  PASS / VIOLATIONS (list each with principle ID)
  ADRs:          PASS / CONFLICTS (list each with ADR number)
  Boundaries:    PASS / VIOLATIONS (list each file out of scope)
  Status:        CLEAR / BLOCKED
```

**STOP if Status = BLOCKED.** Do not write implementation code against a violated
architecture.

---

## Phase 9 — Implementation Plan (Step 6)

**Produce this plan before writing any code. Only begin coding after Phase 5
approval requirements are satisfied and ADE (Phases 2–3) decision = CONTINUE.**

The plan must reflect Architecture Decision Engine outcomes: list reused Platform Objects, metadata
configuration surfaces, and composition paths identified in ADE (Phases 2–3).

```
## Implementation Plan: {story_id} — {story_title}

### Solution Overview
{2-4 sentences: what we are building, why, and how it fits the platform}

### Architecture Decision Engine Reuse (from ADE (Phases 2–3))
{Platform Objects reused, configuration vs code choice, composition path — or N/A if RFC was required and approved}

### Design Decisions
{key choices with rationale — alternatives considered for MEDIUM/HIGH risk}

### Sequence
{ordered implementation steps — dependencies between files/modules}

### Estimated Complexity
{LOW / MEDIUM / HIGH — with brief justification}

### Estimated Effort
{rough sizing: hours or story-points equivalent — not a commitment}

### Design
{high-level design: aggregate roots, bounded context, service boundaries, event flows}
{how this story fits Architecture v2.0 primitives and metadata-driven model}

### Files to create
- {path}: {purpose and which AC it serves}

### Files to modify
- {path}: {what changes and why}

### Interfaces
{domain ports, application services, API handlers, Kafka producers/consumers}
{hexagonal: domain → application → infrastructure adapters}

### Contracts
{JSON Schema files, event envelope shapes, Platform Object envelope usage}
{NONE if story produces no new contracts}

### Package structure
{only if new packages or modules are introduced — otherwise omit}

### APIs
{new endpoints: method, path, auth dependency, purpose}
{NONE if story produces no endpoints}

### Events
{new Kafka topics/event types: topic name, producer service, consumer service}
{NONE if story produces no events}

### Database changes
{new tables, columns, indexes, and migration file path}
{NONE if story requires no schema changes}

### Configuration changes
{new environment variables — name, type, description, example value}
{NONE if no new env vars — everything configurable, no hardcoded business logic}

### Observability changes
{new Prometheus metrics, OTEL trace spans, structured log events, Grafana dashboards}
{NONE if story requires no new observability}

### Infrastructure to provision (from Infrastructure Assessment)
{what is being added, referencing the specific AC that requires it}
{NONE if no new infrastructure}

### Risks
{technical risks, migration risks, tenancy risks, performance risks}
{mitigation for each}

### Testing strategy
{unit / integration / contract / regression / tenancy isolation — mapped to ACs}

### Rollback
{how to revert: migration downgrade, feature flag, deployment order}
{NONE if purely additive with safe downgrade}

### Constitutional constraints applied
- {principle_id}: {how compliance is enforced in this implementation}
```

This plan must cover **this story only**. Any item that references a future story
or a "nice to have" must be removed before proceeding.

For **MEDIUM** risk: deliver plan outline, pause for confirmation (Phase 5).  
For **HIGH** risk: full plan only after Architecture Review approval (Phase 5).

---

## Phase 11 — Implementation (Step 7)

**Implement exactly what is in the approved plan. Nothing more.**

### Enterprise Implementation Principles

Apply these in addition to all code standards below:

| Principle | Requirement |
|-----------|-------------|
| **Configuration over Customization** | Business rules, tenant policies, workflow definitions from config/metadata — not code branches |
| **Composition over Hardcoding** | Compose from Platform Objects, registries, providers, plugins — no bespoke one-off logic |
| **DDD** | Bounded contexts, aggregates, domain events; business rules in `domain/` only |
| **SOLID** | Single responsibility per module; depend on ports not adapters |
| **Hexagonal** | `domain/` → `application/` → `infrastructure/`; no infrastructure imports in domain |
| **Platform Contracts** | Validate at boundaries against JSON Schema in `contracts/` |
| **Metadata Driven** | Platform Objects use `aep_meta` + `platform-object.schema.json` envelope |
| **Configurable** | No hardcoded business logic, tenant rules, or workflow definitions in code |
| **Generic primitives** | No business-specific logic in shared libraries (`aep_common`, `aep_meta`) |

### Non-Negotiable Code Standards

**Architecture:**
- All inter-service communication via Kafka using `aep_common.kafka` — no direct HTTP
  calls between services for business logic
- All database queries include `tenant_id` — RLS enforced at the storage layer
- No vendor SDK imports in agent or tool code — all external tools accessed via
  Tool Registry / Provider Framework
- Platform Objects inherit the universal envelope — identity, lifecycle, versioning,
  relationships, audit, health, metrics, extensions per `PLATFORM_PRIMITIVES.md` §3

**Configuration:**
- All configuration from environment variables via Pydantic Settings
- No hardcoded values — credentials, URLs, tenant IDs, topic names, model names

**Error handling:**
- All exceptions are typed — no bare `except:` or `except Exception: pass`
- All errors logged with structured context before re-raising or returning
- Agent and tool failures publish `AgentFailed` or `ToolFailed` events
- No silent failures

**Logging:**
- All log lines use `aep_common.logging` — never `print()` or Python's built-in
  `logging` directly
- Every log line in task context includes `task_id`, `workflow_run_id`, `tenant_id`

**Observability — on every new public domain method:**

```python
from aep_common.tracing import get_tracer

tracer = get_tracer(__name__)

with tracer.start_as_current_span("method_name") as span:
    span.set_attribute("task_id", str(task_id))
    span.set_attribute("tenant_id", tenant_id)
```

Every new service exposes:
- `aep_{service}_requests_total` — counter by status
- `aep_{service}_request_duration_seconds` — histogram
- `aep_{service}_errors_total` — counter by error type

**Code quality:**
- Type hints on every function signature
- Docstrings on public methods describe intent, not mechanics
- No `TODO`, `FIXME`, or `HACK` in production code paths
- No placeholder implementations or stubs

---

## Phase 12 — Testing (Step 8)

Generate all test categories required by the story. Mark tests with `@pytest.mark.story_{story_id}`.

### Test categories (extended)

| Category | Scope |
|----------|-------|
| **Unit tests** | One test file per `domain/` module, happy path and ≥2 edge cases per method |
| **Integration tests** | End-to-end primary flow (Kafka, REST API, DB migration) |
| **Contract tests** | Payloads against `contracts/*.schema.json`; include `platform-object.schema.json` when applicable |
| **API tests** | Endpoint request/response, auth, error codes, pagination |
| **Negative tests** | Invalid input, missing auth, wrong tenant, malformed payloads |
| **Regression tests** | No breaking change to shared interfaces, event schemas, API paths |
| **Security tests** | Tenant isolation, authz boundaries, no credential leakage |
| **Performance tests** | Hot-path latency or throughput where AC specifies SLAs — else N/A |
| **Configuration tests** | Settings load, defaults, env override, invalid config rejection |
| **Metadata tests** | Platform Object envelope, lifecycle FSM, metadata field validation |
| **Acceptance tests** | One test per Given/When/Then, named `test_ac_{criterion_id}_{description}` |
| **Isolation test** | Cross-tenant query returns zero rows, if story touches data |

Every test must fail when the code it tests is removed. No vacuous assertions.

### Coverage report

```bash
pytest -m "story_{story_id}" -v --cov={target_folder} --cov-report=term-missing
python scripts/validate_contract.py contracts/
```

Produce coverage summary:

```
Testing summary:
  Tests executed:    {N} passed, {N} failed, {N} skipped
  Coverage (new code): {N}%
  Contract validation: PASS / FAIL
  Status:              PASS / FAIL
```

**Return to Phase 11 if any test or contract validation fails.**

---

## Phase 13 — Engineering Reviews (Step 9)

**Auto-execute all review passes. Generate findings; fix where possible.**

Use PI `REVIEW_CHECKLIST.md` and review skill criteria. Produce a verdict for each.

#### Architecture Review
- [ ] Bounded context respected — no cross-service data access (AR5)
- [ ] Hexagonal layers correct — domain has no infrastructure imports
- [ ] Platform Object envelope complete if applicable
- [ ] Config over Customization — no hardcoded business rules
- [ ] Composition over Hardcoding — registries/primitives used correctly
- [ ] No constitutional violations (re-run Architecture Validation on implemented code)
- **Verdict:** PASS / FAIL — {findings}

#### Code Review
- [ ] Matches approved implementation plan
- [ ] Type hints, docstrings, no TODO/FIXME in production paths
- [ ] Error handling typed and logged; no silent failures
- **Verdict:** PASS / FAIL — {findings}

#### Security Review
- [ ] No credentials in code, images, or config (SR1)
- [ ] `tenant_id` in every data query (SR3)
- [ ] RBAC, Policy, Secrets remain separate (SR1/S4)
- [ ] Input validated at boundaries (SR5)
- [ ] `detect-secrets` finds zero new secrets
- **Verdict:** PASS / FAIL — {findings}

#### Performance Review
- [ ] No unbounded queries or N+1 patterns in new hot paths
- [ ] Indexes on tenant-scoped query columns where applicable
- [ ] Kafka consumer commits offset after successful processing
- **Verdict:** PASS / N/A / FAIL — {findings}

#### Regression Review
- [ ] No breaking changes to existing contract schemas (additive only, or version bumped + ADR)
- [ ] No renamed/removed exports in `aep_common` without importer audit
- [ ] No breaking API path or payload changes without version increment
- [ ] Database migration is additive or has documented migration path
- [ ] If PR is open: recommend `/regression-review <PR_NUMBER>` for full 11-lens review
- **Verdict:** PASS / NEEDS PR REVIEW / FAIL — {findings}

#### Documentation Review
- [ ] PI `STATUS.md`, `CHANGELOG.md`, `METRICS.md` updated (Phase 11)
- [ ] Contract README updated if new schema added
- [ ] `.env.example` updated for new variables
- [ ] ADR added if architectural decision made
- **Verdict:** PASS / FAIL — {findings}

**Return to Phase 11 if any review verdict is FAIL.** Fix findings where possible before re-running reviews.

### Self Validation (Preserved from Phase 8)

#### Acceptance Criteria Coverage

For each criterion defined in Story Readiness:

```
AC-{n}: {criterion text}
  Satisfied by: {file and method}
  Tested by:    {test file and test name}
  Status:       SATISFIED / NOT SATISFIED
```

**Return to Phase 11 if any criterion is NOT SATISFIED.**

#### Definition of Done — Story-Level Gate

```
[ ] Architecture — no direct HTTP calls between services
[ ] Architecture — config from environment variables only
[ ] Architecture — no hardcoded credentials
[ ] Database — tenant_id in every query
[ ] Database — RLS policy on every new table
[ ] Database — migration has downgrade()
[ ] Kafka — offset committed after successful processing
[ ] Kafka — failed messages routed to DLQ
[ ] Code quality — ruff check exits 0
[ ] Code quality — black --check exits 0
[ ] Code quality — mypy --strict exits 0
[ ] Code quality — no TODO/FIXME in production paths
[ ] Testing — unit coverage ≥ 80% on new code
[ ] Testing — acceptance test per AC criterion
[ ] Security — detect-secrets finds zero new secrets
[ ] Security — non-root user in Dockerfile (if applicable)
[ ] Observability — OTEL traces on all public domain methods
[ ] Observability — Prometheus metrics exposed
[ ] Observability — structured logs with correlation IDs
[ ] Documentation — .env.example updated for new variables
```

#### Contract Compliance

If the story produces or consumes Kafka events:
- [ ] Every published message validates against `contracts/event-envelope.schema.json`
- [ ] Event type follows PascalCase convention (`AgentCompleted`, not `agent_completed`)
- [ ] Topic name follows `aep.{domain}.{event-type-kebab}` convention

If the story registers an agent or tool:
- [ ] Registration validates against `contracts/agent-contract.schema.json` or
  `contracts/tool-contract.schema.json`

If the story produces or consumes Platform Objects:
- [ ] Payload validates against `contracts/platform-object.schema.json`
- [ ] Lifecycle transitions follow FSM in `PLATFORM_PRIMITIVES.md` §3.4

### Constitution Compliance Re-check

```bash
rg "from agents\." src/{target_folder}/ --include="*.py"
rg "bypass|skip_gate|auto_approve|EMERGENCY" src/{target_folder}/
rg "claude-|gpt-4|gemini-" src/{target_folder}/ --include="*.py"
rg "print(" src/{target_folder}/ --include="*.py"
python -m detect_secrets scan src/{target_folder}/
ruff check src/{target_folder}/
black --check src/{target_folder}/
mypy --strict src/{target_folder}/
```

**Do not proceed to Phase 15 with any unmet item.**

---

## Phase 14 — Documentation (Step 10)

Update PI tracking documents and architecture artifacts for `{story_id}`:

```bash
# Required updates in docs/engineering/implementation-roadmap/{PI}/
# STATUS.md    — mark story Complete; update deliverable table
# CHANGELOG.md — add entry under [version] with story changes
# METRICS.md   — update test counts, coverage, endpoints, tables
```

Also update when applicable:
- **Architecture Diagrams** — `docs/engineering/implementation-roadmap/{PI}/diagrams/` if story changes structure
- **ADR** — `docs/architecture/ADR/DECISIONS.md` if constitutional or architectural decision made
- **Implementation Notes** — `docs/engineering/implementation-roadmap/{PI}/docs/US-{PI}-{NN}-implementation-plan.md` and `US-{PI}-{NN}-implementation-summary.md`
- `contracts/README.md` — if new contract schema added
- `.env.example` — for new environment variables

---

## Phase 15 — Completion (Step 11)

**Produce this summary when all Phase 13 reviews pass and Phase 14 documentation is updated.**

```
## Implementation Summary: {story_id} — {story_title}

### Architecture v2.0 context
PI:                {PI}
Capability:        {CAP-XX} — {name}
Risk classification: {LOW / MEDIUM / HIGH}
Approval:          {AUTO-CONTINUE / CONFIRMED / EXPLICITLY APPROVED}
ADE:          {CONTINUE / STOP — RFC} — Reuse Score: {0-100}
Primitives used:   {list Platform Object types, Providers, etc. or NONE}
Contracts:         {list contract schemas touched}

### Files changed
Created:
- {path}: {one-line description}
Modified:
- {path}: {what changed}

### Tests executed
| Category | Count | Status |
|----------|-------|--------|
| Unit | {N} | PASS/FAIL |
| Integration | {N} | PASS/FAIL |
| Contract | {N} | PASS/FAIL |
| API | {N} | PASS/FAIL |
| Negative | {N} | PASS/FAIL |
| Regression | {N} | PASS/FAIL |
| Security | {N} | PASS/FAIL |
| Acceptance | {N} | PASS/FAIL |

### Coverage
New code coverage: {N}%
Contract validation: PASS / FAIL

### Architecture / Security compliance
| Gate | Status |
|------|--------|
| Architecture Compliance | PASS / FAIL |
| Platform Contracts | PASS / FAIL |
| Metadata Driven | PASS / FAIL |
| Config over Customization | PASS / FAIL |
| Composition over Hardcoding | PASS / FAIL |
| Security | PASS / FAIL |

### Performance summary
{key metrics or N/A — latency, query counts, Kafka lag}

### Infrastructure added
- {component}: {what was configured, which AC required it}

### Infrastructure deferred
- {component}: {why not needed for this story}

### Review verdicts (Phase 13)
| Review | Verdict |
|--------|---------|
| Architecture | PASS / FAIL |
| Code | PASS / FAIL |
| Security | PASS / FAIL |
| Performance | PASS / N/A / FAIL |
| Regression | PASS / NEEDS PR REVIEW / FAIL |
| Documentation | PASS / FAIL |

### Future improvements
{deferred items, tech debt, follow-up stories — or NONE}

### Commands to run

  # Install
  {command}

  # Migrations (if applicable)
  alembic upgrade head

  # Tests
  pytest -m "story_{story_id}" -v
  pytest src/tests/unit/{service_name}/ -v --cov={target_folder}
  pytest src/tests/integration/{service_name}/ -v

  # Lint and type check
  ruff check src/{target_folder}/
  black --check src/{target_folder}/
  mypy --strict src/{target_folder}/

  # Contract validation
  python scripts/validate_contract.py contracts/

### Known risks
{residual risks from implementation plan — or NONE}

### Known limitations
{anything not covered that a reviewer should know — or NONE}

### PR summary (draft)
**Title:** feat({scope}): {story_id} {story_title}
**Summary:** {2-3 bullets}
**Test plan:** {checklist}

### Recommended next story
{story_id from STATUS.md / SPRINT_PLAN.md that logically follows}

### Next workflow step
Run: /generate-tests {story_id}   # if additional test coverage needed
Then: /regression-review <PR_NUMBER>
Then: /aep-review <PR_NUMBER>
Then: /release-story <PR_NUMBER>
```

---

## Engineering Rules

- Never redesign the architecture
- Never modify `CONSTITUTION.md`, `ARCHITECTURE.md`, `CLAUDE.md`, or PI tracking
  documents (`STATUS.md`, `CHANGELOG.md`, `METRICS.md`) **except** as required by
  Phase 14 documentation updates for the current story
- Never introduce new platform capabilities not defined in `CAPABILITIES.md`
- Never implement more than one story per execution
- Never provision infrastructure not required by the current story's AC
- Never generate placeholder code or leave `TODO` comments in production paths
- Never hardcode business logic — use configuration, metadata, and Platform Objects
- Always discover repository context (Phase 1) before architecture load
- Always classify risk (Phase 4) and satisfy approval gates (Phase 5) before coding
- Always run Architecture Decision Engine (Phases 2–3) before Story Resolution — mandatory for every story
- Always produce production-ready code — assume Principal Engineer review
- Always stop and report when a required input is missing or a dependency is unmet
- Always optimise for maintainability over speed

---

## Forbidden Actions

- Skip any phase or reorder phases
- Skip ADE (Phases 2–3) — mandatory for every story
- Proceed past a Stop condition without resolving it
- Write production code before Phase 10 approval gates are satisfied
- Write production code when ADE decision = STOP (Architecture RFC required)
- Implement more than one User Story
- Add infrastructure "for later" — every infrastructure decision must trace to an AC
- Import vendor SDKs in agent or tool code
- Hardcode credentials, URLs, topic names, model names, or tenant IDs
- Silent exception handling
- Placeholder implementations or stubs
- Add a new direct HTTP call between platform services
- Modify a contract schema without an ADR in `docs/architecture/ADR/DECISIONS.md`
- Omit type hints or use `any` in TypeScript
- Skip Phase 10 engineering reviews or Phase 11 documentation updates
- Proceed past HIGH risk without explicit engineer approval
- Invoke `/release-story` during this skill — run after PR is opened
- Sprint planning, velocity tracking, risk register management, or PI objectives review
  are not part of this skill (except reading `STATUS.md` for story resolution)
