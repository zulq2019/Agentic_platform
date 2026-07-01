# PI-07 — Governance

**Status:** `PLANNED`  
**Depends on:** PI-03 complete (orchestrator + approval service operational)  
**Target:** Sprint 26–29 (weeks 51–58)  
**Architecture baseline:** [ARCHITECTURE_BASELINE_V2.md](../../architecture/ARCHITECTURE_BASELINE_V2.md). Implements **Governance Contract** (versioning, approval, audit, lifecycle) for all Platform Objects at runtime.

## Architecture v2 alignment

| Field | Value |
|-------|-------|
| **Classification** | Extended |
| **Report** | [ARCHITECTURE_ALIGNMENT_REPORT.md](../../engineering/ARCHITECTURE_ALIGNMENT_REPORT.md) |
| **Migration note** | Metadata publish/approve audit hooks added at PI-09 boundary. RBAC ≠ Policy ≠ Secrets unchanged. |

## What This PI Delivers

- `policy-engine` (OPA-backed) governs every agent action before execution
- `audit-service` writes every platform event to ClickHouse — immutable, append-only
- `auth-service` — full OIDC/SAML integration with Entra ID / Okta / Cognito
- `rbac-service` — role-permission model for approvers and administrators
- Governance dashboards: gate audit trail, named approver report, compliance exports
- Explainability: every workflow outcome is fully reconstructable from the audit log alone

## Key Constitutional Constraints

- Every agent action checked against policy before execution (H1)
- Audit log is append-only — no UPDATE, no DELETE, ever (E3)
- RBAC, Policy Engine, and Secrets are three separate services (S1)
- Every state transition produces an immutable audit event (E2)

## Governance Deliverables for Enterprise

- CSV/JSON export of all gate decisions with approver names (compliance)
- Audit query API: reconstruct any workflow outcome from ClickHouse
- Policy-as-code: per-tenant OPA bundles stored in Git
