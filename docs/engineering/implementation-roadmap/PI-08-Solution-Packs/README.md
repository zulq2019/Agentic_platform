# PI-08 — Enterprise

**Status:** `PLANNED`  
**Depends on:** PI-07 complete (governance + auth operational)  
**Target:** Sprint 30–33 (weeks 59–66)  
**Architecture baseline:** [ARCHITECTURE_BASELINE_V2.md](../../../architecture/ARCHITECTURE_BASELINE_V2.md). Owns **Entitlements**, configuration hierarchy, and Marketplace preparation per Baseline v2.

## Architecture v2 alignment

| Field | Value |
|-------|-------|
| **Classification** | Extended |
| **Report** | [ARCHITECTURE_ALIGNMENT_REPORT.md](../../architecture-alignment/ARCHITECTURE_ALIGNMENT_REPORT.md) |
| **Migration note** | config-service = ME Phase 1. Entitlement runtime checks (G-10). Marketplace prep — full pipeline in PI-09/10. |

## What This PI Delivers

- Full 3-layer multi-tenancy (data isolation, policy isolation, resource isolation)
- `config-service` — per-tenant configuration, feature flags, tool visibility (**effective_configuration** layers)
- **Entitlement** enforcement hooks for Commercial Pack grants (runtime checks in PI-08/09)
- Enterprise SSO integration (SAML, SCIM provisioning)
- Per-tenant resource quotas enforced at all layers
- Tenant onboarding workflow — self-service in under 15 minutes
- Enterprise SLA monitoring (p99 latency, uptime by tenant)
- Data residency controls (tenant data pinned to specified region)

## Key Multi-Tenancy Constraints

- One codebase for all tenants — no per-tenant code forks (MT3)
- All tenant isolation enforced in infrastructure, not application code (MT2)
- Tenant ID present in every Kafka message, DB query, and log line (SR3)
- New tenant onboarding does not require code changes (MT1)
