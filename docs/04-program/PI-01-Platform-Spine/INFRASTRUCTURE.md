# US-01.01 — Service Bootstrap Infrastructure Assessment

## US-01.01

| Component | Required for this story | Already Exists | Action |
|-----------|------------------------|----------------|--------|
| Docker Compose | Yes | No | Add `docker-compose.yml` with infra + 16 services |
| PostgreSQL | Yes | No | Add postgres:16 service for readiness checks |
| Kafka | Yes | No | Add bitnami/kafka KRaft single broker |
| Redis | Yes | No | Add redis:7 service for readiness checks |
| OpenTelemetry | No | No | Defer to US-01.07 |
| Prometheus | No | No | Defer to US-01.07 |
| Grafana | No | No | Defer to US-01.07 |
| Vault | No | No | Defer to PI-08 |
| Kubernetes | No | No | Defer to deployment PI |

## US-01.02

| Component | Required for this story | Already Exists | Action |
|-----------|------------------------|----------------|--------|
| Docker Compose | Yes | Partial (US-01.01) | Extend with observability stack |
| PostgreSQL | Yes | Yes | Switch to pgvector/pgvector:pg16 image |
| Kafka | Yes | Yes | Use existing single KRaft broker |
| Redis | Yes | Yes | Use existing |
| OpenTelemetry | Yes | No | Add otel-collector service |
| Prometheus | Yes | No | Add prometheus service + scrape config |
| Grafana | Yes | No | Add grafana service + health dashboard |
| Vault | No | No | Defer to PI-08 |
| Kubernetes | No | No | Defer to deployment PI |

## US-01.03

| Component | Required for this story | Already Exists | Action |
|-----------|------------------------|----------------|--------|
| Docker Compose | Yes | Yes (US-01.02) | Add `kafka-init` provisioning container |
| PostgreSQL | No | Yes | Not required for this story |
| Kafka | Yes | Yes | Topic provisioning + topology verification; ACL catalog at `infra/kafka/acls.yaml` (broker enforcement deferred — Sprint 2.2 / deployment PI) |
| Redis | No | Yes | Not required for this story |
| OpenTelemetry | No | Yes | Not required for this story |
| Prometheus | No | Yes | Not required for this story |
| Grafana | No | Yes | Not required for this story |
| Vault | No | No | Defer to PI-08 |
| Kubernetes | No | No | Defer to deployment PI |

## US-01.04

| Component | Required for this story | Already Exists | Action |
|-----------|------------------------|----------------|--------|
| Docker Compose | Yes | Yes (US-01.02) | Use existing postgres service |
| PostgreSQL | Yes | Yes | Run Alembic migrations via `make migrate` |
| Kafka | No | Yes | Not required for database story |
| Redis | No | Yes | Not required for database story |
| OpenTelemetry | No | Yes | Not required for database story |
| Prometheus | No | Yes | Not required for database story |
| Grafana | No | Yes | Not required for this story |
| Vault | No | No | Defer to PI-08 |
| Kubernetes | No | No | Defer to deployment PI |

### Deployment (US-01.04)

1. Set `POSTGRES_DSN`, `AEP_APP_DB_PASSWORD`, and `AEP_APP_POSTGRES_DSN` in `.env` (password in DSN must match `AEP_APP_DB_PASSWORD`).
2. Start Postgres (`make dev-up` or existing instance).
3. Run `make migrate` — verify Alembic reaches revision `005_app_role_grants`.
4. Verify RLS: `pytest src/tests -m "story_us_01_04 and integration" -v`.

### Rollback (US-01.04)

**Risk:** MEDIUM — downgrade drops schemas/tables and the `aep_app` role. Safe only when no production data exists in platform tables.

1. Stop services writing to platform schemas.
2. With `POSTGRES_DSN` set: `alembic downgrade base` (or repeated `alembic downgrade -1` through `001`).
3. Verify: `alembic current` is empty or at the pre-migration revision.
4. If only the app role password was wrong: `DROP ROLE IF EXISTS aep_app` and re-run `make migrate` with the correct `AEP_APP_DB_PASSWORD`.
5. Re-deploy previous application image if service code was updated (PI-01 services do not query new tables yet).

## US-01.07

| Component | Required for this story | Already Exists | Action |
|-----------|------------------------|----------------|--------|
| Docker Compose | Yes | Yes (US-01.02) | Add `tempo` service; wire otel-collector → Tempo |
| PostgreSQL | No | Yes | Not required for observability story |
| Kafka | No | Yes | Not required for observability story |
| Redis | No | Yes | Not required for observability story |
| OpenTelemetry | Yes | Partial (US-01.02 collector) | `aep_common.tracing` + Go gateway `otelecho`; export to Tempo |
| Prometheus | Yes | Yes (US-01.02) | Verify scrape config covers all 16 services |
| Grafana | Yes | Yes (US-01.02) | Add Tempo datasource; keep service health dashboard |
| Vault | No | No | Defer to PI-08 |
| Kubernetes | No | No | Defer to deployment PI |

### Deployment (US-01.07)

1. `make dev-up` — confirm Tempo healthy at `http://localhost:3200/ready`.
2. `python scripts/verify_dev_environment.py` — exits 0 (Prometheus, Grafana, OTEL Collector, Tempo).
3. Hit any service `/metrics` and confirm Prometheus `up` for all 16 targets.
4. Generate traffic; confirm traces visible in Grafana → Tempo.

### Rollback (US-01.07)

**Risk:** LOW — observability is additive; disabling export does not affect service behaviour.

1. Unset `OTEL_EXPORTER_OTLP_ENDPOINT` / set `OTEL_SDK_DISABLED=true` on services.
2. Remove `tempo` from compose if Tempo causes resource issues (traces buffer at collector only).
3. Revert `aep_common.tracing` wiring in `create_platform_app` if needed.
