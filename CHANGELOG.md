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
- Security gates: pip-audit, detect-secrets baseline, Trivy image scan (CRITICAL/HIGH, fixable CVEs only)
- mypy --strict on `aep_common`; acceptance tests for AC-01.04 CI pipeline criteria
- US-01.05 CI enforces ≥80% coverage on `validate_contract.py`

### Changed (US-01.05)

- Trivy container scans use `ignore-unfixed: true` during PI-01 bootstrap so CI blocks only on vendor-patched CRITICAL/HIGH CVEs (PI-level zero-unfixed-CVE gate deferred — see TASKS.md)
- Gateway image upgraded to Go 1.25.11 (via `GOTOOLCHAIN`) and Alpine 3.21 for patched stdlib and dependency CVEs

### Added (US-01.02)

- Observability stack in docker-compose: OTEL Collector, Prometheus, Grafana
- PostgreSQL image upgraded to `pgvector/pgvector:pg16`
- `scripts/verify_dev_environment.py` and `scripts/generate_prometheus_config.py`
- README local development onboarding (clone → `make dev-up`)

### Added (US-01.03)

- Kafka topic catalog (11 topics + `aep.dlq`) with idempotent provisioning via `kafka-init`
- `aep_common.kafka`: EventEnvelope validation, producer/consumer with DLQ routing
- `scripts/provision_kafka_topics.py` and `scripts/verify_kafka_topology.py`
- ACL catalog at `infra/kafka/acls.yaml` (broker enforcement deferred to deployment PI / Sprint 2.2)
- Host Kafka access moved to `localhost:9094` (containers continue using `kafka:9092`)
