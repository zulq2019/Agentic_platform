# Domain Interaction

**Status:** Living document  
**Version:** 1.0  
**Last updated:** 29 June 2026

---

## Principle

Studios **never call each other directly**. Collaboration is always **mediated by Platform Core**: Event Bus events, registry lookups, workflow state transitions, memory reads, and policy checks ([CONSTITUTION.md](../../CONSTITUTION.md) A1, AR4).

Sequence and API detail live in PI `SEQUENCE_DIAGRAMS.md` files and [ARCHITECTURE.md](../../ARCHITECTURE.md). This document describes **product-level interaction patterns** only.

---

## Interaction Topology

```mermaid
flowchart TB
    subgraph RS[Requirements Studio]
        RA[requirement-agent]
    end

    subgraph AS[Architecture Studio]
        AA[architecture-agent]
    end

    subgraph DS[Development Studio]
        BA[backend-agent]
    end

    subgraph TS[Testing Studio]
        TA[testing-agent]
    end

    subgraph SS[Security Studio]
        SA[security-agent]
    end

    subgraph RLS[Release Studio]
        REA[release-agent]
    end

    subgraph IM[Integration Marketplace]
        TR[Tool Registry]
    end

    subgraph PC[Platform Core]
        OR[Orchestrator / Workflow Engine]
        EB[(Event Bus)]
        AR[Agent Registry]
        MR[Model Router]
        MS[Memory Service]
        PE[Policy Engine]
        AU[Audit]
    end

    OR -->|TaskCreated| EB
    EB --> AR
    AR -->|dispatch| RA & AA & BA & TA & SA & REA
    RA & AA & BA & TA & SA & REA -->|capability tag| TR
    BA & AA -->|tier request| MR
    AA -->|read context| MS
    RA & BA & TA -->|pre-check| PE
    RA & BA & TA & SA & REA -->|AgentCompleted| EB
    EB --> AU
    EB --> OR
```

---

## Pattern 1 — Workflow-Orchestrated Studio Handoff

**Scenario:** Greenfield workflow moves from scope → architecture → implementation → test.

```mermaid
sequenceDiagram
    participant WE as Workflow Engine
    participant EB as Event Bus
    participant AR as Agent Registry
    participant Req as Requirements Studio
    participant Arch as Architecture Studio
    participant Dev as Development Studio
    participant Test as Testing Studio

    WE->>EB: TaskCreated (state: Scoped)
    EB->>AR: resolve capability
    AR->>Req: dispatch requirement-agent
    Req->>EB: AgentCompleted (scope doc)
    EB->>WE: advance state

    WE->>EB: TaskCreated (state: Architected)
    AR->>Arch: dispatch architecture-agent
    Arch->>EB: AgentCompleted (ADR)
    EB->>WE: advance state

    WE->>EB: TaskCreated (state: Implemented)
    AR->>Dev: dispatch backend-agent
    Dev->>EB: AgentCompleted (PR URL)
    EB->>WE: gate: approval required

    WE->>EB: TaskCreated (state: Tested)
    AR->>Test: dispatch testing-agent
    Test->>EB: AgentCompleted (test report)
```

**Core services used:** Workflow Engine, Event Bus, Agent Registry, Gate Enforcer (human approval between states — [PI-03](../engineering/implementation-roadmap/PI-03-Provider-Framework/README.md)).

---

## Pattern 2 — Tool Registry (Integration Marketplace)

Studios invoke external systems **only** by capability tag through Tool Registry — never by embedding vendor SDKs in agents ([CONSTITUTION.md](../../CONSTITUTION.md) AP5).

| Studio | Example capability tag | Typical tool |
|--------|------------------------|--------------|
| Requirements Studio | `create-issue` | Jira ([PI-05](../engineering/implementation-roadmap/PI-05-Execution-Framework/README.md)) |
| Development Studio | `create-pull-request` | GitHub |
| Testing Studio | `run-automated-suite` | Katalon / CI CD |
| Security Studio | `scan-repository` | Security scanner |
| Release Studio | `trigger-deployment` | CI/CD pipeline |
| Architecture Studio | `publish-document` | Confluence |

```mermaid
sequenceDiagram
    participant Agent as Studio Agent
    participant AR as Agent Registry
    participant TR as Tool Registry
    participant SEC as Secrets Vault
    participant EXT as External System

    Agent->>AR: request tool by capability tag
    AR->>TR: resolve create-issue
    TR->>SEC: fetch scoped token
    TR->>EXT: normalised API call
    EXT-->>TR: vendor response
    TR-->>Agent: common shape (Tool Contract)
```

---

## Pattern 3 — Model Router (AI Operations + Development)

**Scenario:** Development Studio agents request LLM inference with cost governance.

```mermaid
sequenceDiagram
    participant Dev as backend-agent
    participant RT as Agent Runtime
    participant MR as Model Router
    participant LLM as Model endpoint

    Dev->>RT: execute task (cost_class: high)
    RT->>MR: resolve tier for tenant + cost_class
    MR-->>RT: endpoint + quota OK
    RT->>LLM: inference request
    LLM-->>RT: completion
    RT-->>Dev: result
```

**PI reference:** [PI-02](../engineering/implementation-roadmap/PI-02-Metadata-Engine/README.md) O3; enterprise quotas in [PI-08](../engineering/implementation-roadmap/PI-08-Solution-Packs/README.md).

---

## Pattern 4 — Memory Service (Architecture + Requirements)

**Scenario:** Architecture Studio retrieves project context; Requirements Studio does not write long-term memory directly.

```mermaid
sequenceDiagram
    participant Arch as architecture-agent
    participant MS as Memory Service
    participant OR as Orchestrator
    participant PW as PostWorkflowWriter

    Arch->>MS: query (tenant_id + filters)
    MS-->>Arch: ranked context chunks
    Arch->>OR: AgentCompleted (ADR in output)
    Note over OR,PW: After workflow gate passes
    OR->>PW: workflow outcome verified
    PW->>MS: deliberate LTM write (provenance)
```

**Constraints:** [PI-04](../engineering/implementation-roadmap/PI-04-Workflow-Framework/README.md) — agents never write LTM directly (M3, AI3).

---

## Pattern 5 — Release Studio + Workflow Engine

**Scenario:** Release Studio orchestrates deployment through workflow states and approval gates.

```mermaid
sequenceDiagram
    participant WE as Workflow Engine
    participant Rel as release-agent
    participant TR as Tool Registry
    participant AP as Approval Service
    participant CI as CI/CD tool

    WE->>Rel: TaskCreated (state: ReleaseCandidate)
    Rel->>TR: create-release capability
    TR->>CI: trigger pipeline
    CI-->>Rel: release artifact ID
    Rel->>WE: AgentCompleted
    WE->>AP: ApprovalRequested (deploy gate)
    AP-->>WE: approval_record
    WE->>Rel: TaskCreated (state: Deployed)
```

---

## Pattern 6 — Administration (Policy + Audit)

Every Studio action passes through policy and emits audit evidence.

```mermaid
sequenceDiagram
    participant Agent as Any Studio agent
    participant PE as Policy Engine
    participant RT as Agent Runtime
    participant AU as Audit Store

    Agent->>PE: evaluate(action, tenant, role)
    alt denied
        PE-->>Agent: deny
        Agent->>AU: PolicyDenied event
    else allowed
        PE-->>RT: allow
        RT->>Agent: execute
        Agent->>AU: AgentCompleted + correlation IDs
    end
```

**PI reference:** [PI-07 Governance](../engineering/implementation-roadmap/PI-07-Platform-Services/README.md).

---

## Pattern 7 — Observability (Cross-Cutting)

All Studios and Core services emit structured logs and OTEL traces with `task_id`, `workflow_run_id`, and `tenant_id`. The **Observability** product domain packages dashboards ([PI-09](../engineering/implementation-roadmap/PI-09-Platform-UX/README.md) Metrics Dashboard; [PI-01](../engineering/implementation-roadmap/PI-01-Platform-Core/README.md) baseline stack).

Studios do not implement bespoke monitoring stacks — they consume Core observability contracts.

---

## Anti-Patterns (Forbidden)

| Anti-pattern | Why forbidden | Constitutional ref |
|--------------|---------------|-------------------|
| `testing-agent` calls `backend-agent` directly | Breaks event mediation | A1 |
| Studio bypasses Tool Registry for GitHub | Vendor lock-in in agent code | AP5 |
| Agent writes to LTM without PostWorkflowWriter | Unaudited memory mutation | M3 |
| Orchestrator generates code or runs tests | Specialist logic in Orchestrator | A2 |
| Cross-tenant memory query without `tenant_id` | Data isolation breach | SR3 |

---

## Further Reading

| Topic | Document |
|-------|----------|
| Container boundaries | [ARCHITECTURE.md](../../ARCHITECTURE.md) |
| Event types | [contracts/event-envelope.schema.json](../../contracts/event-envelope.schema.json) |
| Workflow templates | [workflows/](../../workflows/) |
| PI sequence diagrams | `docs/engineering/implementation-roadmap/PI-*/SEQUENCE_DIAGRAMS.md` |
| Studio summaries | [STUDIO_OVERVIEW.md](./STUDIO_OVERVIEW.md) |
| PI ↔ domain map | [PI_TO_DOMAIN_MAPPING.md](./PI_TO_DOMAIN_MAPPING.md) |
