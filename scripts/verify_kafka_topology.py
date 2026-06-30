#!/usr/bin/env python3
"""Verify PI-01 Kafka topology: 11 topics + DLQ with correct configuration."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from aep_common.kafka.bootstrap import resolve_bootstrap_servers
from aep_common.kafka.topic_catalog import (
    LOCAL_REPLICATION_FACTOR,
    TOPIC_SPECS,
    business_topic_count,
)

ROOT = Path(__file__).resolve().parents[1]
ACL_CATALOG = ROOT / "infra" / "kafka" / "acls.yaml"


def verify_acl_catalog() -> list[str]:
    errors: list[str] = []
    if not ACL_CATALOG.is_file():
        return [f"missing ACL catalog: {ACL_CATALOG}"]

    with ACL_CATALOG.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    acls = data.get("acls") if isinstance(data, dict) else None
    if not isinstance(acls, list) or not acls:
        return ["ACL catalog must define a non-empty acls list"]

    topic_names = {spec.name for spec in TOPIC_SPECS}
    for entry in acls:
        if not isinstance(entry, dict):
            errors.append("ACL entry must be a mapping")
            continue
        topics = entry.get("topics")
        if not isinstance(topics, list):
            errors.append(f"ACL entry missing topics list: {entry}")
            continue
        for topic in topics:
            if topic not in topic_names:
                errors.append(f"ACL references unknown topic: {topic}")

    return errors


def verify_topics(*, bootstrap_servers: str | None = None) -> list[str]:
    try:
        from confluent_kafka.admin import AdminClient
    except ImportError:
        return [
            "confluent-kafka not installed — pip install -e 'src/shared/aep_common[kafka]'"
        ]

    servers = resolve_bootstrap_servers(bootstrap_servers)
    admin = AdminClient({"bootstrap.servers": servers})

    try:
        metadata = admin.list_topics(timeout=15)
    except Exception as exc:
        return [f"cannot reach Kafka at {servers}: {exc}"]

    errors: list[str] = []
    existing = metadata.topics

    for spec in TOPIC_SPECS:
        if spec.name not in existing:
            errors.append(f"missing topic: {spec.name}")
            continue

        topic_meta = existing[spec.name]
        if topic_meta.error is not None:
            errors.append(f"topic {spec.name} error: {topic_meta.error}")
            continue

        partitions = topic_meta.partitions
        if len(partitions) != spec.partitions:
            errors.append(
                f"topic {spec.name}: expected {spec.partitions} partitions, "
                f"found {len(partitions)}"
            )

        for partition in partitions.values():
            if (
                partition.replicas
                and len(partition.replicas) != LOCAL_REPLICATION_FACTOR
            ):
                errors.append(
                    f"topic {spec.name}: expected replication factor "
                    f"{LOCAL_REPLICATION_FACTOR}, found {len(partition.replicas)}"
                )
                break

    return errors


def verify_topology(*, bootstrap_servers: str | None = None) -> tuple[bool, list[str]]:
    errors = verify_acl_catalog()
    errors.extend(verify_topics(bootstrap_servers=bootstrap_servers))
    return not errors, errors


def main() -> int:
    ok, errors = verify_topology()
    if ok:
        print(
            f"OK: {business_topic_count()} topics + DLQ provisioned with correct configuration"
        )
        return 0

    print("Kafka topology verification failed:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
