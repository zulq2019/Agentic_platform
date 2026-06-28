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
