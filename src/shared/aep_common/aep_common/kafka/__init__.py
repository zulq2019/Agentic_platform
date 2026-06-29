"""Kafka utilities for the Agentic Engineering Platform."""

from aep_common.kafka.consumer import EventConsumer
from aep_common.kafka.dlq import build_dlq_record, dlq_topic_name
from aep_common.kafka.envelope import EventEnvelope, validate_envelope_dict
from aep_common.kafka.exceptions import EventEnvelopeValidationError
from aep_common.kafka.producer import EventProducer
from aep_common.kafka.topic_catalog import (
    DLQ_TOPIC,
    LOCAL_REPLICATION_FACTOR,
    TOPIC_SPECS,
    topic_names,
)

__all__ = [
    "DLQ_TOPIC",
    "LOCAL_REPLICATION_FACTOR",
    "TOPIC_SPECS",
    "EventConsumer",
    "EventEnvelope",
    "EventEnvelopeValidationError",
    "EventProducer",
    "build_dlq_record",
    "dlq_topic_name",
    "topic_names",
    "validate_envelope_dict",
]
