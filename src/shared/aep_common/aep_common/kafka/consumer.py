"""Kafka consumer with EventEnvelope validation and DLQ routing."""

from __future__ import annotations

from collections.abc import Callable, MutableSet
from typing import Any, Protocol

from aep_common.kafka.dlq import build_dlq_record, dlq_record_to_bytes, dlq_topic_name
from aep_common.kafka.envelope import EventEnvelope, parse_envelope_bytes
from aep_common.kafka.exceptions import EventEnvelopeValidationError
from aep_common.kafka.tracing import kafka_span
from aep_common.logging import correlation_context, get_logger


class KafkaMessage(Protocol):
    def value(self) -> bytes | None: ...

    def topic(self) -> str: ...

    def error(self) -> Any: ...


class MessageConsumer(Protocol):
    def poll(self, timeout: float = 1.0) -> KafkaMessage | None: ...

    def commit(
        self, message: KafkaMessage | None = None, asynchronous: bool = False
    ) -> None: ...

    def produce(
        self,
        topic: str,
        value: bytes,
        *,
        key: bytes | None = None,
    ) -> None: ...

    def flush(self, timeout: float = 10) -> int: ...


EventHandler = Callable[[EventEnvelope], None]


class EventConsumer:
    """Validates consumed messages; invalid envelopes are routed to DLQ."""

    def __init__(
        self,
        consumer: MessageConsumer,
        *,
        service_name: str,
        handler: EventHandler,
        processed_event_ids: MutableSet[str] | None = None,
    ) -> None:
        self._consumer = consumer
        self._service_name = service_name
        self._handler = handler
        self._processed_event_ids = (
            processed_event_ids if processed_event_ids is not None else set()
        )
        self._logger = get_logger(service_name)

    def process_next(self, *, poll_timeout: float = 1.0) -> bool:
        """Poll one message, validate, handle or DLQ. Returns False when idle."""
        with kafka_span("kafka.consume", service=self._service_name):
            message = self._consumer.poll(poll_timeout)
            if message is None:
                return False

            if message.error():
                return False

            raw = message.value()
            if raw is None:
                self._consumer.commit(message)
                return True

            try:
                envelope = parse_envelope_bytes(raw)
            except EventEnvelopeValidationError as exc:
                self._reject_to_dlq(message.topic(), raw, str(exc))
                self._consumer.commit(message)
                return True

            event_id = str(envelope.event_id)
            if event_id in self._processed_event_ids:
                self._logger.info("event_duplicate_skipped", event_id=event_id)
                self._consumer.commit(message)
                return True

            try:
                with correlation_context(
                    task_id=str(envelope.task_id),
                    workflow_run_id=str(envelope.workflow_run_id),
                    tenant_id=envelope.tenant_id,
                ):
                    self._handler(envelope)
            except Exception as exc:
                self._reject_to_dlq(
                    message.topic(),
                    raw,
                    f"handler failed: {exc}",
                    tenant_id=envelope.tenant_id,
                    task_id=str(envelope.task_id),
                )
                self._consumer.commit(message)
                return True

            self._processed_event_ids.add(event_id)
            self._consumer.commit(message)
            return True

    def _reject_to_dlq(
        self,
        original_topic: str,
        raw: bytes,
        error: str,
        *,
        tenant_id: str | None = None,
        task_id: str | None = None,
    ) -> None:
        if tenant_id is None and task_id is None:
            try:
                import json

                parsed = json.loads(raw.decode("utf-8"))
                if isinstance(parsed, dict):
                    tenant_id = parsed.get("tenant_id")
                    task_id = parsed.get("task_id")
            except (UnicodeDecodeError, json.JSONDecodeError):
                pass

        record = build_dlq_record(
            original_topic=original_topic,
            error=error,
            raw_message=raw,
            tenant_id=str(tenant_id) if tenant_id is not None else None,
            task_id=str(task_id) if task_id is not None else None,
        )
        self._logger.error(
            "event_envelope_rejected_on_consume",
            original_topic=original_topic,
            error=error,
            tenant_id=tenant_id,
            task_id=task_id,
        )
        self._consumer.produce(dlq_topic_name(), dlq_record_to_bytes(record))
        self._consumer.flush()
