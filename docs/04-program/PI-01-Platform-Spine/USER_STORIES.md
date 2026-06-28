# PI-01 — User Stories

> Stories only. Acceptance criteria live in `ACCEPTANCE_CRITERIA.md`.
> Implementation guidance lives in `IMPLEMENTATION.md`.
> Capability context lives in `CAPABILITIES.md`.

---

### US-01.01 — Service Bootstrap

**As a** platform engineer,  
**I want** every service to boot and expose health and metrics endpoints,  
**so that** I can verify the platform is alive at a glance.

**Capability:** CAP-01  
**Sprint:** 1

---

### US-01.02 — Local Developer Environment

**As a** backend developer,  
**I want** to run the entire platform locally with one command,  
**so that** I can develop and test without a cloud account.

**Capability:** CAP-03  
**Sprint:** 1

---

### US-01.03 — Event Bus Ready

**As a** backend developer,  
**I want** Kafka topics pre-provisioned with correct configuration,  
**so that** I can start publishing and consuming events without manual setup.

**Capability:** CAP-04  
**Sprint:** 2

---

### US-01.04 — Database Migrated

**As a** backend developer,  
**I want** the database schema applied automatically with tenant isolation enforced,  
**so that** I can start writing code against real tables immediately.

**Capability:** CAP-05  
**Sprint:** 2

---

### US-01.05 — CI Feedback

**As a** developer,  
**I want** the CI pipeline to give me lint, test, and build feedback within 8 minutes,  
**so that** I can iterate quickly.

**Capability:** CAP-06  
**Sprint:** 3

---

### US-01.06 — Shared Logging

**As a** backend developer,  
**I want** a shared logging library that automatically adds `task_id`, `workflow_run_id`, and `tenant_id` to every log line,  
**so that** I can trace any event across all services without manual instrumentation.

**Capability:** CAP-02  
**Sprint:** 1

---

### US-01.07 — Observability Baseline

**As an** SRE,  
**I want** Prometheus metrics and OTEL traces flowing from all services from day one,  
**so that** I can observe the platform from the first deployment.

**Capability:** CAP-01, CAP-03  
**Sprint:** 3
