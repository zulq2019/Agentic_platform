# PI-01 — Review Checklist

Use this checklist for every PR in PI-01.

## Architecture
- [ ] No service makes a direct HTTP call to another service (all via Kafka)
- [ ] No business logic exists in PI-01 code (scaffold only)
- [ ] All config read from environment variables via Pydantic Settings
- [ ] No hardcoded IPs, ports, passwords, or API keys

## Code Quality
- [ ] `ruff check .` exits 0
- [ ] `black --check .` exits 0
- [ ] `mypy --strict` exits 0
- [ ] All new functions have type annotations
- [ ] No `TODO` or `FIXME` comments left in production code paths

## Database
- [ ] Every new table has `RLS ENABLED`
- [ ] Every new table has a `tenant_isolation` policy
- [ ] Migration has a `downgrade()` implementation
- [ ] Migration is idempotent (safe to run twice)

## Kafka
- [ ] Every produced message is validated against EventEnvelope before publishing
- [ ] Consumer commits offset only after successful processing
- [ ] Failed messages are routed to DLQ, not silently dropped

## Testing
- [ ] Unit test coverage ≥ 80% for new code
- [ ] New integration tests added for cross-service interactions
- [ ] Contract validation tests pass

## Security
- [ ] `detect-secrets scan` finds zero new secrets
- [ ] Trivy scan added to CI for new Dockerfiles
- [ ] Non-root user in all Dockerfiles

## Documentation
- [ ] `.env.example` updated for any new environment variables
- [ ] PR description explains what changed and why
