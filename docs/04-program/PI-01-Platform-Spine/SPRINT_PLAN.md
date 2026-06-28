# PI-01 — Sprint Plan

## Sprint 1 (Days 1–10): Foundation

| # | Task | Owner | Points |
|---|------|-------|--------|
| 1.1 | Create `aep-common` package with logging, health, errors | Backend Lead | 3 |
| 1.2 | Scaffold `orchestrator-service` with health + metrics endpoints | Backend Lead | 2 |
| 1.3 | Scaffold `agent-runtime` and `agent-registry` | Backend | 2 |
| 1.4 | Scaffold remaining 13 services | Backend | 5 |
| 1.5 | Write Dockerfile for each service (multi-stage, non-root) | DevOps | 3 |
| 1.6 | Write `docker-compose.yml` with Kafka, PG, Redis | DevOps | 3 |
| 1.7 | Verify all 16 `/health/live` endpoints return 200 | QA | 2 |

**Sprint Goal:** `docker compose up` → 16 green health endpoints.

---

## Sprint 2 (Days 11–20): Event Bus + Database

| # | Task | Owner | Points |
|---|------|-------|--------|
| 2.1 | Kafka topic provisioning script (11 topics + DLQ) | Backend | 3 |
| 2.2 | Per-service Kafka ACLs | DevOps | 2 |
| 2.3 | `aep_common.kafka` producer + consumer base classes | Backend Lead | 3 |
| 2.4 | Alembic migration: `workflow_runs`, `tasks` tables | Backend | 3 |
| 2.5 | Alembic migration: `agents`, `tools`, `approval_records` | Backend | 3 |
| 2.6 | RLS policies on all tables | Backend Lead | 2 |
| 2.7 | `pytest tests/db/test_rls_isolation.py` — cross-tenant check | QA | 2 |

**Sprint Goal:** Kafka operational + all tables migrated + RLS verified.

---

## Sprint 3 (Days 21–30): Observability + CI

| # | Task | Owner | Points |
|---|------|-------|--------|
| 3.1 | OTEL auto-instrumentation in `aep-common` | Backend Lead | 2 |
| 3.2 | OTEL Collector config (traces → Tempo, metrics → Prometheus) | DevOps | 2 |
| 3.3 | Prometheus scrape config for all 16 services | DevOps | 1 |
| 3.4 | Grafana service health dashboard | DevOps | 2 |
| 3.5 | GitHub Actions `ci.yml` — lint + unit + contract validation + build | DevOps | 3 |
| 3.6 | GitHub Actions `cd-dev.yml` — build + push + deploy to dev | DevOps | 3 |
| 3.7 | `make dev-up` onboarding trial with new team member (timed) | PM | 1 |

**Sprint Goal:** CI green + observability running + onboarding < 30 min.

---

## Sprint 4 (Days 31–40): Hardening + PI-01 Close

| # | Task | Owner | Points |
|---|------|-------|--------|
| 4.1 | Unit tests for `aep-common` (≥ 80% coverage) | Backend | 3 |
| 4.2 | Integration test: Kafka round-trip (produce → consume → ack) | QA | 2 |
| 4.3 | Contract validation CI step (validate_contract.py) | DevOps | 1 |
| 4.4 | Security scan (Trivy on all images) — zero critical/high | DevOps | 2 |
| 4.5 | Seed data migration for dev environment | Backend | 2 |
| 4.6 | PI-01 retrospective + PI-02 kick-off preparation | PM | 1 |
| 4.7 | Update TASKS.md to reflect PI-01 completion | PM | 1 |

**Sprint Goal:** All PI-01 acceptance criteria met. Handoff to PI-02 signed off.
