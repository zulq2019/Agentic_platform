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
- A running local developer environment (Docker Compose + Makefile)
- Kafka cluster with all 11 topics + DLQ provisioned and ACLs applied
- PostgreSQL with all schemas, RLS policies, and migrations applied
- Redis with keyspace conventions enforced
- All 7 JSON Schema contracts validated in CI
- A CI/CD pipeline that lints, tests, builds, and deploys every service
- An OTEL collector wired to every service

---

## What Is Already Done

| Deliverable | Status |
|-------------|--------|
| `contracts/` — 7 JSON Schema files | ✅ Complete |
| `contracts/examples/coding-agent-registration.json` | ✅ Complete |
| `workflows/greenfield-v1.0.0.json` | ✅ Complete |
| `scripts/validate_contract.py` | ✅ Complete |
| Root documentation (CONSTITUTION, ARCHITECTURE, CLAUDE, etc.) | ✅ Complete |

## What Is Being Built in This PI

| Deliverable | Capability | Status |
|-------------|-----------|--------|
| 16 service skeletons | CAP-01 | 🔲 Not started |
| Shared library `aep-common` | CAP-02 | 🔲 Not started |
| Docker Compose local environment | CAP-03 | 🔲 Not started |
| Kafka topic provisioning | CAP-04 | 🔲 Not started |
| PostgreSQL migrations + RLS | CAP-05 | 🔲 Not started |
| CI/CD pipeline (GitHub Actions) | CAP-06 | 🔲 Not started |
| OTEL collector config | CAP-01, CAP-03 | 🔲 Not started |

---

## Document Index

| Document | Purpose |
|----------|---------|
| `OBJECTIVES.md` | Measurable PI-level outcomes |
| `CAPABILITIES.md` | What is built — technical contracts, schemas, sequences, data model |
| `USER_STORIES.md` | Stories only — who wants what and why |
| `ACCEPTANCE_CRITERIA.md` | Given/When/Then criteria per story |
| `IMPLEMENTATION.md` | Tech stack, patterns, code conventions |
| `PROMPT_MAPPING.md` | Maps each story to `.ai/commands/` |
| `SPRINT_PLAN.md` | Sprint-by-sprint task breakdown |
| `TESTING.md` | Test pyramid, test files, security and performance baseline |
| `RISKS.md` | Risk register with likelihood, impact, and mitigations |
| `DEFINITION_OF_DONE.md` | Story-level gate + PI-level gate (single source of truth) |

---

## Dependencies

None. PI-01 has no upstream platform dependencies.

---

## Handoff to PI-02

PI-02 (Agent Runtime) requires all of the following from PI-01:

- `agent-runtime/` service skeleton with health endpoint live
- `agent-registry/` service skeleton with health endpoint live
- Kafka topics `aep.task.created`, `aep.agent.started`, `aep.agent.completed`, `aep.agent.failed` provisioned
- PostgreSQL `agents.registrations` table migrated with RLS applied
- `aep-common` library importable via `pip install`
