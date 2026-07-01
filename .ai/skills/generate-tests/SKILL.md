---
name: generate-tests
description: |
  When the engineer types /generate-tests <story_id>, generate the complete
  testing suite for one implemented User Story. Executes 6 phases in order:
  Read Context → Extract Acceptance Criteria → Identify Test Categories →
  Generate Tests by Category → Verify Coverage → Produce Test Summary.
  Never touches production code. Every acceptance criterion must have a
  corresponding test. Coverage must reach ≥80% on new code before the skill
  declares completion.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq, pytest
  file: read, write
---

# AEP Generate Tests

<purpose>
Complete test suite generation for one User Story on the Agentic Engineering
Platform. Driven entirely by acceptance criteria — every Given/When/Then
criterion maps to at least one test. The skill operates in write-only mode on
the test tree and read-only mode on production code. It never modifies
implementation files. All generated tests must actually fail when the
implementation is deleted — vacuous assertions are a constitutional violation
of this skill's contract.
</purpose>

---

## When To Activate

Trigger when the engineer types `/generate-tests` followed by a User Story ID.

```
/generate-tests US-01.03
/generate-tests US-02.07
```

The story ID format is `US-{PI}.{sequence}` where `{PI}` is the two-digit
Programme Increment number and `{sequence}` is the two-digit story sequence
within that PI.

---

## Repository Context to Read

Read these documents before writing a single test. They define the authoritative
standards every test must meet. Do not re-output their contents.

```bash
# Platform authorities — always required
cat CONSTITUTION.md
cat ARCHITECTURE.md

# Resolve the PI from the story ID prefix (e.g. US-01 → PI-01)
PI_DIR=$(ls docs/engineering/implementation-roadmap/ | grep "PI-$(echo $STORY_ID | cut -d- -f2 | cut -d. -f1)")

# PI planning documents
cat docs/engineering/implementation-roadmap/${PI_DIR}/ACCEPTANCE_CRITERIA.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/TESTING.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/DEFINITION_OF_DONE.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/IMPLEMENTATION.md
cat docs/engineering/implementation-roadmap/${PI_DIR}/CAPABILITIES.md

# Contracts — validate published events and registrations against these
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
cat contracts/tool-contract.schema.json
cat contracts/task-schema.schema.json
cat contracts/memory-schema.schema.json

# Locate implementation source files for the story
rg "${STORY_ID}" --include="*.py" -l
rg "${STORY_ID}" --include="*.ts" -l

# Discover existing test structure
find tests/ -name "*.py" | head -40
find tests/ -name "conftest.py"
cat pytest.ini 2>/dev/null || cat pyproject.toml | grep -A 20 "\[tool.pytest"
cat requirements-test.txt 2>/dev/null || cat requirements/test.txt 2>/dev/null
```

**Stop condition:** If `CONSTITUTION.md`, `ACCEPTANCE_CRITERIA.md`, or the
implementation source files cannot be read, stop and report. Test generation
cannot proceed without the acceptance criteria and the code under test.

---

## Preconditions

Verify all three conditions before proceeding to Phase 1. Report which
condition is unmet and stop.

### PC-1: Implementation Must Exist

```bash
# Find implementation files tagged with or related to the story
rg "${STORY_ID}" --include="*.py" -l
```

If no implementation files are found, stop with:

```
BLOCKED: No implementation found for {STORY_ID}.
Tests cannot be written before the implementation exists.
Complete the implementation first, then re-run /generate-tests {STORY_ID}.
```

**Why:** Tests that reference non-existent modules cannot be run or maintained.
Writing tests before implementation produces import errors and misleads coverage
tools into reporting false negatives.

### PC-2: Acceptance Criteria Must Be Written as Given/When/Then

Open `ACCEPTANCE_CRITERIA.md` and locate all criteria for `{STORY_ID}`.

Each criterion must follow this structure:
```
AC-{n}: {short title}
  Given: {precondition}
  When:  {action or event}
  Then:  {expected outcome}
```

If any criterion is not in Given/When/Then form, stop with:

```
BLOCKED: AC-{n} for {STORY_ID} is not in Given/When/Then format.
Rewrite the acceptance criteria before generating tests.
Ambiguous AC → ambiguous tests → false confidence in coverage.
```

**Why:** Tests derived from unstructured acceptance criteria drift from the
actual requirements and create a false sense of coverage. A Given/When/Then
criterion maps cleanly to a test fixture (Given), test action (When), and
assertion (Then). Without this structure, the test author must guess intent.

### PC-3: No Other Test Session in Progress

```bash
# Check for in-progress test generation marker
ls .ai/.generate-tests-lock 2>/dev/null
```

If a lock file exists, stop with:

```
BLOCKED: Another /generate-tests session is in progress (lock file present).
Check .ai/.generate-tests-lock for details. Remove it only if the previous
session terminated uncleanly.
```

Create the lock file when all preconditions pass:

```bash
echo "${STORY_ID} $(date -u +%Y-%m-%dT%H:%M:%SZ)" > .ai/.generate-tests-lock
```

Remove it at the end of Phase 6.

**Why:** Concurrent test generation sessions targeting the same story will
produce conflicting test files and non-deterministic coverage results.

---

## Execution Workflow

Execute these six phases in strict order. Do not skip a phase or reorder them.
Each phase has explicit outputs that the next phase depends on.

---

### Phase 1 — Read Context and Locate Implementation Files

**Goal:** Build a complete picture of what is implemented before writing any
test code. Tests must be faithful to the implementation — not aspirational.

#### 1.1 Read the User Story

```bash
# Extract the story from USER_STORIES.md
rg -A 20 "${STORY_ID}" docs/engineering/implementation-roadmap/${PI_DIR}/USER_STORIES.md | head -30
```

Record:
```
Story ID:        {STORY_ID}
As a:            {persona}
I want:          {capability}
So that:         {business value}
Capability:      {CAP-XX}
PI:              {PI_DIR}
```

#### 1.2 Locate Implementation Files

```bash
# Find all Python source files belonging to this story
rg "${STORY_ID}" --include="*.py" -l

# Find by capability if story tag not present
CAPABILITY=$(grep "${STORY_ID}" docs/engineering/implementation-roadmap/${PI_DIR}/CAPABILITIES.md | grep -oP "CAP-\d+")
rg "${CAPABILITY}" --include="*.py" -l

# Discover public surface — classes and functions exported
rg "^(class|def|async def)" <impl_files> -n
```

Build the **Implementation Map**:

```
Implementation Map for {STORY_ID}
──────────────────────────────────
src/{service}/domain/{module}.py
  Classes:   {ClassName1}, {ClassName2}
  Functions: {func1}(), {func2}()

src/{service}/api/{router}.py
  Endpoints: POST /api/v1/{resource}, GET /api/v1/{resource}/{id}

src/{service}/events/{producer}.py
  Publishes:  {EventType1} → aep.{domain}.{event-type}

src/{service}/events/{consumer}.py
  Consumes:  {EventType2} ← aep.{domain}.{event-type}

src/{service}/infra/{repository}.py
  Stores:    {EntityName} in PostgreSQL
```

#### 1.3 Read Existing Tests

```bash
# Find all existing test files for the affected modules
find tests/ -name "*.py" | xargs grep -l "{module_name}" 2>/dev/null

# Read conftest.py to understand shared fixtures
cat tests/conftest.py
cat tests/integration/conftest.py 2>/dev/null
```

Record which test files already exist, which fixtures are already provided, and
which test helpers can be reused. Do not duplicate existing test infrastructure.

**Output of Phase 1:**
- Implementation Map (file paths, classes, functions, endpoints, events)
- List of existing test files for this module
- Shared fixtures available in conftest.py

---

### Phase 2 — Extract Acceptance Criteria and Map to Tests

**Goal:** Every acceptance criterion maps to one or more named tests. No AC
without a test. No test without an AC it satisfies.

#### 2.1 Extract All Criteria for the Story

```bash
# Extract AC block from ACCEPTANCE_CRITERIA.md
rg -A 8 "^## ${STORY_ID}" docs/engineering/implementation-roadmap/${PI_DIR}/ACCEPTANCE_CRITERIA.md
```

For each criterion, build the **AC–Test Matrix**:

```
AC-{n}: {title}
  Given:    {fixture or setup}
  When:     {action}
  Then:     {assertion}
  Category: {unit|integration|contract|event|api|failure|retry|concurrency|e2e}
  Test ID:  test_ac_{n}_{short_description}
  File:     tests/{category}/test_{module}.py
```

**Category assignment rules:**

| Then clause contains…                                  | Category        |
|--------------------------------------------------------|-----------------|
| A specific domain return value or state change         | Unit            |
| Data persisted or retrieved from a real database       | Integration     |
| An event envelope field or schema validation result    | Contract        |
| A Kafka topic, offset, idempotency, or DLQ outcome     | Event           |
| An HTTP status code or response body                   | API             |
| A dependency down (DB, Kafka, Redis) → error published | Failure         |
| Retry count, back-off delay, or idempotency key reuse  | Retry           |
| Tenant A cannot see tenant B, or concurrent writes     | Concurrency     |
| A complete workflow from trigger to terminal state     | E2E             |

#### 2.2 Identify Coverage Gaps

Compare the Implementation Map (Phase 1) against the AC–Test Matrix. For every
public method, endpoint, and event handler with no corresponding AC, raise a
warning:

```
WARNING: {module}.{method}() has no corresponding AC in ACCEPTANCE_CRITERIA.md.
  Options:
    a) Add a missing AC to ACCEPTANCE_CRITERIA.md (preferred)
    b) Write a defensive unit test with a comment referencing this warning
```

Do not silently skip uncovered code. Uncovered public surface is a test debt
risk — a future change to that method will not be caught by the test suite.

**Output of Phase 2:**
- AC–Test Matrix (every criterion → test ID, category, file)
- Coverage gap warnings for uncovered implementation surface

---

### Phase 3 — Identify Test Categories Needed

**Goal:** Determine exactly which test categories the story requires. Not every
story needs E2E tests. Not every story produces Kafka events. Generate only
what is needed — but generate all of what is needed.

```
Required categories for {STORY_ID}:
  Unit           YES — {N} domain methods to test
  Integration    YES — persists to PostgreSQL
  Contract       YES — publishes {EventType} event
  Event          YES — Kafka consumer present
  API            YES — {N} HTTP endpoints exposed
  Failure        YES — dependency failures must publish AgentFailed
  Retry          YES — retry logic with idempotency key present
  Concurrency    YES — story touches tenant-scoped data
  E2E            NO  — story is not an end-to-end workflow trigger

Skipped categories with justification:
  E2E: {STORY_ID} is an internal domain operation, not a workflow trigger.
       E2E tests will be generated when the workflow-initiating story is tested.
```

**Why this step matters:** Generating all categories by default creates test
noise. Generating too few creates blind spots. An explicit declaration forces
the engineer to reason about what the story actually does.

---

### Phase 4 — Generate Tests by Category

Generate tests in this order. For each category, create one test file unless
the existing file structure dictates otherwise. Reuse conftest.py fixtures
wherever possible — do not re-implement shared setup inside test functions.

---

#### Category 1 — Unit Tests

**File pattern:** `tests/unit/test_{module_name}.py`

**Rules:**
- One test file per domain module or class
- Every public method: one happy-path test + at least two edge cases
- All dependencies (repositories, event publishers, HTTP clients) mocked
- No real database, no real Kafka, no real Redis in unit tests
- Assertions verify return values and calls on mocks — not log output

**Why mocking matters:** Unit tests must be fast (< 1 second each) and
deterministic. A test that waits for PostgreSQL is an integration test wearing
unit test clothes. It will be slow, flaky in CI, and misleading when the
domain logic has a bug unrelated to the database.

**Pytest structure:**

```python
# tests/unit/test_agent_registry_domain.py
"""
Unit tests for AgentRegistryDomain.
Covers: register(), resolve_by_capability(), deregister()
Story: {STORY_ID}
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.agent_registry.domain.agent_registry_domain import AgentRegistryDomain
from src.agent_registry.domain.exceptions import (
    AgentAlreadyRegisteredError,
    CapabilityNotFoundError,
)


@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.find_by_capability.return_value = None
    repo.save.return_value = None
    return repo


@pytest.fixture
def mock_event_publisher():
    return AsyncMock()


@pytest.fixture
def domain(mock_repository, mock_event_publisher):
    return AgentRegistryDomain(
        repository=mock_repository,
        event_publisher=mock_event_publisher,
    )


# ── AC-1: Happy path ──────────────────────────────────────────────────────────

class TestRegister:
    """describe('AgentRegistryDomain') > describe('register()')"""

    async def test_ac_1_registers_agent_and_publishes_event(
        self, domain, mock_repository, mock_event_publisher
    ):
        """
        AC-1: Given a valid agent contract, When register() is called,
        Then the agent is persisted and AgentRegistered event is published.
        """
        contract = _valid_agent_contract()

        await domain.register(contract)

        mock_repository.save.assert_awaited_once()
        saved_agent = mock_repository.save.call_args[0][0]
        assert saved_agent.agent_id == contract["agent_id"]

        mock_event_publisher.publish.assert_awaited_once()
        event = mock_event_publisher.publish.call_args[0][0]
        assert event["event_type"] == "AgentRegistered"
        assert event["payload"]["agent_id"] == contract["agent_id"]

    async def test_raises_when_agent_already_registered(
        self, domain, mock_repository
    ):
        """
        Edge case: duplicate registration must be rejected, not silently
        overwritten. Silent overwrites would allow a malicious or buggy
        agent to hijack an existing registration.
        """
        mock_repository.find_by_id.return_value = _existing_agent()
        contract = _valid_agent_contract()

        with pytest.raises(AgentAlreadyRegisteredError):
            await domain.register(contract)

    async def test_raises_when_contract_missing_required_fields(self, domain):
        """
        Edge case: incomplete contract must be rejected at domain boundary,
        not at the database layer. Failing at the DB layer leaks internal
        schema details and produces harder-to-diagnose errors.
        """
        incomplete_contract = {"agent_id": "test-agent"}  # missing capabilities etc.

        with pytest.raises(ValueError, match="contract"):
            await domain.register(incomplete_contract)

    async def test_does_not_publish_event_when_save_fails(
        self, domain, mock_repository, mock_event_publisher
    ):
        """
        Edge case: if the repository raises, the event must NOT be published.
        Publishing an event for an operation that was not durably committed
        produces phantom agents in the system and breaks idempotency.
        """
        mock_repository.save.side_effect = RuntimeError("DB unavailable")
        contract = _valid_agent_contract()

        with pytest.raises(RuntimeError):
            await domain.register(contract)

        mock_event_publisher.publish.assert_not_awaited()


class TestResolveByCapability:
    """describe('AgentRegistryDomain') > describe('resolve_by_capability()')"""

    async def test_ac_2_returns_agent_for_matching_capability(
        self, domain, mock_repository
    ):
        """
        AC-2: Given an agent registered with capability 'generates-unit-tests',
        When resolve_by_capability('generates-unit-tests') is called,
        Then the registered agent is returned.
        """
        mock_repository.find_by_capability.return_value = _existing_agent()

        result = await domain.resolve_by_capability("generates-unit-tests")

        assert result.agent_id == "test-agent-v1"

    async def test_raises_when_no_agent_has_capability(
        self, domain, mock_repository
    ):
        """
        Edge case: an unresolvable capability must raise CapabilityNotFoundError,
        not return None. Callers that forget to check for None would silently
        proceed without an agent, producing invisible failures.
        """
        mock_repository.find_by_capability.return_value = None

        with pytest.raises(CapabilityNotFoundError, match="generates-unit-tests"):
            await domain.resolve_by_capability("generates-unit-tests")

    async def test_resolution_is_scoped_to_tenant(
        self, domain, mock_repository
    ):
        """
        Edge case: capability resolution must pass tenant_id to the repository.
        Without tenant scoping, tenant A could resolve to an agent registered
        by tenant B — a direct Constitution S-series violation.
        """
        tenant_id = uuid4()

        await domain.resolve_by_capability("generates-unit-tests", tenant_id=tenant_id)

        mock_repository.find_by_capability.assert_awaited_once_with(
            capability="generates-unit-tests",
            tenant_id=tenant_id,
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _valid_agent_contract() -> dict:
    return {
        "agent_id": "test-agent-v1",
        "version": "1.0.0",
        "capabilities": ["generates-unit-tests"],
        "input_schema": {},
        "output_schema": {},
        "cost_class": "low",
        "idempotency_key_strategy": "task_id",
    }


def _existing_agent():
    from src.agent_registry.domain.models import RegisteredAgent
    return RegisteredAgent(agent_id="test-agent-v1", capabilities=["generates-unit-tests"])
```

---

#### Category 2 — Integration Tests

**File pattern:** `tests/integration/test_{module_name}_integration.py`

**Rules:**
- Use Testcontainers for all infrastructure (PostgreSQL, Kafka, Redis)
- No mocked infrastructure — the point is to test the real interaction
- Tests must verify data is durably persisted and retrievable
- Each test must clean up its own data (use transactions rolled back, or
  per-test schema isolation)
- Never mock the service under test — only mock external systems outside the
  platform boundary (third-party APIs, vendor SDKs)

**Why Testcontainers:** Integration tests that use a shared persistent database
are non-deterministic — test A's data bleeds into test B. Testcontainers starts
a clean container per test session and tears it down afterwards. This guarantees
isolation and makes tests safe to run in parallel in CI.

**Why no mocked infrastructure:** The entire value of an integration test is
verifying that the domain model maps correctly to the real database schema, that
Kafka serialisation round-trips cleanly, and that Redis TTLs behave as expected.
Mocking the infrastructure reverts the test to a unit test with extra ceremony.

**Pytest structure:**

```python
# tests/integration/test_agent_registry_integration.py
"""
Integration tests for AgentRegistryDomain with real PostgreSQL.
Story: {STORY_ID}
"""
import pytest
import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.agent_registry.infra.repository import PostgresAgentRepository
from src.agent_registry.domain.agent_registry_domain import AgentRegistryDomain
from src.agent_registry.infra.migrations import run_migrations


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as pg:
        yield pg


@pytest_asyncio.fixture(scope="session")
async def db_engine(postgres_container):
    engine = create_async_engine(postgres_container.get_connection_url())
    await run_migrations(engine)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    async with AsyncSession(db_engine) as session:
        async with session.begin():
            yield session
            await session.rollback()  # clean up after every test


@pytest_asyncio.fixture
async def repository(db_session):
    return PostgresAgentRepository(session=db_session)


class TestAgentRegistryIntegration:

    async def test_ac_1_persists_agent_and_retrieves_it(self, repository):
        """
        AC-1 integration: agent saved to PostgreSQL is retrievable by ID.
        Verifies the full domain → repository → database → retrieval round trip.
        """
        contract = _valid_agent_contract()
        await repository.save(contract)

        retrieved = await repository.find_by_id(contract["agent_id"])

        assert retrieved is not None
        assert retrieved.agent_id == contract["agent_id"]
        assert "generates-unit-tests" in retrieved.capabilities

    async def test_ac_2_capability_query_returns_correct_agent(self, repository):
        """
        AC-2 integration: capability-based lookup produces the registered agent.
        Verifies the SQL query and index behaviour under real PostgreSQL.
        """
        contract = _valid_agent_contract()
        await repository.save(contract)

        result = await repository.find_by_capability(
            capability="generates-unit-tests",
            tenant_id=contract["tenant_id"],
        )

        assert result is not None
        assert result.agent_id == contract["agent_id"]

    async def test_tenant_isolation_in_capability_query(self, repository):
        """
        Cross-tenant isolation: agent registered by tenant A is not returned
        when tenant B queries the same capability. Without this, any tenant
        can hijack any other tenant's agent resolution — a Constitution S2
        and MT1 violation.
        """
        from uuid import uuid4
        tenant_a = uuid4()
        tenant_b = uuid4()

        contract_a = {**_valid_agent_contract(), "tenant_id": str(tenant_a)}
        await repository.save(contract_a)

        result = await repository.find_by_capability(
            capability="generates-unit-tests",
            tenant_id=tenant_b,  # different tenant
        )

        assert result is None  # tenant B must not see tenant A's agent
```

---

#### Category 3 — Contract Tests

**File pattern:** `tests/contract/test_{story_id}_contracts.py`

**Rules:**
- Validate every published event envelope against `contracts/event-envelope.schema.json`
- Validate every agent registration payload against `contracts/agent-contract.schema.json`
- Validate every tool registration payload against `contracts/tool-contract.schema.json`
- Contract tests run against static payloads — no live infrastructure needed
- A contract test must fail if a required field is removed from the schema

**Why contract tests exist separately from unit tests:** Unit tests verify
domain behaviour. Contract tests verify that the signals the service emits to
the rest of the platform are structurally sound. A unit test for `publish_event`
may pass while the emitted envelope is missing `workflow_run_id`. This would
cause silent consumer failures in a different service — a cross-service bug that
unit tests never catch.

**Pytest structure:**

```python
# tests/contract/test_us_01_03_contracts.py
"""
Contract tests for {STORY_ID}.
Validates: event envelopes, agent registration payloads.
"""
import json
import pytest
from jsonschema import validate, ValidationError
from pathlib import Path

CONTRACTS_DIR = Path("contracts")


@pytest.fixture(scope="session")
def event_envelope_schema():
    return json.loads((CONTRACTS_DIR / "event-envelope.schema.json").read_text())


@pytest.fixture(scope="session")
def agent_contract_schema():
    return json.loads((CONTRACTS_DIR / "agent-contract.schema.json").read_text())


class TestEventEnvelopeContracts:

    def test_agent_registered_event_passes_envelope_schema(
        self, event_envelope_schema
    ):
        """
        Every AgentRegistered event the service publishes must contain all
        required envelope fields. Missing fields cause consumers to reject the
        message silently or raise schema validation errors at runtime.
        """
        from src.agent_registry.events.producers import build_agent_registered_event
        event = build_agent_registered_event(
            agent_id="test-agent-v1",
            tenant_id="tenant-acme",
            task_id="t-550e8400-e29b-41d4-a716-446655440000",
            workflow_run_id="wr-550e8400-e29b-41d4-a716-446655440000",
        )
        validate(instance=event, schema=event_envelope_schema)

    def test_event_type_is_pascal_case(self, event_envelope_schema):
        """
        Event type strings must be PascalCase per platform naming conventions.
        A type like 'agent_registered' will not match consumer subscriptions
        that filter on 'AgentRegistered', causing silent message loss.
        """
        from src.agent_registry.events.producers import build_agent_registered_event
        event = build_agent_registered_event(
            agent_id="test-agent-v1",
            tenant_id="tenant-acme",
            task_id="t-550e8400-e29b-41d4-a716-446655440000",
            workflow_run_id="wr-550e8400-e29b-41d4-a716-446655440000",
        )
        assert event["event_type"][0].isupper(), (
            f"event_type '{event['event_type']}' must be PascalCase"
        )
        assert "_" not in event["event_type"], (
            f"event_type '{event['event_type']}' must not contain underscores"
        )

    def test_envelope_rejected_when_tenant_id_missing(self, event_envelope_schema):
        """
        An envelope without tenant_id must fail schema validation. This ensures
        the schema itself enforces tenant isolation — not just the application
        code. Defence in depth.
        """
        envelope_without_tenant = {
            "event_id": "e-123",
            "event_type": "AgentRegistered",
            "schema_version": "1.0",
            "emitted_by": "agent-registry",
            "timestamp": "2026-06-28T00:00:00Z",
            "payload": {},
            # tenant_id intentionally omitted
        }
        with pytest.raises(ValidationError):
            validate(instance=envelope_without_tenant, schema=event_envelope_schema)


class TestAgentContractValidation:

    def test_valid_agent_contract_passes_schema(self, agent_contract_schema):
        """
        A correctly formed agent registration payload passes the JSON Schema.
        This is the golden path — verifying the schema and the builder agree.
        """
        from src.agent_registry.domain.builders import build_agent_registration
        contract = build_agent_registration(
            agent_id="test-agent-v1",
            version="1.0.0",
            capabilities=["generates-unit-tests"],
            cost_class="low",
        )
        validate(instance=contract, schema=agent_contract_schema)

    def test_contract_rejected_when_model_name_specified(self, agent_contract_schema):
        """
        Agents must NOT select a model by name — Constitution MI3. The contract
        schema must reject any payload that includes a model_name field.
        Enforcing this at the schema level prevents the MI3 violation from ever
        reaching the registry.
        """
        contract_with_model = {
            **_valid_registration_dict(),
            "model_name": "claude-opus-4",  # MI3 violation
        }
        with pytest.raises(ValidationError):
            validate(instance=contract_with_model, schema=agent_contract_schema)
```

---

#### Category 4 — Event Tests

**File pattern:** `tests/events/test_{story_id}_events.py`

**Rules:**
- Use Testcontainers with a real Kafka broker
- Verify the producer publishes to the correct topic with the correct envelope
- Verify the consumer is idempotent: delivering the same message twice must
  produce exactly one side effect, not two
- Verify the DLQ receives the message after `max_retries` consecutive failures
- Verify the offset is committed only after the handler succeeds, not on receipt
- Verify `acks=all` on the producer for durability-critical events

**Why idempotency is non-negotiable:** Kafka's "at-least-once" delivery
guarantee means a consumer may receive the same message more than once (network
partition recovery, consumer group rebalance). Without idempotency checks, a
retried `AgentCompleted` event could trigger a second workflow step, create
duplicate database records, or send a duplicate notification. These are the
category of bugs that are hardest to reproduce and diagnose.

**Why offset-after-processing:** If the consumer commits the offset on receipt
and then crashes during processing, the message is lost. Committing after
successful processing guarantees at-least-once processing semantics. The
idempotency check handles the duplicate delivery that at-least-once allows.

**Pytest structure:**

```python
# tests/events/test_us_01_03_events.py
"""
Event tests for {STORY_ID}.
Requires: real Kafka via Testcontainers.
"""
import asyncio
import pytest
from testcontainers.kafka import KafkaContainer
from kafka import KafkaProducer, KafkaConsumer
import json


@pytest.fixture(scope="session")
def kafka_container():
    with KafkaContainer("confluentinc/cp-kafka:7.6.0") as kafka:
        yield kafka


class TestAgentRegisteredEventPublishing:

    async def test_ac_3_publishes_to_correct_topic(self, kafka_container):
        """
        AC-3: When an agent is registered, AgentRegistered is published to
        aep.agent.registered. Publishing to the wrong topic means downstream
        consumers never receive the event — a silent system failure.
        """
        bootstrap = kafka_container.get_bootstrap_server()
        consumer = KafkaConsumer(
            "aep.agent.registered",
            bootstrap_servers=bootstrap,
            auto_offset_reset="earliest",
            consumer_timeout_ms=5000,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        # Trigger the registration
        from src.agent_registry.service import AgentRegistryService
        service = AgentRegistryService(bootstrap_servers=bootstrap)
        await service.register(_valid_agent_contract())

        messages = list(consumer)
        assert len(messages) == 1
        event = messages[0].value
        assert event["event_type"] == "AgentRegistered"
        assert event["tenant_id"] == _valid_agent_contract()["tenant_id"]

    async def test_consumer_is_idempotent(self, kafka_container):
        """
        Delivering the same AgentRegistered message twice must result in exactly
        one agent in the registry. Without idempotency, a Kafka partition leader
        failover during consumer group rebalance would cause duplicate agents —
        corrupting capability resolution for all tenants.
        """
        bootstrap = kafka_container.get_bootstrap_server()
        service = _make_service(bootstrap)

        message = _serialised_agent_registered_event()

        await service.handle_agent_registered(message)
        await service.handle_agent_registered(message)  # second delivery

        agents = await service.list_agents(agent_id=message["payload"]["agent_id"])
        assert len(agents) == 1  # exactly one, not two

    async def test_dlq_receives_message_after_max_retries(self, kafka_container):
        """
        When a consumer handler raises a non-retryable error on every attempt,
        the message must appear on aep.dlq after max_retries exhausted. Without
        a DLQ, the consumer would either loop forever (blocking the partition)
        or silently drop the message (losing data).
        """
        bootstrap = kafka_container.get_bootstrap_server()
        dlq_consumer = KafkaConsumer(
            "aep.dlq",
            bootstrap_servers=bootstrap,
            auto_offset_reset="earliest",
            consumer_timeout_ms=8000,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        # Inject a handler that always fails
        service = _make_service(bootstrap, handler_always_fails=True)
        message = _serialised_agent_registered_event()
        await service.handle_agent_registered(message)

        dlq_messages = list(dlq_consumer)
        assert any(
            m.value.get("original_topic") == "aep.agent.registered"
            for m in dlq_messages
        ), "Failed message must appear on the DLQ after max retries"

    async def test_offset_committed_only_after_success(self, kafka_container, mocker):
        """
        The Kafka offset must not be committed until the handler completes
        successfully. Committing on receipt and then crashing loses the message.
        Verify the commit call comes after the handler's await, not before.
        """
        bootstrap = kafka_container.get_bootstrap_server()
        commit_order = []

        async def tracking_handler(msg):
            commit_order.append("handler")
            return "ok"

        def tracking_commit():
            commit_order.append("commit")

        service = _make_service(bootstrap)
        mocker.patch.object(service._consumer, "commit", side_effect=tracking_commit)
        service._handler = tracking_handler

        await service._process_one_message(_serialised_agent_registered_event())

        assert commit_order == ["handler", "commit"], (
            f"Expected handler then commit, got: {commit_order}"
        )
```

---

#### Category 5 — API Tests

**File pattern:** `tests/api/test_{story_id}_api.py`

**Rules:**
- Use FastAPI `TestClient` or `httpx.AsyncClient` with the app mounted
- One test per HTTP status code that the endpoint can return
- Happy path: verify 200/201 response body shape
- Auth: missing JWT → 401, wrong tenant → 403
- Validation: extra fields forbidden, missing required field → 422
- Not found: unknown ID → 404
- Rate limit: exceed threshold → 429
- Domain error: verify it maps to the correct status code (not 500)
- Never test FastAPI internals — test the HTTP contract at the route level

**Why every status code needs a test:** An endpoint that returns 200 for a
missing resource is a silent data integrity error. An endpoint that returns 500
for a validation failure leaks internal exception details. Each HTTP status code
represents a distinct failure mode with different client recovery strategies.
Testing only the happy path leaves all error paths unverified until a production
incident exposes them.

**Pytest structure:**

```python
# tests/api/test_us_01_03_api.py
"""
API tests for {STORY_ID}.
Endpoints: POST /api/v1/agents, GET /api/v1/agents/{agent_id}
"""
import pytest
from httpx import AsyncClient
from fastapi import status

from src.agent_registry.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.fixture
def valid_auth_headers():
    return {"Authorization": "Bearer valid-tenant-a-token"}


@pytest.fixture
def wrong_tenant_headers():
    return {"Authorization": "Bearer tenant-b-token"}


class TestPostAgentRegistration:

    async def test_ac_4_returns_201_on_valid_registration(
        self, client, valid_auth_headers
    ):
        """
        AC-4: POST /api/v1/agents with a valid contract returns 201 Created
        with the agent_id in the response body.
        """
        response = await client.post(
            "/api/v1/agents",
            json=_valid_api_payload(),
            headers=valid_auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["agent_id"] == _valid_api_payload()["agent_id"]

    async def test_returns_401_when_auth_header_missing(self, client):
        """
        Every public endpoint must reject unauthenticated requests with 401.
        A missing auth check allows any caller to register arbitrary agents
        into the platform — a Constitution SR2 violation.
        """
        response = await client.post("/api/v1/agents", json=_valid_api_payload())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_returns_403_when_tenant_does_not_match(
        self, client, wrong_tenant_headers
    ):
        """
        tenant_id is extracted from the auth context, not the request body.
        Passing a token for tenant B when registering an agent for tenant A
        must be rejected with 403, not silently registered under the wrong tenant.
        """
        payload = {**_valid_api_payload(), "tenant_id": "tenant-a"}
        response = await client.post(
            "/api/v1/agents",
            json=payload,
            headers=wrong_tenant_headers,  # tenant B token
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_returns_422_when_required_field_missing(
        self, client, valid_auth_headers
    ):
        """
        Missing capabilities field must be caught by Pydantic at the API
        boundary and returned as 422. This prevents malformed contracts from
        reaching the domain layer.
        """
        payload = {k: v for k, v in _valid_api_payload().items() if k != "capabilities"}
        response = await client.post(
            "/api/v1/agents",
            json=payload,
            headers=valid_auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_returns_409_on_duplicate_registration(
        self, client, valid_auth_headers
    ):
        """
        Registering the same agent_id twice must return 409 Conflict, not 500.
        A 500 response leaks the internal AlreadyRegisteredError message
        and prevents clients from distinguishing duplicate from server error.
        """
        payload = _valid_api_payload()
        await client.post("/api/v1/agents", json=payload, headers=valid_auth_headers)

        response = await client.post(
            "/api/v1/agents",
            json=payload,
            headers=valid_auth_headers,
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_returns_429_when_rate_limit_exceeded(
        self, client, valid_auth_headers
    ):
        """
        Exceeding the per-tenant rate limit must return 429. Without this,
        a runaway agent or a misconfigured tenant can flood the registry
        and degrade performance for all tenants — an MT2 violation.
        """
        for _ in range(100):  # exceed the rate limit threshold
            payload = {**_valid_api_payload(), "agent_id": f"agent-{_}"}
            await client.post("/api/v1/agents", json=payload, headers=valid_auth_headers)

        response = await client.post(
            "/api/v1/agents",
            json={**_valid_api_payload(), "agent_id": "agent-overload"},
            headers=valid_auth_headers,
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
```

---

#### Category 6 — Failure Tests

**File pattern:** `tests/failure/test_{story_id}_failures.py`

**Rules:**
- Simulate each infrastructure dependency being unavailable: database down,
  Kafka unreachable, Redis connection refused
- Verify the correct error event is published when the dependency is down
  (usually `AgentFailed` with a structured error payload)
- Verify there are no silent failures — every error path has an observable output
- Use `unittest.mock.patch` to raise `ConnectionRefusedError`, `TimeoutError`,
  or vendor-specific exceptions

**Why failure tests exist as a separate category:** Happy-path tests verify the
system works. Failure tests verify the system fails gracefully. A service that
silently swallows a database timeout and returns HTTP 200 with empty data is
worse than one that returns 503 — the caller cannot distinguish success from
failure. The AEP Constitution principle P1 requires explicit failure signalling.

**Pytest structure:**

```python
# tests/failure/test_us_01_03_failures.py
"""
Failure mode tests for {STORY_ID}.
Covers: database unavailable, Kafka unavailable, Redis unavailable.
"""
import pytest
from unittest.mock import AsyncMock, patch


class TestDatabaseUnavailable:

    async def test_publishes_agent_failed_when_db_is_down(
        self, domain, mock_event_publisher, mock_repository
    ):
        """
        When PostgreSQL is unreachable during agent registration, an AgentFailed
        event must be published. Silent failures leave the orchestrator waiting
        forever for a completion event that never arrives.
        """
        mock_repository.save.side_effect = ConnectionRefusedError("DB unreachable")

        with pytest.raises(ConnectionRefusedError):
            await domain.register(_valid_agent_contract())

        # AgentFailed must be published — not swallowed
        mock_event_publisher.publish.assert_awaited_once()
        event = mock_event_publisher.publish.call_args[0][0]
        assert event["event_type"] == "AgentFailed"
        assert "ConnectionRefusedError" in event["payload"]["error_type"]

    async def test_no_partial_write_when_db_fails_mid_transaction(
        self, domain, mock_repository, mock_event_publisher
    ):
        """
        If the database raises mid-transaction (e.g. after insert but before
        index update), the domain must roll back completely. Partial writes
        corrupt the registry state and cause non-deterministic capability
        resolution.
        """
        mock_repository.save.side_effect = RuntimeError("constraint violation")

        with pytest.raises(RuntimeError):
            await domain.register(_valid_agent_contract())

        # Verify no capability index entry was left behind
        mock_repository.delete_capability_index.assert_not_called()


class TestKafkaUnavailable:

    async def test_registration_succeeds_even_when_kafka_is_down(
        self, domain, mock_repository, mock_event_publisher
    ):
        """
        Agent registration is a write-side operation. The database write must
        succeed even if Kafka is temporarily unavailable. The event will be
        retried via the outbox pattern. Failing the registration because the
        event bus is down violates the independence of concerns.
        """
        mock_event_publisher.publish.side_effect = TimeoutError("Kafka unreachable")

        # Registration should succeed (persisted to DB)
        result = await domain.register_with_outbox(_valid_agent_contract())
        assert result.agent_id == _valid_agent_contract()["agent_id"]

        # Verify the outbox entry was created for later retry
        mock_repository.save_outbox_entry.assert_awaited_once()


class TestRedisUnavailable:

    async def test_capability_resolution_falls_back_to_db_when_cache_is_down(
        self, domain, mock_repository, mock_cache
    ):
        """
        The capability resolution cache (Redis) is an optimisation, not a
        correctness dependency. When Redis is unreachable, resolution must
        fall back to the PostgreSQL query. Crashing on cache failure would
        make agent resolution fragile — violating P1 (resilience).
        """
        mock_cache.get.side_effect = ConnectionRefusedError("Redis unreachable")
        mock_repository.find_by_capability.return_value = _existing_agent()

        result = await domain.resolve_by_capability("generates-unit-tests")

        assert result is not None
        mock_repository.find_by_capability.assert_awaited_once()
```

---

#### Category 7 — Retry Tests

**File pattern:** `tests/retry/test_{story_id}_retry.py`

**Rules:**
- Verify exponential back-off: each retry waits longer than the previous
- Verify the maximum retry count is respected — no infinite loops
- Verify idempotency key prevents duplicate side effects across retries
- Mock `asyncio.sleep` or the retry library's sleep to make tests fast
- Verify that a retried operation with the same idempotency key produces
  the same output, not a second operation

**Why max retries matter:** An unbounded retry loop on a database failure will
consume all connections in the pool, degrading service for all tenants. A bounded
retry with exponential back-off and jitter is the standard resilience pattern.

**Why idempotency across retries matters:** If the first attempt persists the
agent to the database but then fails before publishing the event, a retry will
attempt the persist again. Without an idempotency key, this creates a duplicate
agent. With an idempotency key derived from `task_id`, the second persist is
rejected as a no-op.

**Pytest structure:**

```python
# tests/retry/test_us_01_03_retry.py
"""
Retry and idempotency tests for {STORY_ID}.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, call


class TestRetryBehaviour:

    async def test_retries_with_exponential_backoff(self, domain, mock_repository):
        """
        Each successive retry must wait at least 2× longer than the previous.
        Fixed-interval retries can cause retry storms when many consumers
        fail simultaneously — each retries at the same instant, flooding
        the recovering dependency.
        """
        mock_repository.save.side_effect = [
            ConnectionRefusedError("attempt 1"),
            ConnectionRefusedError("attempt 2"),
            None,  # third attempt succeeds
        ]
        sleep_calls = []

        with patch("asyncio.sleep", side_effect=lambda t: sleep_calls.append(t)):
            await domain.register_with_retry(_valid_agent_contract(), max_retries=3)

        assert len(sleep_calls) == 2
        assert sleep_calls[1] >= sleep_calls[0] * 1.5, (
            f"Expected exponential back-off, got delays: {sleep_calls}"
        )

    async def test_raises_after_max_retries_exhausted(self, domain, mock_repository):
        """
        After max_retries consecutive failures, the domain must stop retrying
        and raise the terminal exception. Continuing indefinitely would block
        the caller's task slot and starve other tasks.
        """
        mock_repository.save.side_effect = ConnectionRefusedError("always fails")

        with pytest.raises(ConnectionRefusedError):
            with patch("asyncio.sleep"):
                await domain.register_with_retry(_valid_agent_contract(), max_retries=3)

        assert mock_repository.save.call_count == 3

    async def test_idempotency_key_prevents_duplicate_on_retry(
        self, domain, mock_repository, mock_event_publisher
    ):
        """
        If the first attempt persists the agent but fails before publishing
        the event, a retry must not create a second agent. The idempotency key
        derived from task_id must cause the second persist to be a no-op.
        """
        task_id = "t-550e8400-e29b-41d4-a716-446655440000"
        contract = {**_valid_agent_contract(), "task_id": task_id}

        # First attempt: save succeeds, publish fails
        mock_event_publisher.publish.side_effect = [
            TimeoutError("Kafka down"),
            None,  # second attempt succeeds
        ]

        with patch("asyncio.sleep"):
            await domain.register_with_retry(contract, max_retries=2)

        # Repository save called once despite two publish attempts
        assert mock_repository.save.call_count == 1, (
            "Idempotency key must prevent a second database write on retry"
        )
```

---

#### Category 8 — Concurrency Tests

**File pattern:** `tests/concurrency/test_{story_id}_concurrency.py`

**Rules:**
- Cross-tenant isolation: tenant A must not be able to see, modify, or
  interfere with tenant B's data — under concurrent load
- Concurrent writes: two concurrent operations on the same resource must not
  corrupt state (last-write-wins is not acceptable for agent registration)
- Use `asyncio.gather` to simulate concurrent requests in tests
- Verify row-level locking or optimistic concurrency control prevents races

**Why concurrency tests cannot be skipped when a story touches data:** A
single-threaded test suite passes for a multi-tenant service even if the
isolation is completely broken, because only one tenant is tested at a time.
Concurrency tests are the only way to verify that tenant A and tenant B
exercising the system simultaneously do not corrupt each other's state.

**Pytest structure:**

```python
# tests/concurrency/test_us_01_03_concurrency.py
"""
Concurrency and cross-tenant isolation tests for {STORY_ID}.
"""
import asyncio
import pytest
from uuid import uuid4


class TestCrossTenantIsolation:

    async def test_tenant_a_cannot_see_tenant_b_agents(
        self, repository
    ):
        """
        Constitution MT1: tenant isolation is absolute. Tenant A listing its
        agents must receive only its own agents, even if tenant B registered
        agents with identical capability names concurrently.
        """
        tenant_a = str(uuid4())
        tenant_b = str(uuid4())

        await asyncio.gather(
            repository.save({**_valid_agent_contract(), "tenant_id": tenant_a}),
            repository.save({**_valid_agent_contract(), "agent_id": "agent-b", "tenant_id": tenant_b}),
        )

        tenant_a_agents = await repository.list_by_tenant(tenant_id=tenant_a)
        agent_ids = [a.agent_id for a in tenant_a_agents]

        assert "test-agent-v1" in agent_ids
        assert "agent-b" not in agent_ids, (
            "Tenant A must not see tenant B's agents"
        )


class TestConcurrentWrites:

    async def test_concurrent_registration_does_not_corrupt_state(
        self, repository
    ):
        """
        Two concurrent attempts to register the same agent_id (e.g. from two
        identical request replays) must result in exactly one agent record —
        not two. Database unique constraint must be enforced under concurrent
        load.
        """
        contract = _valid_agent_contract()

        results = await asyncio.gather(
            repository.save(contract),
            repository.save(contract),
            return_exceptions=True,
        )

        # One succeeds, one raises a duplicate-key error
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 1, (
            "Exactly one of the concurrent saves must fail to prevent duplicates"
        )

        agents = await repository.list_by_tenant(tenant_id=contract["tenant_id"])
        assert len([a for a in agents if a.agent_id == contract["agent_id"]]) == 1
```

---

#### Category 9 — End-to-End Tests

**Only generate E2E tests when the story is an end-to-end workflow trigger.**

Indicators that E2E tests are required:
- The story's `Then` clause describes a terminal workflow state
- The story publishes `TaskCreated` or a workflow-initiating event
- The story's IMPLEMENTATION.md references the `make dev-up` environment

**File pattern:** `tests/e2e/test_{story_id}_e2e.py`

**Rules:**
- Use the `make dev-up` Docker Compose environment — all real services
- No mocks of any platform service — only mock third-party vendor APIs
- Test must create real state, observe real events, verify real outcomes
- E2E tests are slow by design — tag with `@pytest.mark.e2e` for CI filtering
- Tear down all created resources at the end of the test

**Why E2E tests are restricted to workflow triggers:** E2E tests are expensive
to run and maintain. Writing them for every story produces a test suite that is
slow and brittle. Restricting them to stories that initiate or complete a
workflow ensures the full system integration is tested exactly once per workflow
boundary, not for every intermediate step.

**Pytest structure:**

```python
# tests/e2e/test_us_01_03_e2e.py
"""
E2E test for {STORY_ID} — end-to-end workflow trigger.
Requires: make dev-up environment running.
Tag: pytest.mark.e2e
"""
import pytest
import asyncio


@pytest.mark.e2e
class TestWorkflowTriggerE2E:

    async def test_ac_5_task_created_triggers_agent_selection(
        self, dev_env_client
    ):
        """
        AC-5 (E2E): Given the platform is running, When a TaskCreated event is
        published for story {STORY_ID}, Then the orchestrator selects an agent
        and publishes AgentDispatched within 10 seconds.

        This test covers the full event chain:
          TaskCreated → Orchestrator → AgentRegistry.resolve → AgentDispatched
        """
        task_id = await dev_env_client.publish_task_created(
            story_id="{STORY_ID}",
            capability_required="generates-unit-tests",
        )

        event = await dev_env_client.wait_for_event(
            topic="aep.agent.dispatched",
            predicate=lambda e: e["payload"]["task_id"] == task_id,
            timeout_seconds=10,
        )

        assert event is not None, (
            f"AgentDispatched not received within 10s for task {task_id}"
        )
        assert event["payload"]["capability"] == "generates-unit-tests"
        assert event["tenant_id"] == dev_env_client.tenant_id
```

---

### Phase 5 — Verify Coverage

**Goal:** Confirm that the generated tests collectively achieve ≥80% coverage
on all implementation files belonging to this story. Confirm that every test
actually fails when the implementation is removed.

#### 5.1 Run pytest with coverage

```bash
# Identify implementation modules
IMPL_MODULES=$(rg "${STORY_ID}" --include="*.py" -l | grep -v test | tr '\n' ',')

# Run all tests for the story
pytest tests/ -m "story_${STORY_ID//./_}" \
  --cov=src \
  --cov-report=term-missing \
  --cov-fail-under=80 \
  -v

# If story marker is not applied, run by directory
pytest tests/unit/ tests/integration/ tests/contract/ tests/events/ \
  tests/api/ tests/failure/ tests/retry/ tests/concurrency/ \
  --cov=src/${SERVICE_NAME} \
  --cov-report=term-missing \
  --cov-fail-under=80 \
  -v
```

**If coverage is below 80%:**

1. Read the coverage report `term-missing` output — identify the uncovered lines
2. For each uncovered block, determine whether it is:
   - A missing test case (add the test)
   - Dead code that can never execute (document with a comment — do not test)
   - Error handling that is hard to reach (add a failure test for it)
3. Do not add tests that trivially execute the line without asserting anything
   meaningful — vacuous coverage is worse than honest uncoverage

#### 5.2 Verify Tests Fail Without Implementation

```bash
# Rename the implementation module temporarily
mv src/${SERVICE}/domain/${MODULE}.py src/${SERVICE}/domain/${MODULE}.py.bak

# Run the unit tests — they must ALL fail (ImportError or assertion failure)
pytest tests/unit/test_${MODULE}.py -v 2>&1 | grep -E "PASSED|FAILED|ERROR"

# Restore the implementation
mv src/${SERVICE}/domain/${MODULE}.py.bak src/${SERVICE}/domain/${MODULE}.py
```

If any test passes after the implementation is removed, that test is vacuous.
It passes regardless of what the implementation does — it provides zero
confidence and should be rewritten to assert something meaningful.

**Why this verification is mandatory:** A test suite that achieves 80% coverage
with vacuous assertions is identical in practice to a 0% test suite. The CI
pipeline will be green while the implementation can be completely broken. This
check costs 30 seconds and eliminates that failure mode entirely.

---

### Phase 6 — Produce Test Summary

Remove the lock file:

```bash
rm .ai/.generate-tests-lock
```

Produce the following structured output:

```
## Test Generation Summary — {STORY_ID}

Story: {title}
PI:    {PI_DIR}

### AC Coverage Matrix

| AC   | Title                       | Category    | Test File                              | Test Function                              | Status   |
|------|-----------------------------|-------------|----------------------------------------|--------------------------------------------|----------|
| AC-1 | {title}                     | Unit        | tests/unit/test_{module}.py            | test_ac_1_{description}                    | COVERED  |
| AC-2 | {title}                     | Integration | tests/integration/test_{module}_i.py   | test_ac_2_{description}                    | COVERED  |
| AC-3 | {title}                     | Event       | tests/events/test_{story}_events.py    | test_ac_3_{description}                    | COVERED  |
| AC-4 | {title}                     | API         | tests/api/test_{story}_api.py          | test_ac_4_{description}                    | COVERED  |
| AC-5 | {title}                     | E2E         | tests/e2e/test_{story}_e2e.py          | test_ac_5_{description}                    | COVERED  |

### Tests Generated

| Category    | Count | File(s)                                  |
|-------------|-------|------------------------------------------|
| Unit        | {N}   | tests/unit/test_{module}.py              |
| Integration | {N}   | tests/integration/test_{module}_i.py     |
| Contract    | {N}   | tests/contract/test_{story}_contracts.py |
| Event       | {N}   | tests/events/test_{story}_events.py      |
| API         | {N}   | tests/api/test_{story}_api.py            |
| Failure     | {N}   | tests/failure/test_{story}_failures.py   |
| Retry       | {N}   | tests/retry/test_{story}_retry.py        |
| Concurrency | {N}   | tests/concurrency/test_{story}_conc.py   |
| E2E         | {N}   | tests/e2e/test_{story}_e2e.py            |
| **TOTAL**   | **{N}** |                                        |

### Coverage Report

Module                                   Statements   Missing   Coverage
──────────────────────────────────────────────────────────────────────────
src/{service}/domain/{module}.py         {N}          {N}       {N}%
src/{service}/api/{router}.py            {N}          {N}       {N}%
src/{service}/events/{producer}.py       {N}          {N}       {N}%
──────────────────────────────────────────────────────────────────────────
TOTAL                                    {N}          {N}       {N}%

Status: {PASS ≥80% / FAIL <80%}

### Vacuous Test Check

{N} tests verified to fail when implementation removed.
{N} tests required remediation (identified and rewritten).

### Definition of Done — Testing Gate

- [ ] Every AC criterion has at least one named test
- [ ] Coverage ≥ 80% on all new implementation files
- [ ] All tests pass in CI (pytest exit code 0)
- [ ] No test passes when the implementation is removed
- [ ] Cross-tenant isolation verified (if story touches data)
- [ ] DLQ path tested (if story includes a Kafka consumer)
- [ ] Idempotency verified (if story includes a write operation)
- [ ] Failure modes tested for every infrastructure dependency
```

---

## Test Naming Conventions

Every test name must be self-documenting. A failing test name is the first
thing an engineer sees in CI — it must communicate exactly what failed without
requiring them to read the test body.

### Standard Pattern

```
test_{method}_{scenario}
```

Examples:
```python
test_register_happy_path
test_register_raises_when_contract_missing_required_fields
test_resolve_by_capability_raises_when_no_agent_matches
test_resolve_by_capability_scopes_query_to_tenant
```

### Acceptance Criterion Pattern

For tests that directly implement a Given/When/Then criterion:

```
test_ac_{criterion_id}_{short_description}
```

Examples:
```python
test_ac_1_registers_agent_and_publishes_event
test_ac_2_capability_query_returns_correct_agent
test_ac_3_publishes_to_correct_topic
test_ac_4_returns_201_on_valid_registration
test_ac_5_task_created_triggers_agent_selection
```

### Class + describe Nesting Pattern

Group tests by class, nesting by the `describe / it` convention from the
platform testing rules:

```python
class TestRegister:
    """describe('AgentRegistryDomain') > describe('register()')"""

    async def test_ac_1_registers_agent_and_publishes_event(self): ...
    async def test_raises_when_agent_already_registered(self): ...
    async def test_raises_when_contract_missing_required_fields(self): ...
```

### Marker Convention

Apply story-level pytest markers to all generated tests so they can be run
in isolation:

```python
@pytest.mark.story_us_01_03
async def test_ac_1_registers_agent_and_publishes_event(self): ...
```

Register the marker in `pytest.ini` or `pyproject.toml`:

```ini
[pytest]
markers =
    story_us_01_03: Tests for User Story US-01.03
    e2e: End-to-end tests requiring make dev-up environment
```

---

## Expected Outputs

| Artifact                                         | Location                                          | Created by Phase |
|--------------------------------------------------|---------------------------------------------------|-----------------|
| Unit test file                                   | `tests/unit/test_{module}.py`                     | Phase 4         |
| Integration test file                            | `tests/integration/test_{module}_integration.py`  | Phase 4         |
| Contract test file                               | `tests/contract/test_{story_id}_contracts.py`     | Phase 4         |
| Event test file                                  | `tests/events/test_{story_id}_events.py`          | Phase 4         |
| API test file                                    | `tests/api/test_{story_id}_api.py`                | Phase 4         |
| Failure test file                                | `tests/failure/test_{story_id}_failures.py`       | Phase 4         |
| Retry test file                                  | `tests/retry/test_{story_id}_retry.py`            | Phase 4         |
| Concurrency test file                            | `tests/concurrency/test_{story_id}_concurrency.py`| Phase 4         |
| E2E test file (conditional)                      | `tests/e2e/test_{story_id}_e2e.py`                | Phase 4         |
| pytest coverage report                           | Terminal output + `.coverage`                     | Phase 5         |
| Test summary (AC matrix + coverage table)        | Terminal output                                   | Phase 6         |

---

## Completion Checklist

Every item must be checked before declaring test generation complete.

### AC Coverage
- [ ] Every Given/When/Then criterion in ACCEPTANCE_CRITERIA.md for this story
      has at least one test named `test_ac_{n}_*`
- [ ] The AC–Test Matrix in the summary shows COVERED for every criterion
- [ ] No criterion marked COVERED without a corresponding test function that
      exists and passes

### Coverage Threshold
- [ ] `pytest --cov-fail-under=80` passes on all new implementation files
- [ ] Coverage is not inflated by vacuous assertions (Phase 5 verification done)

### Test Quality
- [ ] No test body consists only of `assert True` or `pass`
- [ ] Every mock `assert_called` or `assert_awaited` assertion verifies the
      argument value, not just the call count
- [ ] Every test has a docstring explaining the AC it covers and why the
      failure mode it tests matters
- [ ] All tests removed from coverage by `# pragma: no cover` have a documented
      reason

### Isolation and Correctness
- [ ] Unit tests use no real infrastructure (no Testcontainers, no real DB URLs)
- [ ] Integration tests use Testcontainers — no shared persistent test database
- [ ] Each integration test cleans up its own data (transaction rollback or
      per-test schema)
- [ ] E2E tests tagged `@pytest.mark.e2e` and skipped in standard CI runs

### Platform Principles (Constitution Compliance)
- [ ] Cross-tenant isolation verified if story touches any data store
- [ ] DLQ path tested if story includes a Kafka consumer
- [ ] Idempotency tested for every write operation in the story
- [ ] No test imports from another agent's module (A1 — even in tests)
- [ ] No credentials hardcoded in test files or fixtures (SR1)
- [ ] All test fixtures use `tenant_id` derived from a fixture, not a hardcoded
      string constant shared across tests

---

## Forbidden Actions

Every forbidden action below includes the failure mode it prevents. These are
not stylistic preferences — each prohibition protects against a specific class
of production incident.

### FBD-1: Never Modify Production Code

**Forbidden:** Editing any file under `src/` while the skill is active.

**Failure mode prevented:** Test generation that requires changing production
code to be testable is a sign the production code has inadequate seams. Adding
seams under time pressure produces poorly designed interfaces that are
subsequently adopted as the production API. All test seams must be present in
the implementation before tests are written.

### FBD-2: Never Write Tests That Always Pass Regardless of Implementation

**Forbidden:** `assert True`, `assert 1 == 1`, asserting only that a function
was called without asserting what it was called with, or mocking the return
value and then asserting it equals the mocked value.

**Failure mode prevented:** A test suite with vacuous assertions achieves 100%
coverage while providing zero confidence. The CI pipeline reports green on a
broken build. Engineers discover the bug in production when a customer reports
it.

### FBD-3: Never Mock the Service Under Test in Integration Tests

**Forbidden:** Mocking `AgentRegistryDomain` in a test file that is supposed to
test `AgentRegistryDomain`.

**Failure mode prevented:** An integration test that mocks its subject is
testing the mock library, not the subject. It provides false confidence that
the real service behaves correctly when talking to real infrastructure.

### FBD-4: Never Skip Acceptance Criteria Tests

**Forbidden:** Generating tests only for edge cases while omitting tests named
after the Given/When/Then criteria in ACCEPTANCE_CRITERIA.md.

**Failure mode prevented:** The acceptance criteria are the contract between
the engineering team and the business. A story where no test references an AC
can be closed as "done" in the PI board while the acceptance criteria remain
unverified. This is the most common source of failed sprint reviews.

### FBD-5: Never Use External Network Resources in Tests

**Forbidden:** Tests that make real HTTP calls to GitHub, AWS, Stripe, or any
external API. Tests that connect to a cloud Kafka cluster or a production database.

**Failure mode prevented:** External network calls in tests make the test suite
non-deterministic (the external service may be unavailable), slow (network
latency), and insecure (tests may leak data to production systems). Testcontainers
provides isolated, local, ephemeral infrastructure that eliminates all three
failure modes.

### FBD-6: Never Assert on Log Output as a Substitute for Behavioural Assertions

**Forbidden:** `assert "AgentRegistered" in caplog.text` as the only assertion
in a test that is supposed to verify an event was published.

**Failure mode prevented:** Log output is an observability aid, not a
behavioural contract. Log messages can be changed, removed, or reformatted
without breaking the system. Tests that rely on log output will fail on
refactors that change logging without changing behaviour — producing noise —
and will pass when the actual behaviour is broken but the log message happens
to still be emitted — producing false confidence.

### FBD-7: Never Accept Coverage Below 80%

**Forbidden:** Declaring test generation complete when `pytest --cov-fail-under=80`
fails, or adding `# pragma: no cover` to implementation code to artificially
inflate the coverage percentage.

**Failure mode prevented:** Coverage below 80% on new code means at least one
in five lines of new logic is untested. On a story with complex domain logic,
the untested 20% is statistically more likely to contain the edge cases that
fail in production. The 80% threshold is the minimum bar — not the target.

### FBD-8: Never Run Only the Happy Path

**Forbidden:** Generating only the `test_ac_{n}_happy_path` test and skipping
edge cases, failure modes, and negative tests.

**Failure mode prevented:** Production systems fail at their edges. A payment
service that handles `charge_card()` successfully but throws an unhandled
exception on `charge_card()` with an expired card will cause a production
incident. Edge cases and failure modes are where the interesting bugs live.
Happy-path-only test suites catch integration errors but not logic errors.

### FBD-9: Never Hardcode Credentials in Test Files

**Forbidden:** `API_KEY = "sk-prod-abcd1234"`, connection strings with real
passwords, or tenant IDs that correspond to real production tenants.

**Failure mode prevented:** Test files are committed to version control. A
hardcoded credential in a test file is a credential leak. It will be detected
by `detect-secrets` in CI and will require credential rotation — disrupting
production systems while the leak window is assessed.

### FBD-10: Never Import from Another Agent's Module in Tests

**Forbidden:** `from agents.coding_agent import CodingAgent` in a test file
for the agent registry.

**Failure mode prevented:** Importing another agent's module in tests creates a
coupling that mirrors the A1 architecture violation. It means the test suite
for service A depends on the implementation of service B — a change to service B
can break service A's tests with no code change to service A. This is the test
analogue of the forbidden agent-calls-agent pattern.

---

## Output Format Reference

The Phase 6 summary is the deliverable of this skill. It must always include:

1. **AC Coverage Matrix** — every AC criterion with its category, test file,
   test function, and COVERED/MISSING status. One row per criterion.

2. **Tests Generated Table** — total count per category with file paths.

3. **Coverage Report** — module-level coverage percentages from
   `pytest --cov-report=term-missing`. Include the total line.

4. **Vacuous Test Check** — confirmation that tests were verified to fail when
   the implementation was removed.

5. **Definition of Done — Testing Gate** — checklist with every item explicitly
   checked or flagged. A checked list with incomplete items is not acceptable —
   flag incomplete items as BLOCKED with a reason.

**The test summary is not optional.** It is the audit trail that connects
acceptance criteria to tests to coverage. Without it, the PI review cannot
verify that the story's testing gate is met.
