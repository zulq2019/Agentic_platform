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

## US-01.04

| Component | Required for this story | Already Exists | Action |
|-----------|------------------------|----------------|--------|
| Docker Compose | Yes | Yes (US-01.02) | Use existing postgres service |
| PostgreSQL | Yes | Yes | Run Alembic migrations via `make migrate` |
| Kafka | No | Yes | Not required for database story |
| Redis | No | Yes | Not required for database story |
| OpenTelemetry | No | Yes | Not required for database story |
| Prometheus | No | Yes | Not required for database story |
| Grafana | No | Yes | Not required for database story |
| Vault | No | No | Defer to PI-08 |
| Kubernetes | No | No | Defer to deployment PI |
