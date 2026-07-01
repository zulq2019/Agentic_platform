# PI-01 — Objectives

**Architecture baseline:** [ARCHITECTURE_BASELINE_V2.md](../../../architecture/ARCHITECTURE_BASELINE_V2.md) · Terminology: [PLATFORM_GLOSSARY.md](../../../architecture/PLATFORM_GLOSSARY.md)

## O1. Every service has a runnable skeleton

Every one of the 16 platform services must boot, pass its liveness probe, and return `200 OK` from `GET /health/live` and `GET /health/ready` before PI-01 closes.

**Measure:** `docker compose up` → all 16 health endpoints green within 60 seconds.

## O2. Event bus is operational with correct topology

Kafka cluster runs with all 11 topics provisioned, correct partition counts, replication factor, and per-service ACLs applied.

**Measure:** `scripts/verify_kafka_topology.py` exits 0.

## O3. All database schemas are migrated and RLS-enforced

PostgreSQL has every table from `contracts/` and `ARCHITECTURE.md` created via versioned Alembic migrations. RLS is enabled on every table. Cross-tenant query returns 0 rows.

**Measure:** `pytest tests/db/test_rls_isolation.py` — 100% pass.

## O4. CI pipeline runs on every pull request

GitHub Actions pipeline runs lint → unit tests → contract validation → build on every PR targeting `main`. Pipeline must complete in under 8 minutes.

**Measure:** First green CI run on a feature branch PR.

## O5. Developer can onboard in under 30 minutes

A developer with `git`, `docker`, and `python 3.12` installed can clone the repo, run `make dev-up`, and have a fully running local environment.

**Measure:** New team member onboard trial — timed from clone to green health dashboard.
