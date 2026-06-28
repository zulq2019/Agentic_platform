# PI-07 — Sprint Plan

## Sprint 26 (Days 251–260): Policy Engine

| # | Task | Points |
|---|------|--------|
| 26.1 | Implement `policy-engine` OPA integration | 4 |
| 26.2 | Define base policy bundle (deny-all default, explicit allows) | 3 |
| 26.3 | Per-tenant policy bundle loading from Git | 3 |
| 26.4 | Wire policy check into `agent-runtime` before execute() | 2 |
| 26.5 | Test: forbidden action returns 403, permitted returns 200 | 2 |

---

## Sprint 27 (Days 261–270): Audit Service + ClickHouse

| # | Task | Points |
|---|------|--------|
| 27.1 | Implement `audit-service` Kafka consumer (subscribes ALL topics) | 3 |
| 27.2 | Implement ClickHouse writer — append-only, no UPDATE/DELETE | 4 |
| 27.3 | Implement audit query API: reconstruct workflow from event log | 3 |
| 27.4 | Test: verify no UPDATE or DELETE possible on audit tables | 2 |

---

## Sprint 28 (Days 271–280): Auth + RBAC

| # | Task | Points |
|---|------|--------|
| 28.1 | Implement `auth-service` OIDC flow (Entra ID / Okta) | 4 |
| 28.2 | Implement `auth-service` JWT issuance and validation | 3 |
| 28.3 | Implement `rbac-service` role assignment | 2 |
| 28.4 | Implement `rbac-service` permission check (who approves which gate) | 3 |

---

## Sprint 29 (Days 281–290): Governance Dashboards + PI-07 Close

| # | Task | Points |
|---|------|--------|
| 29.1 | Grafana governance dashboard (gate audit trail, named approvers) | 3 |
| 29.2 | Compliance export API (CSV/JSON of all gate decisions) | 2 |
| 29.3 | Policy-as-code: per-tenant bundles in Git | 2 |
| 29.4 | Explainability test: reconstruct full workflow from audit log | 2 |
| 29.5 | PI-07 retrospective + PI-08 kick-off | 1 |
