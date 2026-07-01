# Platform Architecture v2 — Change Summary

**Status:** Architecture release notes  
**Version:** 2.0  
**Effective:** 1 July 2026  
**Base:** Platform Architecture v1.0 (`platformDoc_ReleaseV1`)  
**Authority:** Subordinate to [CONSTITUTION.md](../../CONSTITUTION.md)

---

## Executive summary

Platform Architecture **v2** formally declares the Agentic Engineering Platform a **metadata-driven enterprise platform**. v2 **extends** v1 — it does not replace document structure, remove primitives, or break v1 semantics. All four normative architecture documents are bumped to **Version 2.0 (extends v1.0; backward compatible)**.

The central v2 bet:

> **Every definable entity is a Platform Object. Customer outcomes are assembled from metadata. Engines interpret; customers configure.**

---

## What changed

### 1. Platform Object as universal base class

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §3 | Platform Object explicitly defined as **conceptual base class** inherited by all thirteen primitives |
| **PLATFORM_META_MODEL.md** §2.2 | Reinforced single inheritance hierarchy — primitive type is a role discriminator |
| **PLATFORM_CONTRACTS.md** CR-16 | Contract rule: no parallel type hierarchies |

**Backward compatibility:** v1 already treated primitives as Platform Objects. v2 makes inheritance explicit and normative.

---

### 2. Metadata Engine

| Area | Change |
|------|--------|
| **PLATFORM_META_MODEL.md** §3.1 | Extended responsibilities: **Configuration Overrides**, **Runtime Resolution** (alongside existing registry, validation, inheritance, composition, dependency resolution, publishing, discovery, lifecycle) |
| **PLATFORM_META_MODEL.md** MM-16 | Rule: Metadata Engine owns overrides and runtime resolution |
| **PLATFORM_PRIMITIVES.md** §2 | Metadata-driven platform philosophy retained and cross-linked |

**Backward compatibility:** v1 Metadata Engine responsibilities retained; v2 names additional pipelines explicitly.

---

### 3. Provider Model (replaces Agent as first-class primitive)

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §5.1, §6.4 | **Provider** is generic first-class primitive; `provider_kind` discriminator (`ai-agent`, `connector`, `human`, `script`, `rest-api`, `container`, `mcp`, `automation`, `marketplace`, `partner`) |
| **PLATFORM_PRIMITIVES.md** §6.3 | Orchestrator described as **Planner** with dynamic Provider discovery by capability tag |
| **PLATFORM_META_MODEL.md** MM-13 | Connectors remain Provider metadata |
| **PLATFORM_CONTRACTS.md** CR-16 | Capability-tag discovery mandated |

**Backward compatibility:** "Agent", "Agent Registry", and "Agent Runtime" remain **implementation and product language** for `provider_kind: ai-agent`. No primitive removed.

---

### 4. Provider Builder

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §5.1, §6.4 | Provider Builder — customer-authored Providers without platform code changes |
| **PLATFORM_UX_MODEL.md** §10.0 | Provider Builder UX templates and invariants |
| **PLATFORM_CONTRACTS.md** CR-17 | Builder output must satisfy Provider Contract |
| **PLATFORM_META_MODEL.md** MM-17 | Builder output is validated metadata only |

**Backward compatibility:** Existing vendor-published Providers unchanged; Builder is additive authoring path.

---

### 5. Execution Profiles

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §6.5 | Profiles expanded: **preferred**, **fallback**, **consensus** models; prompt profiles; context policies; budget; latency; quality; **retry strategy** |
| **PLATFORM_UX_MODEL.md** §9 | Execution Profile Designer panels aligned to v2 fields |
| **PLATFORM_CONTRACTS.md** CR-18 | Model strategy fields required at publish |

**Backward compatibility:** Legacy keys (`model_tier`, `retry_policy_ref`) retained where noted; new keys extend schema.

---

### 6. Connector Model

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §5.1, §6.4 | Connectors explicitly **Provider Plugins** (`provider_kind: connector`); Marketplace install; **auto_register** |
| **PLATFORM_UX_MODEL.md** §10 | Connector UX framed as Provider Plugin configuration |
| **PLATFORM_PRIMITIVES.md** PR-12 | Rule retained and reinforced |

**Backward compatibility:** Connector remains valid product term; not a separate primitive.

---

### 7. Solution Packs

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §4.12, §6.11 | Pack categories: Engineering, Industry, Team, Customer, Partner (+ legacy `vertical` / `horizontal` / `starter`) |
| **PLATFORM_PRIMITIVES.md** §4.12, §6.11 | Composable members expanded: Studios, Capabilities, Providers, Policies, Workflows, Execution Profiles, Knowledge, Dashboards, Reports, Templates, Plugins |

**Backward compatibility:** Legacy `pack_type` values retained in metadata table.

---

### 8. Commercial Model

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §4.11, §6.12 | Commercial Packs **produce Entitlements**; expanded gating: licensing, studios, marketplace access, execution profiles, providers, solution packs, connector limits, support levels |
| **PLATFORM_PRIMITIVES.md** §6.12 | Extended metadata keys: `licensing`, `studio_allowlist`, `marketplace_access`, `connector_limits`, `support_level`, etc. |

**Backward compatibility:** Existing `sku`, `edition`, `feature_flags`, `default_quotas`, `billing_meters` retained.

---

### 9. Marketplace

| Area | Change |
|------|--------|
| **PLATFORM_META_MODEL.md** §12.1 | Full distribution catalogue: Provider Plugins, Workflow Plugins, Policy Plugins, Execution Profiles, Knowledge Packs, Solution Packs, Studio Extensions, UI Extensions |
| **PLATFORM_META_MODEL.md** §12.1 | Explicit: **never business logic** — metadata and plugins only |
| **PLATFORM_PRIMITIVES.md** PR-19 | Platform rule added |
| **PLATFORM_META_MODEL.md** MM-18 | Meta-model rule added |

**Backward compatibility:** v1 install pipeline unchanged; artefact taxonomy extended.

---

### 10. Platform UX

| Area | Change |
|------|--------|
| **PLATFORM_UX_MODEL.md** §3.2 | v2 inherited surfaces documented; **Dependencies** and **Versions** tabs retained as v1 extensions |
| **PLATFORM_CONTRACTS.md** §23.2 | UI Contract aligned to v2 tab set + Documentation and Examples |
| **PLATFORM_UX_MODEL.md** UX-13, UX-14 | New UX rules for Builder and inherited tabs |

**Backward compatibility:** Tab order and count unchanged from v1; v2 canonical set is a subset mapping, not a tab removal.

---

### 11. Observability

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §3.8 | Full signal set: Events, Metrics, Logs, Traces, **Audit records**, Health, Cost, Usage, Performance, **Correlation IDs** — **no primitive exempt** |
| **PLATFORM_CONTRACTS.md** §13.2 | Observability Contract aligned; audit records and correlation IDs explicit |
| **PLATFORM_PRIMITIVES.md** PR-20 | Platform rule added |

**Backward compatibility:** v1 signals retained; naming normalised (`Usage statistics` → `Usage`).

---

### 12. Configuration over customization

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §1.2 | Design conviction added |
| **PLATFORM_CONTRACTS.md** §2.2 | Configuration over customization philosophy |
| **PLATFORM_META_MODEL.md** MM-19 | Customer behaviour is metadata-only |

**Backward compatibility:** Aligns with existing CONSTITUTION MT3 and v1 "metadata over code" conviction.

---

### 13. Platform Governance

| Area | Change |
|------|--------|
| **PLATFORM_PRIMITIVES.md** §4.13 | Unified governance table: versioning, approval, publishing, rollback, audit, ownership, dependencies, validation, security, lifecycle |
| **PLATFORM_CONTRACTS.md** §14.2, CR-20 | Governance Contract responsibilities extended |
| **PLATFORM_PRIMITIVES.md** PR-21 | No primitive may opt out |

**Backward compatibility:** v1 governance fields (§3.9) unchanged; v2 consolidates cross-cutting model.

---

### 14. Platform rules (new IDs)

| Document | New rules |
|----------|-----------|
| **PLATFORM_PRIMITIVES.md** | PR-16 through PR-21 |
| **PLATFORM_CONTRACTS.md** | CR-16 through CR-20 |
| **PLATFORM_META_MODEL.md** | MM-16 through MM-19 |
| **PLATFORM_UX_MODEL.md** | UX-13, UX-14 |

---

## Why it changed

| Driver | Rationale |
|--------|-----------|
| **Enterprise positioning** | Salesforce/ServiceNow-class configurability requires explicit metadata-first ontology |
| **Provider diversity** | Engineering platforms integrate AI, humans, APIs, MCP, and automation — one Provider abstraction reduces conceptual debt |
| **Customer self-service** | Provider Builder and configuration-over-customization reduce vendor engineering load per tenant |
| **Commercial scale** | Expanded Commercial Packs and Marketplace artefact taxonomy support ISV and partner ecosystems |
| **Operational maturity** | Uniform observability and UX inheritance reduce SRE and training cost |
| **Governance** | Regulated customers require explicit versioning, approval, and audit on every object class |

v2 decisions **do not** weaken [CONSTITUTION.md](../../CONSTITUTION.md): event-mediated coordination, orchestrator-as-planner, registry-based extension, tenant isolation, and human gates remain in force.

---

## Documents updated

| Document | Version | Scope of v2 edits |
|----------|---------|-------------------|
| [PLATFORM_PRIMITIVES.md](./PLATFORM_PRIMITIVES.md) | 2.0 | Platform Object, Provider Model, Provider Builder, Execution Profiles, Solution/Commercial Packs, governance, observability, platform rules |
| [PLATFORM_CONTRACTS.md](./PLATFORM_CONTRACTS.md) | 2.0 | Configuration philosophy, observability, governance, UI Contract, platform rules |
| [PLATFORM_META_MODEL.md](./PLATFORM_META_MODEL.md) | 2.0 | Metadata Engine, Marketplace, extension model, platform rules |
| [PLATFORM_UX_MODEL.md](./PLATFORM_UX_MODEL.md) | 2.0 | Inherited surfaces, Provider Builder UX, UX rules |
| **This document** | 1.0 | Release summary |

**Not modified:** [CONSTITUTION.md](../../CONSTITUTION.md), [ARCHITECTURE.md](../../ARCHITECTURE.md), [DECISIONS.md](../../DECISIONS.md) — v2 extends platform architecture docs only. Constitutional alignment should be verified when implementing engines.

---

## Future considerations

### Implementation backlog (out of scope for v2 docs)

| Topic | Consideration |
|-------|---------------|
| **Schema migration** | JSON Schema updates for `provider_kind`, Execution Profile v2 fields, Commercial Pack keys — requires contract validation CI |
| **Agent Registry rename** | Product may rebrand to Provider Registry in UI while retaining typed `ai-agent` index |
| **Provider Builder GA** | Wizard flows per template; certification pipeline for partner Providers |
| **Marketplace signing** | Package manifest signatures and provenance (§12.3) — operational hardening |
| **Execution Profile consensus** | Multi-model voting runtime — engine capability not yet normative in CONSTITUTION |
| **ADR** | Formal ADR recommended for Provider Model superseding Agent-as-primitive in implementation docs |
| **ARCHITECTURE.md sync** | Container diagram may still say "Agent Runtime" — align in separate change when implementation catches up |

### Compatibility guarantees

- v1 Published metadata **remains valid** unless a field is explicitly marked deprecated in a future schema MINOR
- v1 tab chrome **unchanged** — Dependencies and Versions tabs kept
- v1 primitive count **unchanged** — still exactly thirteen primitives
- v1 lifecycle states **unchanged**

### Review cadence

Revisit Architecture v2 when:

1. First customer-authored Provider reaches production via Provider Builder
2. Marketplace ships third-party MCP Provider Plugins at scale
3. Commercial Pack entitlements require cross-region federation
4. Contract MAJOR is proposed — requires Decision Record per [CLAUDE.md](../../CLAUDE.md) documentation rules

---

## Verification checklist

Architecture reviewers should confirm:

- [ ] All thirteen primitives inherit Platform Object §3 envelope
- [ ] No document removes v1 concepts or restructures top-level sections
- [ ] Provider Model does not introduce agent-to-agent calls
- [ ] Marketplace described as metadata/plugin distribution only
- [ ] Observability and UX inheritance stated as mandatory with no exemptions
- [ ] Platform rules PR/CR/MM/UX IDs are internally consistent
- [ ] CONSTITUTION principles A1–A3, P3, H2, MT3, S2 remain satisfied

---

*Architecture v2 is a documentation release. Engine and Studio implementation may trail; v2 docs are the target state for incremental delivery.*
