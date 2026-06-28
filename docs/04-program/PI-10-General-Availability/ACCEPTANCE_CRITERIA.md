# PI-10-General-Availability — Acceptance Criteria

## AC-PI-10-General-Availability-01 — Functional
**Given** the platform spine (PI-01) is running,
**When** all General Availability services start,
**Then** all health endpoints return 200 and all integration tests pass.

## AC-PI-10-General-Availability-02 — Event Contract
**Given** any service in this PI publishes a Kafka event,
**When** the event is consumed,
**Then** it conforms to the EventEnvelope schema (contracts/event-envelope.schema.json).

## AC-PI-10-General-Availability-03 — Tenant Isolation
**Given** two tenants A and B have data in this PI's services,
**When** a query runs in tenant A's context,
**Then** zero rows belonging to tenant B are returned.

## AC-PI-10-General-Availability-04 — No Hardcoded Credentials
**Given** any file in this PI's services,
**When** detect-secrets scans the codebase,
**Then** zero new credential findings are reported.

## AC-PI-10-General-Availability-05 — Observability
**Given** this PI is deployed to the dev cluster,
**When** Grafana is opened,
**Then** metrics from all new services are visible within 5 minutes.
