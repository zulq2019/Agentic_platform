"""Kafka producer with EventEnvelope validation and DLQ routing."""

from __future__ import annotations

from typing import Any, Protocol

from aep_common.kafka.dlq import build_dlq_record, dlq_record_to_bytes, dlq_topic_name
from aep_common.kafka.envelope import (
    EventEnvelope,
    envelope_to_bytes,
    validate_envelope_dict,
)
from aep_common.kafka.exceptions import EventEnvelopeValidationError
from aep_common.kafka.tracing import kafka_span
from aep_common.logging import get_logger


class MessageProducer(Protocol):
    def produce(
        self,
        topic: str,
        value: bytes,
        *,
        key: bytes | None = None,
        on_delivery: Any | None = None,
    ) -> None: ...

    def flush(self, timeout: float = 10) -> int: ...


class EventProducer:
    """Validates envelopes before publish; invalid messages go to DLQ."""

    def __init__(
        self,
        producer: MessageProducer,
        *,
        service_name: str,
        flush_after_publish: bool = True,
    ) -> None:
        self._producer = producer
        self._service_name = service_name
        self._flush_after_publish = flush_after_publish
        self._logger = get_logger(service_name)

    def publish(
        self,
        topic: str,
        message: EventEnvelope | dict[str, Any],
    ) -> None:
        with kafka_span(
            "kafka.publish",
            topic=topic,
            service=self._service_name,
        ):
            try:
                if isinstance(message, EventEnvelope):
                    envelope = message
                else:
                    envelope = validate_envelope_dict(message)
            except EventEnvelopeValidationError as exc:
                self._route_invalid_to_dlq(
                    original_topic=topic,
                    error=str(exc),
                    raw_message=message if isinstance(message, dict) else None,
                )
                return

            payload = envelope_to_bytes(envelope)
            key = envelope.tenant_id.encode("utf-8")
            self._producer.produce(topic, payload, key=key)
            if self._flush_after_publish:
                self._producer.flush()

    def _route_invalid_to_dlq(
        self,
        *,
        original_topic: str,
        error: str,
        raw_message: dict[str, Any] | None,
    ) -> None:
        tenant_id = None
        task_id = None
        if isinstance(raw_message, dict):
            tenant_id = raw_message.get("tenant_id")
            task_id = raw_message.get("task_id")

        record = build_dlq_record(
            original_topic=original_topic,
            error=error,
            raw_message=raw_message,
            tenant_id=str(tenant_id) if tenant_id is not None else None,
            task_id=str(task_id) if task_id is not None else None,
        )
        self._logger.error(
            "event_envelope_rejected",
            original_topic=original_topic,
            error=error,
            tenant_id=tenant_id,
            task_id=task_id,
        )
        self._producer.produce(
            dlq_topic_name(),
            dlq_record_to_bytes(record),
            key=(str(tenant_id).encode("utf-8") if tenant_id else None),
        )
        if self._flush_after_publish:
            self._producer.flush()
