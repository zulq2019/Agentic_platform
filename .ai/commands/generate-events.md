# generate-events.md

**Command:** `generate-events`  
**Version:** 1.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs — use when a story requires producing or consuming Kafka events

---

## Purpose

Use this command to generate all event-related code for a service: event definitions, producers, consumers, dead-letter queue handlers, and the corresponding contract validation tests.

This command enforces the platform's event contract standards. Every event must comply with the `EventEnvelope` schema. Every producer and consumer is observable and resilient by default.

One execution = one event flow (one topic, one producer, one consumer pair).

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Constitution — Architecture principles | `CONSTITUTION.md` (A-series) | Mandatory |
| Architecture — Event Bus section | `docs/architecture/REFERENCE_ARCHITECTURE.md` (Sections 7, 8) | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| Event Envelope schema | `contracts/event-envelope.schema.json` | Mandatory |
| Sequence Diagrams | `docs/engineering/implementation-roadmap/{PI}/SEQUENCE_DIAGRAMS.md` — target flow | Mandatory |
| User Story | `docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md` — target story | Mandatory |
| Data Model | `docs/engineering/implementation-roadmap/{PI}/DATA_MODEL.md` | If event carries entity state |
| Relevant ADRs | `DECISIONS.md` | For event naming and versioning decisions |

**Substitutions required:**

```
{PI}               = e.g. PI-01-Platform-Core
{story_id}         = e.g. US-PI-01-02
{service_name}     = e.g. task-queue-service
{topic_name}       = e.g. aep.task.created
{event_type}       = e.g. TaskCreated
{producer_service} = e.g. orchestrator-service
{consumer_service} = e.g. agent-runtime-service
{target_folder}    = e.g. src/platform/task/
```

---

## Preconditions

- [ ] The event flow is documented in `SEQUENCE_DIAGRAMS.md` for this PI
- [ ] The event topic name follows the naming convention: `aep.{domain}.{event_type_kebab}`
- [ ] The `EventEnvelope` schema is read and understood
- [ ] The domain service that triggers the event exists (for producers)
- [ ] The consumer action/domain service that handles the event exists (for consumers)

---

## Execution Steps

### Step 1 — Define the event schema

Create the event payload schema in `src/{target_folder}/events/schemas.py`:

Topic naming convention:
```
aep.{domain}.{event_type_kebab}

Examples:
  aep.task.created
  aep.agent.completed
  aep.workflow.gate.awaiting-approval
  aep.tool.invocation.failed
```

Event type naming:
- PascalCase: `TaskCreated`, `AgentCompleted`, `GateApprovalRequested`
- Never: `task_created`, `TASK_CREATED`

```python
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Literal

class {EventType}Payload(BaseModel):
    """Payload for {event_type} events."""
    # Domain-specific fields — no infrastructure fields here
    # Infrastructure fields (task_id, tenant_id, timestamp) live in the envelope
    resource_id: uuid.UUID = Field(..., description="ID of the resource that changed")
    ...

class {EventType}Envelope(BaseModel):
    """Full EventEnvelope-compliant wrapper for {event_type}."""
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: Literal["{EventType}"] = "{EventType}"
    schema_version: str = "1.0.0"
    emitted_by: str  # service name
    emitted_at: datetime = Field(default_factory=datetime.utcnow)
    task_id: uuid.UUID
    workflow_run_id: uuid.UUID
    tenant_id: uuid.UUID
    idempotency_key: str  # {task_id}:{operation} for deduplication
    payload: {EventType}Payload
```

Validate the schema against `contracts/event-envelope.schema.json` in a unit test immediately.

### Step 2 — Generate the producer

Create the producer in `src/{target_folder}/events/producers/{event_type_snake}.py`:

```python
from aep_common.kafka import KafkaProducer, ProducerConfig
from aep_common.logging import get_logger
from aep_common.tracing import get_tracer
from .schemas import {EventType}Envelope, {EventType}Payload

logger = get_logger(__name__)
tracer = get_tracer(__name__)

TOPIC = "{topic_name}"

class {EventType}Producer:
    def __init__(self, producer: KafkaProducer) -> None:
        self._producer = producer

    async def publish(
        self,
        payload: {EventType}Payload,
        task_id: uuid.UUID,
        workflow_run_id: uuid.UUID,
        tenant_id: uuid.UUID,
        idempotency_key: str,
    ) -> None:
        envelope = {EventType}Envelope(
            emitted_by="{producer_service}",
            task_id=task_id,
            workflow_run_id=workflow_run_id,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            payload=payload,
        )
        with tracer.start_as_current_span("publish_{event_type_snake}") as span:
            span.set_attribute("topic", TOPIC)
            span.set_attribute("task_id", str(task_id))
            span.set_attribute("tenant_id", str(tenant_id))
            span.set_attribute("idempotency_key", idempotency_key)
            
            await self._producer.send(
                topic=TOPIC,
                key=str(tenant_id),  # Partition by tenant for ordering
                value=envelope.model_dump_json(),
            )
            logger.info(
                "event.published",
                event_type="{EventType}",
                topic=TOPIC,
                task_id=str(task_id),
                tenant_id=str(tenant_id),
                event_id=str(envelope.event_id),
            )
```

### Step 3 — Generate the consumer

Create the consumer in `src/{target_folder}/events/consumers/{event_type_snake}.py`:

```python
from aep_common.kafka import KafkaConsumer, ConsumerConfig, MessageContext
from aep_common.logging import get_logger
from aep_common.tracing import get_tracer
from .schemas import {EventType}Envelope

logger = get_logger(__name__)
tracer = get_tracer(__name__)

TOPIC = "{topic_name}"
CONSUMER_GROUP = "{consumer_service}.{event_type_kebab}-consumer"
DLQ_TOPIC = "{topic_name}.dlq"

class {EventType}Consumer:
    def __init__(self, consumer: KafkaConsumer, handler: {EventType}Handler) -> None:
        self._consumer = consumer
        self._handler = handler

    async def start(self) -> None:
        await self._consumer.subscribe(
            topics=[TOPIC],
            group_id=CONSUMER_GROUP,
            max_poll_records=50,  # Bounded batch size
        )
        async for message in self._consumer:
            await self._process_with_retry(message)

    async def _process_with_retry(self, message: MessageContext) -> None:
        with tracer.start_as_current_span("consume_{event_type_snake}") as span:
            try:
                envelope = {EventType}Envelope.model_validate_json(message.value)
                span.set_attribute("task_id", str(envelope.task_id))
                span.set_attribute("tenant_id", str(envelope.tenant_id))
                span.set_attribute("event_id", str(envelope.event_id))
                
                # Idempotency check
                if await self._already_processed(envelope.idempotency_key):
                    logger.info("event.duplicate.skipped", idempotency_key=envelope.idempotency_key)
                    await message.ack()
                    return
                
                await self._handler.handle(envelope)
                await self._mark_processed(envelope.idempotency_key)
                await message.ack()
                
                logger.info(
                    "event.processed",
                    event_type="{EventType}",
                    task_id=str(envelope.task_id),
                    tenant_id=str(envelope.tenant_id),
                )
            except {EventType}ProcessingError as exc:
                logger.error(
                    "event.processing_failed",
                    error=str(exc),
                    task_id=str(envelope.task_id) if envelope else "unknown",
                    retry_count=message.retry_count,
                )
                if message.retry_count >= 3:
                    await self._send_to_dlq(message, exc)
                    await message.ack()
                else:
                    await message.nack(requeue=True, delay_seconds=2 ** message.retry_count)
```

### Step 4 — Generate the DLQ handler

Create the DLQ consumer in `src/{target_folder}/events/consumers/dlq_{event_type_snake}.py`:

The DLQ handler must:
- Log the failed message with full context at `ERROR` level
- Publish an `AuditEvent` recording the failure
- Optionally alert on-call via `alerting-service`
- Never silently discard messages

### Step 5 — Wire idempotency

Use Redis as the idempotency store:
```python
IDEMPOTENCY_KEY_TTL = 86400  # 24 hours — covers maximum retry window

async def _already_processed(self, key: str) -> bool:
    redis_key = f"aep:{self._tenant_id}:idempotency:{key}"
    return await self._redis.exists(redis_key)

async def _mark_processed(self, key: str) -> None:
    redis_key = f"aep:{self._tenant_id}:idempotency:{key}"
    await self._redis.setex(redis_key, IDEMPOTENCY_KEY_TTL, "1")
```

### Step 6 — Write contract validation tests

```python
def test_event_envelope_conforms_to_contract():
    """Published envelope must validate against contracts/event-envelope.schema.json"""
    payload = {EventType}Payload(resource_id=uuid.uuid4(), ...)
    envelope = {EventType}Envelope(
        emitted_by="test-service",
        task_id=uuid.uuid4(),
        workflow_run_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        idempotency_key="test-key",
        payload=payload,
    )
    schema = json.loads(Path("contracts/event-envelope.schema.json").read_text())
    jsonschema.validate(json.loads(envelope.model_dump_json()), schema)
```

### Step 7 — Write consumer resilience tests

Required tests:
- Happy path: valid event processed, handler called, offset committed
- Duplicate event: idempotency check fires, handler NOT called twice
- Malformed event: parsing error does not crash consumer
- Processing failure ≤ 3 retries: event requeued with delay
- Processing failure > 3 retries: event sent to DLQ, offset committed

---

## Expected Outputs

| Artifact | Location |
|----------|----------|
| Event schema models | `src/{target_folder}/events/schemas.py` |
| Producer | `src/{target_folder}/events/producers/{event_type_snake}.py` |
| Consumer | `src/{target_folder}/events/consumers/{event_type_snake}.py` |
| DLQ handler | `src/{target_folder}/events/consumers/dlq_{event_type_snake}.py` |
| Contract validation tests | `src/tests/contract/test_event_{event_type_snake}.py` |
| Consumer resilience tests | `src/tests/integration/{service_name}/test_consumer_{event_type_snake}.py` |
| Updated event catalogue | `docs/architecture/REFERENCE_ARCHITECTURE.md` Section 8 |

---

## Quality Gates

- [ ] Event envelope validates against `contracts/event-envelope.schema.json`
- [ ] Idempotency check implemented in every consumer
- [ ] DLQ configured with max retry of 3
- [ ] Consumer offset committed only after successful processing
- [ ] Tenant ID included in every envelope
- [ ] Idempotency key follows `{task_id}:{operation}` pattern
- [ ] All consumer resilience tests pass

---

## Completion Checklist

```
[ ] Event schema defined and validated against contract
[ ] Topic name follows aep.{domain}.{event_type_kebab} convention
[ ] Producer generated with tracing and structured logging
[ ] Consumer generated with idempotency, retry, and DLQ
[ ] DLQ handler generated
[ ] Contract validation tests written and passing
[ ] Consumer resilience tests written and passing
[ ] Event catalogue updated in REFERENCE_ARCHITECTURE.md
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Publish events without tenant_id in the envelope
- Commit Kafka offset before successful processing
- Skip idempotency — every consumer must be idempotent
- Route events directly between agents (events go to topics, not to named services)
- Use event type strings not matching `PascalCase` convention
- Hardcode Kafka broker addresses (use environment variables via Pydantic Settings)
- Implement business logic inside the consumer class (delegate to handler)
- Skip the DLQ — every consumer must have a dead-letter path
- Publish an event without emitting an OTEL trace span
- Send a different payload schema to the same topic for backward-incompatible changes without a version bump
