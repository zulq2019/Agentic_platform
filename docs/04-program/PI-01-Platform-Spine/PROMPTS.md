# PI-01 — AI Implementation Prompts

Use these prompts when working with an AI assistant (Claude, Cursor) to implement PI-01 deliverables. Always include the referenced files as context.

---

## PROMPT-01.01 — Scaffold a Platform Service

```
Context files to attach: CLAUDE.md, contracts/agent-contract.schema.json

Implement the service scaffold for `{service-name}` in the Agentic Engineering Platform.

Container: platform/{service-name}/
Constitutional constraints: AR4 (event bus only), SR1 (no hardcoded secrets)

Requirements:
- FastAPI application factory in src/main.py
- GET /health/live → {"status": "ok"}
- GET /health/ready → {"status": "ok", "checks": {}} (check DB and Kafka connectivity)
- GET /metrics → Prometheus text format via prometheus_client
- GET /info → {"service": "{service-name}", "version": "0.1.0", "contract_version": "1.0"}
- Structured JSON logger via structlog with service, task_id, workflow_run_id fields
- Pydantic Settings config reading from environment variables
- Multi-stage Dockerfile with non-root user
- pyproject.toml with FastAPI, structlog, prometheus-client, opentelemetry-sdk

Tests required:
- test_health.py: liveness returns 200, readiness returns 503 when dependency is down

Forbidden:
- No hardcoded values (SR1)
- No direct calls to other services via HTTP (AR4)
```

---

## PROMPT-01.02 — aep-common Library

```
Context files: CLAUDE.md, ARCHITECTURE.md (aep-common section)

Implement the `aep-common` shared Python library for the Agentic Engineering Platform.

Package: sdk/aep-common/
Constitutional constraints: AR4, SR1, SR5

Modules to implement:
1. aep_common.logging — structlog factory, adds service/task_id/workflow_run_id/tenant_id
2. aep_common.health — FastAPI router with /health/live and /health/ready
3. aep_common.kafka — KafkaProducer and KafkaConsumer base classes using confluent-kafka
   - Producer validates every message against EventEnvelope schema before publishing
   - Consumer deserialises envelope and routes to handler
4. aep_common.schemas — Pydantic models for EventEnvelope and all event type payloads
5. aep_common.tracing — OpenTelemetry tracer factory with auto-propagation
6. aep_common.errors — typed exception hierarchy (PlatformError, TaskError, AgentError, ToolError)
7. aep_common.security — JWT decode middleware, extracts tenant_id and sets app.current_tenant_id

Tests required:
- test_kafka_envelope.py: publishing without required field raises ValidationError
- test_rls_context.py: security middleware sets correct tenant_id

Forbidden: No vendor SDK imports outside infrastructure/ modules
```

---

## PROMPT-01.03 — Kafka Topic Provisioning

```
Context files: CLAUDE.md, docs/artifacts/TECHNICAL_ARCHITECTURE.md (Event Flow section)

Implement a Kafka topic provisioning script for the Agentic Engineering Platform.

File: scripts/provision_kafka_topics.py
Constitutional constraints: AR4

Topics to create (from ARCHITECTURE.md Event Topology):
- aep.task.created (24 partitions, RF=3)
- aep.agent.started (24 partitions, RF=3)
- aep.agent.completed (24 partitions, RF=3)
- aep.agent.failed (24 partitions, RF=3)
- aep.approval.requested (12 partitions, RF=3)
- aep.approval.granted (12 partitions, RF=3)
- aep.approval.denied (12 partitions, RF=3)
- aep.state.transitioned (24 partitions, RF=3)
- aep.rollback.triggered (12 partitions, RF=3)
- aep.audit.events (48 partitions, RF=3)
- aep.dlq (12 partitions, RF=3)

Also create ACLs: each service may only produce/consume its own topics.
Script must be idempotent (safe to run multiple times).

Tests: verify_kafka_topology.py confirms all topics exist with correct config.
```

---

## PROMPT-01.04 — Database Migrations

```
Context files: CLAUDE.md, docs/artifacts/TECHNICAL_ARCHITECTURE.md (Database Architecture section)

Implement Alembic database migrations for the Agentic Engineering Platform.

Directory: platform/shared/migrations/
Constitutional constraints: SR3 (tenant_id in every query), SR5 (input validation), MT2

Migrations to implement:
1. 001_create_schemas.py — create PostgreSQL schemas: orchestrator, agents, audit, memory
2. 002_workflow_runs.py — table from DATA_MODEL.md including RLS
3. 003_tasks.py — tasks table with approval_record JSONB, RLS
4. 004_agents.py — agent registry table with capabilities JSONB, RLS
5. 005_tools.py — tool registry table, RLS
6. 006_approval_records.py — gate decisions, RLS
7. 007_memory_entries.py — pgvector table with ivfflat index, RLS

Every migration must:
- Enable RLS immediately after CREATE TABLE
- Create the tenant_isolation policy using current_setting('app.current_tenant_id')
- Be reversible (downgrade() implemented)

Tests required:
- test_rls_isolation.py: query in tenant A context returns 0 rows from tenant B
```

---

## PROMPT-01.05 — CI/CD Pipeline

```
Context files: CLAUDE.md (CI/CD section), CONSTITUTION.md

Implement GitHub Actions CI/CD workflows for the Agentic Engineering Platform.

Files:
- .github/workflows/ci.yml — runs on every PR to main
- .github/workflows/cd-dev.yml — runs on merge to main

ci.yml stages (must complete in < 8 minutes):
1. Lint: ruff + black (Python), eslint (TypeScript)
2. Unit Tests: pytest for every service that has tests
3. Contract Validation: python scripts/validate_contract.py on all contracts/
4. Build: docker build for all 16 services (can be parallelised)

cd-dev.yml stages:
1. Build + tag images with git SHA
2. Push to container registry
3. Deploy to dev cluster via kubectl apply

Forbidden:
- No secrets in workflow files (SR1)
- No skip-checks flags
- No direct pushes to main (branch protection)
```
