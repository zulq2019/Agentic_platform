# Repository Restructure Report

**Status:** Complete  
**Version:** 1.0  
**Effective:** 1 July 2026  
**Authority:** Architecture Baseline v2.0 approved  
**Method:** `git mv` (history preserved) + link updates + redirect stubs

---

## Executive summary

The repository documentation was reorganised into **four domains** — Architecture, Product, Engineering, Reference — plus **Migration** reports. No documentation or implementation code was deleted. PI folders moved from `docs/04-program/` to `docs/engineering/implementation-roadmap/` and were **renamed** to reflect v2 framework names.

---

## What moved

### Program Increments (PIs)

| Former path | New path | Rationale |
|-------------|----------|-----------|
| `docs/04-program/PI-01-Platform-Spine/` | `docs/engineering/implementation-roadmap/PI-01-Platform-Core/` | Aligns with Platform Core framework |
| `docs/04-program/PI-02-Agent-Runtime/` | `docs/engineering/implementation-roadmap/PI-02-Metadata-Engine/` | Metadata Engine ownership in v2 |
| `docs/04-program/PI-03-Orchestrator/` | `docs/engineering/implementation-roadmap/PI-03-Provider-Framework/` | Provider Framework |
| `docs/04-program/PI-04-Memory/` | `docs/engineering/implementation-roadmap/PI-04-Workflow-Framework/` | Workflow Framework |
| `docs/04-program/PI-05-Tool-Registry/` | `docs/engineering/implementation-roadmap/PI-05-Execution-Framework/` | Execution Framework |
| `docs/04-program/PI-06-Engineering-Agents/` | `docs/engineering/implementation-roadmap/PI-06-Studio-Framework/` | Studio Framework |
| `docs/04-program/PI-07-Governance/` | `docs/engineering/implementation-roadmap/PI-07-Platform-Services/` | Platform Services |
| `docs/04-program/PI-08-Enterprise/` | `docs/engineering/implementation-roadmap/PI-08-Solution-Packs/` | Solution Packs |
| `docs/04-program/PI-09-Developer-Experience/` | `docs/engineering/implementation-roadmap/PI-09-Platform-UX/` | Platform UX |
| `docs/04-program/PI-10-General-Availability/` | `docs/engineering/implementation-roadmap/PI-10-General-Availability/` | Unchanged name |

### Architecture domain

| Former | New | Rationale |
|--------|-----|-----------|
| `DECISIONS.md` (root) | `docs/architecture/ADR/DECISIONS.md` | ADR home under Architecture |
| `docs/artifacts/TECHNICAL_ARCHITECTURE.md` | `docs/architecture/REFERENCE_ARCHITECTURE.md` | Reference Architecture in Architecture domain |
| `docs/architecture/*` (existing) | Unchanged location | Already correct |

### Product domain

| Former | New | Rationale |
|--------|-----|-----------|
| `VISION.md` (root) | `docs/product/VISION.md` | Customer-facing vision |
| `ROADMAP.md` (root) | `docs/product/ROADMAP.md` | Customer-facing roadmap |
| — | `docs/product/COMMERCIAL_MODEL.md` | New product overview |
| — | `docs/product/MARKETPLACE.md` | New product overview |
| — | `docs/product/SOLUTION_PACKS.md` | New product overview |

Root `VISION.md`, `ROADMAP.md`, `DECISIONS.md` retained as **redirect stubs**.

### Engineering domain

| Former | New | Rationale |
|--------|-----|-----------|
| `docs/engineering/ARCHITECTURE_ALIGNMENT_REPORT.md` | `docs/engineering/architecture-alignment/ARCHITECTURE_ALIGNMENT_REPORT.md` | Engineering alignment area |
| — | `docs/engineering/release-plan.md` | Engineering execution view |
| — | `docs/engineering/sprint-history/README.md` | Sprint log placeholder |

### Reference domain

| Former | New | Rationale |
|--------|-----|-----------|
| `docs/05-blueprints/*/` | `docs/reference/blueprints/*/` | Blueprints are reference material |

`docs/05-blueprints/README.md` redirect retained.

### Migration domain

| Former | New |
|--------|-----|
| `docs/MIGRATION_PLAN.md` | `docs/migration/MIGRATION_PLAN.md` |
| `docs/MIGRATION_REPORT.md` | `docs/migration/MIGRATION_REPORT.md` |

---

## Why it moved

| Driver | Outcome |
|--------|---------|
| Architecture v2.0 approved | Documentation structure must mirror ontology |
| Customer vs engineering separation | Product domain is customer-facing; PIs are internal |
| Four-domain clarity | Architects, PM, engineers, and integrators each have a home |
| Git history | `git mv` preserves blame and history on all PI files |
| No data loss | Redirect stubs at legacy paths; no file deletions |

---

## Updated folder tree

```
docs/
├── architecture/                 # Domain 1 — Ontology & ADR
│   ├── README.md
│   ├── ARCHITECTURE_BASELINE_V2.md
│   ├── PLATFORM_PRIMITIVES.md
│   ├── PLATFORM_CONTRACTS.md
│   ├── PLATFORM_META_MODEL.md
│   ├── PLATFORM_UX_MODEL.md
│   ├── PLATFORM_GLOSSARY.md
│   ├── METADATA_DRIVEN_ENTERPRISE_PLATFORM.md
│   ├── REFERENCE_ARCHITECTURE.md
│   ├── ARCHITECTURE_CHANGELOG_V2.md
│   ├── IMPLEMENTATION_READINESS.md
│   └── ADR/
│       └── DECISIONS.md
│
├── product/                      # Domain 2 — Customer-facing
│   ├── README.md
│   ├── VISION.md
│   ├── ROADMAP.md
│   ├── COMMERCIAL_MODEL.md
│   ├── MARKETPLACE.md
│   ├── SOLUTION_PACKS.md
│   └── PRODUCT_*.md
│
├── engineering/                  # Domain 3 — Internal execution
│   ├── README.md
│   ├── release-plan.md
│   ├── implementation-roadmap/
│   │   ├── PI-01-Platform-Core/
│   │   ├── PI-02-Metadata-Engine/
│   │   ├── PI-03-Provider-Framework/
│   │   ├── PI-04-Workflow-Framework/
│   │   ├── PI-05-Execution-Framework/
│   │   ├── PI-06-Studio-Framework/
│   │   ├── PI-07-Platform-Services/
│   │   ├── PI-08-Solution-Packs/
│   │   ├── PI-09-Platform-UX/
│   │   └── PI-10-General-Availability/
│   ├── architecture-alignment/
│   │   └── ARCHITECTURE_ALIGNMENT_REPORT.md
│   └── sprint-history/
│       └── README.md
│
├── reference/                    # Domain 4 — Blueprints & indexes
│   ├── README.md
│   └── blueprints/
│       └── {capability}/BLUEPRINT.md
│
├── migration/
│   ├── README.md
│   ├── MIGRATION_PLAN.md
│   └── MIGRATION_REPORT.md
│
├── 04-program/README.md          # Redirect only
├── 05-blueprints/README.md       # Redirect only
└── artifacts/README.md           # Redirect only
```

**Unchanged at repository root:** `src/`, `contracts/`, `workflows/`, `CONSTITUTION.md`, `ARCHITECTURE.md`, `CLAUDE.md`

---

## Broken links fixed

| Pattern | Replacement |
|---------|-------------|
| `docs/04-program/` | `docs/engineering/implementation-roadmap/` |
| `../04-program/` | `../engineering/implementation-roadmap/` |
| `PI-01-Platform-Spine` → … | `PI-01-Platform-Core` → … (all PI renames) |
| `docs/05-blueprints/` | `docs/reference/blueprints/` |
| `../05-blueprints/` | `../reference/blueprints/` |
| `docs/artifacts/TECHNICAL_ARCHITECTURE.md` | `docs/architecture/REFERENCE_ARCHITECTURE.md` |
| `docs/MIGRATION_*.md` | `docs/migration/MIGRATION_*.md` |
| `DECISIONS.md` (root links) | `docs/architecture/ADR/DECISIONS.md` |
| `VISION.md` / `ROADMAP.md` (root links) | `docs/product/VISION.md` / `ROADMAP.md` |
| PI `../../architecture/` | `../../../architecture/` (depth +1) |
| PI alignment report path | `../../architecture-alignment/ARCHITECTURE_ALIGNMENT_REPORT.md` |

**Bulk-updated:** `.ai/commands/`, `.ai/skills/`, `REPOSITORY_GUIDE.md`, `ARCHITECTURE.md`, `CLAUDE.md`, product docs, migration docs, architecture baseline.

---

## Future conventions

| Content type | Location |
|--------------|----------|
| Platform ontology, contracts, ADR | `docs/architecture/` |
| Vision, roadmap, commercial, marketplace | `docs/product/` |
| PI plans, sprint history, alignment | `docs/engineering/` |
| Blueprints, contract/workflow index | `docs/reference/` |
| Migration reports | `docs/migration/` |
| Production code | `src/` only |
| JSON Schema | `contracts/` (root) |
| Workflow JSON templates | `workflows/` (root) |

**PI naming:** `PI-{NN}-{Framework-Name}` under `docs/engineering/implementation-roadmap/`.

**Redirects:** Do not remove `docs/04-program/README.md` or root stubs without a major version bump — external links may still target old paths.

---

## Implementation impact

| Area | Impact |
|------|--------|
| `src/` | **None** — service paths unchanged |
| CI / scripts | Update only if hardcoded `docs/04-program` paths exist |
| AI skills | Updated to new PI paths |
| Open PRs | May need rebase for doc path conflicts |

---

*Restructure performed with `git mv`. See `git log --follow` on any PI file for full history.*
