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

### Added (US-01.02)

- Observability stack in docker-compose: OTEL Collector, Prometheus, Grafana
- PostgreSQL image upgraded to `pgvector/pgvector:pg16`
- `scripts/verify_dev_environment.py` and `scripts/generate_prometheus_config.py`
- README local development onboarding (clone → `make dev-up`)

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
