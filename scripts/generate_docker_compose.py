#!/usr/bin/env python3
"""Generate docker-compose.yml for PI-01 local development."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SERVICES = [
    ("api-gateway", "platform/gateway", 8080, False),
    ("auth-service", "platform/services/auth-service", 8001, True),
    ("rbac-service", "platform/services/rbac-service", 8002, True),
    ("orchestrator-service", "platform/orchestrator", 8003, True),
    ("workflow-engine", "platform/workflow", 8004, True),
    ("task-engine", "platform/task", 8005, True),
    ("approval-service", "platform/services/approval-service", 8006, True),
    ("agent-runtime", "platform/runtime", 8007, True),
    ("agent-registry", "platform/registry/agent-registry", 8008, True),
    ("model-router", "platform/registry/model-router", 8009, True),
    ("tool-registry", "platform/registry/tool-registry", 8010, True),
    ("memory-service", "platform/services/memory-service", 8011, True),
    ("audit-service", "platform/services/audit-service", 8012, True),
    ("secrets-service", "platform/services/secrets-service", 8013, True),
    ("policy-engine", "platform/services/policy-engine", 8014, True),
    ("config-service", "platform/services/config-service", 8015, True),
]

HEADER = """\
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: aep
      POSTGRES_PASSWORD: aep
      POSTGRES_DB: aep
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aep -d aep"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

  kafka:
    image: apache/kafka:3.8.1
    hostname: kafka
    ports:
      - "9094:9094"
    environment:
      KAFKA_NODE_ID: "1"
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: INTERNAL://0.0.0.0:9092,EXTERNAL://0.0.0.0:9094,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka:9092,EXTERNAL://localhost:9094
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: "1"
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: "1"
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: "1"
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk
    healthcheck:
      test: ["CMD-SHELL", "/opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092 || exit 1"]
      interval: 10s
      timeout: 10s
      retries: 12
      start_period: 30s

  kafka-init:
    image: python:3.12-slim
    depends_on:
      kafka:
        condition: service_healthy
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      PYTHONPATH: /app/src/shared/aep_common
    volumes:
      - ./src/shared/aep_common:/app/src/shared/aep_common:ro
      - ./scripts/provision_kafka_topics.py:/app/scripts/provision_kafka_topics.py:ro
    working_dir: /app
    command:
      - /bin/sh
      - -c
      - |
        pip install --quiet -e '/app/src/shared/aep_common[kafka]' && \
        python /app/scripts/provision_kafka_topics.py
    restart: "no"

  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.96.0
    command: ["--config=/etc/otel-collector/otel-config.yaml"]
    volumes:
      - ./observability/otel-collector/otel-config.yaml:/etc/otel-collector/otel-config.yaml:ro
    ports:
      - "4317:4317"
      - "4318:4318"
      - "13133:13133"
    healthcheck:
      disable: true

  prometheus:
    image: prom/prometheus:v2.49.1
    volumes:
      - ./observability/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    ports:
      - "9090:9090"
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus
      - --web.enable-lifecycle
    depends_on:
      otel-collector:
        condition: service_started
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:9090/-/ready"]
      interval: 10s
      timeout: 5s
      retries: 6
      start_period: 10s

  grafana:
    image: grafana/grafana:10.3.1
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes:
      - ./observability/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./observability/grafana/dashboards:/var/lib/grafana/dashboards:ro
    ports:
      - "3001:3000"
    depends_on:
      prometheus:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:3000/api/health"]
      interval: 10s
      timeout: 5s
      retries: 6
      start_period: 20s

"""

PYTHON_TEMPLATE = """\
  {name}:
    build:
      context: .
      dockerfile: src/{path}/Dockerfile
    ports:
      - "{port}:{port}"
    environment:
      SERVICE_NAME: {name}
      PORT: {port}
      POSTGRES_DSN: postgresql://aep:aep@postgres:5432/aep
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      REDIS_URL: redis://redis:6379/0
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
      ENVIRONMENT: dev
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_healthy
      redis:
        condition: service_healthy
      otel-collector:
        condition: service_started
"""

GATEWAY = """\
  api-gateway:
    build:
      context: .
      dockerfile: src/platform/gateway/Dockerfile
    ports:
      - "8080:8080"
    environment:
      SERVICE_NAME: api-gateway
      PORT: 8080
      POSTGRES_HOST: postgres:5432
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      REDIS_HOST: redis:6379
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
      ENVIRONMENT: dev
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_healthy
      redis:
        condition: service_healthy
      otel-collector:
        condition: service_started
"""


def main() -> None:
    lines = [HEADER, GATEWAY]
    for name, path, port, is_python in SERVICES:
        if name == "api-gateway":
            continue
        if is_python:
            lines.append(PYTHON_TEMPLATE.format(name=name, path=path, port=port))
    output = ROOT / "docker-compose.yml"
    output.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
