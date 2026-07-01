# PI-01 — Acceptance Criteria

## AC-01.01 — Service Scaffolding

**Given** the repository is cloned on a machine with Docker,  
**When** `make dev-up` is run,  
**Then** all 16 services start and return HTTP 200 from `GET /health/live` within 60 seconds.

**Given** any service,  
**When** `GET /health/ready` is called and a dependency (DB, Kafka) is down,  
**Then** the endpoint returns HTTP 503 with the failing check identified.

## AC-01.02 — Event Bus

**Given** Kafka is running,  
**When** `scripts/verify_kafka_topology.py` is executed,  
**Then** it exits 0 confirming all 11 topics + DLQ exist with correct configuration.

**Given** a service publishes an event with a missing required envelope field,  
**When** the consumer receives it,  
**Then** the message is rejected to DLQ and an error is logged.

## AC-01.03 — Database

**Given** the database is empty,  
**When** `make migrate` is run,  
**Then** all tables are created with RLS enabled and the migration history records every step.

**Given** two tenant contexts A and B exist,  
**When** a query runs in tenant A's context,  
**Then** it returns zero rows belonging to tenant B.

## AC-01.04 — CI Pipeline

**Given** a pull request is opened against `main`,  
**When** the CI pipeline runs,  
**Then** it completes lint + unit tests + contract validation + build within 8 minutes.

**Given** any file in `contracts/` is modified to break a schema,  
**When** CI runs,  
**Then** the contract validation step fails and the PR is blocked.

## AC-01.05 — Developer Onboarding

**Given** a developer has Docker, Git, and Python 3.12 installed,  
**When** they follow the README from clone to `make dev-up`,  
**Then** the full environment is running in under 30 minutes.

## AC-01.07 — Observability Baseline

**Given** a Python platform service with `otel_exporter_otlp_endpoint` configured,  
**When** the service starts and handles HTTP traffic,  
**Then** OpenTelemetry traces are exported to the OTEL collector and forwarded to Tempo.

**Given** the api-gateway (Go) with `OTEL_EXPORTER_OTLP_ENDPOINT` set,  
**When** the gateway handles HTTP traffic,  
**Then** request spans are exported to the OTEL collector.

**Given** Prometheus is running after `make dev-up`,  
**When** scrape targets are listed,  
**Then** all 16 platform services (ports 8001–8015 and api-gateway:8080) expose `/metrics`.

**Given** Grafana is provisioned,  
**When** datasources and dashboards load,  
**Then** Prometheus and Tempo are available and the service health dashboard is present.
