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

### Added (US-01.03)

- Kafka topic catalog (11 topics + `aep.dlq`) with idempotent provisioning via `kafka-init`
- `aep_common.kafka`: EventEnvelope validation, producer/consumer with DLQ routing
- `scripts/provision_kafka_topics.py` and `scripts/verify_kafka_topology.py`
- ACL catalog at `infra/kafka/acls.yaml` (broker enforcement deferred to deployment PI / Sprint 2.2)
- Host Kafka access moved to `localhost:9094` (containers continue using `kafka:9092`)
