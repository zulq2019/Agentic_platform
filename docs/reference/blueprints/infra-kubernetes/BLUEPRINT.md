# Blueprint: Infrastructure — Kubernetes

**Status:** DEFERRED — Implemented in PI-10  
**Target PI:** PI-10-General-Availability

## Purpose

Kubernetes manifests and Helm chart for deploying all 16 platform services to production.

## Namespace Strategy

| Namespace | Contents |
|-----------|----------|
| `aep-ingress` | Kong API Gateway, NGINX Ingress Controller |
| `aep-platform` | All 16 microservices |
| `aep-agents` | Dynamically scheduled agent pods |
| `aep-observability` | Prometheus, Grafana, OTEL Collector, Loki, Tempo |
| `aep-data` | Self-hosted Kafka, Redis (if not using managed) |

## Per-Service Resources

Every service has:
- `Deployment` — min 2 replicas, rollingUpdate maxUnavailable=1
- `HorizontalPodAutoscaler` — CPU + custom Kafka lag metric
- `PodDisruptionBudget` — minAvailable: 1
- `Service` — ClusterIP
- `ConfigMap` — non-secret configuration
- `NetworkPolicy` — deny-all default, explicit allow per pair
- `ServiceMonitor` — Prometheus scrape

## Directory Structure

```
infra/k8s/
├── base/
│   ├── namespaces.yaml
│   ├── network-policies/
│   │   ├── default-deny-all.yaml
│   │   ├── allow-agent-runtime.yaml
│   │   └── allow-orchestrator.yaml
│   └── rbac/
│       ├── service-accounts.yaml
│       └── role-bindings.yaml
└── services/
    ├── api-gateway/
    │   ├── deployment.yaml
    │   ├── hpa.yaml
    │   ├── pdb.yaml
    │   ├── service.yaml
    │   └── network-policy.yaml
    ├── orchestrator-service/
    └── ... (one directory per service)
```

## Helm Chart

```
infra/helm/aep/
├── Chart.yaml
├── values.yaml           # Default values
├── values-dev.yaml       # Dev overrides
├── values-prod.yaml      # Prod overrides
└── templates/
    ├── _helpers.tpl
    ├── deployment.yaml
    ├── hpa.yaml
    └── ...
```

## Key HPA Configurations

```yaml
# agent-runtime: scales on Kafka consumer lag
- type: External
  external:
    metric:
      name: kafka_consumer_lag
      selector:
        matchLabels:
          topic: aep.task.created
    target:
      type: AverageValue
      averageValue: 100
```

## Network Policy: Critical Rules

- `agent-runtime` → `agent-runtime`: **DENY** (agents never call agents)
- `agent-runtime` → `orchestrator-service`: **DENY** (event bus only)
- `agent-runtime` → Kafka :9092: **ALLOW**
- `agent-runtime` → `tool-registry` :8110: **ALLOW**
- `agent-runtime` → `policy-engine` :8114: **ALLOW**
- `agent-runtime` → `secrets-service` :8113: **ALLOW**
- Any → Vault directly: **DENY** (via secrets-service only)
