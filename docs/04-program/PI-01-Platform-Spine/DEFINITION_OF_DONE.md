# PI-01 — Definition of Done

> A PI-01 deliverable is **Done** when **every** item below is checked.
> This document absorbs the PR review checklist. Engineers use this as the single
> source of truth for what "complete" means — at the story level and at the PI level.

---

## Story-Level Gate (applies to every PR in PI-01)

### Architecture

- [ ] No service makes a direct HTTP call to another service — all inter-service communication is via Kafka with EventEnvelope
- [ ] No business logic exists in PI-01 code — scaffold and infrastructure only
- [ ] All config read from environment variables via Pydantic Settings
- [ ] No hardcoded IPs, ports, passwords, or API keys anywhere

### Code Quality

- [ ] `ruff check .` exits 0
- [ ] `black --check .` exits 0
- [ ] `mypy --strict` exits 0
- [ ] All new functions have type annotations
- [ ] No `TODO` or `FIXME` in production code paths
- [ ] Unit test coverage ≥ 80% on all new code
- [ ] All tests pass in CI

### Database (if migration included)

- [ ] Every new table has `ENABLE ROW LEVEL SECURITY`
- [ ] Every new table has a `tenant_isolation` policy
- [ ] Migration has a `downgrade()` implementation
- [ ] Migration is idempotent — safe to run twice without error

### Kafka (if event code included)

- [ ] Every produced message validated against EventEnvelope before publishing
- [ ] Consumer commits offset only after successful processing
- [ ] Failed messages routed to `aep.dlq` — never silently dropped

### Security

- [ ] `detect-secrets scan` finds zero new secrets
- [ ] Trivy scan included in CI for any new Dockerfile
- [ ] Non-root user in all Dockerfiles
- [ ] `pip-audit` finds zero critical CVEs in Python dependencies

### Documentation

- [ ] `.env.example` updated for every new environment variable
- [ ] PR description explains what changed and why

---

## PI-Level Gate (required before PI-01 is closed)

### Operational Readiness

- [ ] All 16 services expose `/health/live`, `/health/ready`, `/metrics`, `/info`
- [ ] All 16 `/health/ready` endpoints return 200 after `make dev-up`
- [ ] All services emit structured JSON logs with `task_id`, `workflow_run_id`, and `tenant_id`
- [ ] OTEL traces flowing to Tempo backend from all services
- [ ] Prometheus scraping metrics from all 16 services
- [ ] Grafana service health dashboard is green

### Event Bus

- [ ] All 11 topics + `aep.dlq` provisioned with correct partition counts and ACLs
- [ ] `scripts/verify_kafka_topology.py` exits 0
- [ ] Kafka round-trip test passes: produce → consume → ack with valid EventEnvelope

### Database

- [ ] All migrations applied via `make migrate` — idempotent
- [ ] RLS verified: cross-tenant query returns 0 rows (`pytest tests/db/test_rls_isolation.py`)
- [ ] Seed data for dev environment applied

### CI/CD

- [ ] `ci.yml` completes in under 8 minutes on a standard GitHub runner
- [ ] `cd-dev.yml` deploys to dev cluster on merge to `main`
- [ ] Contract validation step blocks PRs that break any schema in `contracts/`

### Security

- [ ] Trivy scan: zero critical or high CVEs in all 16 container images
- [ ] `detect-secrets`: zero findings across the full repository
- [ ] `pip-audit`: zero critical CVEs in all Python dependencies

### Documentation

- [ ] `README.md` updated with complete setup steps
- [ ] All environment variables documented in `.env.example` for each service
- [ ] `TASKS.md` updated to mark all PI-01 stories complete

### PI Handoff

- [ ] PI-01 retrospective documented
- [ ] PI-02 kick-off meeting held
- [ ] PI-02 team confirms: all services boot, Kafka topics exist, database migrated, `aep-common` importable
