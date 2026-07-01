# PI-04-Workflow-Framework — Implementation Guide

## Architecture Pattern

All services in Memory follow the standard layered architecture:

```
platform/{service-name}/
+-- src/
¦   +-- main.py           # FastAPI app factory
¦   +-- api/              # HTTP route handlers
¦   +-- domain/           # Business logic (no framework imports)
¦   +-- infrastructure/   # DB, Kafka, Redis, external clients
¦   +-- config.py         # Pydantic Settings
+-- tests/
¦   +-- unit/
¦   +-- integration/
+-- Dockerfile
+-- pyproject.toml
```

## Key Domain Components

See README.md for the list of services. Each service's domain/ contains:
- Service class: orchestrates domain logic
- Repository class: data access (DB or Redis)
- Event publisher: Kafka event production via aep_common.kafka

## Dependency Injection Pattern

```python
# All services use FastAPI dependency injection
from fastapi import FastAPI, Depends
from aep_common.logging import get_logger
from aep_common.kafka import KafkaProducer

app = FastAPI()

async def get_producer() -> KafkaProducer:
    return KafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)

@app.post("/endpoint")
async def handler(producer: KafkaProducer = Depends(get_producer)):
    ...
```

## Error Handling

```python
from aep_common.errors import PlatformError

class ServiceSpecificError(PlatformError):
    """Raised when service-specific invariant is violated."""
    pass

# All errors are caught at the API layer and return structured JSON:
# {"error": "ServiceSpecificError", "message": "...", "task_id": "..."}
```

## Constitutional Compliance Checklist for This PI

- [ ] No service calls another service via HTTP (AR4)
- [ ] No business logic added to orchestrator-service (AR2)
- [ ] All credentials via environment variables (SR1)
- [ ] tenant_id in every query (SR3)
- [ ] Events use standard envelope (AR6)
