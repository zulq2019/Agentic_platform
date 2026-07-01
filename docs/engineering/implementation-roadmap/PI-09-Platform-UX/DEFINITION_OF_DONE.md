# PI-09-Platform-UX — Definition of Done

A Developer Experience deliverable is Done when ALL of the following are true:

## Code
- [ ] Zero lint warnings (ruff, black)
- [ ] Zero type errors (mypy strict)
- [ ] Unit test coverage = 80%
- [ ] All tests pass in CI

## Architecture
- [ ] No hardcoded credentials
- [ ] No direct service-to-service HTTP calls
- [ ] All events use EventEnvelope schema
- [ ] RLS on every new database table
- [ ] tenant_id in every query and log line

## Security
- [ ] Trivy: zero critical/high CVEs
- [ ] detect-secrets: zero findings

## Observability
- [ ] OTEL traces flowing
- [ ] Prometheus metrics scraping
- [ ] Grafana dashboard updated

## Documentation
- [ ] README.md current
- [ ] .env.example updated
- [ ] TASKS.md updated

## PI Handoff
- [ ] Next PI team confirmed handoff criteria met
- [ ] Retrospective completed
