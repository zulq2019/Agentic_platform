# PI-04-Memory — AI Implementation Prompts

Use these prompts when working with AI assistants to implement Memory.
Always attach CLAUDE.md and the relevant contract schemas as context.

## PROMPT-PI-04-Memory-01 — Core Service Implementation

```
Context files: CLAUDE.md, contracts/event-envelope.schema.json, ARCHITECTURE.md

Implement the Memory services for the Agentic Engineering Platform.

Services: memory-service (working context + LTM)
Constitutional constraints: AR1, AR2, AR4, SR1, SR3, SR5

Requirements:
- Each service follows the scaffold pattern from PI-01
- All business logic in domain/ layer
- All Kafka events validated against EventEnvelope before publishing
- All DB queries include tenant_id (RLS enforced at storage layer)
- No hardcoded credentials — all via environment variables

Tests required:
- Unit tests for all domain logic (= 80% coverage)
- Integration test for primary event flow
- Tenancy isolation test

Forbidden:
- No direct service-to-service HTTP calls (AR4)
- No hardcoded credentials (SR1)
- No unscoped DB queries (SR3)
```

## PROMPT-PI-04-Memory-02 — Integration Test

```
Context files: CLAUDE.md, existing test files in tests/integration/

Write an integration test for the primary event flow introduced in Memory.

The test should:
1. Produce a triggering Kafka event
2. Wait for the expected response event (with timeout)
3. Assert the response conforms to the expected schema
4. Assert tenant isolation: event from tenant A is not processed in tenant B context
5. Assert audit event was written to ClickHouse

Use Testcontainers for all external dependencies.
```

## PROMPT-PI-04-Memory-03 — Observability

```
Add OpenTelemetry instrumentation to all Memory services.

Requirements:
- Every public method in domain/ is auto-traced via @trace decorator
- Span attributes include: task_id, workflow_run_id, tenant_id, service_name
- Custom metrics: request count, duration histogram, error rate
- All metrics exported in Prometheus format from /metrics

Use aep_common.tracing.get_tracer() — do not import OTEL SDK directly.
```
