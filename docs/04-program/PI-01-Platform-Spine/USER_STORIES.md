# PI-01 — User Stories

## Infrastructure Stories

### US-01.01 — Service Bootstrap
**As a** platform engineer,  
**I want** every service to boot and expose health + metrics endpoints,  
**so that** I can verify the platform is alive at a glance.

**Acceptance:** `docker compose up` → all 16 `/health/live` return 200 within 60s.

---

### US-01.02 — Local Developer Environment
**As a** backend developer,  
**I want** to run the entire platform locally with one command,  
**so that** I can develop and test without a cloud account.

**Acceptance:** `make dev-up` brings up all services + dependencies in < 5 minutes on a 16 GB machine.

---

### US-01.03 — Event Bus Ready
**As a** backend developer,  
**I want** Kafka topics pre-provisioned with correct configuration,  
**so that** I can start publishing and consuming events without manual setup.

**Acceptance:** All 11 topics exist with correct partitions and ACLs after `make dev-up`.

---

### US-01.04 — Database Migrated
**As a** backend developer,  
**I want** the database schema to be applied automatically on startup,  
**so that** I can start writing code against real tables immediately.

**Acceptance:** `make migrate` applies all migrations idempotently; cross-tenant query returns 0 rows.

---

### US-01.05 — CI Feedback
**As a** developer,  
**I want** the CI pipeline to give me lint, test, and build feedback within 8 minutes,  
**so that** I can iterate quickly.

**Acceptance:** GitHub Actions `ci.yml` completes within 8 minutes on a standard runner.

---

### US-01.06 — Shared Logging
**As a** backend developer,  
**I want** a shared logging library that automatically adds `task_id`, `workflow_run_id`, and `tenant_id` to every log line,  
**so that** I can trace any event across all services.

**Acceptance:** Log lines from any service contain all three correlation IDs when in task context.

---

### US-01.07 — Observability Baseline
**As an** SRE,  
**I want** Prometheus metrics and OTEL traces from all services from day one,  
**so that** I can observe the platform from the first deployment.

**Acceptance:** Grafana shows live metrics from all 16 services within 5 minutes of `make dev-up`.
