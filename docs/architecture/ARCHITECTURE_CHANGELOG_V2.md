# Architecture Changelog — Baseline v2.0

**Status:** Release notes  
**Version:** 2.0  
**Effective:** 1 July 2026  
**Baseline:** [ARCHITECTURE_BASELINE_V2.md](./ARCHITECTURE_BASELINE_V2.md)  
**Prior baseline:** Reference Architecture v1.0 / Platform Architecture v1.0 (June 2026)

---

## Summary

Architecture Baseline **v2.0** stabilises the platform as a **metadata-driven enterprise platform**. v2 **extends** v1 — it does not invalidate constitutional principles, container topology, or completed PI-01 spine work. It **reframes ontology** (Provider Model, Platform Objects, Execution Profiles) and **defines the path** for Metadata Engine, Marketplace, and Builders.

---

## Architecture decisions

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| **D-v2-01** | Platform Object as universal base class | One API, UI, audit, and lifecycle model | Accepted in PLATFORM_PRIMITIVES v2 |
| **D-v2-02** | Provider replaces Agent as meta-model primitive | Unify AI, human, API, MCP integrations | Accepted; Agent remains product language |
| **D-v2-03** | Connector is Provider Plugin (`connector` kind) | Eliminate duplicate primitive | Accepted |
| **D-v2-04** | Execution Profiles replace ad hoc model routing | Governed, versioned AI execution | Accepted |
| **D-v2-05** | Provider Builder for customer Providers | Configuration over customization | Accepted (UX); not implemented |
| **D-v2-06** | Metadata Engine owns publish and resolve | Salesforce-class metadata lifecycle | Accepted; not implemented |
| **D-v2-07** | Marketplace distributes metadata only | Partner ecosystem without core forks | Accepted; not implemented |
| **D-v2-08** | Commercial Pack → Entitlement chain | Commercial gating at runtime | Accepted; partial in docs |
| **D-v2-09** | Observability on every object — no exemptions | Enterprise operability | Accepted in contracts |
| **D-v2-10** | Thirteen primitives unchanged | Stability | Accepted |

**Proposed formal ADRs:** ADR-025 (Provider Model), ADR-026 (Metadata Engine), ADR-027 (Execution Profiles supersede ADR-012 authoring) — to be added to [DECISIONS.md](../../DECISIONS.md).

---

## New concepts

| Concept | Document |
|---------|----------|
| Platform Object (explicit base class) | PLATFORM_PRIMITIVES §3 |
| Provider Model + `provider_kind` | PLATFORM_PRIMITIVES §5.1, §6.4 |
| Provider Builder | PLATFORM_PRIMITIVES §6.4; PLATFORM_UX_MODEL §10.0 |
| Execution Profile (preferred/fallback/consensus) | PLATFORM_PRIMITIVES §6.5 |
| Metadata Engine (extended responsibilities) | PLATFORM_META_MODEL §3 |
| Solution Pack categories (Engineering, Industry, Team, Customer, Partner) | PLATFORM_PRIMITIVES §4.12 |
| Commercial Pack expansion | PLATFORM_PRIMITIVES §6.12 |
| Platform Builders (catalogue) | METADATA_DRIVEN_ENTERPRISE_PLATFORM §6 |
| PLATFORM_GLOSSARY | Official vocabulary |
| METADATA_DRIVEN_ENTERPRISE_PLATFORM | Philosophy whitepaper |
| ARCHITECTURE_BASELINE_V2 | Implementation master reference |

---

## Deprecated concepts (lexical — not removed)

| Deprecated as primitive | Preferred term | Notes |
|-------------------------|----------------|-------|
| Agent (meta-model) | Provider (`ai-agent`) | Agent Registry → typed Provider index |
| Connector (primitive) | Provider (`connector`) | Connector Plugin = Provider Plugin |
| Tool (as parallel to Agent) | Provider (`connector` / `rest-api`) | tool-contract → subset of Provider |
| Model routing (ad hoc) | Execution Profile | Model Router becomes resolver |
| Customization / tenant fork | Configuration / Solution Pack | CONSTITUTION MT3 |

**Not deprecated:** Event Bus, Orchestrator as Planner, capability tags, human gates, audit store, nine-container logical model (evolves to sixteen services in implementation).

---

## Migration guidance

### For architects

1. Read [ARCHITECTURE_BASELINE_V2.md](./ARCHITECTURE_BASELINE_V2.md) and [PLATFORM_GLOSSARY.md](./PLATFORM_GLOSSARY.md).
2. Use Provider and Capability in new designs; map legacy Agent/Tool diagrams to Provider kinds.
3. Reference Execution Profiles in workflow and agent stories.

### For implementers

| Area | v1 pattern | v2 target | Transition |
|------|------------|-----------|------------|
| Registry | Agent Registry + Tool Registry | Provider Registry views | Keep services; unify query API over time |
| Registration JSON | agent-contract / tool-contract | provider-contract (future) | Validate both against Provider shape when schema lands |
| Model selection | model-router config | Execution Profile metadata | Router reads Active Profile |
| Workflows | JSON files in workflows/ | Workflow Platform Objects | Dual-read during PI-03+ |
| Docs | ARCHITECTURE.md only | Baseline + primitives stack | Link; do not delete v1 container doc |

### For product / PI

- PI-03+: Planner selects Provider by capability tag (already constitutional; now explicit in baseline).
- PI-05: Frame Tool Registry as connector Provider index.
- PI-08: Own Entitlements, config hierarchy, Marketplace prep.
- PI-09: Own Builders and Object Explorer.

### For partners

- Ship Provider Plugins and Solution Packs — not orchestrator patches.
- Use [PLATFORM_GLOSSARY.md](./PLATFORM_GLOSSARY.md) for all public terminology.

---

## Repository impact

| Path | Change type |
|------|-------------|
| `docs/architecture/ARCHITECTURE_BASELINE_V2.md` | **New** — master reference |
| `docs/architecture/ARCHITECTURE_CHANGELOG_V2.md` | **New** — this file |
| `docs/architecture/IMPLEMENTATION_READINESS.md` | **New** — readiness assessment |
| `docs/architecture/*` (v2 docs) | Already committed — primitives, contracts, meta, UX, glossary, philosophy |
| `ARCHITECTURE.md` | **Updated** — baseline pointer, v1.1 |
| `VISION.md` | **Updated** — metadata-driven positioning |
| `ROADMAP.md` | **Updated** — baseline v2 milestone |
| `docs/04-program/PI-*/` | **Surgical** — objectives, README, prompt context |
| `contracts/` | **No change in v2 stabilisation** — gap G-02; implement in PI |
| `src/` | **No change** — architecture only |
| `DECISIONS.md` | **Recommended** — ADR-025+ (not in this stabilisation commit) |

---

## Implementation impact

| Phase | Work |
|-------|------|
| **Immediate** | Implement against baseline docs; use glossary in stories and APIs |
| **PI-01 completion** | Spine unchanged; add baseline reference in PI docs |
| **PI-02–06** | Map agents/tools to Provider kinds in registration and docs |
| **PI-03** | Workflow Engine; prepare for Workflow Object registry |
| **PI-08** | config-service, Entitlements, tenant configuration hierarchy |
| **PI-09** | Metadata Engine MVP, Builder UX, provider-contract schema |
| **PI-10** | Marketplace install pipeline, partner certification |

**Critical path blockers:** Metadata Engine (G-01), Provider Contract schema (G-02) — see [IMPLEMENTATION_READINESS.md](./IMPLEMENTATION_READINESS.md).

---

## Document version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-27 | Reference Architecture / nine containers |
| 2.0 | 2026-07-01 | Metadata-driven enterprise platform; Provider Model; Baseline v2 |

Related: [ARCHITECTURE_V2_CHANGE_SUMMARY.md](./ARCHITECTURE_V2_CHANGE_SUMMARY.md) (platform architecture doc delta).

---

*Changelog v2.0 closes the architecture stabilisation phase. Implementation resumes under ARCHITECTURE_BASELINE_V2.md.*
