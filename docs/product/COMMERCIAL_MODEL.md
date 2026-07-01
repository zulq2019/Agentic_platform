# Commercial Model

**Status:** Product overview (customer-facing)  
**Normative detail:** [../architecture/PLATFORM_GLOSSARY.md](../architecture/PLATFORM_GLOSSARY.md) · [../architecture/PLATFORM_CONTRACTS.md](../architecture/PLATFORM_CONTRACTS.md)

---

## Overview

The Agentic Engineering Platform is sold as a **metadata-driven enterprise product**. Customers purchase **Commercial Packs** that grant **Entitlements** to Platform Objects, Studios, and execution capacity — not per-tenant source-code forks.

## Packaging layers

| Layer | Customer sees | Platform delivers |
|-------|---------------|-------------------|
| **Platform Core** | Base subscription | Spine, engines, governance, observability |
| **Commercial Pack** | SKU / contract line | Entitlement grants (features, quotas, objects) |
| **Solution Pack** | Industry or engineering template | Composed Workflows, Providers, Policies |
| **Marketplace** | Add-on connectors and partner agents | Certified Provider Plugins |

## Entitlements

Entitlements enforce what a tenant may **activate**, **publish**, and **execute**. Revenue protection and quota enforcement are implemented in PI-08 (engineering: [PI-08-Solution-Packs](../engineering/implementation-roadmap/PI-08-Solution-Packs/)).

## Configuration hierarchy

Effective configuration merges: vendor defaults → Commercial Pack → Solution Pack → tenant → environment → object overrides. See [PLATFORM_META_MODEL.md](../architecture/PLATFORM_META_MODEL.md).
