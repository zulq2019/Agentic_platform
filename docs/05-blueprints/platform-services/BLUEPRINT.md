# Blueprint: Platform Services (16 Microservices)

**Status:** DEFERRED — Implemented progressively through PI-01 to PI-09  
**Target PI:** PI-01 (scaffolding) → PI-09 (all services production-ready)

## Purpose

This blueprint describes the full directory structure and architecture for all 16 platform microservices. Actual code is created when each PI begins, not before.

## Why Deferred

Creating empty code folders before implementation begins:
- misleads new contributors about what is actually built
- creates dead code paths that CI must handle with stubs
- obscures the current implementation maturity

Each service folder is created at the start of its PI and contains production code from day one.

## Service Delivery Schedule

| Service | Created In | Scaffolded | Production |
|---------|-----------|-----------|-----------|
| api-gateway | PI-01 | PI-01 | PI-09 |
| auth-service | PI-01 | PI-01 | PI-07 |
| rbac-service | PI-01 | PI-01 | PI-07 |
| orchestrator-service | PI-01 | PI-03 | PI-03 |
| workflow-engine | PI-01 | PI-03 | PI-03 |
| task-engine | PI-01 | PI-03 | PI-03 |
| approval-service | PI-01 | PI-03 | PI-03 |
| agent-runtime | PI-01 | PI-02 | PI-02 |
| agent-registry | PI-01 | PI-02 | PI-02 |
| model-router | PI-01 | PI-02 | PI-02 |
| tool-registry | PI-01 | PI-05 | PI-05 |
| memory-service | PI-01 | PI-04 | PI-04 |
| audit-service | PI-01 | PI-07 | PI-07 |
| secrets-service | PI-01 | PI-05 | PI-05 |
| policy-engine | PI-01 | PI-07 | PI-07 |
| config-service | PI-01 | PI-08 | PI-08 |

## Directory Structure (target state at GA)

```
platform/
├── api-gateway/         # Go + Echo
├── auth-service/        # Python + FastAPI
├── rbac-service/        # Python + FastAPI
├── orchestrator-service/
├── workflow-engine/
├── task-engine/
├── approval-service/
├── agent-runtime/
├── agent-registry/
├── model-router/
├── tool-registry/
├── memory-service/
├── audit-service/
├── secrets-service/
├── policy-engine/
├── config-service/
└── shared/
    ├── migrations/      # Alembic migrations
    └── proto/           # gRPC proto definitions
```

## Standard Service Layout

```
platform/{service-name}/
├── src/
│   ├── main.py
│   ├── api/
│   │   ├── health.py
│   │   ├── metrics.py
│   │   └── routes.py
│   ├── domain/
│   │   └── {service}_service.py
│   ├── infrastructure/
│   │   ├── db.py
│   │   ├── kafka.py
│   │   └── redis.py
│   └── config.py
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
├── pyproject.toml
└── .env.example
```

## Implementation Reference

- See `docs/04-program/PI-01-Platform-Spine/IMPLEMENTATION.md` for scaffold pattern
- See `docs/artifacts/TECHNICAL_ARCHITECTURE.md` Section 7 for the microservices map
- See `contracts/` for all JSON Schema contracts services must implement
