"""Dead letter queue routing for invalid Kafka messages."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from aep_common.kafka.topic_catalog import DLQ_TOPIC


def build_dlq_record(
    *,
    original_topic: str,
    error: str,
    raw_message: bytes | str | dict[str, Any] | None,
    tenant_id: str | None = None,
    task_id: str | None = None,
) -> dict[str, Any]:
    if isinstance(raw_message, bytes):
        raw_value: str | dict[str, Any] | None = raw_message.decode(
            "utf-8", errors="replace"
        )
    elif isinstance(raw_message, dict):
        raw_value = raw_message
    else:
        raw_value = raw_message

    return {
        "original_topic": original_topic,
        "error": error,
        "raw_message": raw_value,
        "tenant_id": tenant_id,
        "task_id": task_id,
        "rejected_at": datetime.now(UTC).isoformat(),
    }


def dlq_record_to_bytes(record: dict[str, Any]) -> bytes:
    return json.dumps(record, separators=(",", ":")).encode("utf-8")


def dlq_topic_name() -> str:
    return DLQ_TOPIC
