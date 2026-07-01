# PI-02-Metadata-Engine — API Specification

## Services Introducing APIs in This PI
agent-registry :8101, model-router :8102

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
| See service source | src/api/ | agent-runtime, agent-registry, model-router, aep-agent-sdk | See IMPLEMENTATION.md for design |

## Event Contracts (Kafka)

All events published in this PI conform to contracts/event-envelope.schema.json.
PI-specific event payloads are defined in contracts/ and validated in CI.

## gRPC (Internal Only)

Internal service-to-service calls that bypass Kafka for synchronous lookups
(registry resolution, policy checks) use gRPC. Proto files live in:
platform/{service-name}/src/proto/
