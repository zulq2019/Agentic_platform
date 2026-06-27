# Agentic Engineering Platform — Vision

**Status:** Living document  
**Version:** 1.0  
**Last updated:** 27 June 2026  
**Derived from:** [CONSTITUTION.md](CONSTITUTION.md) · Reference Architecture v1.0

---

## Product Vision

The Agentic Engineering Platform is the **coordination layer** for enterprise software engineering in the agentic era. It sits between the people who request and approve work, and the external systems that already hold an enterprise's code, tickets, and infrastructure.

It does not replace those systems. It orchestrates them — through specialist agents, durable workflows, non-bypassable human gates, and an immutable audit trail — so that AI-assisted engineering scales from a five-agent pilot to a thousand-engineer organisation without architectural change.

**In one sentence:** A vendor-neutral, multi-agent engineering platform where humans approve, agents propose, and every decision is reconstructable.

---

## Market Positioning

### Category

**Enterprise Agentic SDLC Orchestration Platform** — distinct from:

| Category | What they do | What we do differently |
|----------|--------------|------------------------|
| AI coding assistants (Copilot, Cursor, Cody) | Help individual developers write code faster | Orchestrate multi-agent workflows across the full SDLC with governance |
| CI/CD platforms (GitHub Actions, Azure DevOps) | Automate build/test/deploy pipelines | Coordinate AI agents that propose changes; humans approve before merge |
| Low-code / no-code platforms | Replace development with visual builders | Augment professional engineering teams; no new system of record |
| Agent frameworks (LangChain, AutoGen, CrewAI) | Provide libraries to build agents | Provide a production platform with tenancy, audit, gates, and registries |
| ITSM / workflow tools (ServiceNow, Jira) | Track work items and approvals | Execute agentic workflows with specialist agents and event-driven coordination |

### Positioning Statement

For **enterprise engineering organisations** (100–10,000+ engineers) that need to adopt agentic AI without sacrificing safety, compliance, or toolchain flexibility, the Agentic Engineering Platform is the **orchestration and governance layer** that coordinates specialist agents across Greenfield and Brownfield software engineering workflows. Unlike point AI coding tools or agent frameworks, it provides durable workflows, non-bypassable human approval gates, vendor-neutral tool and model integration, and immutable auditability — at scale.

### Target Market

- **Primary:** Large enterprises (1,000–10,000+ engineers) in regulated or safety-critical industries (healthcare, finance, defence, critical infrastructure)
- **Secondary:** Mid-market engineering organisations (100–1,000 engineers) modernising Brownfield systems with agentic assistance
- **Entry:** Pilot teams (5–50 engineers) proving the platform spine before org-wide rollout

### Build vs Buy Framing

The platform is designed to be **built or evaluated** using the Reference Architecture. It is not a shrink-wrapped product claim — it is a precise blueprint precise enough to build or assess a build-vs-buy decision. Organisations that buy must verify the vendor satisfies the constitutional invariants. Organisations that build follow the staged roadmap.

---

## Personas

### P1. Platform Engineer

**Role:** Builds, deploys, and operates the platform infrastructure.  
**Goals:** Deploy the nine containers reliably. Scale agent replicas. Configure tenancy, secrets, and observability.  
**Pain points:** Fragile agent-to-agent coupling. Undifferentiated heavy lifting for every new integration.  
**Success:** A new specialist agent registers without touching orchestrator code. Platform upgrades do not break existing agents.

### P2. Solution Architect

**Role:** Designs workflow templates, gate placement, and tenant policy for a business unit.  
**Goals:** Map organisational SDLC to platform workflows. Configure approval gates for compliance.  
**Pain points:** AI tools that bypass governance. Workflows that cannot be audited.  
**Success:** Greenfield and Brownfield workflows run on the same platform primitives with different state machines and gates.

### P3. Engineering Team Lead

**Role:** Approves architecture, reviews agent output, merges exceptions.  
**Goals:** Faster delivery without quality regression. Clear accountability for AI-proposed changes.  
**Pain points:** Unreviewed AI code reaching production. No traceability for "why was this merged."  
**Success:** Every merge has a named approver record. Rejected proposals loop back as revision tasks, not dead ends.

### P4. Individual Software Engineer

**Role:** Initiates workflows, reviews agent output, provides feedback at gates.  
**Goals:** Offload routine tasks (test scaffolding, documentation, dependency scans) to agents. Focus on judgement-heavy work.  
**Pain points:** AI tools that require constant babysitting. Context lost between agent runs.  
**Success:** Task-level tracing shows exactly what each agent did. Working context is explicit and complete.

### P5. On-Call / SRE Engineer

**Role:** Approves hotfix deploys, responds to escalated failures, trusts automatic rollback.  
**Goals:** Reduce MTTR for production incidents. AI-assisted root-cause analysis under time pressure.  
**Pain points:** AI tools too slow for P1 incidents. Rollback gated behind human approval during outages.  
**Success:** Defect resolution workflow with time-boxed gates and automatic rollback on non-recovery.

### P6. Security / Compliance Lead

**Role:** Defines policy, audits agent actions, approves security remediation.  
**Goals:** Least-privilege agent access. Immutable audit trail. Named approvers at security gates.  
**Pain points:** Agents with blanket credentials. No reconstructable decision chain.  
**Success:** Query the audit store for any workflow run and receive a complete, attributed chain of agent and human actions.

### P7. CTO / VP Engineering

**Role:** Evaluates build-vs-buy. Funds platform rollout. Reports DORA metrics to leadership.  
**Goals:** Org-wide agentic capability without vendor lock-in. Predictable inference costs. Governance at scale.  
**Pain points:** Pilot success that does not generalise. Unbounded AI spend. Governance theatre.  
**Success:** DORA metrics aggregated across workflows. Per-tenant cost attribution. Platform shape stable after agent catalog is complete.

### P8. Clinical Safety Officer / CAB Chair (Governance)

**Role:** Mandatory approver at release gates in regulated environments.  
**Goals:** Evidence that AI-proposed releases were reviewed by a named authority before deployment.  
**Pain points:** Notification-only "approvals" that do not block workflow.  
**Success:** Workflow cannot proceed past the gate without a recorded `ApprovalGranted` from a named approver.

---

## Use Cases

### UC1. Greenfield Product Development

A product team scopes a new feature. The Requirement Agent produces stories and acceptance criteria. The Product Owner approves scope. The Architecture Agent designs ADRs and API contracts. The Tech Lead approves architecture. Coding, Test, Security, and Review agents execute in sequence. A Senior Engineer merges (exceptions only). The Release Manager gives final sign-off.

**Value:** Cycle time from approved scope to release candidate. Zero unreviewed code in production.

### UC2. Brownfield Modernization

An engineering team modernises a legacy module. Discovery and Dependency Analysis agents characterise the as-built system. The Architect confirms scope and blast radius. Refactor proceeds incrementally — each increment is independently revertible. Regression agents verify against a characterization baseline captured before any change.

**Value:** Behavioural equivalence maintained. No big-bang cutover. Dependency risk trending down.

### UC3. Production Defect Resolution

A P1 alert fires. Triage/Diagnosis and Root-Cause agents correlate telemetry. On-call confirms diagnosis (time-boxed gate). Coding and Test agents produce a minimal hotfix. On-call/Release Manager approves deploy. Automatic rollback if metrics do not recover within N minutes.

**Value:** Reduced MTTR. AI root-cause accuracy tracked. On-call trusts automatic rollback.

### UC4. Security Remediation

A CVE is detected. Security agent integrates with Snyk/SAST. Root-Cause and Coding agents produce a fix. Security Lead approves the fix does not introduce new findings. Time-boxed gates for actively exploited CVEs; open-ended for low severity.

**Value:** Faster CVE closure without introducing regressions.

### UC5. Feature Enhancement

A team enhances an existing product. Architecture Agent runs in impact-analysis mode. Tech Lead confirms the change does not violate architecture invariants. Feature-flagged rollout for high-traffic paths.

**Value:** Safe evolution of live systems with architectural guardrails.

### UC6. Technical Debt Reduction

Discovery and Refactor agents identify and address debt items. Engineering Manager prioritises which items enter a sprint — the platform proposes, it does not self-schedule.

**Value:** Governed debt reduction without autonomous scope creep.

### UC7. Legacy Migration

Discovery and Dependency Analysis agents map the legacy system. Migration agent executes platform-specific migration. Architect approves target-platform mapping before any migration begins. Dual-run period before legacy decommission.

**Value:** Highest-stakes gate enforced. Parallel-run safety net.

### UC8. Release Management

Release-Readiness, Documentation, and Security agents prepare a release candidate. Release Manager and CAB/Clinical Safety Officer sign off. Standard CI/CD rollback informed by upstream workflow rollback strategies.

**Value:** Every workflow feeds into a governed release gate.

---

## Competitive Landscape

| Competitor / Alternative | Strengths | Weaknesses vs our platform | Our differentiation |
|--------------------------|-----------|---------------------------|---------------------|
| **GitHub Copilot / Copilot Workspace** | Deep IDE integration, large user base | Individual developer focus; no multi-agent orchestration; no enterprise gates/audit | Full SDLC workflows, human gates, audit trail, multi-agent coordination |
| **Cursor / Windsurf** | Fast AI-native IDE experience | Not a platform; no workflow engine; no tenancy | Enterprise orchestration layer that works with any IDE |
| **Devin / autonomous coding agents** | Impressive autonomous demos | "Fully autonomous" violates our constitution; no governance model | Humans approve, agents propose — enterprise-safe by design |
| **LangChain / LangGraph / AutoGen** | Flexible agent framework | No production platform concerns (tenancy, audit, gates, registries) | Batteries-included enterprise platform, not a library |
| **Azure DevOps + GitHub Actions + AI extensions** | Existing enterprise adoption | Bolt-on AI; no agent registry; no event-mediated agent coordination | Purpose-built agentic orchestration with plug-in agent model |
| **ServiceNow / Jira + automation** | Workflow and approval maturity | Not agentic; no specialist agent model; no model routing | Agent-native with specialist capabilities and model tier routing |
| **Internal "build our own"** | Tailored to org | O(n²) agent coupling risk; no constitutional guardrails; reinvents platform spine | Reference Architecture + Constitution prevents known failure modes |
| **Consulting-led custom builds** | Domain expertise | Not reusable; vendor-dependent; no registry/contract model | Vendor-neutral, reusable blueprint valid for 10+ years |

---

## Platform Capabilities

### Core Capabilities (Platform Spine)

| Capability | Description |
|------------|-------------|
| Event Bus | Sole inter-container communication path; publish/subscribe |
| Task Queue & Workflow Engine | Durable, persisted task state; saga-style compensation |
| Agent Registry | Dynamic discovery by capability tag |
| Tool Registry | Vendor-neutral external system integration |
| Audit Store | Immutable, append-only decision and action record |

### Orchestration Capabilities

| Capability | Description |
|------------|-------------|
| Workflow State Machine | Eight workflow templates; differing state machines and gates |
| Agent Selector | Capability-based agent dispatch |
| Context Assembler | Explicit working-context packet per task |
| Cost-Aware Dispatcher | Model tier routing by complexity and risk |
| Gate Enforcer | Non-bypassable human approval checkpoints |
| Retry & Compensation Manager | Three-tier failure recovery |

### Agent Capabilities (Specialist Catalog)

Requirement · Architecture · Coding · Test · Security · Review · Release · Discovery · Dependency Analysis · Refactor · Regression · Triage/Diagnosis · Root-Cause · Migration · Release-Readiness · Documentation

### Platform Services

| Service | Description |
|---------|-------------|
| Human Approval Checkpoint | Named-approver records; time-boxed and open-ended gates |
| Shared Memory | Working context (short-lived) + long-term memory (durable, provenance-tracked) |
| Model Router | Per-task, per-tenant model tier routing and quota |
| Policy Engine | Agent action permissions independent of human RBAC |
| Secrets Vault | Short-lived, scoped tokens per tool invocation |
| Observability Backbone | One event stream; engineer, leadership, and governance views |

### Integration Capabilities

Source control · Issue tracking · CI/CD · Security scanning · Infrastructure-as-code · Documentation · Container orchestration — all via Tool Contract with response normalisation.

---

## Success Metrics

### Engineering Effectiveness (DORA)

| Metric | Target (Year 1 pilot) | Target (Year 3 enterprise) |
|--------|----------------------|---------------------------|
| Deployment frequency | 2x pilot baseline | Top-quartile industry |
| Lead time for changes | 30% reduction | 50% reduction |
| Change failure rate | No increase vs baseline | 20% reduction |
| MTTR (incidents) | 25% reduction | 40% reduction |

### Platform Health

| Metric | Target |
|--------|--------|
| Agent registration without orchestrator change | 100% of new agents |
| Workflow completion rate (non-abandoned) | > 95% |
| Audit query completeness (full chain reconstructable) | 100% |
| Gate bypass incidents | 0 |
| Cross-tenant data leakage incidents | 0 |

### AI Quality

| Metric | Target |
|--------|--------|
| % PRs merged without human-found defects | > 85% (pilot), > 90% (enterprise) |
| AI-proposed root cause matches confirmed cause (incidents) | > 70% (pilot), > 85% (enterprise) |
| Rollback false-positive rate (defect resolution) | < 5% |

### Cost

| Metric | Target |
|--------|--------|
| Inference cost per workflow run (attributed) | Tracked and trending down via model routing |
| Cost ratio: routine vs critical tasks | > 3:1 tier differentiation |
| Per-tenant quota compliance | 100% enforcement |

### Adoption

| Metric | Target |
|--------|--------|
| Pilot team satisfaction (NPS) | > 40 |
| Time to register new agent (platform engineer) | < 1 day |
| Time to onboard new tenant | < 1 week (after Stage 2) |
| Teams on platform (5-year) | 50+ teams / 5,000+ engineers |

---

## Five-Year Roadmap

### Year 1 — Prove the Spine (Stages 0–1)

**Theme:** Platform spine + first vertical slice

- Deliver Event Bus, Task Queue, Agent Registry, Tool Registry, Audit Store
- Orchestrator with 2–3 agents (Requirement, Coding, Test) on Greenfield workflow
- One pilot team, one real workflow, real load
- First human approval gates operational
- Basic observability (task-level tracing)

**Exit criteria:** Pilot team completes end-to-end Greenfield workflow with full audit trail. No orchestrator changes required to add a fourth agent.

### Year 2 — Scale Foundations (Stages 2–3)

**Theme:** Multi-tenancy + full agent catalog

- Namespace isolation, per-tenant policy, per-tenant model quota
- Second business unit onboarded
- All eight workflow templates loaded
- Full specialist agent catalog registered
- Brownfield and Defect Resolution workflows operational
- Org-wide observability dashboard (Stage 4 begins)

**Exit criteria:** Two tenants isolated. All workflow types running. Platform shape stops changing.

### Year 3 — Govern at Scale (Stage 4–5)

**Theme:** Enterprise governance + wave rollout

- Policy-as-code library
- Self-serve agent invocation UI
- DORA metrics dashboard for leadership
- Compliance audit export
- 10+ teams onboarded in waves
- Third-party agent registration (partner ecosystem)

**Exit criteria:** Governance backed by real workflow history. 1,000+ engineers active.

### Year 4 — Ecosystem & Optimisation

**Theme:** Partner agents, cost intelligence, advanced workflows

- Agent marketplace / certified partner agents
- Cost optimisation recommendations (model tier analysis)
- Advanced Brownfield: multi-repo modernisation
- Legacy Migration workflow at scale
- Cross-workflow analytics (bottleneck detection)

**Exit criteria:** 50% of agents from registry are third-party. Inference cost per workflow down 30% from Year 2.

### Year 5 — Platform Maturity

**Theme:** 5,000+ engineer scale; platform as industry reference

- 5,000+ engineers across 50+ teams
- Platform shape unchanged since Year 2 (rollout problem, not architecture problem)
- Industry reference implementation published
- Constitutional governance model adopted by contributor community
- Ten-year architecture validity confirmed by third-party review

**Exit criteria:** Adding team 51 requires onboarding, not architecture. Constitution unamended except via Decision Records.

---

## Document Relationships

| Document | Relationship |
|----------|---------------|
| [CONSTITUTION.md](CONSTITUTION.md) | Immutable principles this vision must not violate |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Technical realisation of this vision |
| [ROADMAP.md](./ROADMAP.md) | Phased delivery plan |
| [TASKS.md](./TASKS.md) | Engineering work breakdown |
| [DECISIONS.md](./DECISIONS.md) | Architectural decision records |

---

*This is a living document. Update when market positioning, personas, or roadmap priorities change. Changes that conflict with CONSTITUTION.md require a Decision Record.*
