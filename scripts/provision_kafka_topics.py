#!/usr/bin/env python3
"""Provision PI-01 Kafka topics idempotently (CAP-04 / US-01.03)."""

from __future__ import annotations

import os
import sys

from aep_common.kafka.topic_catalog import (
    HOST_BOOTSTRAP_SERVERS,
    LOCAL_REPLICATION_FACTOR,
    TOPIC_SPECS,
)


def _bootstrap_servers() -> str:
    value = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", HOST_BOOTSTRAP_SERVERS)
    if value in {"localhost:9092", "kafka:9092"}:
        return HOST_BOOTSTRAP_SERVERS
    return value


def provision_topics(*, bootstrap_servers: str | None = None) -> None:
    try:
        from confluent_kafka.admin import AdminClient, NewTopic
    except ImportError as exc:
        raise SystemExit(
            "Install kafka extras: pip install -e 'src/shared/aep_common[kafka]'"
        ) from exc

    servers = bootstrap_servers or _bootstrap_servers()
    admin = AdminClient({"bootstrap.servers": servers})

    metadata = admin.list_topics(timeout=15)
    existing = metadata.topics

    to_create: list[NewTopic] = []
    for spec in TOPIC_SPECS:
        if spec.name not in existing:
            to_create.append(
                NewTopic(
                    spec.name,
                    num_partitions=spec.partitions,
                    replication_factor=LOCAL_REPLICATION_FACTOR,
                )
            )
            continue

        topic_meta = existing[spec.name]
        if topic_meta.error is not None:
            raise RuntimeError(f"topic {spec.name} metadata error: {topic_meta.error}")

        partition_count = len(topic_meta.partitions)
        if partition_count != spec.partitions:
            raise RuntimeError(
                f"topic {spec.name} has {partition_count} partitions, "
                f"expected {spec.partitions}"
            )

    if to_create:
        futures = admin.create_topics(to_create)
        for topic_name, future in futures.items():
            try:
                future.result(timeout=30)
                print(f"Created topic {topic_name}")
            except Exception as exc:
                if "TOPIC_ALREADY_EXISTS" in str(exc):
                    print(f"Topic {topic_name} already exists")
                    continue
                raise RuntimeError(f"failed to create {topic_name}: {exc}") from exc

    print(f"Kafka topics ready at {servers} ({len(TOPIC_SPECS)} topics)")


def main() -> int:
    try:
        provision_topics()
    except Exception as exc:
        print(f"Kafka topic provisioning failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
