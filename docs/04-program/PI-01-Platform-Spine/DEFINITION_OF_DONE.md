# PI-01 — Definition of Done

A PI-01 deliverable is **Done** when ALL of the following are true:

## Code Quality
- [ ] Zero lint warnings (ruff, black, pylint)
- [ ] Zero type errors (mypy strict mode)
- [ ] Unit test coverage ≥ 80% on all new code
- [ ] All tests pass in CI

## Architecture Compliance
- [ ] No hardcoded credentials anywhere in the codebase
- [ ] No service makes a direct HTTP call to another service
- [ ] All inter-service communication is via Kafka with EventEnvelope
- [ ] Every table has RLS enabled with tenant_id policy

## Operational Readiness
- [ ] All 16 services expose `/health/live`, `/health/ready`, `/metrics`, `/info`
- [ ] All services emit structured JSON logs with task_id and workflow_run_id
- [ ] OTEL traces are flowing to Tempo backend
- [ ] Prometheus metrics are being scraped from all services
- [ ] Grafana health dashboard is green

## Security
- [ ] Trivy scan: zero critical or high CVEs in any container image
- [ ] detect-secrets: zero findings
- [ ] pip-audit: zero critical CVEs in Python dependencies

## Documentation
- [ ] `README.md` updated with setup steps
- [ ] All new environment variables documented in `.env.example`
- [ ] TASKS.md updated to mark PI-01 stories complete

## PI Handoff
- [ ] PI-02 kick-off meeting held
- [ ] PI-02 team has confirmed: all services boot, Kafka topics exist, DB migrated
- [ ] PI-01 retrospective documented
