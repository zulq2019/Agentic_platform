# Agentic Engineering Platform — Engineering Tasks

**Status:** Living document  
**Version:** 1.0  
**Last updated:** 27 June 2026  
**Derived from:** [ROADMAP.md](./ROADMAP.md) · [ARCHITECTURE.md](./ARCHITECTURE.md) · Reference Architecture v1.0

---

## How to Read This Document

Work is organised as **Epic → Feature → Story → Task**. Each story includes acceptance criteria, priority, dependencies, estimate, owner, and definition of done.

**Priority:** P0 (blocker) · P1 (critical) · P2 (important) · P3 (nice-to-have)  
**Estimate:** Person-days (pd) unless noted  
**Owner:** Role, not individual — assign names per team

---

## Epic E1: Platform Spine (MVP — Stage 0)

**Goal:** Deliver the five containers every other component depends on.  
**Phase:** MVP · **Milestone:** M1–M2 · **Total estimate:** ~60 pd

---

### Feature F1.1: Event Bus

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S1.1.1 | Event Bus infrastructure provisioning | P0 | 3 pd | Platform Engineer |
| S1.1.2 | Event envelope schema implementation | P0 | 2 pd | Platform Engineer |
| S1.1.3 | Publish/subscribe client library | P0 | 3 pd | Platform Engineer |
| S1.1.4 | Event Bus integration tests | P1 | 2 pd | Platform Engineer |

#### S1.1.1 — Event Bus infrastructure provisioning

| Task | Description | Estimate |
|------|-------------|----------|
| T1.1.1.1 | Terraform module for Event Bus (Azure Service Bus / AWS EventBridge) | 1 pd |
| T1.1.1.2 | Topic and subscription provisioning per event type | 1 pd |
| T1.1.1.3 | Dead-letter queue configuration | 0.5 pd |
| T1.1.1.4 | Smoke test: publish and consume test event | 0.5 pd |

**Acceptance Criteria:**
- [ ] Event Bus deploys via Terraform on Azure and AWS
- [ ] Topics exist for all core event types (Section 10.1)
- [ ] Dead-letter queue captures failed deliveries
- [ ] Publish/consume latency < 100ms p99

**Dependencies:** None  
**Definition of Done:** Deployed to dev environment. Integration test passes. Documented in ARCHITECTURE.md.

#### S1.1.2 — Event envelope schema implementation

| Task | Description | Estimate |
|------|-------------|----------|
| T1.1.2.1 | Define event envelope JSON schema (event_id, event_type, timestamp, task_id, workflow_run_id, emitted_by, payload) | 0.5 pd |
| T1.1.2.2 | Schema validation library | 1 pd |
| T1.1.2.3 | Envelope serialization/deserialization | 0.5 pd |

**Acceptance Criteria:**
- [ ] All seven envelope fields validated on publish
- [ ] Invalid envelopes rejected with clear error
- [ ] Schema versioned and documented

**Dependencies:** None  
**Definition of Done:** Schema published. Validator library in shared package. Unit tests pass.

---

### Feature F1.2: Task Queue & Workflow Engine

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S1.2.1 | Durable task persistence | P0 | 5 pd | Platform Engineer |
| S1.2.2 | Task Schema implementation | P0 | 3 pd | Platform Engineer |
| S1.2.3 | Workflow state persistence | P0 | 3 pd | Platform Engineer |
| S1.2.4 | Task Queue integration tests | P1 | 2 pd | Platform Engineer |

#### S1.2.1 — Durable task persistence

| Task | Description | Estimate |
|------|-------------|----------|
| T1.2.1.1 | Task store schema (task_id, workflow_run_id, workflow_type, context, assigned_agent_id, state, retry_count, approval_record) | 1 pd |
| T1.2.1.2 | CRUD operations with optimistic locking | 2 pd |
| T1.2.1.3 | Platform restart recovery test | 1 pd |
| T1.2.1.4 | Task state transition audit logging | 1 pd |

**Acceptance Criteria:**
- [ ] Task state persisted before action taken
- [ ] Platform restart resumes in-progress tasks
- [ ] No task state lost during container restart
- [ ] Concurrent task updates handled safely

**Dependencies:** S1.1.2 (event envelope)  
**Definition of Done:** Persistence layer deployed. Recovery test passes. Task Schema documented.

---

### Feature F1.3: Agent Registry

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S1.3.1 | Agent registration API | P0 | 3 pd | Platform Engineer |
| S1.3.2 | Capability-based query | P0 | 2 pd | Platform Engineer |
| S1.3.3 | Contract validation at registration | P0 | 3 pd | Platform Engineer |
| S1.3.4 | Agent Registry integration tests | P1 | 2 pd | Platform Engineer |

#### S1.3.1 — Agent registration API

| Task | Description | Estimate |
|------|-------------|----------|
| T1.3.1.1 | Registration endpoint (agent_id, capabilities, input_schema, output_schema, required_tools, cost_class, approval_required, idempotency_key_strategy, contract_version) | 1 pd |
| T1.3.1.2 | Deregistration endpoint | 0.5 pd |
| T1.3.1.3 | Health check / heartbeat | 0.5 pd |
| T1.3.1.4 | Registration persistence | 1 pd |

**Acceptance Criteria:**
- [ ] Agent registers with full Agent Contract fields
- [ ] Duplicate agent_id rejected
- [ ] Deregistration removes agent from capability index
- [ ] Registration does not require orchestrator code change

**Dependencies:** None  
**Definition of Done:** API deployed. First test agent registered. Contract validation enforced.

---

### Feature F1.4: Tool Registry

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S1.4.1 | Tool registration API | P0 | 3 pd | Platform Engineer |
| S1.4.2 | Capability-based tool resolution | P0 | 2 pd | Platform Engineer |
| S1.4.3 | First tool integration (source control) | P0 | 5 pd | Platform Engineer |
| S1.4.4 | Response normaliser implementation | P1 | 3 pd | Platform Engineer |

#### S1.4.3 — First tool integration (source control)

| Task | Description | Estimate |
|------|-------------|----------|
| T1.4.3.1 | Tool Contract implementation for source control | 1 pd |
| T1.4.3.2 | `create-pull-request` capability | 2 pd |
| T1.4.3.3 | `read-repository` capability | 1 pd |
| T1.4.3.4 | Response normaliser (vendor → common shape) | 1 pd |

**Acceptance Criteria:**
- [ ] Tool registers with full Tool Contract fields
- [ ] Agent requests tool by capability tag, not tool name
- [ ] Response normalised to common shape
- [ ] Scoped access (not org-wide credentials)

**Dependencies:** S1.4.1  
**Definition of Done:** Source control tool registered. Agent can create PR via capability tag.

---

### Feature F1.5: Audit Store

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|-------|
| S1.5.1 | Immutable append-only store | P0 | 3 pd | Platform Engineer |
| S1.5.2 | Event consumer (all events → audit) | P0 | 2 pd | Platform Engineer |
| S1.5.3 | Audit query API | P0 | 3 pd | Platform Engineer |
| S1.5.4 | Audit Store integration tests | P1 | 2 pd | Platform Engineer |

#### S1.5.1 — Immutable append-only store

| Task | Description | Estimate |
|------|-------------|----------|
| T1.5.1.1 | Append-only storage backend | 1 pd |
| T1.5.1.2 | Write-once enforcement (no update/delete API) | 1 pd |
| T1.5.1.3 | Correlation index (task_id, workflow_run_id) | 1 pd |

**Acceptance Criteria:**
- [ ] All events from Event Bus consumed and stored
- [ ] No update or delete operations exposed
- [ ] Query by task_id returns complete event chain
- [ ] Query by workflow_run_id returns complete workflow audit

**Dependencies:** S1.1.1 (Event Bus)  
**Definition of Done:** Audit store deployed. Full event chain queryable. Immutability verified.

---

## Epic E2: Orchestrator (MVP — Stage 1)

**Goal:** Workflow planning, agent selection, context assembly, gate enforcement.  
**Phase:** MVP · **Milestone:** M3 · **Total estimate:** ~50 pd

---

### Feature F2.1: Workflow State Machine

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S2.1.1 | State machine engine | P0 | 5 pd | Platform Engineer |
| S2.1.2 | Greenfield workflow template (subset) | P0 | 3 pd | Solution Architect |
| S2.1.3 | State transition persistence | P0 | 2 pd | Platform Engineer |
| S2.1.4 | StateTransitioned event publishing | P0 | 1 pd | Platform Engineer |

#### S2.1.2 — Greenfield workflow template (subset)

| Task | Description | Estimate |
|------|-------------|----------|
| T2.1.2.1 | Define states: Scoped → Architected → Implemented → Tested | 1 pd |
| T2.1.2.2 | Define transitions and required agent capabilities per state | 1 pd |
| T2.1.2.3 | Define gate placement (scope, architecture) | 0.5 pd |
| T2.1.2.4 | Template versioning support | 0.5 pd |

**Acceptance Criteria:**
- [ ] Greenfield workflow loads from template
- [ ] State transitions persisted before action
- [ ] StateTransitioned events published on every transition
- [ ] Template versioned; in-flight runs unaffected by template update

**Dependencies:** E1 (Platform Spine)  
**Definition of Done:** Greenfield workflow executes end-to-end in dev. All transitions audited.

---

### Feature F2.2: Agent Selector

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S2.2.1 | Capability-based agent resolution | P0 | 2 pd | Platform Engineer |
| S2.2.2 | Contract version compatibility check | P1 | 1 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Agent resolved by capability tag, not name
- [ ] Multiple agents with same capability: select by policy/preference
- [ ] Incompatible contract_version rejected at dispatch

**Dependencies:** F1.3 (Agent Registry)  
**Definition of Done:** Agent Selector resolves agents for all Greenfield states.

---

### Feature F2.3: Context Assembler

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S2.3.1 | Working context packet builder | P0 | 3 pd | Platform Engineer |
| S2.3.2 | Prior agent output aggregation | P0 | 2 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Context packet built from prior agent outputs for current workflow run
- [ ] Context passed via Task Schema `context` field
- [ ] No silent shared state between concurrent workflow runs

**Dependencies:** F1.2 (Task Queue)  
**Definition of Done:** Each task receives explicit context packet. No ambient state.

---

### Feature F2.4: Gate Enforcer

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S2.4.1 | Gate check before state transition | P0 | 3 pd | Platform Engineer |
| S2.4.2 | ApprovalRequested event publishing | P0 | 1 pd | Platform Engineer |
| S2.4.3 | ApprovalDenied → revision task routing | P1 | 2 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] State transition blocked until approval_record populated
- [ ] No bypass mechanism exists (no flag, no override, no timeout-auto-approve)
- [ ] ApprovalDenied creates revision task, not workflow failure

**Dependencies:** F2.5 (Approval Checkpoint)  
**Definition of Done:** Gate blocks transition. Approval recorded. Denial loops back.

---

### Feature F2.5: Human Approval Checkpoint Service

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S2.5.1 | Approval record API | P0 | 3 pd | Platform Engineer |
| S2.5.2 | Named approver enforcement | P0 | 1 pd | Platform Engineer |
| S2.5.3 | Approval UI (minimal) | P1 | 5 pd | Frontend Engineer |

**Acceptance Criteria:**
- [ ] Approval record contains: who, when, what they saw, what they decided
- [ ] Anonymous/system approvals rejected
- [ ] ApprovalGranted and ApprovalDenied events published

**Dependencies:** E1 (Event Bus, Audit Store)  
**Definition of Done:** Human can approve/deny via UI. Record stored. Events published.

---

## Epic E3: Specialist Agents — MVP Set (Stage 1)

**Goal:** Requirement, Coding, and Test agents for Greenfield pilot.  
**Phase:** MVP · **Milestone:** M3–M4 · **Total estimate:** ~40 pd

---

### Feature F3.1: Requirement Agent

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S3.1.1 | Agent Contract implementation | P0 | 1 pd | Agent Engineer |
| S3.1.2 | Story and acceptance criteria generation | P0 | 5 pd | Agent Engineer |
| S3.1.3 | Agent registration and integration test | P0 | 2 pd | Agent Engineer |

**Acceptance Criteria:**
- [ ] Agent registers with capabilities: `generates-requirements`, `generates-acceptance-criteria`
- [ ] Input: workflow initiation context. Output: stories + acceptance criteria per output_schema
- [ ] Idempotent on retry
- [ ] AgentStarted/AgentCompleted events published

**Dependencies:** E1, E2  
**Definition of Done:** Agent completes Requirement step in Greenfield workflow. Output in audit trail.

---

### Feature F3.2: Coding Agent

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S3.2.1 | Agent Contract implementation | P0 | 1 pd | Agent Engineer |
| S3.2.2 | Code generation from ADRs/API contracts | P0 | 8 pd | Agent Engineer |
| S3.2.3 | PR creation via Tool Registry | P0 | 3 pd | Agent Engineer |
| S3.2.4 | Idempotency (no duplicate PRs on retry) | P0 | 2 pd | Agent Engineer |

**Acceptance Criteria:**
- [ ] Agent registers with capabilities: `generates-code`, `creates-pull-request`
- [ ] Uses `create-pull-request` tool via capability tag
- [ ] Retry does not create duplicate PR
- [ ] Output: diff + PR URL per output_schema

**Dependencies:** F1.4 (Tool Registry), F3.1  
**Definition of Done:** Agent creates PR in source control. Retry safe. Audit trail complete.

---

### Feature F3.3: Test Agent

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S3.3.1 | Agent Contract implementation | P0 | 1 pd | Agent Engineer |
| S3.3.2 | Unit test generation | P0 | 5 pd | Agent Engineer |
| S3.3.3 | Test execution and coverage report | P0 | 3 pd | Agent Engineer |

**Acceptance Criteria:**
- [ ] Agent registers with capabilities: `generates-unit-tests`, `runs-tests`
- [ ] Output: coverage report per output_schema
- [ ] Uses CI/CD tool via Tool Registry

**Dependencies:** F3.2  
**Definition of Done:** Agent generates and runs tests. Coverage report in audit trail.

---

## Epic E4: Multi-Tenancy (Alpha — Stage 2)

**Goal:** Namespace isolation, per-tenant policy, per-tenant quota.  
**Phase:** Alpha · **Milestone:** M5 · **Total estimate:** ~35 pd

---

### Feature F4.1: Namespace Isolation

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S4.1.1 | Task Queue namespace per tenant | P0 | 3 pd | Platform Engineer |
| S4.1.2 | Memory Store tenant_id enforcement | P0 | 3 pd | Platform Engineer |
| S4.1.3 | Cross-tenant leakage test suite | P0 | 3 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Tenant A tasks invisible to Tenant B queries
- [ ] Tenant A memory entries invisible to Tenant B retrieval
- [ ] Automated test suite proves zero cross-tenant leakage

**Dependencies:** E1, E2  
**Definition of Done:** Two tenants deployed. Leakage test suite passes 100%.

---

### Feature F4.2: Per-Tenant Policy Configuration

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S4.2.1 | Gate configuration per tenant | P0 | 3 pd | Platform Engineer |
| S4.2.2 | Tool permission configuration per tenant | P0 | 2 pd | Platform Engineer |
| S4.2.3 | Agent visibility configuration per tenant | P1 | 2 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Tenant A can require architecture gate; Tenant B can omit it
- [ ] Tenant A permitted tools differ from Tenant B
- [ ] Policy changes do not require code deployment

**Dependencies:** F4.1  
**Definition of Done:** Two tenants with different policies operational.

---

### Feature F4.3: Per-Tenant Model Quota

| Story | Description | Priority | Estimate | Owner |
|-------|-------------|----------|----------|-------|
| S4.3.1 | Quota configuration per tenant | P0 | 2 pd | Platform Engineer |
| S4.3.2 | Quota enforcement in Model Router | P0 | 3 pd | Platform Engineer |
| S4.3.3 | Quota exhaustion backpressure | P1 | 2 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Tenant exceeding quota receives backpressure, not dropped tasks
- [ ] Quota configurable per tenant without code change
- [ ] Quota usage tracked and queryable

**Dependencies:** F5.1 (Model Router)  
**Definition of Done:** Quota enforced. Usage report available per tenant.

---

## Epic E5: Security & Model Routing (Alpha)

**Goal:** RBAC, Policy Engine, Secrets Vault, Model Router.  
**Phase:** Alpha · **Total estimate:** ~40 pd

---

### Feature F5.1: Model Router & Cost-Aware Dispatcher

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S5.1.1 | Model tier configuration (low/medium/high endpoints) | 3 pd | Platform Engineer |
| S5.1.2 | Cost-Aware Dispatcher integration with Orchestrator | 3 pd | Platform Engineer |
| S5.1.3 | Per-task tier override support | 2 pd | Platform Engineer |
| S5.1.4 | Cost attribution per task/workflow | 3 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Tasks routed to configured tier based on cost_class + task metadata
- [ ] Model endpoints are configuration, not code
- [ ] Cost attributed to task_id and workflow_run_id

**Dependencies:** E2  
**Definition of Done:** Three model tiers operational. Cost report per workflow.

---

### Feature F5.2: Secrets Vault Integration

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S5.2.1 | Token issuance API (short-lived, scoped) | 3 pd | Platform Engineer |
| S5.2.2 | Tool Registry integration (token per invocation) | 2 pd | Platform Engineer |
| S5.2.3 | No credential in agent container verification | 1 pd | Security Engineer |

**Acceptance Criteria:**
- [ ] No agent or tool container contains long-lived credentials
- [ ] Token scoped to tool's registered scope ceiling
- [ ] Token expires after invocation

**Dependencies:** F1.4  
**Definition of Done:** Security scan confirms zero credentials in agent/tool images.

---

### Feature F5.3: RBAC & Policy Engine

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S5.3.1 | RBAC integration with Identity Provider | 3 pd | Platform Engineer |
| S5.3.2 | Policy Engine (agent action permissions) | 5 pd | Platform Engineer |
| S5.3.3 | Separation verification (RBAC ≠ Policy ≠ Secrets) | 1 pd | Security Engineer |

**Acceptance Criteria:**
- [ ] RBAC governs human gate approval authority
- [ ] Policy Engine governs agent actions independent of triggering user
- [ ] Three controls deployed as separate services

**Dependencies:** F2.5  
**Definition of Done:** RBAC and Policy Engine independently testable. Separation documented.

---

## Epic E6: Memory & Additional Workflows (Alpha)

**Goal:** Long-term memory, Brownfield and Defect Resolution workflows.  
**Phase:** Alpha · **Milestone:** M6–M7 · **Total estimate:** ~45 pd

---

### Feature F6.1: Long-Term Memory Store

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S6.1.1 | Vector store provisioning | 3 pd | Platform Engineer |
| S6.1.2 | Memory Schema implementation | 2 pd | Platform Engineer |
| S6.1.3 | Filtered retrieval (tenant_id, source_type, recency_weight) | 3 pd | Platform Engineer |
| S6.1.4 | Deliberate write API with provenance | 2 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Memory entries have all schema fields
- [ ] Retrieval filtered by metadata, not blind similarity
- [ ] Writes require explicit provenance
- [ ] tenant_id enforced at storage layer

**Dependencies:** F4.1  
**Definition of Done:** Memory store operational. Filtered query returns correct results. No cross-tenant retrieval.

---

### Feature F6.2: Brownfield Workflow Template

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S6.2.1 | State machine: Discovered → Dependency-Mapped → Scope-Confirmed → Characterized → Refactored → Regression-Verified → Staged | 3 pd | Solution Architect |
| S6.2.2 | Per-increment rollback support | 3 pd | Platform Engineer |
| S6.2.3 | Discovery and Dependency Analysis agents | 8 pd | Agent Engineer |
| S6.2.4 | Characterization test baseline capture | 3 pd | Agent Engineer |

**Acceptance Criteria:**
- [ ] Brownfield workflow completes end-to-end
- [ ] Failed increment reverts without affecting other increments
- [ ] Characterization baseline captured before any code change

**Dependencies:** E2, E3  
**Definition of Done:** Brownfield workflow demonstrated on legacy codebase.

---

### Feature F6.3: Defect Resolution Workflow Template

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S6.3.1 | State machine with time-boxed gates | 2 pd | Solution Architect |
| S6.3.2 | Automatic rollback on non-recovery | 3 pd | Platform Engineer |
| S6.3.3 | Triage and Root-Cause agents | 8 pd | Agent Engineer |

**Acceptance Criteria:**
- [ ] Time-boxed diagnosis gate with escalation
- [ ] Automatic RollbackTriggered when metrics don't recover within N minutes
- [ ] No human approval required for rollback

**Dependencies:** E2, F5.1  
**Definition of Done:** Defect resolution demonstrated with simulated P1. Auto-rollback verified.

---

## Epic E7: Failure Recovery (Alpha)

**Goal:** Three-tier recovery, saga compensation.  
**Phase:** Alpha · **Total estimate:** ~20 pd

---

### Feature F7.1: Retry & Compensation Manager

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S7.1.1 | Tier 1: Automatic retry with exponential backoff | 3 pd | Platform Engineer |
| S7.1.2 | Tier 2: Saga-style compensation | 5 pd | Platform Engineer |
| S7.1.3 | Tier 3: Human escalation on retry exhaustion | 2 pd | Platform Engineer |
| S7.1.4 | RollbackTriggered event and handling | 2 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Transient failure retried automatically
- [ ] Partial multi-step failure triggers compensation
- [ ] Exhausted retries escalate to human gate
- [ ] No silent failure or infinite retry

**Dependencies:** E2, E1  
**Definition of Done:** All three tiers demonstrated. No silent failures in test suite.

---

## Epic E8: Full Agent Catalog & Workflows (Beta — Stage 3)

**Goal:** All 8 workflow templates, 16+ agents.  
**Phase:** Beta · **Milestone:** M8 · **Total estimate:** ~80 pd

---

### Feature F8.1: Remaining Specialist Agents

| Agent | Capabilities | Estimate | Owner |
|-------|-------------|----------|-------|
| Architecture Agent | `designs-architecture`, `generates-adrs` | 8 pd | Agent Engineer |
| Security Agent | `scans-dependencies`, `scans-sast` | 8 pd | Agent Engineer |
| Review Agent | `reviews-code`, `checks-standards` | 5 pd | Agent Engineer |
| Release Agent | `prepares-release`, `generates-changelog` | 5 pd | Agent Engineer |
| Refactor Agent | `refactors-code`, `applies-patterns` | 8 pd | Agent Engineer |
| Regression Agent | `runs-regression`, `verifies-equivalence` | 5 pd | Agent Engineer |
| Migration Agent | `plans-migration`, `executes-migration` | 10 pd | Agent Engineer |
| Release-Readiness Agent | `assesses-readiness`, `checks-preconditions` | 5 pd | Agent Engineer |
| Documentation Agent | `generates-docs`, `updates-readme` | 5 pd | Agent Engineer |

**Acceptance Criteria (all agents):**
- [ ] Full Agent Contract implemented
- [ ] Registers without orchestrator code change
- [ ] Idempotent on retry
- [ ] Events published with correct envelope

---

### Feature F8.2: Remaining Workflow Templates

| Workflow | Estimate | Owner |
|----------|----------|-------|
| Feature Enhancement | 3 pd | Solution Architect |
| Security Remediation | 3 pd | Solution Architect |
| Technical Debt Reduction | 3 pd | Solution Architect |
| Legacy Migration | 5 pd | Solution Architect |
| Release Management | 3 pd | Solution Architect |

**Acceptance Criteria (all workflows):**
- [ ] State machine defined with gates and rollback strategy
- [ ] At least one end-to-end run completed
- [ ] Uses same platform primitives as Greenfield/Brownfield/Defect

---

## Epic E9: Governance & Observability (Beta — Stage 4)

**Goal:** Dashboards, DORA metrics, audit export, self-serve UI.  
**Phase:** Beta · **Milestone:** M9–M10 · **Total estimate:** ~40 pd

---

### Feature F9.1: Observability Dashboard

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S9.1.1 | Engineer view: task-level tracing | 5 pd | Platform Engineer |
| S9.1.2 | Leadership view: DORA metrics aggregation | 5 pd | Platform Engineer |
| S9.1.3 | Governance view: gate decision audit filter | 3 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] All three views consume same event stream
- [ ] Engineer can trace any task_id end-to-end
- [ ] DORA metrics calculated from StateTransitioned events
- [ ] Governance can filter and export gate decisions

**Dependencies:** E1 (Audit Store), E8  
**Definition of Done:** Dashboards populated with real workflow data from Beta tenants.

---

### Feature F9.2: Self-Serve Agent Invocation UI

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S9.2.1 | Workflow initiation UI | 5 pd | Frontend Engineer |
| S9.2.2 | Gate approval UI (enhanced) | 3 pd | Frontend Engineer |
| S9.2.3 | Workflow status tracking UI | 3 pd | Frontend Engineer |

**Acceptance Criteria:**
- [ ] Engineer can initiate any enabled workflow for their tenant
- [ ] Approver can review and approve/deny with context
- [ ] Workflow progress visible in real time

**Dependencies:** E2, F2.5  
**Definition of Done:** Self-serve UI used by 5+ teams.

---

## Epic E10: SDK & Developer Experience (Beta)

**Goal:** Agent SDK, Tool SDK, documentation.  
**Phase:** Beta · **Total estimate:** ~25 pd

---

### Feature F10.1: Agent SDK

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S10.1.1 | Contract validator | 2 pd | Platform Engineer |
| S10.1.2 | Registration client | 2 pd | Platform Engineer |
| S10.1.3 | Event publisher helper | 2 pd | Platform Engineer |
| S10.1.4 | Tool client (capability-based) | 2 pd | Platform Engineer |
| S10.1.5 | Idempotency helper | 1 pd | Platform Engineer |
| S10.1.6 | SDK documentation and examples | 3 pd | Technical Writer |

**Acceptance Criteria:**
- [ ] Third-party agent registers using SDK only
- [ ] No platform code changes required
- [ ] SDK enforces contract_version compatibility

**Dependencies:** E1, E3  
**Definition of Done:** External team registers agent using SDK in < 1 day.

---

### Feature F10.2: Tool SDK

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S10.2.1 | Contract validator | 2 pd | Platform Engineer |
| S10.2.2 | Registration client | 2 pd | Platform Engineer |
| S10.2.3 | Response normaliser scaffold | 2 pd | Platform Engineer |
| S10.2.4 | Auth adapter (Secrets Vault) | 2 pd | Platform Engineer |
| S10.2.5 | SDK documentation and examples | 3 pd | Technical Writer |

**Acceptance Criteria:**
- [ ] Third-party tool registers using SDK only
- [ ] Response normalisation enforced at registration
- [ ] Auth via Secrets Vault, not embedded credentials

**Dependencies:** F1.4, F5.2  
**Definition of Done:** External team registers tool using SDK in < 1 day.

---

## Epic E11: Enterprise Hardening (Enterprise — Stage 5)

**Goal:** HA, DR, policy-as-code, wave onboarding.  
**Phase:** Enterprise · **Milestone:** M11–M14 · **Total estimate:** ~50 pd

---

### Feature F11.1: High Availability & Disaster Recovery

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S11.1.1 | Multi-AZ deployment | 5 pd | Platform Engineer |
| S11.1.2 | Event Bus durability configuration | 2 pd | Platform Engineer |
| S11.1.3 | Workflow state recovery after region failure | 5 pd | Platform Engineer |
| S11.1.4 | DR runbook and test | 3 pd | SRE |

**Acceptance Criteria:**
- [ ] Single-AZ failure: zero workflow loss, automatic recovery
- [ ] Recovery time < 15 minutes
- [ ] DR test executed and documented quarterly

**Dependencies:** E1, E2  
**Definition of Done:** HA/DR test passed. Runbook published.

---

### Feature F11.2: Policy-as-Code Library

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S11.2.1 | Policy definition language | 5 pd | Platform Engineer |
| S11.2.2 | Pre-built policy templates (security, compliance) | 5 pd | Security Engineer |
| S11.2.3 | Per-tenant policy assignment | 2 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Policies govern agent actions without code deployment
- [ ] Pre-built templates for common compliance requirements
- [ ] Policy violations blocked and audited

**Dependencies:** F5.3  
**Definition of Done:** Policy library deployed. 3+ tenants using custom policies.

---

### Feature F11.3: Wave Onboarding Tooling

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S11.3.1 | Tenant provisioning automation | 3 pd | Platform Engineer |
| S11.3.2 | Onboarding checklist and validation | 2 pd | Platform Engineer |
| S11.3.3 | Team onboarding documentation | 3 pd | Technical Writer |

**Acceptance Criteria:**
- [ ] New tenant provisioned in < 1 day
- [ ] Onboarding checklist validates isolation, policy, quota
- [ ] Documentation enables self-service onboarding

**Dependencies:** E4  
**Definition of Done:** 3 teams onboarded in a single wave using tooling.

---

## Epic E12: GA & Ecosystem (GA)

**Goal:** Security audit, partner agents, performance benchmarks.  
**Phase:** GA · **Milestone:** M15–M17 · **Total estimate:** ~35 pd

---

### Feature F12.1: Security Audit & Compliance

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S12.1.1 | External penetration test | 10 pd | Security Engineer |
| S12.1.2 | Constitutional compliance audit | 5 pd | Solution Architect |
| S12.1.3 | Remediation of findings | 10 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Zero critical/high findings unresolved
- [ ] All constitutional principles verified in production
- [ ] Compliance export validated by governance persona

**Dependencies:** All prior epics  
**Definition of Done:** Security audit passed. Constitutional compliance certified.

---

### Feature F12.2: Partner Agent Certification

| Story | Description | Estimate | Owner |
|-------|-------------|----------|-------|
| S12.2.1 | Certification process and criteria | 3 pd | Platform Engineer |
| S12.2.2 | Partner agent review workflow | 3 pd | Platform Engineer |
| S12.2.3 | Certified agent catalog | 2 pd | Platform Engineer |

**Acceptance Criteria:**
- [ ] Partner agent certified through documented process
- [ ] Certified agents appear in registry with certification badge
- [ ] Non-certified agents cannot be enabled in production tenants

**Dependencies:** F10.1  
**Definition of Done:** At least one partner agent certified and operational.

---

## Summary

| Epic | Phase | Estimate | Milestone |
|------|-------|----------|-----------|
| E1: Platform Spine | MVP | 60 pd | M1–M2 |
| E2: Orchestrator | MVP | 50 pd | M3 |
| E3: MVP Agents | MVP | 40 pd | M3–M4 |
| E4: Multi-Tenancy | Alpha | 35 pd | M5 |
| E5: Security & Model Routing | Alpha | 40 pd | M5 |
| E6: Memory & Workflows | Alpha | 45 pd | M6–M7 |
| E7: Failure Recovery | Alpha | 20 pd | M7 |
| E8: Full Catalog | Beta | 80 pd | M8 |
| E9: Governance | Beta | 40 pd | M9–M10 |
| E10: SDK | Beta | 25 pd | M10 |
| E11: Enterprise | Enterprise | 50 pd | M11–M14 |
| E12: GA | GA | 35 pd | M15–M17 |
| **Total** | | **~520 pd** | |

---

## Global Definition of Done

A task is done when:

1. Code merged to main branch via PR with passing CI
2. Unit and integration tests pass
3. No constitutional violations (see CLAUDE.md review checklist)
4. Documented in relevant living document if architectural
5. Deployed to dev environment and smoke-tested
6. Acceptance criteria met and verified by story owner

---

*This is a living document. Add stories as scope is refined. Estimates are planning values — recalibrate per sprint.*
