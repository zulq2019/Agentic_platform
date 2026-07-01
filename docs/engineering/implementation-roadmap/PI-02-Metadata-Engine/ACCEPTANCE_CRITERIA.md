# PI-02-Metadata-Engine — Acceptance Criteria

## AC-PI-02-Metadata-Engine-01 — Functional
**Given** the platform spine (PI-01) is running,
**When** all Agent Runtime services start,
**Then** all health endpoints return 200 and all integration tests pass.

## AC-PI-02-Metadata-Engine-02 — Event Contract
**Given** any service in this PI publishes a Kafka event,
**When** the event is consumed,
**Then** it conforms to the EventEnvelope schema (contracts/event-envelope.schema.json).

## AC-PI-02-Metadata-Engine-03 — Tenant Isolation
**Given** two tenants A and B have data in this PI's services,
**When** a query runs in tenant A's context,
**Then** zero rows belonging to tenant B are returned.

## AC-PI-02-Metadata-Engine-04 — No Hardcoded Credentials
**Given** any file in this PI's services,
**When** detect-secrets scans the codebase,
**Then** zero new credential findings are reported.

## AC-PI-02-Metadata-Engine-05 — Observability
**Given** this PI is deployed to the dev cluster,
**When** Grafana is opened,
**Then** metrics from all new services are visible within 5 minutes.

---

## US-02.02 — Postgres Platform Object Repository

### AC-US-02.02-01 — Persist and reload
**Given** migration `006_platform_object_tables` has been applied and `AEP_APP_POSTGRES_DSN` is configured,  
**When** a valid Platform Object is saved via `PostgresPlatformObjectRepository`,  
**Then** the same object is returned by `get_by_id` for the same tenant after a new connection.

### AC-US-02.02-02 — Tenant isolation at repository layer
**Given** a Platform Object exists for tenant A,  
**When** `get_by_id` is called with tenant B and the same object id,  
**Then** the repository returns `None`.

### AC-US-02.02-03 — RLS enforcement
**Given** rows exist for tenants A and B in `metadata.platform_objects`,  
**When** a query runs under tenant A session context (`app.current_tenant_id`),  
**Then** zero rows belonging to tenant B are returned.

### AC-US-02.02-04 — Service wiring
**Given** `AEP_APP_POSTGRES_DSN` is set in the metadata-engine environment,  
**When** the service starts,  
**Then** `build_platform_object_service` uses `PostgresPlatformObjectRepository` instead of the in-memory adapter.

