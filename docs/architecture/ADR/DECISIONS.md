# Agentic Engineering Platform — Architectural Decision Records

**Status:** Living document  
**Version:** 1.0  
**Last updated:** 27 June 2026  
**Format:** MADR (Markdown Architectural Decision Records)  
**Authority:** Decisions here are subordinate to [CONSTITUTION.md](../../../CONSTITUTION.md). The constitution can only be amended by Decision Record per constitutional governance rules.

---

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](#adr-001-event-mediated-agent-communication) | Event-mediated agent communication | Accepted | 2026-06-27 |
| [ADR-002](#adr-002-orchestrator-as-planner-not-executor) | Orchestrator as planner, not executor | Accepted | 2026-06-27 |
| [ADR-003](#adr-003-registry-based-agent-extensibility) | Registry-based agent extensibility | Accepted | 2026-06-27 |
| [ADR-004](#adr-004-non-bypassable-human-approval-gates) | Non-bypassable human approval gates | Accepted | 2026-06-27 |
| [ADR-005](#adr-005-immutable-append-only-audit-store) | Immutable append-only audit store | Accepted | 2026-06-27 |
| [ADR-006](#adr-006-vendor-neutral-tool-and-model-integration) | Vendor-neutral tool and model integration | Accepted | 2026-06-27 |
| [ADR-007](#adr-007-tool-contract-with-response-normalisation) | Tool Contract with response normalisation | Accepted | 2026-06-27 |
| [ADR-008](#adr-008-separation-of-working-context-and-long-term-memory) | Separation of working context and long-term memory | Accepted | 2026-06-27 |
| [ADR-009](#adr-009-three-layer-multi-tenancy) | Three-layer multi-tenancy | Accepted | 2026-06-27 |
| [ADR-010](#adr-010-three-tier-failure-recovery) | Three-tier failure recovery | Accepted | 2026-06-27 |
| [ADR-011](#adr-011-separation-of-rbac-policy-engine-and-secrets-vault) | Separation of RBAC, Policy Engine, and Secrets Vault | Accepted | 2026-06-27 |
| [ADR-012](#adr-012-cost-aware-model-routing) | Cost-aware model routing | Accepted | 2026-06-27 |
| [ADR-013](#adr-013-durable-task-state-with-write-before-act) | Durable task state with write-before-act | Accepted | 2026-06-27 |
| [ADR-014](#adr-014-single-event-backbone-for-observability) | Single event backbone for observability | Accepted | 2026-06-27 |
| [ADR-015](#adr-015-workflow-template-versioning) | Workflow template versioning | Accepted | 2026-06-27 |
| [ADR-016](#adr-016-automatic-rollback-for-defect-resolution) | Automatic rollback for defect resolution | Accepted | 2026-06-27 |
| [ADR-017](#adr-017-terraform-as-cross-cloud-constant) | Terraform as cross-cloud constant | Accepted | 2026-06-27 |
| [ADR-018](#adr-018-staged-platform-delivery-roadmap) | Staged platform delivery roadmap | Accepted | 2026-06-27 |
| [ADR-019](#adr-019-approval-denial-as-revision-not-termination) | Approval denial as revision, not termination | Accepted | 2026-06-27 |
| [ADR-020](#adr-020-agent-idempotency-strategy) | Agent idempotency strategy | Accepted | 2026-06-27 |
| [ADR-021](#adr-021-governance-gates-not-notifications) | Governance relationships as gates, not notifications | Accepted | 2026-06-27 |
| [ADR-022](#adr-022-time-boxed-vs-open-ended-gate-strategies) | Time-boxed vs open-ended gate strategies | Accepted | 2026-06-27 |
| [ADR-023](#adr-023-per-increment-rollback-for-brownfield) | Per-increment rollback for Brownfield | Accepted | 2026-06-27 |
| [ADR-024](#adr-024-nine-container-architecture) | Nine-container architecture | Accepted | 2026-06-27 |

---

## ADR Template (for future decisions)

```markdown
## ADR-{NNN}: {Title}

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-{MMM}
**Date:** YYYY-MM-DD
**Constitutional principles affected:** {list or "none"}
**Deciders:** {roles}

### Context
{What is the issue that we're seeing that is motivating this decision?}

### Decision
{What is the change that we're proposing and/or doing?}

### Alternatives Considered
| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| {alt 1} | | | |

### Consequences
**Positive:**
- {benefit}

**Negative:**
- {trade-off}

**Migration:**
- {what existing consumers must do}
```

---

## ADR-001: Event-mediated agent communication

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** A1, AG4, C2  
**Deciders:** Chief Architect, Platform Engineering  
**Reference:** RA Section 1 (Principle 1), Section 3.1, Section 5.4

### Context

Multi-agent platforms face O(n²) coupling when agents communicate directly. Adding agent N requires updating agents 1 through N-1 to know about it. At enterprise scale (50+ specialist agents, 1,000+ engineers), direct coupling makes the platform unmaintainable.

### Decision

All inter-agent communication MUST be publish/subscribe over the Event Bus. Agents publish what they did (facts). The Orchestrator's Workflow State Machine decides what happens next (commands). Agents never instruct other agents.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Direct agent-to-agent RPC | Lower latency, simpler debugging | O(n²) coupling, interface cascade | Does not scale beyond pilot |
| Shared message queue per agent pair | Ordered delivery | Still O(n²) queue management | Same coupling problem |
| Orchestrator mediates all calls (sync) | Central control | Orchestrator becomes bottleneck, blocks on agent latency | Violates container independence |

### Consequences

**Positive:**
- Adding agent N requires zero changes to agents 1 through N-1
- 5-agent pilot and 50-agent enterprise are architecturally identical
- Event Bus enables audit, observability, and replay for free

**Negative:**
- Eventual consistency between agent completion and next task dispatch
- Debugging requires correlating events across the bus

**Migration:** N/A — foundational decision.

---

## ADR-002: Orchestrator as planner, not executor

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** A2  
**Deciders:** Chief Architect  
**Reference:** RA Section 1 (Principle 2), Section 4

### Context

The orchestrator is the most frequently asked-about component. There is constant pressure to add "simple" specialist logic (code formatting, basic test running) to the orchestrator for convenience or latency.

### Decision

The Orchestrator decomposes work, selects agents, assembles context, enforces gates, dispatches tasks, and manages retry/compensation. It NEVER writes code, runs tests, scans dependencies, or makes specialist judgements.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Orchestrator with built-in specialists for "simple" tasks | Faster for trivial cases | Core changes with every domain change | Violates stability principle |
| Tiered orchestrator (planner + executor) | Clear separation | Executor tier duplicates agent runtime | Unnecessary complexity |

### Consequences

**Positive:**
- Orchestrator is stable across agent catalog changes
- Specialist evolution does not require core releases

**Negative:**
- Every capability requires a registered agent, even trivial ones

**Migration:** N/A — foundational decision.

---

## ADR-003: Registry-based agent extensibility

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** A3, PL1  
**Deciders:** Chief Architect, Platform Engineering  
**Reference:** RA Section 1 (Principle 3), Section 5.1, Section 6

### Context

The platform's scalability claim is that new capabilities are added without modifying the core. This requires a formal registration and discovery mechanism.

### Decision

Every specialist agent registers in the Agent Registry at startup with the standard Agent Contract. The Agent Selector queries by capability tag. Adding a new agent is a registry entry, never a code change to the Orchestrator.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Configuration-file agent mapping | Simple | No runtime validation, no health checks | Insufficient for enterprise |
| Orchestrator plugin system | Flexible | Orchestrator still modified per plugin | Violates "never patch in" |
| Service mesh discovery | Infrastructure-native | No contract validation | Missing capability matching |

### Consequences

**Positive:**
- Third-party agents can be added without platform team involvement
- Agent upgrades are registry operations, not deployments

**Negative:**
- Contract validation must be rigorous at registration time
- Malformed agents rejected before they can cause damage

**Migration:** N/A — foundational decision.

---

## ADR-004: Non-bypassable human approval gates

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** AI1, H1, H2, H3  
**Deciders:** Chief Architect, Security, Governance  
**Reference:** RA Section 1 (Principle 4), Section 5.6

### Context

"Fully autonomous" agentic systems are incompatible with enterprise safety, cost, and compliance requirements. Every workflow must have points where human judgement is structurally required.

### Decision

Human Approval Checkpoints are a first-class platform service. Every gate produces a named-approver record. Gates are non-bypassable by design — no flag, no timeout-auto-approve, no emergency override. Gates may be time-boxed (with escalation) or open-ended.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Optional gates (configurable bypass) | Faster for low-risk workflows | Bypass becomes the norm | Governance theatre |
| Auto-approve after timeout | Prevents stuck workflows | Removes human judgement | Violates constitution |
| Post-hoc audit only (no gates) | Maximum speed | No preventive control | Fails compliance |

### Consequences

**Positive:**
- Every production change has a named human approver
- Compliance requirements structurally enforced

**Negative:**
- Workflows are slower than fully autonomous alternatives
- Gate design requires domain expertise per workflow type

**Migration:** N/A — foundational decision.

---

## ADR-005: Immutable append-only audit store

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** A4, G1  
**Deciders:** Chief Architect, Security, Compliance  
**Reference:** RA Section 1 (Principle 5), Section 5.7

### Context

"Trust the AI" is not an enterprise strategy. Regulated industries require reconstructable decision chains. Incident retrospectives require complete timelines.

### Decision

An immutable, append-only Audit Store records every agent action and every human decision, correlated by task_id and workflow_run_id. No update or delete operations. All events from the Event Bus are consumed and stored.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Application logs only | Simple, existing tooling | Mutable, incomplete, not correlated | Fails audit requirements |
| Event sourcing with snapshots | Full replay | Complex; snapshots can diverge | Over-engineered for audit need |
| Blockchain-based audit | Tamper-evident | Operational complexity, performance | Unnecessary for threat model |

### Consequences

**Positive:**
- "Why did this happen?" is always a query, never a guess
- Same mechanism satisfies internal retros and external compliance

**Negative:**
- Storage grows monotonically (plan for retention/archival policy)
- Write throughput must scale with event volume

**Migration:** N/A — foundational decision.

---

## ADR-006: Vendor-neutral tool and model integration

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** P4, MI1, MI3  
**Deciders:** Chief Architect, CTO  
**Reference:** RA Section 1 (Principle 6), Section 5.2, Section 5.10, Section 12

### Context

Enterprises standardise on different toolchains (GitHub vs Azure DevOps vs GitLab) and different model providers. A platform tied to one vendor cannot be reused across clients or survive vendor changes.

### Decision

Tool Registry and Model Router provide vendor-neutral integration. Agents request capabilities, not vendor APIs. Model endpoints are configuration, not architecture. Infrastructure uses portable primitives (Kubernetes, Terraform) with cloud-specific configuration.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Standardise on one vendor per deployment | Simpler integration | Not reusable across clients | Violates vendor neutrality |
| Abstract everything including K8s | Full portability | Lowest-common-denominator infrastructure | Over-engineered |
| Build all integrations in-house | Full control | Massive maintenance burden | Not viable at scale |

### Consequences

**Positive:**
- Tenant toolchain changes are registry configuration changes
- Model provider changes are endpoint configuration changes
- Platform reusable across 100- and 10,000-engineer organisations

**Negative:**
- Response normalisation layer adds development overhead per tool
- Lowest-common-denominator tool capabilities

**Migration:** N/A — foundational decision.

---

## ADR-007: Tool Contract with response normalisation

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** PL2, AG3  
**Deciders:** Chief Architect, Platform Engineering  
**Reference:** RA Section 7

### Context

External systems (GitHub, Jira, Azure DevOps, Snyk) have radically different APIs. Agents cannot parse vendor-specific responses without re-coupling to vendors.

### Decision

Every external system is wrapped in a Tool Contract with a `response_normaliser` that maps vendor-specific responses to a common shape. Agents consume the common shape. Tool registration includes auth_strategy, scope ceiling, and rate_limit_policy.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Agents parse vendor responses directly | No normalisation layer | Agent re-coupled to vendor | Violates vendor neutrality |
| GraphQL federation layer | Unified query | Massive infrastructure; not all vendors support | Over-engineered |
| Lowest-common-denominator API | Simple | Loses vendor-specific capabilities | Too restrictive |

### Consequences

**Positive:**
- Tool swap is a registry change, not an agent rewrite
- Rate limiting and scope enforcement built into contract

**Negative:**
- Each tool integration requires normaliser development
- Common shape may lose vendor-specific metadata

**Migration:** N/A — foundational decision.

---

## ADR-008: Separation of working context and long-term memory

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** M1, M2, M3, AI3  
**Deciders:** Chief Architect, AI Engineering  
**Reference:** RA Section 5.3, Section 9

### Context

Conflating short-lived task context with durable organisational knowledge is the most common cause of inconsistent agent output across runs. Working context that should have been discarded leaks into institutional memory.

### Decision

Two distinct memory types: (1) Working context — short-lived, passed explicitly via Task Schema between agents. (2) Long-term memory — durable vector store with structured metadata, written deliberately with provenance, queried with filters (tenant_id, source_type, recency_weight).

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Single memory store | Simple | Context pollution | Proven failure mode |
| Automatic memory write on every agent output | Rich context | Unverified noise accumulates | Violates deliberate write principle |
| No long-term memory (stateless agents) | Simple | No organisational learning | Insufficient for enterprise |

### Consequences

**Positive:**
- Consistent agent output across runs
- Auditable knowledge provenance

**Negative:**
- Developers must explicitly manage context handoffs
- Long-term memory requires curation

**Migration:** N/A — foundational decision.

---

## ADR-009: Three-layer multi-tenancy

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** MT1, MT2, MT3, G4  
**Deciders:** Chief Architect, Platform Engineering  
**Reference:** RA Section 5.8

### Context

A single platform deployment must serve multiple business units or clients. Single-layer isolation (API-only) leaks data through memory retrieval, task queues, or resource consumption.

### Decision

Tenancy enforced at three layers: (1) Data — namespace isolation in Task Queue and Memory Store with tenant_id at storage layer. (2) Policy — per-tenant gate configuration, tool permissions, agent visibility. (3) Resource — per-tenant Model Router quota and tool rate limits.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Per-tenant deployment | Full isolation | Operational cost scales linearly | Violates MT3 |
| API-level isolation only | Simple | Data layer leakage | Insufficient |
| Database-per-tenant | Strong isolation | Connection management at scale | Operational complexity |

### Consequences

**Positive:**
- One deployment serves many tenants
- Isolation verified at every layer

**Negative:**
- Must be built before second team onboards (retrofit is materially harder)
- Namespace management complexity

**Migration:** Must be in place before Stage 2 onboarding.

---

## ADR-010: Three-tier failure recovery

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** FR1, FR2, FR3  
**Deciders:** Chief Architect, SRE  
**Reference:** RA Section 5.11

### Context

Enterprise workflows run for hours or days (Brownfield modernisation). Failures range from transient API errors to partial multi-step failures to unrecoverable errors. Binary retry-or-fail is insufficient.

### Decision

Three escalating recovery tiers: (1) Automatic retry with exponential backoff for transient failures. (2) Saga-style compensation for partial multi-step failures. (3) Human escalation when retries exhaust. The platform never silently gives up or silently retries forever.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Retry-only (no compensation) | Simple | Partial failures leave inconsistent state | Insufficient for multi-step |
| Fail-fast (no retry) | Predictable | Transient errors cause unnecessary failure | Wastes human escalation |
| Infinite retry | Eventually succeeds | Resources consumed indefinitely | Violates FR2 |

### Consequences

**Positive:**
- Transient failures recovered automatically
- Partial failures compensated without full rollback
- Human attention reserved for genuine escalation

**Negative:**
- Saga compensation logic is complex to implement per workflow
- Retry configuration requires tuning per agent/tool

**Migration:** N/A — foundational decision.

---

## ADR-011: Separation of RBAC, Policy Engine, and Secrets Vault

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** S1, G3  
**Deciders:** Chief Architect, Security  
**Reference:** RA Section 5.9

### Context

Security controls are frequently merged into a single "security module" for convenience. This creates unintended side effects when any control is modified.

### Decision

Three separate services: (1) RBAC — governs which humans can approve which gates. (2) Policy Engine — governs which actions agents may perform regardless of triggering user. (3) Secrets Vault — issues short-lived, scoped tokens per tool invocation. No agent or tool holds credentials directly.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Unified security service | Single deployment | Permission changes cascade | Violates S1 |
| RBAC-only (no agent policy) | Simple | Agents inherit user permissions | Privilege escalation vector |
| Credentials in K8s secrets | Standard pattern | Long-lived, not per-invocation | Violates S2 |

### Consequences

**Positive:**
- Each control independently auditable and modifiable
- Agent permissions independent of human permissions

**Negative:**
- Three services to deploy and maintain
- Developers must understand which control applies

**Migration:** N/A — foundational decision.

---

## ADR-012: Cost-aware model routing

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** CO1, CO2, MI1, MI2  
**Deciders:** Chief Architect, FinOps  
**Reference:** RA Section 5.10

### Context

Not every task requires the most capable (and expensive) model. At enterprise scale, uniform model assignment leads to unsustainable inference costs or under-powered critical tasks.

### Decision

Model Router classifies each dispatched task by complexity and risk. Agents declare a default cost_class (low/medium/high). Cost-Aware Dispatcher routes to configured tier endpoints. Per-tenant quota enforced. Model endpoints are configuration, not code.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Single model for all tasks | Simple | Unsustainable cost or insufficient quality | No cost lever |
| Agent selects own model | Flexible | No central governance or cost control | Violates MI1 |
| Manual model selection per task | Precise | Does not scale | Operational burden |

### Consequences

**Positive:**
- Inference cost manageable at scale
- Critical tasks get capable models; routine tasks get efficient models

**Negative:**
- Routing logic requires tuning
- Model capability ≠ platform capability (honest limit)

**Migration:** N/A — foundational decision.

---

## ADR-013: Durable task state with write-before-act

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** E3  
**Deciders:** Chief Architect, Platform Engineering  
**Reference:** RA Section 5.5, Section 8

### Context

Workflows may run for hours (Brownfield) or days (Legacy Migration). Platform restarts, container crashes, and deployments must not lose in-progress work.

### Decision

Task state is persisted in the Task Queue before any action is taken on it. Every workflow transition is written before it is acted upon. Platform restart resumes mid-workflow rather than losing state.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| In-memory state with checkpointing | Fast | Checkpoint gaps lose work | Unreliable |
| Event sourcing only (no task store) | Full replay | Complex replay logic | Over-engineered |
| External workflow engine (Temporal) | Battle-tested | Additional dependency | Acceptable as implementation choice within this decision |

### Consequences

**Positive:**
- Platform restarts are non-events for in-progress workflows
- Long-running workflows survive maintenance windows

**Negative:**
- Persistence layer must be highly available
- Write-before-act adds latency to transitions

**Migration:** N/A — foundational decision.

---

## ADR-014: Single event backbone for observability

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** O1, O2, O3  
**Deciders:** Chief Architect, Platform Engineering  
**Reference:** RA Section 5.12

### Context

Engineers, leadership, and governance need different views of platform activity. Building separate observability pipelines triples instrumentation burden and creates data inconsistencies.

### Decision

One event stream (the Event Bus consumed by Audit Store and Observability) serves three audiences: engineers (task-level tracing), leadership (DORA metrics from StateTransitioned events), governance (gate decision audit filter).

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Separate pipelines per audience | Optimised per view | Triple instrumentation, data divergence | Maintenance burden |
| APM tool only (Datadog, etc.) | Rich tooling | Not workflow-aware | Insufficient for governance |
| Custom metrics only | Lightweight | No event-level detail | Insufficient for audit |

### Consequences

**Positive:**
- Single instrumentation point
- All views consistent with audit trail

**Negative:**
- Event schema changes affect all three audiences
- Event volume drives storage costs

**Migration:** N/A — foundational decision.

---

## ADR-015: Workflow template versioning

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** BC3, V3  
**Deciders:** Chief Architect  
**Reference:** RA Section 8, Section 11

### Context

Workflow templates evolve (new gates, new states, reordered steps). In-flight workflow runs must not change behaviour when a template is updated.

### Decision

Workflow templates are versioned independently. A workflow run loads the template version it started with. Template updates apply to new runs only. Template version is recorded in the task/workflow metadata.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Mutable templates (update in place) | Simple | In-flight runs break | Unacceptable |
| Template per workflow run (full copy) | Complete isolation | Storage overhead | Acceptable trade-off |
| No versioning (deploy template changes) | Simple | Coordinated deployment required | Operational risk |

### Consequences

**Positive:**
- Template evolution without disrupting in-flight work
- Rollback to prior template version for new runs

**Negative:**
- Multiple template versions in flight simultaneously
- Template management complexity

**Migration:** N/A — foundational decision.

---

## ADR-016: Automatic rollback for defect resolution

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** FR4, W2  
**Deciders:** Chief Architect, SRE  
**Reference:** RA Section 11.3

### Context

In P1 defect resolution, the cost of waiting for human rollback approval exceeds the cost of a false-positive rollback. This is the one workflow where automatic reversal outweighs human gate latency.

### Decision

Defect resolution workflow takes a rollback snapshot at deploy time. If monitored metrics do not recover within N minutes, `RollbackTriggered` fires automatically without human approval. This is the only workflow where automatic rollback is constitutional.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Human-gated rollback for all workflows | Consistent | Extends P1 outage | Unacceptable MTTR |
| Automatic rollback for all workflows | Fast | Inappropriate for Greenfield/Brownfield | Too aggressive |
| No automatic rollback | Safe | P1 MTTR bounded by human response | Violates SRE requirements |

### Consequences

**Positive:**
- P1 MTTR bounded by recovery time, not human response time
- On-call trusts the automatic trigger (when false-positive rate is low)

**Negative:**
- False-positive rollbacks possible (must be monitored)
- Exception to the "humans approve" principle (documented and scoped)

**Migration:** N/A — foundational decision.

---

## ADR-017: Terraform as cross-cloud constant

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** E4, P4  
**Deciders:** Chief Architect, Platform Engineering  
**Reference:** RA Section 12

### Context

The platform deploys on Azure or AWS with configuration changes, not architecture changes. Infrastructure-as-code must be portable across clouds.

### Decision

Terraform is the deliberate constant across cloud deployments. Cloud-specific resources use provider-specific modules (azurerm, aws) behind a common interface. Kubernetes is the container runtime on both clouds.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Cloud-native IaC only (ARM, CloudFormation) | Native integration | Not portable | Violates portability |
| Pulumi | Modern, typed | Less mature ecosystem | Acceptable alternative but Terraform chosen |
| Manual infrastructure | Full control | Not reproducible | Unacceptable |

### Consequences

**Positive:**
- Same IaC patterns on Azure and AWS
- Reproducible environments

**Negative:**
- Lowest-common-denominator cloud features
- Provider-specific workarounds occasionally needed

**Migration:** N/A — foundational decision.

---

## ADR-018: Staged platform delivery roadmap

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** P5, G2, G4, SC3  
**Deciders:** Chief Architect, CTO  
**Reference:** RA Section 14

### Context

Building agents before the platform spine, governance before data, or multi-tenancy after shared state are all known failure modes that require expensive retrofits.

### Decision

Six stages in strict order: (0) Platform spine → (1) First vertical slice → (2) Multi-tenancy → (3) Full agent catalog → (4) Governance at scale → (5) Org-wide rollout. Each stage proves the prior before the next begins.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Big-bang delivery | Faster time to "complete" | Unvalidated architecture at scale | High risk |
| Agent-first (build agents, add spine later) | Demo speed | Agents rewritten when spine added | Wasted work |
| Governance-first | Compliance ready | No data to govern | Governance theatre |

### Consequences

**Positive:**
- Each stage de-risks the next
- Pilot proves spine before org-wide commitment

**Negative:**
- Governance and full catalog delayed until Stages 3–4
- Requires discipline to not skip stages

**Migration:** N/A — foundational decision.

---

## ADR-019: Approval denial as revision, not termination

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** W5  
**Deciders:** Chief Architect  
**Reference:** RA Section 10.1

### Context

If rejection kills the workflow, approvers hesitate to deny (high cost), and quality suffers. Workflows need feedback loops.

### Decision

`ApprovalDenied` routes back into the workflow as a revision task with the denial reason in context. The workflow run continues. Rejection is not a terminal state.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Rejection terminates workflow | Simple | All prior work lost | Expensive rejection |
| Rejection creates new workflow | Preserves history | Loses correlation | Fragmented audit |
| Unlimited revision loops | Flexible | Potential infinite loops | Requires max-revision policy |

### Consequences

**Positive:**
- Approvers can deny without destroying work
- Feedback loops improve agent output quality

**Negative:**
- Revision loops must be bounded (max revisions policy needed)
- Context grows with each revision

**Migration:** N/A — foundational decision.

---

## ADR-020: Agent idempotency strategy

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** E2  
**Deciders:** Chief Architect, Platform Engineering  
**Reference:** RA Section 6

### Context

Tasks are retried on failure. Platform restarts resume in-progress tasks. Agents that create side effects (PRs, tickets, deployments) must not duplicate on retry.

### Decision

Every agent declares an `idempotency_key_strategy` in the Agent Contract. The strategy defines how a retried invocation detects and avoids duplicating prior side effects. Idempotency is validated at registration and tested in CI.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Platform-level deduplication | Central enforcement | Cannot know agent-specific side effects | Insufficient |
| No retry for side-effecting agents | Safe | Reduces resilience | Violates FR1 |
| Exactly-once delivery (bus level) | Strong guarantee | Not supported by all event buses | Implementation-dependent |

### Consequences

**Positive:**
- Retry is safe for all agents
- Platform resilience without side-effect corruption

**Negative:**
- Each agent must implement idempotency logic
- Strategy varies per agent type

**Migration:** N/A — foundational decision.

---

## ADR-021: Governance relationships as gates, not notifications

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** C4  
**Deciders:** Chief Architect, Governance  
**Reference:** RA Section 2

### Context

In regulated industries (healthcare, finance), governance roles (Clinical Safety Officer, CAB Chair) must approve releases. Notification-only approval workflows do not satisfy compliance.

### Decision

Arrows from the platform to governance roles are gates, not notifications. The workflow state machine blocks until a recorded `ApprovalGranted` or `ApprovalDenied` event exists from a named approver.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Email notification + timer | Simple | Workflow proceeds without response | Governance theatre |
| Opt-in approval (approve to proceed, silence = proceed) | Low friction | No structural enforcement | Fails compliance |
| External approval system | Existing tooling | Audit fragmentation | Breaks reconstructability |

### Consequences

**Positive:**
- Compliance structurally enforced
- Release cannot proceed without governance sign-off

**Negative:**
- Governance bottlenecks possible (mitigated by delegation and time-boxing)
- Governance roles must be available or escalation configured

**Migration:** N/A — foundational decision.

---

## ADR-022: Time-boxed vs open-ended gate strategies

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** H4, W2  
**Deciders:** Chief Architect, SRE  
**Reference:** RA Section 11.1, 11.2, 11.3

### Context

Greenfield architecture review benefits from deliberation (open-ended). P1 defect diagnosis cannot wait indefinitely (time-boxed). Uniform gate policy fails both scenarios.

### Decision

Gate strategy is a property of the workflow template, not the platform. Greenfield/Brownfield gates are open-ended. Defect resolution gates are time-boxed with escalation to senior on-call on non-response. Time-boxing escalates — it does not bypass.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| All open-ended | Consistent | P1 blocked by unavailable approver | Unacceptable MTTR |
| All time-boxed with auto-approve | Fast | Architecture decisions rushed | Quality risk |
| All time-boxed with auto-deny | Safe | Workflows stuck on timeout | Too restrictive |

### Consequences

**Positive:**
- Each workflow's gate strategy matches its risk profile
- P1 compatible with human-in-the-loop principle

**Negative:**
- Workflow designers must choose correctly
- Escalation paths must be configured per gate

**Migration:** N/A — foundational decision.

---

## ADR-023: Per-increment rollback for Brownfield

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** W4, FR3  
**Deciders:** Chief Architect  
**Reference:** RA Section 11.2

### Context

Brownfield modernisation spans many increments. A failure in increment 3 must not destroy progress on increments 1, 2, and 4–7.

### Decision

Brownfield rollback is per-increment, not per-project. Each refactor step is a separate, independently revertible commit verified against the characterization baseline captured before any change. Failed increment reverts without touching others.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Full-project rollback | Simple | All progress lost on any failure | Unacceptable for multi-increment |
| No rollback (fix forward) | Progress preserved | Legacy system broken on failure | Too risky |
| Feature flags per increment | Runtime toggle | Code complexity in legacy system | Not always feasible |

### Consequences

**Positive:**
- Incremental modernisation de-risked
- Characterization baseline provides safety net

**Negative:**
- Characterization test suite must be maintained
- Per-increment commits require discipline

**Migration:** N/A — foundational decision.

---

## ADR-024: Nine-container architecture

**Status:** Accepted  
**Date:** 2026-06-27  
**Constitutional principles affected:** P2, P3  
**Deciders:** Chief Architect  
**Reference:** RA Section 3

### Context

The platform must scale components independently, replace components without rewriting others, and deploy components independently. Monolithic architectures fail these requirements.

### Decision

Nine independently deployable containers: Orchestrator, Agent Runtime, Event Bus, Task Queue & Workflow Engine, Agent Registry, Tool Registry, Memory Store, Audit Store, Platform Services (Approval Checkpoint, Model Router, Policy Engine, Secrets Vault, Observability). Event Bus is the sole inter-container communication path.

### Alternatives Considered

| Alternative | Pros | Cons | Why rejected |
|------------|------|------|-------------|
| Monolith (1-2 containers) | Simple deployment | Cannot scale/replace independently | Violates P2 |
| Microservices (20+ containers) | Fine-grained scaling | Operational complexity | Over-decomposed |
| Serverless-only | No infrastructure management | Cold start, state management | Insufficient for durable workflows |

### Consequences

**Positive:**
- Independent scaling, deployment, and replacement per container
- Clear ownership boundaries

**Negative:**
- Nine containers to deploy, monitor, and upgrade
- Event Bus is a single point of failure (must be HA)

**Migration:** N/A — foundational decision.

---

## ADR-025: Provider Model as First-Class Ontology

**Status:** Accepted  
**Date:** 1 July 2026  
**Deciders:** Chief Enterprise Platform Architect  
**Constitutional alignment:** A1, A3, AG4, AP5

### Context

Architecture Baseline v2 unifies AI agents, connectors, humans, APIs, and automation under a single **Provider** primitive with `provider_kind` discriminator. v1 docs and contracts used parallel Agent and Tool abstractions.

### Decision

- **Provider** is the meta-model primitive for all execution backends.
- **Agent** remains product language for `provider_kind: ai-agent`.
- **Tool Registry** is the typed index for `connector` / `rest-api` Providers.
- Discovery is always by **capability tag**, never provider name.
- Unified `provider-contract.schema.json` will supersede separate agent/tool contracts in PI-09 (non-breaking transition).

### Consequences

**Positive:** One ontology for thousands of tenant integrations; partner Marketplace artefacts align to Provider Plugins.

**Negative:** Lexical migration across docs, PI stories, and skills until PI-09 schema lands.

**Supersedes:** Informal "Agent-as-primitive" in platform architecture docs (not ADR-003 container topology).

---

## ADR-026: Metadata Engine Owns Publish and Resolve

**Status:** Accepted  
**Date:** 1 July 2026  
**Deciders:** Chief Enterprise Platform Architect  
**Constitutional alignment:** MT3, P4

### Context

Customer behaviour must be expressed as metadata without platform source forks. v1 distributed configuration across services ad hoc.

### Decision

- **Metadata Engine** is the authoritative service for Platform Object publish, validate, resolve, registry index, and `effective_configuration` materialisation.
- Phase 1: `config-service` (PI-08) for configuration hierarchy.
- Phase 2: full Metadata Engine MVP (PI-09) with Marketplace install pipeline integration.
- Workflow JSON files in `workflows/` remain valid during dual-read transition (gap G-09).

### Consequences

**Positive:** Salesforce-class metadata lifecycle; Builders output validated objects only.

**Negative:** New container/service; PI-01 spine unchanged until PI-08/09.

---

## ADR-027: Execution Profiles Supersede Ad Hoc Model Routing Authoring

**Status:** Accepted  
**Date:** 1 July 2026  
**Deciders:** Chief Enterprise Platform Architect  
**Constitutional alignment:** MI3 (no model names in Agent Contract)

### Context

ADR-012 established Model Router for tier selection. Baseline v2 requires governed, versioned **Execution Profiles** for preferred/fallback/consensus models, prompts, budget, and retry.

### Decision

- **Execution Profiles** are Platform Objects authored via Execution Profile Designer (PI-09).
- **model-router** service becomes the **runtime resolver** of Active Profiles — not the authoring store.
- `cost_class` on agents remains a compatibility hint until Profile schema is enforced.
- Model names stay out of Agent/Provider contracts; profiles reference Model Registry tiers.

### Consequences

**Positive:** Governed AI cost/quality per workflow node; audit trail for profile changes.

**Negative:** Profile storage and Metadata Engine dependency; PI-06 routing logic evolves.

**Related:** ADR-012 (runtime routing — retained); [REFERENCE_ARCHITECTURE.md](docs/architecture/REFERENCE_ARCHITECTURE.md) §24.1.

---

## ADR-028: Platform Object Framework in `aep_meta` Library

**Status:** Accepted  
**Date:** 1 July 2026  
**Deciders:** Principal Platform Engineer, Chief Enterprise Platform Architect  
**Constitutional alignment:** AR6 (contracts before implementations), M2 (no shared mutable agent context)

### Context

Architecture Baseline v2.0 requires every definable entity to inherit the **Platform Object** envelope. US-02.01 implements the Metadata Engine foundation before publish/registry stories.

### Decision

- Implement the **Platform Object framework** as shared library `src/shared/aep_meta` (domain + application + infrastructure ports).
- Authoritative contract: `contracts/platform-object.schema.json` v1.0.0.
- **metadata-engine** service exposes REST API; persistence tables in `metadata` schema (migration 006).
- Lifecycle state machine is universal — no primitive-specific transitions in US-02.01.

### Consequences

**Positive:** All primitives share one validation and lifecycle path; Provider Contract (G-02) can extend envelope.

**Negative:** PI-02 docs partially stale (Agent Runtime naming); broader rename tracked separately.

**Related:** [PLATFORM_PRIMITIVES.md](../PLATFORM_PRIMITIVES.md) §3; US-02.01 implementation plan.

---

## Reserved ADR Numbers

| Range | Reserved for |
|-------|-------------|
| ADR-025–049 | Platform implementation decisions |
| ADR-050–074 | Agent implementation decisions |
| ADR-075–099 | Tool integration decisions |
| ADR-100–124 | Workflow template decisions |
| ADR-125–149 | Security and compliance decisions |
| ADR-150+ | Constitutional amendments (require explicit constitutional reference) |

---

## Document Relationships

| Document | Relationship |
|----------|---------------|
| [CONSTITUTION.md](../../../CONSTITUTION.md) | Supreme authority; ADRs cannot weaken constitutional principles |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Technical realisation of accepted ADRs |
| [CLAUDE.md](./CLAUDE.md) | Implementation rules derived from ADRs |
| [ROADMAP.md](docs/product/ROADMAP.md) | Delivery order influenced by ADR dependencies |

---

*This is a living document. New decisions: copy the template, assign the next number, submit via `adr/*` branch. Accepted ADRs are immutable — supersede, do not edit.*
