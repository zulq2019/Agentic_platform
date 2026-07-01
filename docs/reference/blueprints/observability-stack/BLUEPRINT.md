# Blueprint: Observability Stack

**Status:** DEFERRED — Baseline in PI-01, full stack in PI-10  
**Target PI:** PI-01 (OTEL wiring) → PI-10 (full dashboards + alerting)

## Purpose

The observability stack provides unified visibility for engineers, engineering leaders, governance stakeholders, operations, and finance.

## Components

| Component | Purpose | Delivered In |
|-----------|---------|-------------|
| OpenTelemetry SDK | Auto-instrumentation in all services | PI-01 |
| OTEL Collector | Centralised pipeline, batching, sampling | PI-01 |
| Prometheus | Time-series metrics (90-day retention) | PI-01 |
| Grafana | 5 dashboard sets | PI-01 (health) → PI-10 (full) |
| Grafana Loki | Log aggregation (30-day retention) | PI-03 |
| Grafana Tempo | Distributed tracing (30-day retention) | PI-02 |
| Langfuse | LLM observability — tokens, cost, latency | PI-06 |
| ClickHouse | Audit analytics (7-year retention) | PI-07 |

## Directory Structure

```
observability/
├── grafana/
│   ├── dashboards/
│   │   ├── 01-service-health.json      # PI-01
│   │   ├── 02-agent-runtime.json       # PI-02
│   │   ├── 03-workflow-execution.json  # PI-03
│   │   ├── 04-engineer.json            # Task tracing, agent detail
│   │   ├── 05-leadership.json          # DORA metrics, cycle time
│   │   ├── 06-governance.json          # Gate audit trail, approver report
│   │   ├── 07-operations.json          # Infra health, Kafka lag
│   │   └── 08-cost.json                # LLM spend by tenant
│   └── provisioning/
├── prometheus/
│   ├── rules/
│   │   ├── platform-alerts.yaml
│   │   └── sla-alerts.yaml
│   └── prometheus.yml
├── otel-collector/
│   └── otel-config.yaml
└── langfuse/
    └── docker-compose.yml
```

## Key Platform Metrics

```
# Throughput
aep_tasks_total{tenant, workflow_type, state}
aep_workflows_total{tenant, workflow_type, terminal_state}

# Latency
aep_agent_execution_duration_seconds{agent_id, cost_class}
aep_gate_wait_duration_seconds{gate_id, workflow_type}

# Cost
aep_model_tokens_total{tier, tenant, agent_id}
aep_model_cost_usd_total{tier, tenant}

# Infrastructure
aep_kafka_consumer_lag{topic, consumer_group}
aep_db_connection_pool_used{service}
```

## Alert Policy

| Alert | Threshold | Severity |
|-------|-----------|---------|
| Kafka consumer lag | > 10,000 for 5 min | critical |
| Agent failure rate | > 10% for 10 min | critical |
| Gate wait time | > 24h (open-ended) | warning |
| DB connection pool | > 80% for 5 min | warning |
| Model quota | > 90% of hourly limit | warning |
