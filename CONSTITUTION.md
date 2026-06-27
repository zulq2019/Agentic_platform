# Agentic Engineering Platform — Constitution

**Status:** Immutable  
**Version:** 1.0  
**Derived from:** Agentic Engineering Platform Reference Architecture v1.0  
**Effective:** 27 June 2026

---

## Preamble

This document is the **engineering constitution** of the Agentic Engineering Platform. It defines principles that **MUST NEVER** be violated.

This is not implementation guidance. This is not coding standards. This is not a roadmap. This is the permanent philosophy of the platform — the set of invariants that every design decision, every contribution, and every extension must satisfy.

Future contributors MUST treat this document exactly as Kubernetes contributors treat Kubernetes design principles: as the non-negotiable foundation beneath all other documentation.

**Amendment rule:** No principle in this constitution may be weakened, removed, or reinterpreted without a recorded Decision Record (see [Decision Record Policy](#decision-record-policy)) that explicitly states what is changing, why the change is necessary, and what migration path exists for existing workflows and integrations.

**Derivation rule:** Every principle in this document is derived from the Reference Architecture v1.0. Where a principle appears to add complexity, it traces back to a specific architectural concern defined there. This constitution does not rewrite the reference architecture — it extracts its immutable invariants.

**How to read this document:** Sections titled Mission, Vision, and Core Philosophy establish intent. All subsequent sections contain named principles. Each principle carries five mandatory fields: Why it exists, What problem it prevents, Example, Counter-example, and Consequences of violating it.

---

## Mission

To provide a vendor-neutral, reusable platform that orchestrates multi-agent software engineering — across Greenfield and Brownfield contexts — at enterprise scale, without becoming a new system of record, without coupling specialist agents to one another, and without sacrificing human accountability, auditability, or safety.

The platform exists to coordinate work across the systems, people, and governance structures an enterprise already has — not to replace them.

---

## Vision

A world where adding the fiftieth specialist agent to a thousand-engineer organisation is architecturally identical to running a five-agent pilot. Where every AI-proposed action is reconstructable from an immutable record. Where vendor changes — of tools, models, or cloud — require configuration changes, not platform rewrites. Where human judgement remains the final authority at every point where safety, cost, or compliance is at stake.

The platform MUST remain valid ten years from now regardless of which models, vendors, or cloud providers dominate at any given moment.

---

## Core Philosophy

The platform is a **planner and referee**, never a player. It decomposes work, routes it, enforces gates, and records outcomes. It does not write code, run scans, or make specialist judgements.

The platform introduces **no new system of record**. It orchestrates the ones that exist — source control, issue trackers, CI/CD, security scanners, infrastructure — through scoped, capability-based contracts.

Complexity in the platform is **deliberate and bounded**. Fifteen core concerns exist not as features bolted together but as thin, well-separated responsibilities. Scaling or replacing one MUST NEVER force a rewrite of another.

Communication is **event-mediated, never direct**. Specialist agents publish what they did; they never instruct another agent on what to do next. Sequencing lives solely in the orchestrator's workflow state machine.

Trust is **queryable, not assumed**. If an auditor, incident reviewer, or engineer asks "why did this happen," the answer MUST be retrievable from the audit store — not reconstructed from memory, logs, or guesswork.

---

## Platform Principles

### P1. The Platform Orchestrates; It Does Not Replace

**Why it exists:** Enterprises already have systems of record for code, tickets, infrastructure, and compliance. The platform's role is coordination, not duplication.

**What problem it prevents:** Shadow systems of record that diverge from authoritative sources, creating dual-maintenance burden and audit failures.

**Example:** A workflow creates a pull request in the tenant's configured source-control system. The platform records the action in its audit store but does not maintain a parallel copy of the repository.

**Counter-example:** The platform maintains its own issue tracker, code repository, and deployment pipeline independent of the tenant's existing toolchain.

**Consequences of violating it:** Data divergence between platform state and enterprise systems of record. Compliance audits fail because the platform cannot prove its records match authoritative sources. Engineers maintain two parallel workflows.

*Reference: RA Section 2 — System Context*

---

### P2. Thin, Bounded Responsibilities

**Why it exists:** Fifteen core platform concerns are deliberately kept separate so that scaling or replacing one never forces a rewrite of another.

**What problem it prevents:** Monolithic platform cores where a change to observability requires redeploying the workflow engine, or a security patch cascades into agent logic.

**Example:** The Model Router, Human Approval Checkpoint service, and Audit Store are independently deployable containers that communicate only through the Event Bus.

**Counter-example:** A single "platform-core" service that handles orchestration, memory, secrets, auditing, and model routing in one deployable unit.

**Consequences of violating it:** Every enhancement becomes a full-platform release. Blast radius of any change expands to the entire system. Independent scaling becomes impossible.

*Reference: RA Section 5 — Core Platform Concerns*

---

### P3. The Event Bus Is the Sole Inter-Container Communication Path

**Why it exists:** Nine containers are independently deployable and independently scalable. A single communication backbone makes the plug-in claim real rather than aspirational.

**What problem it prevents:** Point-to-point integrations between containers that create hidden coupling and deployment ordering dependencies.

**Example:** The Orchestrator publishes a `TaskCreated` event. The assigned agent subscribes, executes, and publishes `AgentCompleted`. No container calls another container's API directly.

**Counter-example:** The Orchestrator makes synchronous HTTP calls to the Agent Runtime, which calls the Memory Store, which calls the Audit Store — a synchronous chain that must all be healthy for any single task to proceed.

**Consequences of violating it:** Container independence is destroyed. A failure in one container blocks others. Scaling one container requires understanding and coordinating all its direct callers.

*Reference: RA Section 3 — Containers*

---

### P4. Vendor Neutrality by Construction

**Why it exists:** Tool Registry and Model Router exist specifically so today's toolchain does not mean a rebuild when the client's tools or models change tomorrow.

**What problem it prevents:** Platform lock-in to a specific vendor's APIs, models, or cloud primitives that forces wholesale rewrites on vendor change.

**Example:** A tenant using Jira instead of Azure DevOps changes a Tool Registry entry. Agent logic requesting `create-issue` is unchanged.

**Counter-example:** Agent code imports Azure DevOps SDK types directly and encodes Azure-specific field names in workflow templates.

**Consequences of violating it:** Every new client requires agent rewrites. Model swaps require orchestrator changes. The platform's reusability claim becomes false.

*Reference: RA Section 1, Principle 6; Section 5.2; Section 12*

---

### P5. The Platform Spine Must Exist Before Everything Else

**Why it exists:** Event Bus, Task Queue, Agent Registry, Tool Registry, and Audit Store are the contract every later piece depends on. Nothing else works without them.

**What problem it prevents:** Building agents and workflows on ad-hoc communication patterns that must be retrofitted into the spine later — a materially harder and riskier operation.

**Example:** Stage 0 delivers the five spine containers before any specialist agent or workflow template is built.

**Counter-example:** A pilot team builds three agents communicating via direct HTTP, then "we'll add the Event Bus later."

**Consequences of violating it:** Every agent built before the spine must be rewritten. The pilot proves nothing about the platform's actual architecture. Technical debt compounds from day one.

*Reference: RA Section 14, Stage 0*

---

## Engineering Principles

### E1. Contracts Before Implementations

**Why it exists:** Uniform contract shapes for agents, tools, tasks, memory, and events are what make plug-in extensibility real rather than marketing language.

**What problem it prevents:** Ad-hoc integration patterns where each new agent or tool requires bespoke orchestrator changes and custom context-passing logic.

**Example:** Every specialist agent implements the Agent Contract (capabilities, input_schema, output_schema, required_tools, cost_class, approval_required, idempotency_key_strategy) before it is registered.

**Counter-example:** The Coding Agent accepts a free-form JSON blob while the Test Agent expects a proprietary message format defined only in its README.

**Consequences of violating it:** The Agent Selector cannot match by capability. The Context Assembler cannot build predictable context packets. Audit correlation breaks because outputs have no stable shape.

*Reference: RA Sections 6, 7, 8, 9, 10*

---

### E2. Idempotency Is Mandatory for Side-Effecting Agents

**Why it exists:** Tasks are retried. Workflows are resumed after platform restarts. An agent that cannot handle duplicate invocations will corrupt external systems.

**What problem it prevents:** Duplicate pull requests, double deployments, repeated ticket creation, and other side effects caused by retry logic the agent did not anticipate.

**Example:** The Coding Agent declares an `idempotency_key_strategy` based on `task_id + branch_name`. A retried invocation detects the existing PR and returns its reference instead of creating a second one.

**Counter-example:** A retried agent invocation creates a second pull request because it has no mechanism to detect that the first invocation already succeeded before the timeout.

**Consequences of violating it:** Retry logic becomes dangerous rather than helpful. Operators disable retries, reducing platform resilience. External systems accumulate duplicate artifacts.

*Reference: RA Section 6 — Agent Contract*

---

### E3. State Is Written Before It Is Acted Upon

**Why it exists:** Every workflow transition must survive platform restarts. In-memory state is lost state.

**What problem it prevents:** Workflows that restart from scratch after a crash, losing partial progress, orphaning external side effects, and requiring manual intervention.

**Example:** The workflow state machine persists the transition from `Implemented` to `Tested` before dispatching the Test Agent. A restart resumes from `Tested`, not from the beginning.

**Counter-example:** Workflow state lives in the Orchestrator's process memory. A pod restart loses all in-progress workflows.

**Consequences of violating it:** Platform restarts become production incidents. Engineers lose trust in workflow durability. Long-running Brownfield modernisation workflows cannot survive maintenance windows.

*Reference: RA Section 5.5 — Task Queue & Workflow Engine*

---

### E4. Portable Infrastructure Primitives

**Why it exists:** Vendor-neutral at the platform layer means portable primitives at the infrastructure layer — the same containers deploy on different clouds with configuration changes, not architecture changes.

**What problem it prevents:** Cloud-specific implementations baked into platform containers that make migration between cloud providers a rewrite.

**Example:** The Event Bus container deploys as Azure Service Bus or Amazon EventBridge depending on tenant configuration. The Orchestrator container is identical in both deployments.

**Counter-example:** The Task Queue is implemented exclusively with Azure Durable Functions APIs embedded in the Orchestrator's source code.

**Consequences of violating it:** Multi-cloud deployment requires forking the platform. Clients on non-preferred clouds cannot adopt the platform without a dedicated engineering effort.

*Reference: RA Section 12 — Deployment Architecture*

---

## AI Principles

### AI1. Agents Propose; Humans Dispose

**Why it exists:** Every workflow has named, non-bypassable approval gates. Safety, cost, and compliance require human authority at decision points.

**What problem it prevents:** Fully autonomous pipelines that merge, deploy, or modify production systems without recorded human consent.

**Example:** The Architecture Agent produces ADRs and API contracts. The workflow cannot transition to `Implemented` until a Tech Lead records approval at the architecture gate.

**Counter-example:** The platform auto-merges pull requests that pass automated tests without any human review record.

**Consequences of violating it:** Unreviewed code reaches production. Compliance audits find no named approver. Incident retrospectives cannot identify who authorised a change.

*Reference: RA Section 1, Principle 4; Section 5.6*

---

### AI2. Model Capability and Platform Capability Are Separate Investments

**Why it exists:** A well-architected platform does not improve the judgement quality of a weak model. The Model Router is a lever for cost and routing, not a substitute for model capability.

**What problem it prevents:** False confidence that platform architecture compensates for inadequate model selection, leading to quality failures blamed on "the platform" rather than the model tier.

**Example:** A security-critical architecture review is routed to a high-capability model tier. A routine test-scaffold task uses a lower tier. Both are deliberate choices documented in the cost_class and routing policy.

**Counter-example:** Expecting a low-tier model to produce architecture-quality ADRs because "the platform handles quality through its workflow gates."

**Consequences of violating it:** Quality failures at scale. Misallocated inference spend — expensive models on trivial tasks, cheap models on critical decisions. False marketing claims about platform intelligence.

*Reference: RA Section 13 — "The honest limit"*

---

### AI3. AI Output Is Never Institutional Memory by Default

**Why it exists:** Long-term memory is written to deliberately, not automatically. Ungoverned writes produce inconsistent, stale, or contradictory organisational context.

**What problem it prevents:** Agents retrieving outdated or unverified AI-generated content as if it were authoritative organisational knowledge.

**Example:** A resolved incident's root cause and fix are deliberately written to long-term memory with provenance linking to the workflow run. A routine agent conversation is not.

**Counter-example:** Every agent output is automatically embedded and stored in the vector knowledge store without review or provenance.

**Consequences of violating it:** Memory retrieval returns contradictory guidance. Agents produce inconsistent output across runs. Institutional knowledge becomes ungoverned noise.

*Reference: RA Section 5.3 — Shared Memory & Project Context*

---

### AI4. Every Agent Action Is Attributable

**Why it exists:** The `emitted_by` field on every event is always populated. Anonymous agent actions cannot be audited, costed, or debugged.

**What problem it prevents:** Untraceable agent behaviour where no one can determine which agent produced a given output or triggered a given side effect.

**Example:** An `AgentCompleted` event carries `emitted_by: coding-agent-v2` with a correlation to `task_id` and `workflow_run_id`.

**Counter-example:** A workflow produces a code change but the audit record shows only "agent" with no identity, version, or model tier.

**Consequences of violating it:** Incident investigation cannot identify the responsible agent. Cost attribution is impossible. Agent version rollback cannot target the correct producer.

*Reference: RA Section 10 — Event Model*

---

## Security Principles

### S1. Three Distinct Security Controls, Never Merged

**Why it exists:** RBAC, Policy Engine, and Secrets Vault govern different things and MUST remain separate concerns.

**What problem it prevents:** A single "security module" where changing agent permissions accidentally changes human approval rights, or where credential management is entangled with action authorisation.

**Example:** RBAC determines which human can approve the architecture gate. The Policy Engine determines whether the Coding Agent is permitted to create a branch regardless of who triggered the workflow. The Secrets Vault issues a short-lived token for the GitHub integration per invocation.

**Counter-example:** A unified "security service" that checks user role, agent permission, and credential retrieval in a single monolithic function.

**Consequences of violating it:** Permission changes have unintended side effects. Credential leaks expose broader access than intended. Security audits cannot isolate which control failed.

*Reference: RA Section 5.9*

---

### S2. No Agent or Tool Holds Credentials Directly

**Why it exists:** The Secrets Vault issues short-lived, scoped tokens per invocation. Long-lived credentials in agent or tool code are a permanent breach waiting to happen.

**What problem it prevents:** Credential exposure through agent logs, container images, configuration files, or memory dumps.

**Example:** The GitHub Tool integration requests a scoped PAT from the Secrets Vault with `write` scope limited to the target repository. The token expires after the invocation completes.

**Counter-example:** The Coding Agent's container image contains a GitHub personal access token in an environment variable.

**Consequences of violating it:** Credential rotation requires redeploying agents. A compromised agent container exposes all integrated systems. Least-privilege is impossible to enforce.

*Reference: RA Section 5.9; Section 7 — Tool Contract*

---

### S3. Least-Privilege Scope Ceiling on Every Tool

**Why it exists:** The Tool Contract's `scope` field (read / write / admin) enforces a ceiling regardless of what the underlying credential could technically do.

**What problem it prevents:** Over-permissioned tool integrations where an agent requesting read access receives credentials with admin privileges because "it's easier."

**Example:** A Security Agent's dependency scan tool is registered with `scope: read`. Even if the Snyk API key could modify project settings, the Tool Contract prevents it.

**Counter-example:** All tool integrations receive admin-scoped credentials because the platform administrator configured one master key for simplicity.

**Consequences of violating it:** A compromised agent can perform actions far beyond its intended role. Blast radius of any agent failure expands to full admin access on integrated systems.

*Reference: RA Section 7 — Tool Contract*

---

### S4. External System Access Is Scoped, Never Blanket

**Why it exists:** Arrows into the platform from external systems are read/write per a scoped Tool Contract — never blanket credentials.

**What problem it prevents:** Platform-wide access to all repositories, all projects, or all infrastructure that an agent or workflow does not need.

**Example:** The Tool Registry entry for `github-prod` is scoped to the repositories listed in the tenant's policy configuration. An agent working on Project A cannot access Project B's repositories.

**Counter-example:** The platform holds a GitHub organisation admin token used by all agents for all repositories across all tenants.

**Consequences of violating it:** Cross-project data leakage. A bug in one agent's logic can modify unrelated repositories. Multi-tenant isolation at the tool layer is impossible.

*Reference: RA Section 2 — System Context*

---

## Architecture Principles

### A1. Agents Never Call Agents

**Why it exists:** All inter-agent communication is event-mediated. Direct agent-to-agent calls create O(n²) coupling that worsens with every new capability.

**What problem it prevents:** Tight coupling where adding agent N requires updating agents 1 through N-1 to know about it. Interface changes cascade across the agent graph.

**Example:** The Coding Agent publishes `AgentCompleted` with a diff and PR reference. The Orchestrator's state machine transitions to the testing state and publishes `TaskCreated` for the Test Agent. The Coding Agent never knows the Test Agent exists.

**Counter-example:** The Coding Agent, upon completing its work, directly invokes the Test Agent's API with the diff and branch name.

**Consequences of violating it:** Adding the fiftieth agent requires updating up to forty-nine existing agents. Agent interface changes break callers. The platform's scalability claim is false.

*Reference: RA Section 1, Principle 1; Section 3.1*

---

### A2. The Orchestrator Plans; It Never Executes

**Why it exists:** The orchestrator decomposes and routes. It never writes code, runs a scan, or makes a specialist judgement. This keeps the core stable as specialist agents change.

**What problem it prevents:** Orchestrator bloat where the core accumulates specialist logic that must be updated every time a domain changes — testing frameworks, security scanners, coding standards.

**Example:** The Orchestrator's components are: Workflow State Machine, Agent Selector, Context Assembler, Cost-Aware Dispatcher, Gate Enforcer, and Retry & Compensation Manager. None of these write code or run tests.

**Counter-example:** The Orchestrator contains a built-in code formatter, a dependency vulnerability scanner, and a test runner "for simple cases."

**Consequences of violating it:** Every specialist capability change requires an orchestrator release. The core becomes the bottleneck for all platform evolution. Specialist agents become second-class.

*Reference: RA Section 1, Principle 2; Section 4*

---

### A3. New Agents Plug In; They Never Patch In

**Why it exists:** Adding a capability means registering a new agent against the Agent Registry contract — never editing orchestrator code. This is the platform's actual scalability claim.

**What problem it prevents:** Orchestrator code changes for every new agent type, making the core a merge-conflict battlefield and a deployment risk.

**Example:** A new Documentation Agent registers with capabilities `["generates-api-docs", "updates-readme"]`. The Agent Selector discovers it by capability tag. Zero orchestrator code changes.

**Counter-example:** Adding a Security Agent requires adding a new case to the Orchestrator's workflow switch statement, a new import, and a new dispatch method.

**Consequences of violating it:** Agent additions require core platform releases. Third-party agent development is impossible. The registry becomes decorative.

*Reference: RA Section 1, Principle 3; Section 5.1*

---

### A4. Every Decision Is Reconstructable

**Why it exists:** If an auditor or incident review asks "why did this happen," the answer MUST be a query against the audit store, not a guess.

**What problem it prevents:** Post-hoc reconstruction from fragmented logs, engineer memory, or AI output that cannot be verified.

**Example:** An auditor queries the audit store for `workflow_run_id: wr-2847` and receives a complete chain: task creation, agent execution, approval decisions, state transitions, and rollback events — each timestamped and attributed.

**Counter-example:** An incident reviewer asks why a hotfix was deployed and the team reconstructs the timeline from Slack messages and approximate memory.

**Consequences of violating it:** Compliance audits fail. Incident retrospectives produce incomplete timelines. Legal discovery cannot produce authoritative records. Trust in the platform erodes.

*Reference: RA Section 1, Principle 5; Section 5.7*

---

### A5. Stateless Specialist Agents Scale Horizontally

**Why it exists:** Adding load means adding agent replicas, not redesigning workflow logic. Agent statelessness behind the Event Bus is the mechanism for engineer-scale growth.

**What problem it prevents:** Stateful agents that cannot be replicated, creating throughput bottlenecks as more engineers use the platform.

**Example:** Three Coding Agent replicas consume tasks from the Event Bus. The Orchestrator does not know or care which replica handles a given task.

**Counter-example:** A single Coding Agent instance holds session state in memory and must be the sole handler for a given workflow run.

**Consequences of violating it:** Platform throughput is capped by single-agent capacity. Scaling requires architectural changes, not replica addition. Failover requires state migration.

*Reference: RA Section 13 — Scalability Strategy*

---

## Workflow Principles

### W1. Eight Workflows, One Set of Primitives

**Why it exists:** All workflow types share the same orchestrator, registries, and event vocabulary. What differs is the state machine, the agents engaged, and where approval gates sit.

**What problem it prevents:** Per-workflow platform forks where Greenfield, Brownfield, and defect resolution each require separate orchestrators, separate registries, or separate event models.

**Example:** Greenfield Product Development and Production Defect Resolution both use `TaskCreated`, `AgentCompleted`, and `ApprovalRequested` events. They differ only in their loaded state machine template and gate configuration.

**Counter-example:** Defect resolution is implemented as a separate microservice with its own event bus because "it's too different from Greenfield."

**Consequences of violating it:** Platform complexity multiplies with each workflow type. Shared observability, auditing, and governance break down. New workflows require new infrastructure.

*Reference: RA Section 11*

---

### W2. Gate Placement Reflects What Is Being Protected

**Why it exists:** Greenfield gates protect decisions before work is built on them. Brownfield gates protect existing behaviour before anything is allowed to change it. Defect resolution gates are time-boxed because the cost of waiting exceeds the cost of a reversible mistake.

**What problem it prevents:** Uniform gate policies that are either too slow for incidents or too permissive for architectural decisions.

**Example:** Greenfield architecture review is open-ended — the Tech Lead takes the time needed. Defect resolution diagnosis confirmation is time-boxed with automatic escalation to senior on-call if no response within SLA.

**Counter-example:** A P1 production incident waits indefinitely at an open-ended architecture-style gate while the on-call engineer is in a meeting.

**Consequences of violating it:** P1 incidents exceed SLA because gates designed for deliberation block urgency. Or: architectural mistakes reach implementation because incident-speed gates are applied to design decisions.

*Reference: RA Sections 11.1, 11.2, 11.3*

---

### W3. Context Passes Forward Explicitly Per Task Schema

**Why it exists:** Each workflow step produces context consumed by the next. This context is assembled by the Context Assembler and passed via the Task Schema — not silently shared between agents.

**What problem it prevents:** Implicit context leakage where an agent accesses outputs from agents it was not assigned, or misses context it needs because nothing enforced the handoff.

**Example:** The Architecture Agent's output (ADRs + API contracts) is packaged into the `context` field of the task assigned to the Coding Agent. The Coding Agent receives exactly this packet — no more, no less.

**Counter-example:** The Coding Agent queries a shared cache for "whatever the last agent produced" without a defined schema or task correlation.

**Consequences of violating it:** Agents operate on stale, incomplete, or wrong context. Debugging context issues requires inspecting ambient shared state. Task correlation breaks.

*Reference: RA Section 8 — Task Schema; Section 11*

---

### W4. Rollback Strategy Is Defined Per Workflow, Not Per Platform

**Why it exists:** Greenfield rollback is pre-merge branch discard. Brownfield rollback is per-increment revertible commits. Defect resolution rollback is automatic on non-recovery. Each strategy matches the workflow's risk profile.

**What problem it prevents:** A single rollback mechanism applied uniformly — either too aggressive (auto-rollback on Greenfield scope changes) or too conservative (requiring human approval to rollback a failed hotfix).

**Example:** A failed Brownfield refactor increment reverts independently without touching other increments, verified against the pre-refactor characterization baseline.

**Counter-example:** All workflows use "revert the last commit" regardless of whether the workflow is a multi-increment modernisation or a hotfix deployment.

**Consequences of violating it:** Brownfield rollbacks destroy unrelated increments. Defect resolution rollbacks wait for human approval during active outages. Greenfield rollbacks are unnecessarily complex.

*Reference: RA Sections 11.1, 11.2, 11.3, 11.4*

---

### W5. Approval Denied Is a Revision Task, Not a Dead End

**Why it exists:** `ApprovalDenied` routes back into the workflow as a revision task. Workflows MUST NOT terminate on rejection — they loop back with feedback.

**What problem it prevents:** Binary approve/reject workflows where rejection kills the entire workflow run, forcing the requester to start from scratch.

**Example:** A Tech Lead denies architecture approval with feedback. The workflow creates a revision task assigned to the Architecture Agent with the denial reason in context. The workflow run continues.

**Counter-example:** Architecture approval is denied and the workflow run is marked `Failed` with no path to resubmit.

**Consequences of violating it:** Rejection is expensive — all prior agent work is lost. Approvers hesitate to deny because the cost is so high. Quality suffers because feedback loops are broken.

*Reference: RA Section 10.1 — Core event types*

---

## Agent Principles

### AG1. Uniform Contract Shape for All Agents

**Why it exists:** Every specialist agent — present or future — implements the same contract shape. Uniformity is what makes plug-in extensibility real.

**What problem it prevents:** Agent-specific integration code in the orchestrator that grows with every new agent type.

**Example:** Agent #47 registers the same fields as Agent #1: agent_id, capabilities, input_schema, output_schema, required_tools, cost_class, approval_required, idempotency_key_strategy.

**Counter-example:** The Discovery Agent uses a custom registration format because "it's a special first-in-pipeline agent."

**Consequences of violating it:** The Agent Registry cannot provide uniform discovery. The Agent Selector requires agent-specific logic. The audit store cannot correlate agent actions consistently.

*Reference: RA Section 6 — Agent Contract*

---

### AG2. Capability-Based Discovery, Not Name-Based Dispatch

**Why it exists:** The Agent Selector queries the Agent Registry by capability tag, not by agent name. Agents are interchangeable implementations of capabilities.

**What problem it prevents:** Hardcoded agent name references in workflow templates that break when an agent is replaced, upgraded, or provided by a different vendor.

**Example:** The workflow template requests capability `generates-unit-tests`. The Agent Selector resolves this to whichever agent is registered with that tag — Test Agent v1, Test Agent v2, or a third-party alternative.

**Counter-example:** The Greenfield workflow template contains `assigned_agent_id: "test-agent-v1"` as a hardcoded string.

**Consequences of violating it:** Agent upgrades require workflow template changes. A/B testing agent implementations is impossible. Vendor-provided agents cannot replace built-in ones without editing workflows.

*Reference: RA Section 5.1 — Agent Registry*

---

### AG3. Agents Request Tools by Capability, Not by Integration

**Why it exists:** Agents request a tool by capability tag (e.g., `create-pull-request`). The Tool Registry resolves it to the tenant's configured concrete integration.

**What problem it prevents:** Agent logic encoded with vendor-specific tool references that break on toolchain change.

**Example:** The Coding Agent requests `create-pull-request`. For Tenant A, this resolves to `github-prod`. For Tenant B, it resolves to `azure-devops-tenant-b`.

**Counter-example:** The Coding Agent calls `github.createPullRequest()` directly, with GitHub-specific parameters hardcoded in its logic.

**Consequences of violating it:** Every agent is tied to a specific vendor's API. Toolchain migration requires rewriting agent code. Multi-tenant deployments with different toolchains require agent forks.

*Reference: RA Section 5.2; Section 7 — Tool Contract*

---

### AG4. Agents Publish Results; They Never Command

**Why it exists:** An agent publishes what it did on the Event Bus. It never instructs another agent on what to do next. Sequencing is the orchestrator's exclusive responsibility.

**What problem it prevents:** Agent-embedded workflow logic that duplicates and conflicts with the orchestrator's state machine.

**Example:** The Security Agent publishes `AgentCompleted` with scan findings. It does not publish a `TaskCreated` event for the Coding Agent to fix vulnerabilities.

**Counter-example:** The Security Agent, upon finding vulnerabilities, directly creates a task for the Coding Agent and publishes it to the Event Bus.

**Consequences of violating it:** Workflow logic is split between the orchestrator and agents. State machines become incomplete and untrustworthy. Agents develop hidden dependencies on each other's command patterns.

*Reference: RA Section 5.4; Section 3.1*

---

### AG5. Cost Class Is Declared, Not Inferred

**Why it exists:** Every agent declares a default cost_class (low / medium / high) as a hint to the Model Router. Cost awareness starts at registration, not after the bill arrives.

**What problem it prevents:** Uniform model tier assignment that either over-spends on routine tasks or under-powers critical ones.

**Example:** The Architecture Agent registers with `cost_class: high`. The Documentation Agent registers with `cost_class: low`. The Cost-Aware Dispatcher uses these as defaults, overridable per task.

**Counter-example:** All agents are dispatched to the most capable model because "we don't know which tasks are expensive."

**Consequences of violating it:** Inference costs scale linearly with workflow volume regardless of task complexity. Budget overruns force emergency model downgrades that degrade critical workflows.

*Reference: RA Section 6 — Agent Contract; Section 5.10*

---

## Memory Principles

### M1. Working Context and Long-Term Memory Are Strictly Separated

**Why it exists:** Working context is short-lived — the active task, branch, and conversation state for the current run. Long-term memory is durable organisational knowledge. Conflating them is the most common cause of inconsistent agent output.

**What problem it prevents:** Ephemeral task state leaking into institutional memory, or durable knowledge being discarded at the end of a workflow run.

**Example:** The Coding Agent's branch name and conversation history are working context passed via the Task Schema. Coding standards and ADRs are retrieved from long-term memory by explicit query.

**Counter-example:** At the end of every workflow run, the entire conversation history is embedded and written to the vector store as long-term memory.

**Consequences of violating it:** Agents retrieve stale task-specific context as organisational knowledge. Memory store fills with ephemeral noise. Retrieval quality degrades. Output inconsistency across runs.

*Reference: RA Section 5.3*

---

### M2. Working Context Passes Explicitly, Never Silently

**Why it exists:** Working context is passed explicitly between agents per the Task Schema, not silently shared via ambient state.

**What problem it prevents:** Agents reading or writing shared ambient state that creates hidden coupling and race conditions between concurrent workflow runs.

**Example:** The Context Assembler builds a context packet from prior agent outputs and places it in the `context` field of the next task. No agent reads from a shared "current context" variable.

**Counter-example:** Agents read from and write to a shared Redis key named `current-project-context` that is updated in place during workflow execution.

**Consequences of violating it:** Concurrent workflows corrupt each other's context. Debugging requires understanding ambient shared state. Task isolation is illusory.

*Reference: RA Section 5.3; Section 8 — Task Schema*

---

### M3. Long-Term Memory Is Written Deliberately

**Why it exists:** Long-term memory is a vector knowledge store written to deliberately, not automatically. Every entry has provenance.

**What problem it prevents:** Uncontrolled memory growth where every agent output becomes "knowledge" regardless of quality, relevance, or verification.

**Example:** After a completed incident workflow, the Root-Cause Agent's confirmed finding is deliberately written to long-term memory with `source_type: incident` and provenance linking to the workflow run.

**Counter-example:** Every `AgentCompleted` event automatically triggers an embedding write to long-term memory.

**Consequences of violating it:** Memory store accumulates unverified, contradictory, and ephemeral content. Retrieval returns noise. Agents cannot distinguish authoritative knowledge from discarded proposals.

*Reference: RA Section 5.3; Section 9 — Memory Schema*

---

### M4. Memory Retrieval Is Filtered, Never Blind

**Why it exists:** Long-term memory retrieval uses structured metadata — source_type, tenant_id, recency_weight — not blind similarity search.

**What problem it prevents:** Irrelevant or stale memories outranking current, authoritative ones because they happen to be semantically similar.

**Example:** The Architecture Agent queries long-term memory with `source_type: ADR` and `recency_weight > 0.7`, retrieving recent architecture decisions rather than a three-year-old incident report that mentions similar keywords.

**Counter-example:** The agent performs a pure vector similarity search with no metadata filters and receives the top-5 closest embeddings regardless of type, age, or tenant.

**Consequences of violating it:** Agents act on outdated guidance. Cross-tenant memory leakage occurs at the retrieval layer. Incident reports override current architecture decisions.

*Reference: RA Section 9 — Memory Schema*

---

### M5. Memory Provenance Is Auditable

**Why it exists:** Every long-term memory entry records which task or workflow run wrote it. Memory itself is subject to audit.

**What problem it prevents:** Unattributed knowledge entries where no one can determine why a piece of "organisational knowledge" exists or whether it was verified.

**Example:** A memory entry for a coding standard includes `provenance: { workflow_run_id: "wr-1102", task_id: "t-5531", written_by: "architecture-agent-v1" }`.

**Counter-example:** A memory entry exists in the vector store with no record of when, why, or by whom it was created.

**Consequences of violating it:** Stale or incorrect knowledge cannot be traced to its source. Memory cleanup is impossible because entries cannot be evaluated for continued relevance. Audit scope expands unpredictably.

*Reference: RA Section 9 — Memory Schema*

---

## Communication Principles

### C1. One Event Envelope for All Event Types

**Why it exists:** Every event on the bus follows one envelope shape regardless of which agent or service emits it. Uniformity enables generic observability, auditing, and routing.

**What problem it prevents:** Event-type-specific envelopes that require custom parsers, break generic subscribers, and fragment the observability backbone.

**Example:** Both `AgentCompleted` and `ApprovalGranted` carry `event_id`, `event_type`, `timestamp`, `task_id`, `workflow_run_id`, `emitted_by`, and `payload`.

**Counter-example:** `AgentCompleted` uses one envelope format while `ApprovalGranted` uses a different structure with different correlation fields.

**Consequences of violating it:** The observability backbone requires per-event-type handling. Audit queries cannot uniformly correlate events. New event types require infrastructure changes.

*Reference: RA Section 10 — Event Model*

---

### C2. Events Are Facts, Not Commands

**Why it exists:** An agent publishes what it did (a fact). The orchestrator's state machine decides what happens next (a command). Mixing these roles creates dual workflow logic.

**What problem it prevents:** Events that carry imperative instructions ("now run the Test Agent"), creating two authorities for workflow sequencing.

**Example:** The Coding Agent publishes `AgentCompleted` with `{ diff: "...", pr_url: "..." }`. The Orchestrator's state machine receives this fact and decides the next transition.

**Counter-example:** The Coding Agent publishes an event with `{ next_agent: "test-agent", action: "run-tests", branch: "feature-x" }`.

**Consequences of violating it:** Workflow logic is split between events and state machines. The orchestrator cannot enforce gate and policy checks on agent-commanded transitions. Event consumers act on unvalidated instructions.

*Reference: RA Section 5.4; Section 10*

---

### C3. Every Event Is Correlated to a Task and Workflow Run

**Why it exists:** `task_id` and `workflow_run_id` on every event enable end-to-end tracing from workflow initiation to final outcome.

**What problem it prevents:** Orphan events that cannot be tied to a workflow, making audit reconstruction and debugging impossible.

**Example:** An `AgentFailed` event carries `task_id: "t-8821"` and `workflow_run_id: "wr-4420"`, enabling the Retry & Compensation Manager to locate the exact task and workflow context.

**Counter-example:** An agent publishes a failure notification with no task or workflow correlation, only a timestamp and error message.

**Consequences of violating it:** Failed tasks cannot be retried in context. Audit queries return incomplete chains. Observability dashboards show disconnected events.

*Reference: RA Section 10 — Event Model*

---

### C4. Governance Relationships Are Gates, Not Notifications

**Why it exists:** Arrows from the platform to governance roles (Clinical Safety Officer, CAB Chair, or equivalent) are gates, not notifications. The workflow cannot proceed past that point without a recorded decision.

**What problem it prevents:** Approval requests that are informational only — the workflow proceeds regardless of whether the governance role responded.

**Example:** The Release Management workflow reaches the CAB gate. The state machine blocks at this state until `ApprovalGranted` or `ApprovalDenied` is recorded by a named approver.

**Counter-example:** The platform sends an email to the CAB Chair notifying them of an upcoming release, and the workflow proceeds to deployment after a 24-hour wait regardless of response.

**Consequences of violating it:** Governance is theatre. Releases proceed without required approvals. Compliance requirements are structurally unenforceable.

*Reference: RA Section 2 — System Context*

---

## Governance Principles

### G1. Audit Store Is Immutable and Append-Only

**Why it exists:** Every agent action and every human decision is recorded in an immutable, append-only store tied to task ID, workflow run, and timestamp.

**What problem it prevents:** Retroactive modification of audit records that destroys trust in the platform's accountability.

**Example:** An auditor queries all events for a workflow run and receives a complete, chronologically ordered, unmodified chain of records.

**Counter-example:** An administrator edits an audit record to change the approval decision from "denied" to "granted" after the fact.

**Consequences of violating it:** Audit records are untrustworthy. Compliance certifications are invalidated. Incident investigations produce evidence that cannot be relied upon in legal or regulatory proceedings.

*Reference: RA Section 5.7*

---

### G2. Governance Requires Data, Not Dashboards

**Why it exists:** Org-wide observability dashboards and policy-as-code libraries are only meaningful once enough real workflow history exists to govern. Building governance before data produces governance theatre.

**What problem it prevents:** Empty dashboards, unenforceable policies, and governance frameworks disconnected from actual platform behaviour.

**Example:** Stage 4 (Governance at scale) begins only after Stages 0–3 have produced real workflow history across multiple tenants and agent types.

**Counter-example:** The platform launches with a full governance dashboard and policy library before a single real workflow has completed.

**Consequences of violating it:** Governance metrics reflect no real activity. Policies are written for hypothetical scenarios. Leadership makes decisions based on empty charts. Engineers ignore governance tooling.

*Reference: RA Section 14, Stage 4*

---

### G3. Policy-as-Code Governs Agent Actions, Not Human Intent

**Why it exists:** The Policy Engine governs which actions an agent is permitted to take regardless of who triggered the workflow. It is separate from RBAC (which governs human permissions) and separate from approval gates (which govern workflow transitions).

**What problem it prevents:** Agents performing actions that no human would be permitted to perform, because agent permissions were not independently governed.

**Example:** The Policy Engine prevents the Coding Agent from pushing directly to the `main` branch, even if the workflow was triggered by a senior engineer with broad RBAC permissions.

**Counter-example:** Agent permissions are derived entirely from the triggering user's RBAC role — a senior engineer's workflow run gives the Coding Agent admin access to all repositories.

**Consequences of violating it:** Agents become privilege-escalation vectors. A low-privilege user triggers a workflow that executes high-privilege agent actions. The principle of least privilege is structurally unenforceable for agent behaviour.

*Reference: RA Section 5.9*

---

### G4. Multi-Tenancy Must Precede Multi-Team Onboarding

**Why it exists:** Namespace isolation, per-tenant policy configuration, and per-tenant quota MUST exist before a second business unit onboards. Retrofitting tenancy after multiple teams share state is materially harder than building it first.

**What problem it prevents:** Shared-state contamination between teams that requires painful data migration and access-control retrofits.

**Example:** Stage 2 (Multi-tenancy) is completed before any second business unit is onboarded. Each team enters an already-isolated environment.

**Counter-example:** Three teams onboard in Stage 1. Stage 2 adds tenant isolation later by partitioning data that was never designed for separation.

**Consequences of violating it:** Cross-team data leakage. Policy configuration conflicts. Memory store contamination. Retrofit costs exceed the cost of building tenancy correctly the first time.

*Reference: RA Section 14, Stage 2*

---

## Scalability Principles

### SC1. Three Scaling Dimensions, Three Mechanisms

**Why it exists:** "Scale" conflates three distinct challenges — more engineers, more agent types, more tenants — each addressed by a different mechanism.

**What problem it prevents:** Applying a single scaling strategy (e.g., "add more servers") to problems that require architectural solutions (e.g., agent registry growth).

**Example:** More engineers → horizontal agent replicas. More agent types → Agent Registry entries. More tenants → namespace isolation. Three problems, three mechanisms.

**Counter-example:** "The platform doesn't scale" is addressed by doubling Orchestrator instances, regardless of whether the bottleneck is agent throughput, registry size, or tenant isolation.

**Consequences of violating it:** Scaling investments target the wrong dimension. Engineer growth hits agent throughput limits while the Orchestrator is over-provisioned. New agent types require core changes while replicas sit idle.

*Reference: RA Section 13*

---

### SC2. Agent Registry Growth Is the Scaling Mechanism for New Capabilities

**Why it exists:** Each new agent type is an independent registration, never a change to the orchestrator or existing agents. This is how the platform scales its capability surface.

**What problem it prevents:** Linear growth in core platform complexity for every new capability, eventually making the orchestrator unmaintainable.

**Example:** Adding a Migration Agent for Legacy Migration workflows is a registry entry. The orchestrator, Coding Agent, and Test Agent are untouched.

**Counter-example:** Adding legacy migration support requires new methods in the Orchestrator, new event handlers, and modifications to the Coding Agent's output format.

**Consequences of violating it:** Capability growth is linearly coupled to core platform changes. Time-to-add-a-capability grows with platform age. Innovation is bottlenecked by core release cycles.

*Reference: RA Section 13; Section 5.1*

---

### SC3. Platform Architecture Stops Changing Shape After the Agent Catalog Is Complete

**Why it exists:** After Stage 3 (full agent catalog and all workflow templates), the platform itself stops changing shape. Further growth is a rollout problem, not an architecture problem.

**What problem it prevents:** Perpetual architectural evolution that never stabilises enough for enterprise-wide adoption.

**Example:** Stages 4–5 add governance dashboards and onboard remaining teams. No new containers, no new contracts, no new communication patterns.

**Counter-example:** Every new team onboarding triggers a platform architecture review because "they have unique needs" that require core changes.

**Consequences of violating it:** The platform never reaches stability. Enterprise rollout is perpetually deferred. Teams build workarounds instead of waiting for the next architecture change.

*Reference: RA Section 14, Stages 3–5*

---

## Observability Principles

### O1. One Event Backbone, Three Audiences

**Why it exists:** Engineers, engineering leadership, and governance/compliance all consume the same underlying event stream — filtered and aggregated for their needs. One backbone, not three separate tools.

**What problem it prevents:** Fragmented observability where engineering traces, DORA metrics, and compliance audit trails require separate instrumentation, separate storage, and separate maintenance.

**Example:** An engineer traces `task_id: t-4421` through agent lifecycle events. Leadership views DORA metrics aggregated from `StateTransitioned` events. Governance filters `ApprovalGranted` and `ApprovalDenied` events for audit review. All from the same event stream.

**Counter-example:** Engineering uses Jaeger, leadership uses a custom DORA spreadsheet fed by nightly batch jobs, and compliance uses a separate audit database populated by a different pipeline.

**Consequences of violating it:** Data inconsistencies between views. Triple instrumentation burden on every new event type. Audit trail gaps when engineering and compliance systems diverge.

*Reference: RA Section 5.12*

---

### O2. State Transitions Are the Canonical Observability Record

**Why it exists:** `StateTransitioned` events are the canonical record consumed by observability. Workflow progress is measured by state machine transitions, not by agent-internal metrics.

**What problem it prevents:** Observability that tracks agent-internal signals (token counts, latency) but cannot answer "where is this workflow in its lifecycle?"

**Example:** A dashboard shows workflow run `wr-2847` transitioned from `Implemented` to `Tested` at 14:32 UTC. This is the authoritative progress record.

**Counter-example:** Workflow progress is inferred from agent log timestamps, which may be missing, out of order, or from a failed retry.

**Consequences of violating it:** Workflow status is ambiguous. SLA measurement is unreliable. Leadership cannot trust cycle-time metrics.

*Reference: RA Section 10.1 — StateTransitioned*

---

### O3. Task-Level Tracing Is the Engineer's View

**Why it exists:** Engineers need to see what an agent actually did for a specific task — not aggregated metrics, not governance summaries.

**What problem it prevents:** Engineer debugging that requires correlating events across multiple systems because no single view shows the full task lifecycle.

**Example:** An engineer queries all events for `task_id: t-8821` and sees: TaskCreated → AgentStarted → AgentCompleted → ApprovalRequested → ApprovalGranted → StateTransitioned — with payloads at each step.

**Counter-example:** An engineer debugging a failed task must check agent logs, orchestrator logs, the issue tracker, and the CI system separately and manually correlate timestamps.

**Consequences of violating it:** Mean time to debug increases. Engineers bypass the platform for manual investigation. Trust in platform transparency erodes.

*Reference: RA Section 5.12*

---

## Human-in-the-loop Principles

### H1. Human Approval Checkpoints Are a First-Class Platform Service

**Why it exists:** Approval gates are not a UI afterthought bolted onto workflows. They are a platform service that produces named-approver records before the state machine is permitted to transition.

**What problem it prevents:** Approval mechanisms that can be bypassed by API calls, agent logic, or workflow configuration shortcuts.

**Example:** The Gate Enforcer component refuses to advance workflow state until the Human Approval Checkpoint service returns a recorded decision with who, when, what they saw, and what they decided.

**Counter-example:** Approval is implemented as a checkbox in a web UI that sets a flag on the task object, bypassable by any service with database access.

**Consequences of violating it:** Approvals are cosmetic. Workflows proceed without genuine human review. The "humans approve, agents propose" principle is structurally unenforceable.

*Reference: RA Section 5.6*

---

### H2. Every Gate Is Non-Bypassable by Design

**Why it exists:** Gates can be time-boxed or open-ended, but every gate is non-bypassable. There is no code path, configuration flag, or emergency override that skips a gate.

**What problem it prevents:** "Emergency bypass" mechanisms that become the normal path, eroding every gate in the system.

**Example:** A P1 defect resolution gate is time-boxed (escalates after SLA expiry) but never bypassed. If the on-call does not respond, escalation occurs — the gate is not skipped.

**Counter-example:** An `EMERGENCY_BYPASS=true` environment variable allows workflows to skip all approval gates.

**Consequences of violating it:** Gates exist only for compliance documentation, not actual control. Every workflow has an unofficial fast path. Audit records show gate satisfaction that did not occur.

*Reference: RA Section 5.6; Section 1, Principle 4*

---

### H3. Named Approver, Not Anonymous Approval

**Why it exists:** Every gate produces a record of who approved, when, what they saw, and what they decided. Anonymous or system-generated approvals are not valid.

**What problem it prevents:** Approvals attributed to "system" or "auto-approved" that satisfy the gate mechanism without genuine human judgement.

**Example:** `ApprovalGranted: { approver: "j.smith@org.com", timestamp: "2026-06-27T14:32:00Z", reviewed: ["ADR-042", "API-contract-v3"], decision: "granted" }`.

**Counter-example:** `ApprovalGranted: { approver: "system", decision: "auto-approved-after-timeout" }`.

**Consequences of violating it:** Approvals are meaningless for accountability. Incident reviews cannot identify the responsible human. Regulatory requirements for named sign-off are not met.

*Reference: RA Section 5.6*

---

### H4. Time-Boxing Is a Gate Property, Not a Gate Bypass

**Why it exists:** Time-boxed gates (defect resolution) escalate on non-response — they do not disappear. Open-ended gates (architecture review) wait indefinitely. Both are valid; bypassing is not.

**What problem it prevents:** Confusing time-boxing with bypass — assuming a time-boxed gate that escalates is "less strict" than an open-ended gate.

**Example:** Defect diagnosis gate: 15-minute SLA. No response → escalates to senior on-call. Still a gate, still requires a recorded decision — just from a different approver.

**Counter-example:** Defect diagnosis gate: 15-minute SLA. No response → gate is automatically satisfied with `approver: "timeout"`.

**Consequences of violating it:** Time-boxed gates become auto-approval timers. On-call engineers learn to ignore gates because they auto-resolve. The human-in-the-loop principle is undermined by timeout logic.

*Reference: RA Section 11.3*

---

## Multi-tenancy Principles

### MT1. Three-Layer Tenancy Enforcement

**Why it exists:** Tenancy is enforced at three layers: namespace isolation in Task Queue and Memory stores, per-tenant policy configuration, and per-tenant quota on the Model Router.

**What problem it prevents:** Single-layer isolation (e.g., API-level only) that leaks tenant data through memory retrieval, task queues, or resource consumption.

**Example:** Tenant A's project context is in namespace `tenant-a`. Tenant A's policy mandates architecture gates. Tenant A's Model Router quota is 10,000 tokens/hour. All three layers are independently enforced.

**Counter-example:** Tenancy is enforced only at the API gateway — internal services operate on shared queues and shared memory with no namespace separation.

**Consequences of violating it:** Cross-tenant data leakage. One tenant's agent activity exhausts shared resources. Policy differences between tenants cannot be enforced.

*Reference: RA Section 5.8*

---

### MT2. Tenant Isolation at the Memory Layer Itself

**Why it exists:** `tenant_id` on every memory entry enforces isolation at the memory layer, not just at the API layer. A query without tenant filtering MUST return zero results from other tenants.

**What problem it prevents:** API-level tenant checks that are bypassed by direct memory store queries, misconfigured agents, or retrieval logic that omits tenant filtering.

**Example:** The Architecture Agent queries long-term memory with `tenant_id: "tenant-a"`. The memory store returns only entries belonging to Tenant A, regardless of which service issues the query.

**Counter-example:** Memory entries have no `tenant_id`. Tenant isolation is enforced by the API layer filtering results after retrieval.

**Consequences of violating it:** A misconfigured agent or direct store query exposes cross-tenant organisational knowledge. Compliance violations for data residency and isolation.

*Reference: RA Section 9 — Memory Schema*

---

### MT3. One Platform Deployment, Many Isolated Tenants

**Why it exists:** A single platform deployment serves multiple business units or clients without code forking. Isolation is by namespace and policy, not by deployment.

**What problem it prevents:** Per-tenant platform deployments that multiply operational cost, prevent shared improvements, and create version fragmentation.

**Example:** Business Unit A and Business Unit B share the same platform deployment. They have different tool configurations, different gate policies, and different memory namespaces.

**Counter-example:** Each client gets a dedicated platform deployment with its own codebase branch for customisations.

**Consequences of violating it:** Platform improvements must be deployed N times. Version drift between tenants is guaranteed. Operational cost scales linearly with tenant count.

*Reference: RA Section 5.8*

---

## Plugin Principles

### PL1. Registries Are the Only Extension Points

**Why it exists:** New agents and new tools are added exclusively through the Agent Registry and Tool Registry. There is no other sanctioned extension mechanism.

**What problem it prevents:** Extension through orchestrator modification, event bus middleware hacks, or workflow template overrides that bypass contract validation.

**Example:** A third-party vendor provides a Security Agent. It registers in the Agent Registry with the standard contract. It is discoverable and dispatchable immediately.

**Counter-example:** A team adds custom logic by deploying a sidecar service that intercepts events on the bus and modifies them before they reach the orchestrator.

**Consequences of violating it:** Extensions are ungoverned. Contract validation is bypassed. Audit trails are incomplete for non-registered participants. The platform's integration surface becomes unbounded and unmanageable.

*Reference: RA Section 5.1; Section 5.2*

---

### PL2. Tool Response Normalisation Is Mandatory

**Why it exists:** Every tool integration implements a `response_normaliser` that maps vendor-specific responses to a common shape. This is what makes swapping tools invisible to agent logic.

**What problem it prevents:** Agent logic that parses vendor-specific response formats, re-coupling agents to tools despite the registry abstraction.

**Example:** Both `github-prod` and `azure-devops-tenant-a` normalise their `create-pull-request` response to `{ pr_id, pr_url, status }`. The Coding Agent consumes this shape regardless of which tool created the PR.

**Counter-example:** The Coding Agent checks `if (tool_id === 'github-prod')` and parses GitHub's response format, with a separate parser for Azure DevOps.

**Consequences of violating it:** Tool swaps require agent changes. The Tool Registry abstraction is destroyed. Multi-tenant tool heterogeneity requires agent forks.

*Reference: RA Section 7 — Tool Contract*

---

### PL3. Rate Limiting Is a Tool Property

**Why it exists:** Each tool registration includes a `rate_limit_policy` that prevents one tenant's agent activity from exhausting a shared API quota.

**What problem it prevents:** Noisy-neighbour problems where one tenant's aggressive agent activity degrades tool availability for all other tenants.

**Example:** `github-prod` has a rate limit of 5,000 API calls/hour per tenant. Tenant A's agents are throttled at this ceiling without affecting Tenant B.

**Counter-example:** All tenants share a single GitHub API quota with no per-tenant rate limiting. One tenant's bulk operation blocks all others.

**Consequences of violating it:** Cross-tenant interference. External API quota exhaustion causes platform-wide tool failures. Tenants cannot be given differentiated service levels.

*Reference: RA Section 7 — Tool Contract*

---

## Model Independence Principles

### MI1. Model Router Is a Platform Service, Not an Agent Concern

**Why it exists:** The Cost-Aware Dispatcher routes tasks to model tiers based on complexity and risk. Agents declare a cost_class hint; they do not select or invoke models directly.

**What problem it prevents:** Agent-embedded model selection that cannot be centrally governed, cost-managed, or swapped without redeploying every agent.

**Example:** The Orchestrator's Cost-Aware Dispatcher routes a `cost_class: high` architecture task to the configured high-tier model endpoint. The Architecture Agent receives the result without knowing which model produced it.

**Counter-example:** Each agent embeds its own model client, API key, and model selection logic.

**Consequences of violating it:** Model swaps require redeploying all agents. Cost management is fragmented. Model governance (data residency, capability requirements) cannot be centrally enforced.

*Reference: RA Section 5.10; Section 4 — Cost-Aware Dispatcher*

---

### MI2. Model Tier Is Classified Per Task, Not Per Agent

**Why it exists:** An agent's default cost_class is a hint, overridable per task. A routine task from a high-cost-class agent may warrant a lower tier; a critical task from a low-cost-class agent may warrant a higher tier.

**What problem it prevents:** Rigid model assignment where agent-level defaults cannot adapt to task-level risk and complexity variations.

**Example:** The Coding Agent has `cost_class: medium`, but a specific task flagged as security-critical by the Policy Engine is routed to a high-tier model for that invocation only.

**Counter-example:** The Coding Agent always uses the medium-tier model for every task, including security-critical patches during active CVE exploitation.

**Consequences of violating it:** Security-critical tasks are under-powered. Routine tasks are over-provisioned. Cost and quality optimisation is impossible at the task level.

*Reference: RA Section 5.10; Section 6 — cost_class*

---

### MI3. Model Endpoints Are Configuration, Not Architecture

**Why it exists:** Which model serves which tier is a deployment configuration decision. The platform architecture does not encode model identities, versions, or providers.

**What problem it prevents:** Architecture documents, contracts, or code that reference specific model names, making the platform appear tied to a current provider.

**Example:** The Model Router's high tier points to `endpoint-url-from-config`. Swapping from one provider to another changes configuration, not platform code.

**Counter-example:** The Architecture Agent's contract specifies `model: claude-3-opus` as a required field.

**Consequences of violating it:** Model provider changes require contract amendments and agent redeployment. The platform's vendor-neutral claim is falsified at the model layer.

*Reference: RA Section 5.10; Section 12*

---

## Backward Compatibility Principles

### BC1. Agent Contract Shape Is Stable Across Versions

**Why it exists:** The Agent Contract fields are the platform's longest-lived interface. Agents built for v1.0 MUST register and operate on a platform running v3.0 without contract changes.

**What problem it prevents:** Contract changes that break existing agent registrations, forcing simultaneous upgrades of the platform and all agents.

**Example:** An agent registered in Stage 1 with the v1.0 contract continues to operate after Stages 2–4 are deployed, with no re-registration required.

**Counter-example:** Platform v2.0 adds a mandatory `model_preference` field to the Agent Contract, breaking all v1.0 agent registrations.

**Consequences of violating it:** Platform upgrades require coordinated agent upgrades. Third-party agents become incompatible without notice. The registry's stability guarantee is broken.

*Reference: RA Section 6 — Agent Contract*

---

### BC2. Event Envelope Is Stable; Payloads Evolve

**Why it exists:** The event envelope (event_id, event_type, timestamp, task_id, workflow_run_id, emitted_by, payload) is immutable. New event types and payload fields are additive.

**What problem it prevents:** Envelope changes that break every event consumer, observability pipeline, and audit query in the system.

**Example:** A new event type `SecurityScanCompleted` is added with a new payload shape. The envelope is identical to all existing events. All consumers continue to function.

**Counter-example:** v2.0 renames `emitted_by` to `source` in the event envelope, breaking all existing audit queries and observability dashboards.

**Consequences of violating it:** Platform upgrades break observability, auditing, and governance. Event consumers require simultaneous updates. Historical event data becomes unqueryable.

*Reference: RA Section 10 — Event Model*

---

### BC3. Workflow Templates Are Versioned, Not Mutated

**Why it exists:** A workflow template loaded for a running workflow run MUST NOT change mid-execution. Template updates apply to new runs only.

**What problem it prevents:** In-flight workflows that change behaviour when a template is updated, causing agents to receive tasks for states that no longer exist in the current template.

**Example:** Greenfield v2.0 adds a security gate. Workflow runs started under v1.0 complete under v1.0's state machine. New runs use v2.0.

**Counter-example:** The Greenfield state machine is updated in place, and an in-flight workflow run suddenly encounters a new mandatory gate it was not designed to pass through.

**Consequences of violating it:** In-flight workflows fail unpredictably. Gate enforcement becomes inconsistent within a single workflow run. Audit records reference states that no longer exist in the current template.

*Reference: RA Section 11; Section 8 — workflow_type*

---

## Failure Recovery Principles

### FR1. Three Escalating Recovery Tiers

**Why it exists:** Failure recovery has three tiers: automatic retry with backoff for transient failures, saga-style compensation for partial multi-step failures, and escalation to a human gate when retries exhaust.

**What problem it prevents:** Binary failure handling — either infinite retry or immediate abandonment — both of which are unacceptable in enterprise workflows.

**Example:** A flaky API call fails → automatic retry (tier 1). A multi-step Brownfield increment partially fails → saga compensation reverts the increment (tier 2). Retries exhaust → escalation to on-call engineer (tier 3).

**Counter-example:** Any agent failure immediately marks the workflow as `Failed` with no retry. Or: a failed agent is retried indefinitely with no escalation.

**Consequences of violating it:** Transient failures cause unnecessary workflow abandonment. Partial failures leave inconsistent state. Exhausted retries hang workflows forever or fail silently.

*Reference: RA Section 5.11*

---

### FR2. The Platform Never Silently Gives Up or Silently Retries Forever

**Why it exists:** Both silent abandonment and infinite retry are forbidden. Every failure path MUST end in either recovery, compensation, or human escalation.

**What problem it prevents:** Lost workflows that no one knows have failed, and stuck workflows that consume resources indefinitely without progress.

**Example:** After 3 retries with exponential backoff, the Retry & Compensation Manager publishes an escalation event and creates a human gate task for the on-call engineer.

**Counter-example:** An agent fails, the retry count increments, and after 100 retries over 48 hours the task is still in `retrying` state with no escalation and no abandonment.

**Consequences of violating it:** Silent failures erode trust — workflows appear in-progress but are stuck. Infinite retries consume resources and block workflow completion indefinitely.

*Reference: RA Section 5.11*

---

### FR3. Saga Compensation for Partial Multi-Step Failures

**Why it exists:** Multi-step workflows (especially Brownfield modernisation) require per-step compensation, not all-or-nothing rollback. A failed increment reverts without touching other increments.

**What problem it prevents:** Partial failures that leave the system in an inconsistent state with no automated path to recovery.

**Example:** Brownfield increment 3 of 7 fails regression verification. Saga compensation reverts increment 3 only. Increments 1, 2, and 4–7 are unaffected.

**Counter-example:** Increment 3 fails and the entire 7-increment modernisation workflow is marked `Failed` with no per-increment rollback.

**Consequences of violating it:** A single increment failure abandons all prior progress. Brownfield workflows become high-risk all-or-nothing propositions. Engineers avoid multi-increment strategies.

*Reference: RA Section 5.11; Section 11.2*

---

### FR4. Automatic Rollback Where Speed of Reversal Outweighs False-Positive Cost

**Why it exists:** In defect resolution, a rollback snapshot is taken at deploy time. If monitored metrics do not recover within N minutes, rollback triggers without waiting for a human. This is the one workflow where automatic reversal is constitutional.

**What problem it prevents:** Human-gated rollback during active P1 incidents where every minute of non-recovery extends the outage.

**Example:** Hotfix deployed. Monitoring shows error rate unchanged after 10 minutes. `RollbackTriggered` fires automatically. Prior release artifact is restored.

**Counter-example:** A failed hotfix waits for on-call engineer approval before rollback, adding 20 minutes to the outage while the engineer is paged, logs in, and reviews.

**Consequences of violating it:** P1 MTTR is bounded by human response time, not recovery time. Automatic safety mechanisms that SRE teams depend on are absent. On-call engineers bear full rollback responsibility under time pressure.

*Reference: RA Section 11.3*

---

## Cost Principles

### CO1. Not Every Task Needs the Most Capable Model

**Why it exists:** The Model Router classifies each dispatched task by complexity and risk. Routine tasks and critical tasks MUST NOT cost the same or use the same model tier.

**What problem it prevents:** Uniform model assignment that either bankrupts the inference budget or under-powers critical decisions.

**Example:** Test scaffold generation → low tier. Security architecture review → high tier. Both are deliberate, documented routing decisions.

**Counter-example:** All tasks are routed to the highest-capability model because "quality is paramount."

**Consequences of violating it:** Inference costs scale unsustainably with workflow volume. Budget constraints force platform shutdown rather than intelligent tiering. Cost optimisation has no lever.

*Reference: RA Section 5.10*

---

### CO2. Per-Tenant Quota Is a First-Class Control

**Why it exists:** Per-tenant quota on the Model Router prevents one tenant from consuming disproportionate inference resources.

**What problem it prevents:** Unbounded inference spend by a single tenant that degrades service or exhausts budget for all others.

**Example:** Tenant A has a quota of 50,000 tokens/hour. When exceeded, tasks are queued (not dropped) with a clear backpressure signal.

**Counter-example:** All tenants draw from a shared, unmonitored inference budget. Tenant A's bulk modernisation workflow consumes 80% of the monthly budget in one day.

**Consequences of violating it:** Unpredictable platform costs. Unable to offer differentiated service tiers. Budget overruns with no attribution to the responsible tenant.

*Reference: RA Section 5.8; Section 5.10*

---

### CO3. Cost Attribution Follows Task and Workflow Correlation

**Why it exists:** Every inference call is attributable to a task_id and workflow_run_id, enabling per-workflow, per-tenant, and per-agent cost analysis.

**What problem it prevents:** Aggregate inference bills with no breakdown by workflow type, agent, tenant, or team — making cost optimisation impossible.

**Example:** A query for `workflow_type: brownfield-modernization` across all tenants returns total inference cost, average cost per workflow run, and cost by agent.

**Counter-example:** The monthly inference bill is a single number with no attribution metadata.

**Consequences of violating it:** Cost optimisation is guesswork. Expensive workflows cannot be identified. Tenant chargeback is impossible. Model tier decisions lack data.

*Reference: RA Section 5.10; Section 8 — Task Schema*

---

## Versioning Principles

### V1. Platform Versioning Is Semantic and Contract-Centric

**Why it exists:** Platform versions track contract stability, not feature counts. A major version change means a breaking contract change. A minor version means additive capability. A patch means correction without contract impact.

**What problem it prevents:** Version numbers that communicate nothing about compatibility, forcing consumers to test every upgrade against every integration.

**Example:** Platform v1.1.0 adds the `SecurityScanCompleted` event type (additive, minor). Platform v2.0.0 changes the Agent Contract's `capabilities` field from `string[]` to a structured object (breaking, major).

**Counter-example:** Platform v47.3.1 ships with no documented contract changes and no compatibility matrix.

**Consequences of violating it:** Upgrade risk is unknown. Agent developers cannot plan for compatibility. Enterprise adoption is blocked by upgrade uncertainty.

---

### V2. Agents Declare Their Contract Version at Registration

**Why it exists:** The Agent Registry records which contract version an agent was built against, enabling the platform to validate compatibility before dispatch.

**What problem it prevents:** Silent incompatibility where an agent built for v1.0 is dispatched by a v2.0 platform with different schema expectations.

**Example:** An agent registers with `contract_version: "1.0"`. The platform's Agent Selector validates compatibility before dispatch and rejects registration if the contract version is unsupported.

**Counter-example:** An agent registers with no version information. The platform dispatches tasks and the agent fails at runtime due to schema mismatch.

**Consequences of violating it:** Runtime failures instead of registration-time validation. Debugging contract mismatches requires inspecting failed task payloads. Agent upgrades are trial-and-error.

---

### V3. Workflow Templates Are Independently Versioned

**Why it exists:** Each workflow template (Greenfield, Brownfield, Defect Resolution, etc.) has its own version lifecycle independent of the platform version and independent of other workflow templates.

**What problem it prevents:** Platform version bumps forcing workflow template changes, or one workflow template change affecting all others.

**Example:** `greenfield-v2.0` adds a security gate. `brownfield-v1.3` is unaffected. Both run on platform v2.1.0.

**Counter-example:** Platform v2.0 ships with updated workflow templates that break in-flight runs across all workflow types.

**Consequences of violating it:** Workflow changes cannot be rolled out incrementally. One workflow type's evolution blocks all others. In-flight runs are disrupted by unrelated template changes.

---

## Deprecation Policy

### DP1. Deprecation Requires a Decision Record and a Migration Path

**Why it exists:** Nothing is removed from the platform without explicit documentation of what is being deprecated, why, what replaces it, and how existing consumers migrate.

**What problem it prevents:** Silent removal of contract fields, event types, or agent capabilities that breaks existing integrations without warning.

**Rule:** A deprecation MUST include: (1) a Decision Record, (2) the deprecated element, (3) the replacement, (4) a migration guide, (5) a minimum support window of two platform minor versions, and (6) runtime warnings emitted during the support window.

**Example:** Agent Contract field `cost_class` enum value `medium` is deprecated in v1.3.0, replaced by structured `cost_profile` object. Migration guide published. `medium` continues to function with deprecation warnings until v1.5.0. Removed in v2.0.0.

**Counter-example:** `cost_class: medium` stops working in v1.3.0 with no warning, no migration guide, and no Decision Record.

**Consequences of violating it:** Agent registrations break on upgrade. Workflow runs fail on deprecated event types. Enterprise consumers cannot plan upgrades. Trust in platform stability is destroyed.

---

### DP2. Breaking Changes Require a Major Platform Version

**Why it exists:** Any change that breaks an existing contract, event envelope, or workflow template compatibility MUST be introduced in a major version.

**What problem it prevents:** Breaking changes smuggled into minor or patch releases that consumers deploy automatically without compatibility testing.

**Rule:** Major version increment is mandatory for: contract field removal, event envelope modification, workflow state machine breaking changes, and registry schema breaking changes.

**Example:** Removing the `approval_required` boolean from the Agent Contract is a v2.0.0 change, announced in v1.x deprecation warnings.

**Counter-example:** The `approval_required` field is removed in v1.4.0 (a minor release) because "no agents use it anymore."

**Consequences of violating it:** Automatic upgrades break production workflows. Semantic versioning becomes meaningless. Enterprise change-management processes are bypassed.

---

## Decision Record Policy

### DR1. Every Constitutional Amendment Requires a Decision Record

**Why it exists:** Principles in this constitution are immutable by default. Changing them requires explicit, recorded justification — not informal consensus or undocumented decisions.

**Rule:** A Decision Record MUST contain: (1) title, (2) date, (3) status (proposed / accepted / deprecated / superseded), (4) context, (5) decision, (6) constitutional principle affected, (7) consequences, and (8) migration path.

**Example:** DR-001: "Add automatic rollback as a constitutional principle for defect resolution workflows" — accepted, affects FR4, migration path: existing defect resolution templates gain automatic rollback configuration with opt-in during support window.

**Counter-example:** A team meeting concludes "we should let agents call each other for performance" and implements direct agent calls without a Decision Record.

**Consequences of violating it:** Constitutional principles erode through undocumented exceptions. Contributors cannot distinguish intentional design from accidental drift. The constitution becomes aspirational rather than enforceable.

---

### DR2. Decision Records Are Immutable Once Accepted

**Why it exists:** An accepted Decision Record is a historical fact. It is superseded by a new record, never edited in place.

**What problem it prevents:** Retroactive rewriting of decision rationale to match outcomes, destroying the audit trail of platform evolution.

**Rule:** To change a decision, create a new Decision Record that references and supersedes the prior record. The prior record's status changes to `superseded` — its content is not modified.

**Example:** DR-005 supersedes DR-002. DR-002's status is updated to `superseded`. DR-002's original text remains unchanged.

**Counter-example:** DR-002 is edited in place to reflect a changed decision, with no record of the original rationale.

**Consequences of violating it:** Decision history is unreliable. Contributors cannot learn from past reasoning. "Why did we decide this?" has no trustworthy answer.

---

### DR3. Decision Records Are Public to All Platform Contributors

**Why it exists:** Platform decisions affect every contributor. Decision Records are visible to all contributors, not restricted to architecture teams or leadership.

**Rule:** Decision Records are stored in the platform repository, indexed, and searchable. No Decision Record is confidential.

**Example:** An engineer questioning why agents cannot call agents finds DR-003, which documents the O(n²) coupling analysis and the event-mediated alternative.

**Counter-example:** Key architectural decisions are made in private meetings and communicated only through verbal tradition.

**Consequences of violating it:** Contributors follow principles without understanding rationale. New contributors repeat resolved debates. Institutional knowledge is lost when individuals leave.

---

## Anti-patterns

### AP1. The Orchestrator That Does Everything

**What it is:** Expanding the Orchestrator to include code generation, testing, scanning, or other specialist capabilities "for simple cases" or "to reduce latency."

**Why it is forbidden:** Violates A2 (Orchestrator plans, never executes). The orchestrator accumulates specialist logic that must be updated with every domain change.

**Consequence:** Every specialist capability change requires an orchestrator release. The core becomes the bottleneck. The "plans, never executes" principle is destroyed by a thousand exceptions.

---

### AP2. The Agent Social Network

**What it is:** Agents that call each other directly, maintain awareness of other agents, or embed knowledge of the workflow graph in their logic.

**Why it is forbidden:** Violates A1 (Agents never call agents) and AG4 (Agents publish results, never command). Creates O(n²) coupling.

**Consequence:** Adding agent N requires updating agents 1 through N-1. The platform's fundamental scalability claim is false. A five-agent pilot and a fifty-agent enterprise deployment have fundamentally different architectures.

---

### AP3. The Shared Brain

**What it is:** A shared mutable context store that agents read from and write to without explicit task-scoped context packets. Ambient state that all agents can access at any time.

**Why it is forbidden:** Violates M1 (Working context and long-term memory are strictly separated) and M2 (Working context passes explicitly).

**Consequence:** Concurrent workflows corrupt each other's state. Working context leaks into long-term memory. Agents produce inconsistent output. Debugging requires understanding ambient shared state.

---

### AP4. The Autopilot

**What it is:** Workflows that proceed through approval gates without recorded human decisions. Auto-approval after timeout. System-generated approvals. Emergency bypass flags.

**Why it is forbidden:** Violates H1, H2, H3, and H4 (Human-in-the-loop principles). Transforms "humans approve, agents propose" into "agents approve, humans observe."

**Consequence:** Unreviewed changes reach production. Compliance audits fail. The human-in-the-loop principle becomes cosmetic. Incident retrospectives have no accountable human.

---

### AP5. The Vendor Lock-In

**What it is:** Agent logic, tool integrations, or platform code that directly references vendor-specific APIs, model names, or cloud primitives without registry or normalisation abstraction.

**Why it is forbidden:** Violates P4 (Vendor neutrality by construction), PL2 (Tool response normalisation), and MI3 (Model endpoints are configuration).

**Consequence:** Toolchain or model changes require rewriting agent code. Multi-tenant heterogeneity requires agent forks. The platform's reusability claim is false.

---

### AP6. The Memory Dump

**What it is:** Automatically writing every agent output to long-term memory. Treating the vector store as a log file. Performing blind similarity search without metadata filtering.

**Why it is forbidden:** Violates M3 (Long-term memory is written deliberately), M4 (Memory retrieval is filtered), and AI3 (AI output is never institutional memory by default).

**Consequence:** Memory store fills with unverified noise. Retrieval returns contradictory guidance. Agents cannot distinguish authoritative knowledge from discarded proposals. Output quality degrades over time.

---

### AP7. The Governance Theatre

**What it is:** Building governance dashboards, policy libraries, and compliance reports before sufficient real workflow history exists. Creating the appearance of governance without data to govern.

**Why it is forbidden:** Violates G2 (Governance requires data, not dashboards).

**Consequence:** Leadership makes decisions based on empty charts. Policies are written for hypothetical scenarios. Engineers ignore governance tooling. Real governance problems are masked by ceremonial tooling.

---

### AP8. The Silent Failure

**What it is:** Agent failures that are neither retried, nor compensated, nor escalated. Workflows that appear in-progress but are stuck. Tasks that retry indefinitely without escalation.

**Why it is forbidden:** Violates FR1, FR2 (Three escalating recovery tiers; never silently give up or retry forever).

**Consequence:** Workflows are lost without notification. Resources are consumed by infinite retry loops. Engineers lose trust in workflow durability. On-call teams discover stuck workflows days later.

---

### AP9. The Monolith Security Module

**What it is:** Merging RBAC, agent policy enforcement, and secrets management into a single security service or module.

**Why it is forbidden:** Violates S1 (Three distinct security controls, never merged).

**Consequence:** Permission changes have unintended side effects across control domains. Credential leaks expose broader access. Security audits cannot isolate which control failed. Blast radius of any security change is maximal.

---

### AP10. The Per-Tenant Fork

**What it is:** Deploying separate platform instances per tenant to accommodate different toolchains, policies, or customisations instead of using registry configuration and namespace isolation.

**Why it is forbidden:** Violates MT3 (One platform deployment, many isolated tenants) and P4 (Vendor neutrality by construction).

**Consequence:** Platform improvements must be deployed N times. Version drift is guaranteed. Operational cost scales linearly with tenant count. The multi-tenancy investment is wasted.

---

## Non-goals

### NG1. The Platform Is Not a System of Record

The platform does not replace source control, issue trackers, CI/CD pipelines, security scanners, or infrastructure management tools. It orchestrates them. If the platform is maintaining the authoritative copy of code, tickets, or deployment state, the architecture has been violated.

*Reference: RA Section 2*

---

### NG2. The Platform Is Not Fully Autonomous

There is no code path, configuration, or operational procedure that permits workflows to proceed through safety, cost, or compliance gates without recorded human decisions. "Fully autonomous" framing is explicitly ruled out wherever safety, cost, or compliance is at stake.

*Reference: RA Section 1, Principle 4*

---

### NG3. The Platform Does Not Guarantee Agent Quality

The platform scales the capacity to coordinate work. It does not scale the judgement quality of any individual agent. A weak model does not improve because the platform around it is well-architected. Model capability and platform capability are separate investments.

*Reference: RA Section 13 — "The honest limit"*

---

### NG4. The Platform Is Not a Chatbot

The platform is a workflow orchestration engine with specialist agents, approval gates, audit trails, and durable state machines. It is not a conversational interface that generates code on demand without workflow context, governance, or accountability.

*Reference: RA Sections 3, 5, 11*

---

### NG5. The Platform Does Not Self-Schedule Work

Agents propose. Humans (or human-defined policies) decide what enters a sprint, what gets prioritised, and what gets approved. The platform does not autonomously decide to reduce technical debt, migrate legacy systems, or remediate security findings without human initiation and approval.

*Reference: RA Section 11.4 — Technical Debt Reduction workflow*

---

### NG6. The Platform Is Not a Replacement for Engineering Judgement

Workflow gates, approval checkpoints, and audit trails exist to support engineering judgement — not to replace it. The platform provides proposals, context, and records. Humans provide decisions, prioritisation, and accountability.

*Reference: RA Section 1, Principle 4; Section 5.6*

---

### NG7. The Platform Does Not Optimise for Demo Speed

The staged implementation roadmap (Section 14) deliberately builds the platform spine before agents, tenancy before multi-team onboarding, and governance after real data exists. Shortcuts that skip stages produce demos, not platforms.

*Reference: RA Section 14*

---

### NG8. The Platform Is Not Cloud-Agnostic at the Infrastructure Layer

Vendor-neutral at the platform layer means portable primitives at the infrastructure layer — the same containers deploy on different clouds with configuration changes, not architecture changes. Claiming cloud-agnosticism while embedding cloud-specific implementations is a non-goal misrepresentation.

*Reference: RA Section 12*

---

## Document History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 27 June 2026 | Initial constitution derived from Reference Architecture v1.0 |

---

*This document is the immutable engineering constitution of the Agentic Engineering Platform. It is derived from and subordinate to the Reference Architecture v1.0 as source of truth. In case of apparent conflict between this constitution and the reference architecture, the reference architecture governs until a Decision Record amends this constitution.*
