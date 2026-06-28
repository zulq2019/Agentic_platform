# PI-01 — Features

## F1. Service Scaffolding

Create the directory and boilerplate for all 16 platform services.

Each service must contain:
- `Dockerfile` (multi-stage, non-root user, health check instruction)
- `pyproject.toml` or `go.mod` depending on language
- `src/main.py` or `src/main.go` — FastAPI or Echo app
- `GET /health/live` → `{ "status": "ok" }`
- `GET /health/ready` → `{ "status": "ok", "checks": {...} }`
- `GET /metrics` → Prometheus text format
- `GET /info` → `{ "service": "...", "version": "...", "contract_version": "..." }`
- Structured JSON logger with `service`, `task_id`, `workflow_run_id` fields
- OTEL auto-instrumentation wired

**Services:** api-gateway, auth-service, rbac-service, orchestrator-service, workflow-engine, task-engine, approval-service, agent-runtime, agent-registry, model-router, tool-registry, memory-service, audit-service, secrets-service, policy-engine, config-service

## F2. Shared Library — aep-common

Python package providing shared utilities imported by all services:

- `aep_common.logging` — structured JSON logger factory
- `aep_common.health` — FastAPI health router (live + ready)
- `aep_common.kafka` — producer + consumer base classes with envelope validation
- `aep_common.schemas` — Pydantic models for all event envelope types
- `aep_common.tracing` — OTEL tracer factory
- `aep_common.errors` — typed platform exception hierarchy
- `aep_common.security` — JWT decode + tenant_id extraction middleware

## F3. Local Development Environment

`docker-compose.yml` starting:
- All 16 services
- Kafka (3 brokers via KRaft)
- Zookeeper-free Kafka topic provisioning container
- PostgreSQL 16
- Redis 7
- OTEL Collector
- Prometheus
- Grafana (pre-loaded with service health dashboard)

`Makefile` targets:
- `make dev-up` — start everything
- `make dev-down` — stop and clean
- `make dev-logs` — tail all service logs
- `make migrate` — run all DB migrations
- `make test` — run full test suite

## F4. Kafka Topic Provisioning

Script and Docker init container that creates:
- All 11 event topics with correct partition count and replication factor
- Per-service produce/consume ACLs
- Dead letter queue topic `aep.dlq`

## F5. Database Migration Runner

Alembic migration files for all tables defined in `ARCHITECTURE.md`, with:
- Versioned, ordered migration chain
- RLS policy on every table
- Indexes for common query patterns
- Seed data for development (test tenants, sample agent registrations)

## F6. CI/CD Pipeline — Phase 1

GitHub Actions workflows:
- `ci.yml` — runs on every PR: lint (ruff, black, eslint), unit tests, contract validation, build
- `cd-dev.yml` — runs on merge to `main`: build + push images to registry, deploy to dev cluster
