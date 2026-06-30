"""Kafka topic catalog for PI-01 event bus (CAP-04)."""

from __future__ import annotations

from dataclasses import dataclass

HOST_BOOTSTRAP_SERVERS = "localhost:9094"
DOCKER_BOOTSTRAP_SERVERS = "kafka:9092"
DLQ_TOPIC = "aep.dlq"
LOCAL_REPLICATION_FACTOR = 1


@dataclass(frozen=True, slots=True)
class TopicSpec:
    name: str
    partitions: int
    producers: tuple[str, ...]
    consumers: tuple[str, ...]


TOPIC_SPECS: tuple[TopicSpec, ...] = (
    TopicSpec("aep.task.created", 12, ("orchestrator-service",), ("agent-runtime",)),
    TopicSpec("aep.task.completed", 12, ("agent-runtime",), ("orchestrator-service",)),
    TopicSpec("aep.task.failed", 12, ("agent-runtime",), ("orchestrator-service",)),
    TopicSpec("aep.agent.started", 6, ("agent-runtime",), ("audit-service",)),
    TopicSpec(
        "aep.agent.completed",
        6,
        ("agent-runtime",),
        ("orchestrator-service", "audit-service"),
    ),
    TopicSpec(
        "aep.agent.failed",
        6,
        ("agent-runtime",),
        ("orchestrator-service", "audit-service"),
    ),
    TopicSpec(
        "aep.workflow.state.changed",
        6,
        ("orchestrator-service",),
        ("audit-service",),
    ),
    TopicSpec(
        "aep.approval.requested",
        3,
        ("orchestrator-service",),
        ("approval-service",),
    ),
    TopicSpec(
        "aep.approval.decided",
        3,
        ("approval-service",),
        ("orchestrator-service",),
    ),
    TopicSpec("aep.memory.written", 6, ("agent-runtime",), ("memory-service",)),
    TopicSpec("aep.audit.event", 12, ("all-services",), ("audit-service",)),
    TopicSpec(DLQ_TOPIC, 3, ("all-services",), ("audit-service",)),
)


def topic_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in TOPIC_SPECS)


def business_topic_count() -> int:
    return len(TOPIC_SPECS) - 1
