"""Kafka bootstrap server resolution for local and container environments."""

from __future__ import annotations

import os

from aep_common.kafka.topic_catalog import HOST_BOOTSTRAP_SERVERS

_LEGACY_HOST_BOOTSTRAP = frozenset({"localhost:9092", "kafka:9092"})


def resolve_bootstrap_servers(explicit: str | None = None) -> str:
    """Return bootstrap servers for host scripts or in-container provisioning."""
    if explicit is not None:
        value = explicit
    else:
        value = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", HOST_BOOTSTRAP_SERVERS)
    if value in _LEGACY_HOST_BOOTSTRAP:
        return HOST_BOOTSTRAP_SERVERS
    return value
