# Repository Stabilisation — Migration Report

**Author:** Principal Platform Engineer  
**Date:** 28 June 2026  
**Status:** Awaiting Approval  
**Scope:** Repository structure stabilisation for production implementation  
**Authority:** [CONSTITUTION.md](CONSTITUTION.md) · [REPOSITORY_GUIDE.md](REPOSITORY_GUIDE.md)

---

> This report describes every structural change made to the repository.  
> No code was generated. No documentation was moved. No existing file was deleted.  
> All changes are additive.

---

## Summary of Changes

| Change | Type | Files Added | Files Deleted |
|--------|------|-------------|---------------|
| `src/` production folder structure | New directories + `.gitkeep` | 12 | 0 |
| `.ai/` AI engineering assets structure | New directories + `.gitkeep` | 4 | 0 |
| `REPOSITORY_GUIDE.md` | New document | 1 | 0 |
| `MIGRATION_REPORT.md` | New document (this file) | 1 | 0 |
| **Total** | | **18** | **0** |

---

## 1. `src/` — Production Source Root

### What was created

```
src/
├── platform/
│   ├── gateway/        .gitkeep
│   ├── orchestrator/   .gitkeep
│   ├── workflow/       .gitkeep
│   ├── task/           .gitkeep
│   ├── runtime/        .gitkeep
│   ├── registry/       .gitkeep
│   └── services/       .gitkeep
├── sdk/                .gitkeep
├── agents/             .gitkeep
├── tools/              .gitkeep
├── shared/             .gitkeep
└── tests/              .gitkeep
```

### Why this structure

| Folder | Maps to | Populated in |
|--------|---------|-------------|
| `src/platform/gateway/` | api-gateway service (Go + Echo) | PI-01 |
| `src/platform/orchestrator/` | orchestrator-service | PI-03 |
| `src/platform/workflow/` | workflow-engine | PI-03 |
| `src/platform/task/` | task-engine | PI-03 |
| `src/platform/runtime/` | agent-runtime | PI-02 |
| `src/platform/registry/` | agent-registry, tool-registry, model-router | PI-02 + PI-05 |
| `src/platform/services/` | auth, rbac, approval, memory, audit, secrets, policy, config | PI-02 → PI-08 |
| `src/sdk/` | aep-agent-sdk, aep-tool-sdk | PI-02 + PI-05 |
| `src/agents/` | 15 specialist agents | PI-06 |
| `src/tools/` | 11 external connectors | PI-05 → PI-07 |
| `src/shared/` | aep-common library | PI-01 |
| `src/tests/` | All tests (unit, integration, contract, load, chaos) | PI-01 onwards |

### What this enforces

- **Single source of truth for code.** Every developer, every AI assistant, every CI pipeline knows exactly where production code lives: `src/`.
- **No code outside `src/`.** The repository root is for documentation and configuration only.
- **`.gitkeep` strategy.** Directories are reserved with empty `.gitkeep` files. When a PI begins, the `.gitkeep` is deleted and replaced with production code. An empty directory in `src/` is a placeholder — as soon as a PI starts, real code replaces it.

### What was NOT done

- No implementation code was written
- No service files, Dockerfiles, or configuration files were created
- The directories exist to define the target structure, not to hold code yet

---

## 2. `.ai/` — AI Engineering Assets

### What was created

```
.ai/
├── commands/     .gitkeep
├── templates/    .gitkeep
├── checklists/   .gitkeep
└── reviewers/    .gitkeep
```

### Why this structure

| Folder | Intended contents | Populated in |
|--------|------------------|-------------|
| `.ai/commands/` | Reusable AI prompt commands (slash commands, macros for common tasks) | PI-01 |
| `.ai/templates/` | Starting-point templates for AI to scaffold new services, agents, tools | PI-01 |
| `.ai/checklists/` | Structured pre-commit, pre-merge, constitutional compliance checklists | PI-01 |
| `.ai/reviewers/` | AI reviewer configurations (security, architecture, constitution) | PI-02 |

### What this solves

Previously, AI prompts lived only in `docs/04-program/PI-XX/PROMPTS.md`. Those prompts are PI-specific and describe what to build. `.ai/commands/` will hold cross-cutting, reusable prompts that apply to any PI — for example: "review this PR for constitutional compliance" or "scaffold a new agent from the standard template."

### What was NOT done

- No content was added to any `.ai/` folder
- Structure only — content is produced when implementation begins and the team identifies reusable patterns

---

## 3. `REPOSITORY_GUIDE.md` — Onboarding Document

### What was created

A root-level onboarding guide covering:
- Where production code lives (`src/`)
- Where documentation lives (`docs/`)
- Where AI assets live (`.ai/`)
- Where contracts and workflow templates live
- A per-folder responsibility table
- A lookup table for "where does X go?"
- An onboarding checklist for new engineers
- Ten golden rules summarised in a table

### Why at the root

It is the first document a developer should read after `README.md`. Placing it at the root alongside `README.md` makes it immediately visible on GitHub and in any IDE.

---

## 4. What Was NOT Changed

This is as important as what was changed.

| Existing path | Status | Reason |
|---------------|--------|--------|
| `CONSTITUTION.md` | Unchanged | Immutable by definition |
| `ARCHITECTURE.md` | Unchanged | Long-term vision preserved |
| `CLAUDE.md` | Unchanged | AI rules remain current |
| `DECISIONS.md` | Unchanged | ADR history preserved |
| `ROADMAP.md` | Unchanged | Delivery timeline preserved |
| `TASKS.md` | Unchanged | Work breakdown preserved |
| `VISION.md` | Unchanged | Product vision preserved |
| `README.md` | Unchanged | Will be updated in a future PR to reference REPOSITORY_GUIDE.md |
| `contracts/` | Unchanged | Production deliverables — validated in CI |
| `workflows/greenfield-v1.0.0.json` | Unchanged | Production deliverable |
| `scripts/validate_contract.py` | Unchanged | Active CI tool |
| `docs/04-program/` PI-01 → PI-10 | Unchanged | All 160 PI documents preserved |
| `docs/05-blueprints/` | Unchanged | All 11 capability blueprints preserved |
| `docs/artifacts/TECHNICAL_ARCHITECTURE.md` | Unchanged | 25 architecture diagrams preserved |
| `docs/MIGRATION_PLAN.md` | Unchanged | Previous migration rationale preserved |
| `docs/reference/` | Unchanged | Source reference architecture preserved |

---

## 5. Repository State After This Migration

```
agentic-engineering-platform/
│
├── CONSTITUTION.md                 ← Immutable
├── ARCHITECTURE.md                 ← Living
├── CLAUDE.md                       ← Living
├── DECISIONS.md                    ← Append-only
├── ROADMAP.md                      ← Living
├── TASKS.md                        ← Living
├── VISION.md                       ← Living
├── README.md                       ← Living
├── REPOSITORY_GUIDE.md             ← NEW — onboarding guide
├── .gitignore
├── requirements-dev.txt
│
├── src/                            ← NEW — all production code
│   ├── platform/
│   │   ├── gateway/        (empty — populated PI-01)
│   │   ├── orchestrator/   (empty — populated PI-03)
│   │   ├── workflow/       (empty — populated PI-03)
│   │   ├── task/           (empty — populated PI-03)
│   │   ├── runtime/        (empty — populated PI-02)
│   │   ├── registry/       (empty — populated PI-02+PI-05)
│   │   └── services/       (empty — populated PI-02→PI-08)
│   ├── sdk/                (empty — populated PI-02+PI-05)
│   ├── agents/             (empty — populated PI-06)
│   ├── tools/              (empty — populated PI-05→PI-07)
│   ├── shared/             (empty — populated PI-01)
│   └── tests/              (empty — populated PI-01 onwards)
│
├── .ai/                            ← NEW — AI engineering assets
│   ├── commands/           (empty — populated PI-01)
│   ├── templates/          (empty — populated PI-01)
│   ├── checklists/         (empty — populated PI-01)
│   └── reviewers/          (empty — populated PI-02)
│
├── contracts/                      ← Unchanged — production
├── workflows/                      ← Unchanged — production
├── scripts/                        ← Unchanged — CI tools
│
└── docs/
    ├── MIGRATION_PLAN.md           ← Unchanged
    ├── MIGRATION_REPORT.md         ← NEW — this document
    ├── 04-program/                 ← Unchanged — PI-01 to PI-10
    ├── 05-blueprints/              ← Unchanged — 11 blueprints
    ├── artifacts/                  ← Unchanged
    └── reference/                  ← Unchanged
```

---

## 6. Implementation Readiness Assessment

| Dimension | Status | Notes |
|-----------|--------|-------|
| Architecture | ✅ Complete | `ARCHITECTURE.md` + `docs/artifacts/TECHNICAL_ARCHITECTURE.md` |
| Constitution | ✅ Complete | `CONSTITUTION.md` — 83 principles |
| Contracts | ✅ Complete | `contracts/` — 7 JSON schemas, CI-validated |
| First workflow template | ✅ Complete | `workflows/greenfield-v1.0.0.json` |
| Engineering execution plans | ✅ Complete | `docs/04-program/` — 10 PIs × 16 documents |
| Future capability blueprints | ✅ Complete | `docs/05-blueprints/` — 11 blueprints |
| Source code structure | ✅ Ready | `src/` — reserved, awaiting PI-01 implementation |
| AI engineering assets | ✅ Ready | `.ai/` — reserved, awaiting PI-01 content |
| Onboarding guide | ✅ Complete | `REPOSITORY_GUIDE.md` |
| **Implementation code** | 🔲 Not started | Begins at PI-01 Sprint 1 |

---

## 7. Approval Requested

This report documents the complete state of the repository stabilisation.

**Nothing is irreversible.** All changes are additive — `src/` directories with `.gitkeep` files and `.ai/` directories with `.gitkeep` files. They can be removed in a single commit if the structure needs adjustment.

**Awaiting approval to begin PI-01 Sprint 1 implementation.**

Upon approval, the first action is:

1. Delete `src/shared/.gitkeep` and begin `src/shared/aep_common/` — the shared library
2. Delete `src/platform/gateway/.gitkeep` through `src/platform/services/.gitkeep` and scaffold all 16 service directories
3. Create `src/tests/unit/`, `src/tests/integration/` with first test stubs
4. Wire CI to lint and test everything inside `src/`

See `docs/04-program/PI-01-Platform-Spine/SPRINT_PLAN.md` for the full Sprint 1 task list.
