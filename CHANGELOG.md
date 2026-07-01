# Changelog

All notable changes to the Agentic Engineering Platform are documented here.

## [Unreleased]

### Added

- **ENG-SKILLS-V3** — Skills Release V3: Architecture v2.0 engineering skill library under `.ai/`
  - `implement-story` v5.1: 12 enterprise phases, risk-based approval, Architecture Think Mode
  - `review-story`, `generate-tests`, `security-review`, `performance-review`, `regression-review`, `release-story`: v2.0/v4.0 Architecture v2.0 extensions
  - `next` v1.0: repository-agnostic engineering orchestrator
  - `health-check` v1.0: read-only engineering governance auditor (35 checks, 8 scores, 7 reports)
- US-01.01: 16-service platform bootstrap with `/health/live`, `/health/ready`, `/metrics`, `/info`
- Shared `aep_common` library: health probes, metrics, structured logging, app factory
- Docker Compose stack for local development (Postgres, Redis, Kafka, 16 services)
- CI workflow: lint, format check, unit tests for US-01.01

### Fixed

- Migration `005_app_role_grants` no longer grants on metadata tables before they exist; `006_platform_object_tables` grants `aep_app` access after table creation
- CI lint: remove unused import in `test_us_02_01_platform_object.py`

### Changed

- Python service Dockerfiles use multi-stage builds with non-root runtime user
- Service config defaults no longer embed database credentials; use `POSTGRES_DSN` env var

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

### Added (US-01.04)

- Alembic migrations for orchestrator, agents, tools, memory, and approval schemas
- Row-level security (`tenant_isolation` policy) on all platform tables
- `make migrate` runs versioned migrations via `scripts/run_migrations.py`
- `aep_common.db` tenant context helpers for RLS-scoped queries
- Database migration and RLS isolation tests (`story_us_01_04` marker)
- CI runs `story_us_01_04` unit tests; `AEP_APP_DB_PASSWORD` required for `make migrate`

### Changed (US-01.04)

- Database DSNs and app role password must be supplied via environment variables (no hardcoded defaults in library or migration code)
- Memory embedding index uses HNSW instead of IVFFlat for empty-table safety

### Fixed (US-01.04)

- CI runs US-01.04 database integration tests (AC-01.03) against Postgres service job
- Migration `005_app_role_grants` updates `aep_app` password on re-run and revokes default privileges on downgrade

### Added (US-01.06)

- `aep_common.logging`: HTTP header binding, envelope correlation, `correlation_context` manager
- FastAPI middleware in `create_platform_app` binds `x-task-id`, `x-workflow-run-id`, `x-tenant-id` per request
- Kafka `EventConsumer` binds envelope correlation IDs for handler-scoped structured logs
- CI job for `story_us_01_06` with ≥80% coverage on `aep_common.logging` and `aep_common.app`

### Added (US-01.07)

- `aep_common.tracing`: OTLP trace export, FastAPI auto-instrumentation, shared `get_tracer()`
- OTEL collector exports traces to Grafana Tempo (`observability/tempo/tempo.yaml`)
- Grafana Tempo datasource provisioned; `verify_dev_environment.py` checks Tempo readiness
- Platform app lifespan configures tracing from `otel_exporter_otlp_endpoint`
- API Gateway (Go): OTLP trace export via `otelecho` when `OTEL_EXPORTER_OTLP_ENDPOINT` is set
- `ACCEPTANCE_CRITERIA.md` AC-01.07 and `INFRASTRUCTURE.md` US-01.07 sections added
- CI job for `story_us_01_07` with ≥80% coverage on `aep_common.tracing` and `aep_common.app`
