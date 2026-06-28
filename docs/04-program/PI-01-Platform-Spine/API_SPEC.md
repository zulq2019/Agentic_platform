# PI-01 — API Specification

PI-01 does not implement business APIs. It establishes the **standard contract** every service must expose.

## Standard Endpoints (all 16 services)

### GET /health/live

```yaml
summary: Kubernetes liveness probe
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [ok]
```

### GET /health/ready

```yaml
summary: Kubernetes readiness probe
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [ok, degraded]
            checks:
              type: object
              additionalProperties:
                type: string
                enum: [ok, error]
  503:
    description: One or more dependency checks failed
```

### GET /metrics

```
# HELP aep_http_requests_total Total HTTP requests
# TYPE aep_http_requests_total counter
aep_http_requests_total{service="orchestrator-service",method="GET",status="200"} 42

# HELP aep_http_request_duration_seconds HTTP request duration
# TYPE aep_http_request_duration_seconds histogram
aep_http_request_duration_seconds_bucket{le="0.05"} 38
```

### GET /info

```yaml
summary: Service metadata
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            service:
              type: string
            version:
              type: string
            contract_version:
              type: string
            environment:
              type: string
              enum: [dev, staging, prod]
```

## Event Envelope (Kafka — all topics)

See `contracts/event-envelope.schema.json` for the authoritative schema.

```json
{
  "event_id": "uuid-v4",
  "event_type": "TaskCreated",
  "schema_version": "1.0",
  "emitted_by": "orchestrator-service",
  "tenant_id": "tenant-acme-corp",
  "task_id": "uuid-v4",
  "workflow_run_id": "uuid-v4",
  "timestamp": "2026-06-28T04:00:00Z",
  "payload": {}
}
```
