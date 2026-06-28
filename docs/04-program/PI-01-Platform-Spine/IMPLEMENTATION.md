# PI-01 — Implementation Guide

## Tech Stack Decisions

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Service language | Python 3.12 + FastAPI | All 15 platform services |
| API Gateway language | Go 1.22 + Echo | High-throughput, low-latency ingress |
| Shared library | `aep-common` Python package | DRY across all services |
| Message broker | Apache Kafka (KRaft mode) | No ZooKeeper dependency |
| OLTP database | PostgreSQL 16 | RLS, pgvector extension, JSONB |
| Cache | Redis 7 Cluster | Working context, rate limits, quotas |
| Migrations | Alembic | Versioned, reversible |
| Containerisation | Docker multi-stage | Minimal image size, non-root |
| Orchestration | Docker Compose (local), K8s (deployed) | |
| Observability | OpenTelemetry SDK + auto-instrumentation | |
| CI | GitHub Actions | |

## Service Scaffold Pattern

Every Python service follows this layout:

```
platform/{service-name}/
├── src/
│   ├── main.py           # FastAPI app factory
│   ├── api/
│   │   ├── health.py     # /health/live + /health/ready
│   │   ├── metrics.py    # /metrics (prometheus_client)
│   │   └── info.py       # /info
│   ├── domain/           # Business logic (empty at PI-01)
│   ├── infrastructure/   # DB, Kafka, Redis clients
│   └── config.py         # Pydantic Settings from env vars
├── tests/
│   └── test_health.py
├── Dockerfile
├── pyproject.toml
└── .env.example
```

## aep-common Package Structure

```python
# aep_common/logging.py
import structlog

def get_logger(service: str) -> structlog.BoundLogger:
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )
    return structlog.get_logger().bind(service=service)

# Usage in any service:
# from aep_common.logging import get_logger
# logger = get_logger("orchestrator-service")
# logger.info("task_dispatched", task_id=task_id, workflow_run_id=wfr_id)
```

## Kafka Envelope (from contracts/event-envelope.schema.json)

Every message on any Kafka topic MUST conform to:

```python
# aep_common/schemas/envelope.py
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class EventEnvelope(BaseModel):
    event_id: UUID
    event_type: str            # PascalCase: "TaskCreated"
    schema_version: str        # "1.0"
    emitted_by: str            # service name
    tenant_id: str
    task_id: UUID | None
    workflow_run_id: UUID | None
    timestamp: datetime
    payload: dict
```

## Database Migration Conventions

```python
# alembic/versions/001_initial_schema.py
# All migrations follow this pattern:
# - up() creates tables
# - down() drops tables
# - RLS policy applied immediately after CREATE TABLE
# - No migration may remove a column in < 2 versions

def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS orchestrator.workflow_runs (
            workflow_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id TEXT NOT NULL,
            ...
        );
        ALTER TABLE orchestrator.workflow_runs ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation ON orchestrator.workflow_runs
            USING (tenant_id = current_setting('app.current_tenant_id'));
    """)
```

## Health Endpoint Contract

```python
# aep_common/api/health.py — shared by all services
from fastapi import APIRouter
router = APIRouter()

@router.get("/health/live")
async def liveness():
    return {"status": "ok"}

@router.get("/health/ready")
async def readiness(db=Depends(get_db), kafka=Depends(get_kafka)):
    return {
        "status": "ok",
        "checks": {
            "database": await db.ping(),
            "kafka": await kafka.ping(),
        }
    }
```

## Environment Variables Pattern

Every service reads configuration exclusively from environment variables via Pydantic Settings. No hardcoded values. See `.env.example` in each service.

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str
    kafka_bootstrap_servers: str
    postgres_dsn: str
    redis_url: str
    otel_exporter_otlp_endpoint: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
```
