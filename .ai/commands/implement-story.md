# implement-story.md

**Command:** `implement-story`  
**Version:** 5.0 — Enterprise Principal Engineer implementation engine  
**Skill authority:** `.ai/skills/implement-story/SKILL.md` (full pipeline)  
**Applies to:** All PIs, all sprints

---

## Purpose

Use this command to implement a single User Story from specification to production-ready code.

This command is the standard implementation workflow for every engineer and every AI coding agent working on the Agentic Engineering Platform. Before writing production code, behave like a **Principal Engineer + Technical Lead** — discover repository context, load architecture authorities, classify risk, apply approval gates, then implement with DDD, hexagonal architecture, and metadata-driven patterns.

Execute every phase in order. Do not skip phases. Do not combine phases.

One execution = one User Story. Never more.

### Invocation (unchanged UX)

```
/implement-story US-01.03
/implement-story PI-02 US-02.01
/implement-story US-02.01
/implement-story Platform Object Framework
/implement-story current story
/implement-story next story
```

### v5.0 pipeline — 12 enterprise phases

| Phase | Action |
|-------|--------|
| 1 | Repository Discovery — auto-discover architecture docs, skills, commands, contracts, repo structure |
| 2 | Architecture Context — load PLATFORM_*.md, CONSTITUTION, ARCHITECTURE, ADRs, ROADMAP |
| 3 | Story Resolution — resolve ID, name, current, next; load full PI doc pack |
| — | Story Readiness + Capability Validation (preserved — hard STOP) |
| 4 | Architecture Impact Analysis — classify LOW / MEDIUM / HIGH risk |
| 5 | Risk Based Approval — LOW auto-continue; MEDIUM pause for confirmation; HIGH stop for approval |
| 6 | Dependency Analysis — Platform Objects, providers, workflows, DB, security, contracts |
| — | Infrastructure Assessment (preserved) |
| — | Architecture Validation (preserved — constitution + ADR) |
| 7 | Implementation Planning — solution overview, design decisions, effort — **no code until approved** |
| 8 | Implementation — config over customization, composition over hardcoding |
| 9 | Testing — unit, integration, API, negative, regression, security, performance, metadata + coverage |
| 10 | Engineering Reviews — architecture, code, security, performance, regression, documentation |
| 11 | Documentation — STATUS, CHANGELOG, METRICS, ADR, diagrams, implementation notes |
| 12 | Completion — files changed, tests, coverage, compliance summary, PR draft, next story |

### Progress report format

Report concisely throughout — never overwhelm:

```
Current Phase:     {phase}
Progress:          {1-line status}
Risks:             {LOW / MEDIUM / HIGH}
Approval Status:   {AUTO-CONTINUE / AWAITING CONFIRMATION / STOPPED}
Next Action:       {single next step}
```

See `.ai/skills/implement-story/SKILL.md` for the complete authoritative workflow including Quality Gates and Engineering Principles.

---

## Phase 1 — Repository Discovery

Auto-discover repository context. Never fail if optional docs are missing.

| Category | Locations | Required |
|----------|-----------|----------|
| Architecture docs | `docs/architecture/`, `ARCHITECTURE.md` | Core mandatory |
| Repo constitution | `CONSTITUTION.md`, `CLAUDE.md` | Mandatory |
| Engineering roadmap | `docs/engineering/implementation-roadmap/` | Mandatory |
| Skills & commands | `.ai/skills/`, `.ai/commands/` | Discover |
| Contracts | `contracts/` | If story touches events/objects |
| Repo structure | `src/`, `platform/`, `agents/`, `tools/` | Discover |

**Stop condition:** Only if `CONSTITUTION.md` or `ARCHITECTURE.md` missing.

---

## Phase 2 — Architecture Context

Load when available:

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
| Product roadmap | `docs/product/ROADMAP.md` | Optional |

---

## Phase 3 — Story Resolution

Resolve story and load PI context pack:

| Input | Location | Required |
|-------|----------|----------|
| PI README | `docs/engineering/implementation-roadmap/{PI}/README.md` | Mandatory |
| Objectives | `docs/engineering/implementation-roadmap/{PI}/OBJECTIVES.md` | Mandatory |
| Capabilities | `docs/engineering/implementation-roadmap/{PI}/CAPABILITIES.md` | Mandatory |
| User Stories | `docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md` | Mandatory |
| Acceptance Criteria | `docs/engineering/implementation-roadmap/{PI}/ACCEPTANCE_CRITERIA.md` | Mandatory |
| Sprint Plan | `docs/engineering/implementation-roadmap/{PI}/SPRINT_PLAN.md` | Mandatory |
| Definition of Done | `docs/engineering/implementation-roadmap/{PI}/DEFINITION_OF_DONE.md` | Mandatory |
| Review Checklist | `docs/engineering/implementation-roadmap/{PI}/REVIEW_CHECKLIST.md` | Mandatory |
| STATUS | `docs/engineering/implementation-roadmap/{PI}/STATUS.md` | Mandatory |
| CHANGELOG | `docs/engineering/implementation-roadmap/{PI}/CHANGELOG.md` | Read before; update in Phase 11 |
| METRICS | `docs/engineering/implementation-roadmap/{PI}/METRICS.md` | Read before; update in Phase 11 |
| API Spec | `docs/engineering/implementation-roadmap/{PI}/API_SPEC.md` | If story exposes APIs |
| Data Model | `docs/engineering/implementation-roadmap/{PI}/DATA_MODEL.md` | If story touches data |
| Testing | `docs/engineering/implementation-roadmap/{PI}/TESTING.md` | Mandatory |

**Substitutions required:**

```
{PI}            = e.g. PI-02-Metadata-Engine
{story_id}      = e.g. US-02.03
{service_name}  = e.g. agent-registry-service
{target_folder} = e.g. src/platform/registry/
```

---

## Phase 4 — Architecture Impact Analysis

Classify risk before planning:

| Risk | Examples | Gate |
|------|----------|------|
| **LOW** | Docs, tests, refactor, cleanup, dev tooling | Auto-continue |
| **MEDIUM** | New service, provider, API, DB, plugin | Plan + pause + confirm |
| **HIGH** | Platform Object, contracts, auth, multi-tenancy, breaking schema | Architecture Review + STOP |

HIGH risk requires Architecture Review with: Business Impact, Architecture Impact, Affected Components, Dependencies, Breaking Changes, Migration Strategy, Rollback Strategy, Risks, Alternative Designs, Recommendation.

---

## Phase 5 — Risk Based Approval

| Risk | Behaviour |
|------|-----------|
| LOW | Auto-continue to dependency analysis |
| MEDIUM | Deliver plan outline → pause → await confirmation |
| HIGH | Deliver Architecture Review → STOP → no code until explicit approval |

---

## Phases 6–12 — Execution

Phases 6–12 cover dependency analysis, infrastructure assessment, architecture validation, implementation planning, coding, testing, reviews, documentation, and completion handoff.

**Quality Gates** (must pass before completion): Architecture Compliance, Platform Contracts, Metadata Driven Principles, Config over Customization, Composition over Hardcoding, Observability, Auditability, Security, Performance, Maintainability, Extensibility.

Full phase detail, preserved Story Readiness / Capability Validation / Infrastructure / Architecture Validation sections, test categories, review checklists, and handoff template: **`.ai/skills/implement-story/SKILL.md`**

---

## Engineering Rules

- Never redesign the architecture
- Never modify `CONSTITUTION.md`, `ARCHITECTURE.md`, `CLAUDE.md`, or PI documents except Phase 11 updates for current story
- Never introduce new platform capabilities not defined in `CAPABILITIES.md`
- Never implement more than one story per execution
- Never provision infrastructure not required by the current story's acceptance criteria
- Never generate placeholder code or leave `TODO` comments in production paths
- Never write code before Phase 5 approval gates are satisfied
- Always behave as Principal Engineer — understand impact before coding
- Always produce production-ready code
- Always stop and report when a required input is missing or a dependency is unmet

---

## Forbidden Actions

- Implement more than one User Story
- Skip any phase
- Proceed past a Stop condition without resolving it
- Write code before risk approval gates pass
- Proceed past HIGH risk without explicit engineer approval
- Add infrastructure "for later"
- Import vendor SDKs in agent or tool code
- Hardcode credentials, URLs, topic names, or tenant IDs
- Silent exception handling
- Placeholder implementations or stubs
- Add a new direct HTTP call between services
- Modify a contract schema without an ADR
- Omit type hints or use `any` in TypeScript
- Invoke `review-story.md`, `security-review.md`, `performance-review.md`, or `release-story.md` — those are separate commands run after this one completes
