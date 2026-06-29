# Changelog

All notable changes to the Agentic Engineering Platform are documented here.

## [Unreleased]

### Added

- US-01.01: 16-service platform bootstrap with `/health/live`, `/health/ready`, `/metrics`, `/info`
- Shared `aep_common` library: health probes, metrics, structured logging, app factory
- Docker Compose stack for local development (Postgres, Redis, Kafka, 16 services)
- CI workflow: lint, format check, unit tests for US-01.01

### Changed

- Python service Dockerfiles use multi-stage builds with non-root runtime user
- Service config defaults no longer embed database credentials; use `POSTGRES_DSN` env var
- Logging includes correlation ID context vars (`task_id`, `workflow_run_id`, `tenant_id`)

### Added (US-01.05)

- CI pipeline Phase 1: parallel quality, golangci-lint, and 16-container build matrix
- `scripts/validate_contract.py` bulk mode for `contracts/` directory validation
- Security gates: pip-audit, detect-secrets baseline, Trivy image scan (CRITICAL/HIGH)
- mypy --strict on `aep_common`; acceptance tests for AC-01.04 CI pipeline criteria

### Added (US-01.02)

- Observability stack in docker-compose: OTEL Collector, Prometheus, Grafana
- PostgreSQL image upgraded to `pgvector/pgvector:pg16`
- `scripts/verify_dev_environment.py` and `scripts/generate_prometheus_config.py`
- README local development onboarding (clone → `make dev-up`)
