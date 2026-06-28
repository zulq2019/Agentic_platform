# PI-03-Orchestrator — API Specification

## Services Introducing APIs in This PI
orchestrator-service :8090, workflow-engine :8091, task-engine :8092, approval-service :8093

All services also expose the standard endpoints from PI-01:
- GET /health/live
- GET /health/ready
- GET /metrics
- GET /info

## Key Endpoints

The full OpenAPI 3.1 specifications are generated from the service code and
published to docs/reference/ at PI close.

Key business endpoints introduced in this PI:

| Method | Path | Service | Purpose |
|--------|------|---------|---------|
| See service source | src/api/ | orchestrator-service, workflow-engine, task-engine, approval-service | See IMPLEMENTATION.md for design |

## Event Contracts (Kafka)

All events published in this PI conform to contracts/event-envelope.schema.json.
PI-specific event payloads are defined in contracts/ and validated in CI.

## gRPC (Internal Only)

Internal service-to-service calls that bypass Kafka for synchronous lookups
(registry resolution, policy checks) use gRPC. Proto files live in:
platform/{service-name}/src/proto/
