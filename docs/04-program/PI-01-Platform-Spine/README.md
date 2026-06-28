# PI-01 — Platform Spine

**Status:** `IN PROGRESS`  
**Phase:** 1 of 10  
**Target completion:** Sprint 4 (end of week 8)  
**Owner:** Platform Engineering Lead

---

## What This PI Delivers

The Platform Spine is the non-negotiable foundation every subsequent PI builds on. It has no user-visible features — it is the skeleton that makes everything else possible.

By the end of PI-01, the repository will contain:

- All 16 service directories scaffolded with Dockerfile, pyproject.toml/go.mod, health endpoints, and structured logging
- A running local developer environment (Docker Compose)
- Kafka cluster with all topics provisioned and ACLs applied
- PostgreSQL with all schemas, RLS policies, and migrations applied
- Redis with keyspace conventions enforced
- All 7 JSON Schema contracts validated in CI
- A CI/CD pipeline that lints, tests, builds, and deploys every service
- An OTEL collector wired to every service

## What Is Already Done

| Deliverable | Status |
|-------------|--------|
| `contracts/` — 7 JSON Schema files | ✅ Complete |
| `contracts/examples/coding-agent-registration.json` | ✅ Complete |
| `workflows/greenfield-v1.0.0.json` | ✅ Complete |
| `scripts/validate_contract.py` | ✅ Complete |
| Root documentation (CONSTITUTION, ARCHITECTURE, CLAUDE, etc.) | ✅ Complete |

## What Is Being Built in This PI

| Deliverable | Status |
|-------------|--------|
| 16 service skeletons | 🔲 Not started |
| Docker Compose local environment | 🔲 Not started |
| Kafka topic provisioning | 🔲 Not started |
| PostgreSQL migration runner | 🔲 Not started |
| Shared Python library (`aep-common`) | 🔲 Not started |
| CI pipeline (GitHub Actions) | 🔲 Not started |
| OTEL collector config | 🔲 Not started |

## Dependencies

- None. This PI has no upstream platform dependencies.

## Handoff to PI-02

PI-02 (Agent Runtime) requires:
- `agent-runtime/` service skeleton with health endpoint live
- `agent-registry/` service skeleton with health endpoint live
- Kafka topics `aep.task.created`, `aep.agent.started`, `aep.agent.completed`, `aep.agent.failed` provisioned
- PostgreSQL `agents` table migrated
- `aep-common` library importable
