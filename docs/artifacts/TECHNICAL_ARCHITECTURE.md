# Agentic Engineering Platform — Technical Architecture Diagrams

**Status:** Living document  
**Version:** 1.0  
**Date:** 28 June 2026  
**Authority:** Reference Architecture v1.0 · [CONSTITUTION.md](../../CONSTITUTION.md) · [ARCHITECTURE.md](../ARCHITECTURE.md)  
**Audience:** Platform engineers, solution architects, CTOs, Fortune 500 enterprise evaluators

---

## Document Purpose

This document is the single authoritative home for every technical architecture diagram of the Agentic Engineering Platform. It covers all 15 architectural dimensions required for a production-grade enterprise deployment at Fortune 500 scale:

1. [Architecture Overview](#1-architecture-overview)
2. [C4 Level 1 — System Context](#2-c4-level-1--system-context)
3. [C4 Level 2 — Containers](#3-c4-level-2--containers)
4. [C4 Level 3 — Orchestrator Components](#4-c4-level-3--orchestrator-components)
5. [C4 Level 4 — Agent Runtime Internals](#5-c4-level-4--agent-runtime-internals)
6. [Folder Structure](#6-folder-structure)
7. [Microservices Map](#7-microservices-map)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Kubernetes Layout](#9-kubernetes-layout)
10. [Networking Architecture](#10-networking-architecture)
11. [Database Architecture](#11-database-architecture)
12. [Event Flow Architecture](#12-event-flow-architecture)
13. [Memory Architecture](#13-memory-architecture)
14. [Security Architecture](#14-security-architecture)
15. [Observability Architecture](#15-observability-architecture)
16. [Scalability Architecture](#16-scalability-architecture)
17. [High Availability Architecture](#17-high-availability-architecture)
18. [Disaster Recovery Architecture](#18-disaster-recovery-architecture)
19. [API Architecture](#19-api-architecture)
20. [Multi-Tenancy Architecture](#20-multi-tenancy-architecture)
21. [Workflow Engine Architecture](#21-workflow-engine-architecture)
22. [Agent Lifecycle](#22-agent-lifecycle)
23. [Tool Integration Architecture](#23-tool-integration-architecture)
24. [Model Routing Architecture](#24-model-routing-architecture)
25. [SDK Architecture](#25-sdk-architecture)

---

## 1. Architecture Overview

The platform is a **distributed, event-driven, multi-tenant agentic orchestration system** comprising 16 independently deployable microservices. All inter-service communication is event-mediated through Kafka. No service calls another service synchronously except for registry lookups and security checks.

### Service Tier Map

```mermaid
flowchart TB
    subgraph ingress [Ingress Tier]
        AGW[api-gateway]
        AUTH[auth-service]
        RBAC[rbac-service]
    end

    subgraph orchestration [Orchestration Tier]
        ORCH[orchestrator-service]
        WF[workflow-engine]
        TASK[task-engine]
        APPROV[approval-service]
    end

    subgraph runtime [Agent Runtime Tier]
        AR[agent-runtime]
        AREG[agent-registry]
        MR[model-router]
    end

    subgraph platform [Platform Services Tier]
        TR[tool-registry]
        MEM[memory-service]
        AUD[audit-service]
        SEC[secrets-service]
        POL[policy-engine]
        CFG[config-service]
    end

    subgraph bus [Event Bus - Apache Kafka]
        KAFKA[Kafka Cluster]
    end

    subgraph data [Data Tier]
        PG[(PostgreSQL + RLS)]
        RD[(Redis Cluster)]
        VEC[(pgvector)]
        CH[(ClickHouse)]
        VT[(HashiCorp Vault)]
    end

    ingress --> orchestration
    orchestration <-->|pub/sub| KAFKA
    runtime <-->|pub/sub| KAFKA
    platform <-->|pub/sub| KAFKA

    ORCH --> AREG & TR & WF & TASK
    AR --> AREG & TR & MR & MEM & POL & SEC
    AUD --> CH
    MEM --> VEC & RD
    TASK --> PG & RD
    AREG --> PG & RD
    TR --> PG
    CFG --> PG & RD
    AUTH --> PG & RD
    RBAC --> PG
    SEC --> VT
    WF --> PG
```

### Constitutional Invariants Enforced in Architecture

| Invariant | Architectural Enforcement |
|-----------|--------------------------|
| Agents NEVER call agents | NetworkPolicy blocks agent-to-agent TCP; Kafka-only output |
| Orchestrator plans, never executes | Service boundary — no LLM SDK in orchestrator-service |
| New agents plug in via registry | agent-registry is the ONLY extension point |
| Humans approve at every gate | approval-service blocks state transition via GateEnforcer |
| Every decision is reconstructable | audit-service consumes ALL Kafka topics |
| Vendor-neutral by construction | tool-registry + model-router abstract all vendor APIs |

---

## 2. C4 Level 1 — System Context

```mermaid
flowchart TB
    subgraph actors [Human Actors]
        SWE[Software Engineer\ninitiates workflows]
        TL[Tech Lead / Architect\napproves design gates]
        SRE[On-Call / SRE\napproves hotfix gates]
        GOV[CSO / CAB Chair\napproves release gates]
        PE[Platform Engineer\noperates platform]
        TA[Tenant Admin\nconfigures tenant]
    end

    subgraph AEP [Agentic Engineering Platform Boundary]
        GW[API Gateway\nSingle Entry Point]
    end

    subgraph entsystems [Enterprise External Systems]
        GH[Source Control\nGitHub / GitLab / ADO]
        JIRA[Issue Tracker\nJira / ADO Boards]
        CI[CI/CD\nGitHub Actions / Jenkins / ADO Pipelines]
        SEC[Security Scanners\nSnyk / SonarQube / Checkmarx]
        INFRA[Infrastructure\nTerraform / Kubernetes / Azure / AWS]
        DOC[Documentation\nConfluence / Notion]
        IDP[Identity Provider\nEntra ID / Okta / Cognito]
        OBS[Observability\nGrafana / Datadog / Dynatrace]
    end

    SWE -->|REST / WebSocket| GW
    TL -->|Approval UI| GW
    SRE -->|Hotfix Console| GW
    GOV -->|Release Gate UI| GW
    PE -->|Admin API| GW
    TA -->|Tenant Config Portal| GW

    GW -->|scoped Tool Contract - write| GH
    GW -->|scoped Tool Contract - write| JIRA
    GW -->|scoped Tool Contract - write| CI
    GW -->|scoped Tool Contract - read| SEC
    GW -->|scoped Tool Contract - write| INFRA
    GW -->|scoped Tool Contract - write| DOC
    GW -->|OIDC / SAML| IDP
    GW -->|OTLP metrics + traces| OBS
```

> **Key relationships:** Governance actors interact with the platform via **gates, not notifications** — the workflow cannot advance without a recorded decision. External system access is always per a scoped Tool Contract (Section 7, RA), never blanket credentials.

---

## 3. C4 Level 2 — Containers

```mermaid
flowchart TB
    subgraph external [External]
        USER[Users / Actors]
        EXT[External Systems]
    end

    subgraph platform [Platform Boundary - 16 Microservices]
        subgraph ingressTier [Ingress Tier]
            AGW[api-gateway :8080\nKong / custom\nRate limiting, TLS, routing]
            AUTH[auth-service :8081\nFastAPI\nOIDC JWT issuance + validation]
            RBAC[rbac-service :8082\nFastAPI\nRole assignment + permission]
        end

        subgraph orchTier [Orchestration Tier]
            ORCH[orchestrator-service :8090\nFastAPI\nPlanner, dispatcher, gate enforcer]
            WFE[workflow-engine :8091\nFastAPI\nState machine templates + transitions]
            TASK[task-engine :8092\nFastAPI\nDurable task persistence + scheduling]
            APPR[approval-service :8093\nFastAPI\nHuman-in-the-loop gate management]
        end

        subgraph runtimeTier [Agent Runtime Tier]
            AR[agent-runtime :8100\nFastAPI\nAgent execution host]
            AREG[agent-registry :8101\nFastAPI\nCapability-based discovery]
            MR[model-router :8102\nFastAPI\nLLM tier routing + quota]
        end

        subgraph platformTier [Platform Services Tier]
            TR[tool-registry :8110\nFastAPI\nExternal integration resolution]
            MEM[memory-service :8111\nFastAPI\nWorking context + vector memory]
            AUD[audit-service :8112\nFastAPI\nImmutable append-only audit]
            SS[secrets-service :8113\nFastAPI\nVault-backed token issuance]
            POL[policy-engine :8114\nFastAPI\nOPA agent action governance]
            CFG[config-service :8115\nFastAPI\nPer-tenant configuration]
        end

        KAFKA[Apache Kafka\nEvent Bus - Sole inter-service bus]
    end

    subgraph dataTier [Data Tier]
        PG[(PostgreSQL 16\nAurora / Flexible Server\nOLTP + RLS)]
        RD[(Redis 7 Cluster\nCache + Working State)]
        VEC[(pgvector\nLong-Term Memory)]
        CLK[(ClickHouse\nAudit + Analytics\nAppend-only)]
        VLT[(HashiCorp Vault\nSecrets + PKI)]
    end

    USER --> AGW
    AGW --> AUTH & RBAC
    AGW --> ORCH & APPR & AREG & CFG

    ORCH & WFE & TASK & APPR <-->|publish/subscribe| KAFKA
    AR & AUD <-->|publish/subscribe| KAFKA

    ORCH --> AREG & TR & WFE & TASK
    AR --> AREG & TR & MR & MEM & POL & SS
    AUD --> CLK
    MEM --> VEC & RD
    TASK --> PG & RD
    AREG --> PG & RD
    WFE --> PG
    TR --> PG
    CFG --> PG & RD
    AUTH --> PG & RD
    RBAC --> PG
    SS --> VLT

    AR -->|Tool Contracts| EXT
```

---

## 4. C4 Level 3 — Orchestrator Components

> The orchestrator is a **planner and referee, never a player**. No component here writes code, calls an LLM, or executes a tool.

```mermaid
flowchart TB
    subgraph orchService [orchestrator-service]
        subgraph domain [Planner Domain]
            PL[PlannerService\nDecomposes workflow into tasks]
            WSM[WorkflowStateMachine\nLoads template, manages transitions]
            AS[AgentSelector\nQueries registry by capability tag]
            CA[ContextAssembler\nBuilds explicit context packet]
            CAD[CostAwareDispatcher\nClassifies + routes to model tier]
            GE[GateEnforcer\nBlocks transition without approval_record]
            RCM[RetryCompensationManager\n3-tier failure recovery]
        end

        subgraph infra [Infrastructure Layer]
            KC[KafkaClient\nPublishes TaskCreated, StateTransitioned]
            ARC[AgentRegistryClient\nCapability-based lookup]
            TRC[ToolRegistryClient\nCapability resolution]
            MRC[ModelRouterClient\nTier routing]
            APC[ApprovalServiceClient\nGate satisfaction check]
            TASKC[TaskEngineClient\nWrite-before-act persistence]
        end
    end

    subgraph wfEngine [workflow-engine]
        TL[TemplateLoader\nLoads versioned JSON templates]
        SMP[StateMachineProcessor\nPure state transition logic]
        TV[TransitionValidator\nPre-condition checks]
        RS[RollbackStrategist\nPer-workflow rollback logic]
        GC[GateConfigResolver\nOpen-ended vs time-boxed]
    end

    PL --> WSM
    WSM --> AS & CA & CAD & GE & RCM & KC
    AS --> ARC
    CA --> TASKC & MRC
    CAD --> MRC
    GE --> APC
    RCM --> TASKC & KC
    WSM --> SMP
    SMP --> TL & TV & RS & GC
```

---

## 5. C4 Level 4 — Agent Runtime Internals

```mermaid
flowchart TB
    subgraph agentRuntime [agent-runtime - execution host]
        subgraph executor [Executor Layer]
            AE[AgentExecutor\nOrchestrates agent lifecycle]
            AL[AgentLoader\nDynamic import + validation]
            IK[IdempotencyKeyResolver\nPrevents duplicate side-effects on retry]
        end

        subgraph baseClass [Agent Base Class - SDK]
            AB[Agent\nBase class all agents inherit]
            TC[ToolClient\nRequests tools by capability tag]
            MC[MemoryClient\nWorking context + LTM queries]
            EC[EventClient\nPublishes AgentStarted / Completed / Failed]
            RT[RetryHandler\nExponential backoff + jitter]
            SC[SecurityContext\nPolicy check + scoped token]
            OT[OtelInstrumentation\nAuto-traces every agent method]
            LG[StructuredLogger\nJSON + task_id + workflow_run_id]
            MET[MetricsEmitter\nHistogram per agent per operation]
        end

        subgraph contracts [Agent Contract Validation]
            CV[ContractValidator\nValidates at load time]
            INP[InputSchemaValidator]
            OUT[OutputSchemaValidator]
        end
    end

    subgraph externalClients [External Service Clients]
        TREG[ToolRegistryClient]
        MREG[AgentRegistryClient]
        MSVC[MemoryServiceClient]
        PSVC[PolicyEngineClient]
        SSVC[SecretsServiceClient]
        KPROD[KafkaProducer]
        OTEL[OpenTelemetry SDK]
    end

    AE --> AL & IK
    AL --> CV --> INP & OUT
    AE --> AB
    AB --> TC & MC & EC & RT & SC & OT & LG & MET
    TC --> TREG & SSVC
    MC --> MSVC
    EC --> KPROD
    SC --> PSVC & SSVC
    OT --> OTEL
```

---

## 6. Folder Structure

```
agentic-engineering-platform/
│
├── platform/                           # 16 core microservices
│   ├── api-gateway/                    # Kong / custom Go gateway
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── pyproject.toml / go.mod
│   ├── auth-service/                   # OIDC + JWT (FastAPI)
│   ├── rbac-service/                   # Role + permission (FastAPI)
│   ├── orchestrator-service/           # Planner, dispatcher, gate enforcer
│   │   ├── src/
│   │   │   ├── domain/
│   │   │   │   ├── planner.py
│   │   │   │   ├── workflow_state_machine.py
│   │   │   │   ├── agent_selector.py
│   │   │   │   ├── context_assembler.py
│   │   │   │   ├── cost_aware_dispatcher.py
│   │   │   │   ├── gate_enforcer.py
│   │   │   │   └── retry_compensation_manager.py
│   │   │   ├── application/
│   │   │   ├── infrastructure/
│   │   │   └── api/
│   │   ├── tests/
│   │   └── Dockerfile
│   ├── workflow-engine/                # State machine templates
│   ├── task-engine/                    # Durable task queue
│   ├── approval-service/               # Human-in-the-loop gates
│   ├── agent-runtime/                  # Agent execution host
│   ├── agent-registry/                 # Capability-based discovery
│   ├── model-router/                   # LLM tier routing + quota
│   ├── tool-registry/                  # External integration registry
│   ├── memory-service/                 # Working + long-term memory
│   ├── audit-service/                  # Immutable event audit
│   ├── secrets-service/                # Vault-backed token issuance
│   ├── policy-engine/                  # OPA-based agent governance
│   └── config-service/                 # Centralised configuration
│
├── sdk/
│   ├── agent-sdk/                      # Python SDK for building agents
│   │   ├── aep_sdk/
│   │   │   ├── agent.py               # Base Agent class
│   │   │   ├── context.py
│   │   │   ├── events.py
│   │   │   ├── memory.py
│   │   │   ├── tools.py
│   │   │   ├── retry.py
│   │   │   ├── security.py
│   │   │   ├── metrics.py
│   │   │   └── registry.py
│   │   └── pyproject.toml
│   └── tool-sdk/                       # SDK for building tool connectors
│
├── agents/                             # 15 specialist agents (Phase 4)
│   ├── requirement-agent/
│   ├── architecture-agent/
│   ├── discovery-agent/
│   ├── dependency-analysis-agent/
│   ├── backend-agent/
│   ├── frontend-agent/
│   ├── testing-agent/
│   ├── regression-agent/
│   ├── security-agent/
│   ├── performance-agent/
│   ├── documentation-agent/
│   ├── review-agent/
│   ├── release-agent/
│   ├── migration-agent/
│   └── root-cause-agent/
│
├── tools/                              # 11 external connectors (Phase 7)
│   ├── github-tool/
│   ├── azure-devops-tool/
│   ├── gitlab-tool/
│   ├── jira-tool/
│   ├── confluence-tool/
│   ├── sonarqube-tool/
│   ├── snyk-tool/
│   ├── terraform-tool/
│   ├── kubernetes-tool/
│   ├── azure-tool/
│   └── aws-tool/
│
├── workflows/                          # 8 workflow templates
│   ├── greenfield-v1.0.0.json
│   ├── brownfield-v1.0.0.json
│   ├── defect-resolution-v1.0.0.json
│   ├── feature-enhancement-v1.0.0.json
│   ├── security-remediation-v1.0.0.json
│   ├── technical-debt-v1.0.0.json
│   ├── migration-v1.0.0.json
│   └── release-management-v1.0.0.json
│
├── contracts/                          # JSON Schema (Phase 1 — done)
│
├── frontend/                           # React dashboard (Phase 9)
│   └── src/
│       ├── pages/
│       │   ├── WorkflowDesigner/
│       │   ├── AgentRegistry/
│       │   ├── WorkflowMonitor/
│       │   ├── TaskExplorer/
│       │   ├── AuditExplorer/
│       │   ├── MemoryExplorer/
│       │   ├── ApprovalConsole/
│       │   ├── MetricsDashboard/
│       │   └── ConfigPortal/
│       └── components/
│
├── infra/
│   ├── terraform/
│   │   ├── modules/
│   │   │   ├── eks/
│   │   │   ├── aks/
│   │   │   ├── kafka/
│   │   │   ├── postgres/
│   │   │   ├── redis/
│   │   │   ├── pgvector/
│   │   │   ├── clickhouse/
│   │   │   └── vault/
│   │   └── envs/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── prod/
│   ├── k8s/
│   │   ├── base/
│   │   │   ├── namespaces.yaml
│   │   │   ├── network-policies/
│   │   │   └── rbac/
│   │   └── services/           # One folder per service
│   └── helm/
│       └── aep/
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
│
├── observability/
│   ├── grafana/dashboards/
│   ├── prometheus/rules/
│   ├── otel-collector/
│   └── langfuse/
│
├── docs/
│   ├── artifacts/
│   │   └── TECHNICAL_ARCHITECTURE.md   ← this document
│   └── reference/
│
└── .github/workflows/                  # CI/CD (Phase 10)
```

---

## 7. Microservices Map

```mermaid
flowchart LR
    subgraph services [16 Microservices]
        subgraph ing [Ingress - ports 808x]
            AGW[api-gateway\n:8080]
            AUTH[auth-service\n:8081]
            RBAC[rbac-service\n:8082]
        end
        subgraph orch [Orchestration - ports 809x]
            ORCH[orchestrator-service\n:8090]
            WFE[workflow-engine\n:8091]
            TASK[task-engine\n:8092]
            APPR[approval-service\n:8093]
        end
        subgraph rt [Runtime - ports 810x]
            AR[agent-runtime\n:8100]
            AREG[agent-registry\n:8101]
            MR[model-router\n:8102]
        end
        subgraph ps [Platform Services - ports 811x]
            TR[tool-registry\n:8110]
            MEM[memory-service\n:8111]
            AUD[audit-service\n:8112]
            SS[secrets-service\n:8113]
            POL[policy-engine\n:8114]
            CFG[config-service\n:8115]
        end
    end

    subgraph mandatory [Every Service Exposes]
        H[GET /health/live\nGET /health/ready]
        M[GET /metrics\nPrometheus]
        I[GET /info\nversion + contract_version]
    end
```

| Service | Language | Framework | Key Dependency | Purpose |
|---------|----------|-----------|----------------|---------|
| `api-gateway` | Go | Echo | Kong plugins | Rate limiting, routing, TLS |
| `auth-service` | Python | FastAPI | PostgreSQL, Redis | OIDC/JWT |
| `rbac-service` | Python | FastAPI | PostgreSQL | Role + permissions |
| `orchestrator-service` | Python | FastAPI | Kafka, PostgreSQL | Planner, gate enforcer |
| `workflow-engine` | Python | FastAPI | PostgreSQL | State machines |
| `task-engine` | Python | FastAPI | PostgreSQL, Redis | Durable tasks |
| `approval-service` | Python | FastAPI | Kafka, PostgreSQL | Human gates |
| `agent-runtime` | Python | FastAPI | Kafka | Agent execution |
| `agent-registry` | Python | FastAPI | PostgreSQL, Redis | Agent discovery |
| `model-router` | Python | FastAPI | Redis, Config | LLM routing + quota |
| `tool-registry` | Python | FastAPI | PostgreSQL | Tool resolution |
| `memory-service` | Python | FastAPI | pgvector, Redis | Working + LTM |
| `audit-service` | Python | FastAPI | Kafka, ClickHouse | Immutable audit |
| `secrets-service` | Python | FastAPI | HashiCorp Vault | Token issuance |
| `policy-engine` | Python | FastAPI | OPA, PostgreSQL | Agent governance |
| `config-service` | Python | FastAPI | PostgreSQL, Redis | Configuration |

---

## 8. Deployment Architecture

```mermaid
flowchart TB
    subgraph internet [Public Internet]
        USERS[Users / API Clients]
    end

    subgraph edge [Edge Layer]
        CF[CloudFlare / Azure Front Door\nDDoS protection, WAF, CDN, TLS termination]
    end

    subgraph lb [Load Balancer Layer]
        NLB[Network Load Balancer\nL4 TCP/TLS passthrough]
    end

    subgraph k8sCluster [Kubernetes Cluster - AKS / EKS]
        subgraph ingressNS [Namespace: aep-ingress]
            NGINX[NGINX Ingress Controller]
            KONG[Kong API Gateway\nDP nodes - 3+ replicas]
        end

        subgraph platformNS [Namespace: aep-platform]
            subgraph orchPods [Orchestration Tier\nHPA: 3-20 replicas]
                O1[orchestrator-service]
                O2[workflow-engine]
                O3[task-engine]
                O4[approval-service]
            end
            subgraph agentPods [Agent Runtime Tier\nHPA: 5-200 replicas]
                A1[agent-runtime]
                A2[model-router]
            end
            subgraph platformPods [Platform Services Tier\nHPA: 2-10 replicas]
                P1[tool-registry]
                P2[memory-service]
                P3[audit-service]
                P4[secrets-service]
                P5[policy-engine]
                P6[config-service]
            end
        end

        subgraph agentNS [Namespace: aep-agents]
            AG1[agent pods - dynamically scheduled]
        end

        subgraph obsNS [Namespace: aep-observability]
            PROM[Prometheus]
            GRAF[Grafana]
            OTELC[OTEL Collector]
            LOKI[Loki]
            TEMPO[Tempo]
        end
    end

    subgraph managedData [Managed Data Services]
        PG2[(Aurora PostgreSQL\nMulti-AZ)]
        RD2[(Redis Enterprise\nCluster mode)]
        KFK[Kafka - MSK / Event Hubs\n3 brokers, RF=3]
        VEC2[(pgvector on RDS\nRead replicas)]
        CLK2[(ClickHouse Cloud\nAudit + Analytics)]
        VLT2[(HCP Vault\nEnterprise HA)]
    end

    USERS --> CF --> NLB --> NGINX --> KONG
    KONG --> orchPods & agentPods & platformPods
    orchPods <-->|pub/sub| KFK
    agentPods <-->|pub/sub| KFK
    platformPods --> PG2 & RD2 & VEC2 & CLK2 & VLT2
```

---

## 9. Kubernetes Layout

```mermaid
flowchart TB
    subgraph cluster [Kubernetes Cluster]
        subgraph nodePools [Node Pools]
            SYS[system-pool\nm5.large x3\ntaint: CriticalAddonsOnly]
            PLAT[platform-pool\nm5.xlarge x6\norchestration + platform services]
            AGENT[agent-pool\nc5.2xlarge x10-50\nagent-runtime HPA target]
            DATA[data-pool\nr5.2xlarge x3\nself-hosted Kafka/Redis if needed]
        end

        subgraph namespaces [Namespaces]
            NS1[aep-ingress\nKong, NGINX]
            NS2[aep-platform\nall 16 services]
            NS3[aep-agents\ndynamic agent pods]
            NS4[aep-observability\nPrometheus, Grafana, OTEL]
            NS5[aep-data\nKafka, Redis if self-hosted]
        end

        subgraph perService [Per-Service Resources]
            DEP[Deployment\nmin 2 replicas\nrollingUpdate: maxUnavailable 1]
            HPA2[HorizontalPodAutoscaler\nCPU + custom Kafka lag metric]
            PDB[PodDisruptionBudget\nminAvailable: 1]
            SVC[Service\nClusterIP]
            CM[ConfigMap\nnon-secret config]
            NP[NetworkPolicy\ndeny-all default\nexplicit allow per pair]
            SM[ServiceMonitor\nPrometheus scrape]
        end
    end

    SYS --> NS1 & NS4
    PLAT --> NS2
    AGENT --> NS3
    DATA --> NS5
```

### Key HPA Configurations

```
agent-runtime:
  minReplicas: 5
  maxReplicas: 200
  metric: kafka_consumer_lag{topic="aep.task.created"} < 100
  scaleDown.stabilizationWindowSeconds: 300

orchestrator-service:
  minReplicas: 3
  maxReplicas: 20
  metric: cpu utilization < 70%

audit-service:
  minReplicas: 2
  maxReplicas: 10
  metric: kafka_consumer_lag{topic="aep.audit.events"} < 1000
```

---

## 10. Networking Architecture

```mermaid
flowchart TB
    subgraph external [External]
        WAN[Internet - TCP 443]
    end

    subgraph edge2 [Edge - Layer 7]
        WAF[WAF + DDoS\nCloudFlare / Azure FD]
        CDN[CDN Static Assets]
    end

    subgraph cluster2 [Kubernetes Internal]
        subgraph ingLayer [Ingress Layer - Layer 7]
            INGRESSCTRL[NGINX Ingress Controller\nTLS 1.3 termination]
            KONGDP[Kong Data Plane\nAuth, rate-limit, transform]
        end

        subgraph mesh [Istio Service Mesh - mTLS all East-West]
            SVC1[orchestrator-service]
            SVC2[agent-runtime]
            SVC3[tool-registry]
            SVC4[audit-service]
        end

        subgraph kafkaNet [Kafka Network - SASL_TLS]
            KFK2[Kafka Cluster\nSASL/TLS, per-service ACLs]
        end
    end

    subgraph dataNet [Data Network - Private Subnet]
        PG3[(PostgreSQL - VPC private)]
        RD3[(Redis - VPC private)]
        VLT3[(Vault - VPC private)]
    end

    WAN --> WAF --> INGRESSCTRL --> KONGDP
    KONGDP --> SVC1 & SVC2 & SVC3 & SVC4
    SVC1 & SVC2 --> KFK2
    SVC3 & SVC4 --> PG3 & RD3 & VLT3
```

### Network Policy Matrix (critical rules)

| Source Service | Destination | Protocol | Allowed |
|----------------|-------------|----------|---------|
| `agent-runtime` | `orchestrator-service` | TCP | ❌ Event bus only |
| `agent-runtime` | `agent-runtime` | Any | ❌ Agents never call agents |
| `agent-runtime` | Kafka | TCP 9092 | ✅ |
| `agent-runtime` | `tool-registry` | TCP 8110 | ✅ (capability lookup) |
| `agent-runtime` | `policy-engine` | TCP 8114 | ✅ (action check) |
| `agent-runtime` | `secrets-service` | TCP 8113 | ✅ (token issuance) |
| `orchestrator-service` | `agent-runtime` | Any | ❌ Event bus only |
| `orchestrator-service` | Kafka | TCP 9092 | ✅ |
| `orchestrator-service` | `agent-registry` | TCP 8101 | ✅ |
| `orchestrator-service` | `workflow-engine` | TCP 8091 | ✅ |
| Any | Vault directly | Any | ❌ Via `secrets-service` only |

---

## 11. Database Architecture

### PostgreSQL — Schema Layout

```mermaid
erDiagram
    WORKFLOW_RUNS {
        uuid workflow_run_id PK
        text tenant_id FK
        text workflow_type
        text workflow_template_version
        text current_state
        timestamp started_at
        timestamp completed_at
        jsonb metadata
    }

    TASKS {
        uuid task_id PK
        uuid workflow_run_id FK
        text tenant_id FK
        text assigned_agent_id
        text state
        jsonb context
        int retry_count
        jsonb approval_record
        text model_tier
        timestamp created_at
        timestamp updated_at
    }

    AGENTS {
        text agent_id PK
        text tenant_id FK
        jsonb capabilities
        text input_schema
        text output_schema
        jsonb required_tools
        text cost_class
        bool approval_required
        text idempotency_key_strategy
        text contract_version
        bool active
        timestamp registered_at
    }

    TOOLS {
        text tool_id PK
        text tenant_id FK
        jsonb capability_tags
        text auth_strategy
        text scope
        jsonb rate_limit_policy
        text response_normaliser
        text contract_version
        bool active
    }

    APPROVAL_RECORDS {
        uuid approval_id PK
        uuid task_id FK
        text tenant_id FK
        text gate_id
        text approver
        text decision
        jsonb reviewed_artifacts
        text feedback
        timestamp decided_at
    }

    WORKFLOW_RUNS ||--o{ TASKS : contains
    TASKS ||--o| APPROVAL_RECORDS : has
    WORKFLOW_RUNS }o--|| AGENTS : uses
```

### Row-Level Security Policy (applied to every table)

```sql
-- Every table has this policy — no exceptions
CREATE POLICY tenant_isolation ON orchestrator.workflow_runs
  USING (tenant_id = current_setting('app.current_tenant_id'));

-- Application sets this at connection time:
SET app.current_tenant_id = 'tenant-acme-corp';
```

### Redis Key Schema

```
aep:{tenant_id}:ctx:{task_id}           TTL 24h    Working context packet
aep:{tenant_id}:agent:{agent_id}:hb     TTL 30s    Agent heartbeat
aep:{tenant_id}:sess:{session_id}       TTL 8h     User session
aep:{tenant_id}:quota:{tier}:tokens     TTL 1h     Model quota window
aep:{tenant_id}:rl:{tool_id}:{min}      TTL 60s    Tool rate limit
aep:lock:{resource_id}                  TTL 30s    Distributed lock (Redlock)
```

### ClickHouse — Audit Store

```sql
-- Append-only. No UPDATE. No DELETE. Ever.
CREATE TABLE audit.events
(
    event_id         UUID,
    event_type       LowCardinality(String),
    tenant_id        LowCardinality(String),
    task_id          UUID,
    workflow_run_id  UUID,
    emitted_by       String,
    payload          String,     -- JSON
    timestamp        DateTime64(3),
    date             Date MATERIALIZED toDate(timestamp)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (tenant_id, workflow_run_id, timestamp)
TTL date + INTERVAL 7 YEAR;
```

### pgvector — Long-Term Memory

```sql
CREATE TABLE memory.entries (
    memory_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      TEXT NOT NULL,
    source_type    TEXT NOT NULL CHECK (source_type IN ('standard','adr','incident','codebase')),
    content        TEXT NOT NULL,
    embedding      vector(1536),
    recency_weight FLOAT NOT NULL DEFAULT 1.0,
    provenance     JSONB NOT NULL,    -- {workflow_run_id, task_id, written_by}
    metadata       JSONB,
    created_at     TIMESTAMPTZ DEFAULT now()
);
-- IVFFlat index for ANN search
CREATE INDEX ON memory.entries USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- Composite index for filtered queries
CREATE INDEX ON memory.entries (tenant_id, source_type, recency_weight DESC);
-- Row-Level Security
ALTER TABLE memory.entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON memory.entries
  USING (tenant_id = current_setting('app.current_tenant_id'));
```

---

## 12. Event Flow Architecture

### Core Event Topology (Kafka Topics)

```mermaid
flowchart LR
    subgraph producers [Event Producers]
        ORCH2[orchestrator-service]
        AR2[agent-runtime]
        APPR2[approval-service]
        TASK2[task-engine]
    end

    subgraph topics [Kafka Topics - partitioned by tenant_id]
        T1[aep.task.created\n24 partitions]
        T2[aep.agent.started\n24 partitions]
        T3[aep.agent.completed\n24 partitions]
        T4[aep.agent.failed\n24 partitions]
        T5[aep.approval.requested\n12 partitions]
        T6[aep.approval.granted\n12 partitions]
        T7[aep.approval.denied\n12 partitions]
        T8[aep.state.transitioned\n24 partitions]
        T9[aep.rollback.triggered\n12 partitions]
        T10[aep.audit.events\n48 partitions]
        DLQ[aep.dlq\n12 partitions]
    end

    subgraph consumers [Event Consumers]
        AR3[agent-runtime\nconsumes: task.created]
        ORCH3[orchestrator-service\nconsumes: agent.completed\nagent.failed\napproval.granted\napproval.denied]
        AUD2[audit-service\nconsumes: ALL topics]
        APPR3[approval-service\nconsumes: approval.requested]
        OBS2[observability\nconsumes: state.transitioned]
    end

    ORCH2 --> T1 & T5 & T8
    AR2 --> T2 & T3 & T4
    APPR2 --> T6 & T7
    TASK2 --> T8

    T1 --> AR3
    T3 & T4 & T6 & T7 --> ORCH3
    T1 & T2 & T3 & T4 & T5 & T6 & T7 & T8 & T9 --> AUD2
    T5 --> APPR3
    T8 --> OBS2
    T4 -->|retries exhausted| DLQ
```

### End-to-End Task Lifecycle

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant ORCH4 as orchestrator-service
    participant TASK3 as task-engine
    participant KAFKA2 as Kafka
    participant AR4 as agent-runtime
    participant POL2 as policy-engine
    participant TR2 as tool-registry
    participant SS2 as secrets-service
    participant APPR4 as approval-service
    participant AUD3 as audit-service

    UI->>ORCH4: POST /api/v1/workflows
    ORCH4->>TASK3: persist task (write-before-act)
    TASK3-->>ORCH4: task_id persisted
    ORCH4->>KAFKA2: publish TaskCreated
    KAFKA2->>AR4: consume TaskCreated
    KAFKA2->>AUD3: consume → append
    AR4->>POL2: check action permitted
    POL2-->>AR4: permitted
    AR4->>TR2: resolve tool by capability tag
    TR2->>SS2: request scoped token
    SS2-->>TR2: short-lived token (TTL 15m)
    TR2-->>AR4: tool endpoint + token
    AR4->>KAFKA2: publish AgentStarted
    AR4->>AR4: execute agent logic
    AR4->>KAFKA2: publish AgentCompleted
    KAFKA2->>ORCH4: consume AgentCompleted
    ORCH4->>ORCH4: GateEnforcer.check()
    ORCH4->>KAFKA2: publish ApprovalRequested
    KAFKA2->>APPR4: consume → notify approver
    Note over APPR4: Human reviews and decides
    APPR4->>KAFKA2: publish ApprovalGranted
    KAFKA2->>ORCH4: consume ApprovalGranted
    ORCH4->>TASK3: update task state
    ORCH4->>KAFKA2: publish StateTransitioned
    KAFKA2->>AUD3: consume → append all events
```

### Failure and Retry Flow

```mermaid
flowchart TD
    AF[AgentFailed published\nretry_count++] --> RCM2[RetryCompensationManager]

    RCM2 -->|retry_count 1-3\nTransient failure| T1A[Tier 1\nExponential backoff retry\n1s, 2s, 4s + jitter]
    RCM2 -->|retry_count 4-5\nPartial multi-step failure| T2A[Tier 2\nSaga compensation\nPublish RollbackTriggered]
    RCM2 -->|retry_count gt 5\nExhausted| T3A[Tier 3\nHuman escalation\nPublish ApprovalRequested]
    RCM2 -->|retry_count gt 5| DLQ2[Message → DLQ\nfor post-mortem]

    T1A --> Requeue[TaskRequeued\nback to Kafka]
    T2A --> Comp[Compensation events\nper-increment rollback]
    T3A --> EscGate[On-call gate\ntime-boxed SLA]

    style T3A fill:#ff6b6b
    style DLQ2 fill:#ffa07a
```

---

## 13. Memory Architecture

```mermaid
flowchart TB
    subgraph inputs [Inputs to Context Assembler]
        PRIOR[Prior agent outputs\nfrom task history]
        QUERY[LTM query request\nfrom orchestrator]
    end

    subgraph workingCtx [Working Context - Redis - TTL 24h]
        TC2[task context packet]
        BS2[branch state]
        PO2[prior agent outputs]
        CS2[conversation state]
    end

    subgraph ltm [Long-Term Memory - pgvector]
        subgraph sourceTypes [Filtered by source_type]
            STD2[standard\ncoding standards\nbest practices]
            ADR2[adr\narchitecture decisions\nADR records]
            INC2[incident\npast resolutions\nroot causes]
            CODE2[codebase\nembedded code\nAPI contracts]
        end
        RW[recency_weight\nnewer decisions outrank stale]
        TID[tenant_id\nenforced at storage layer]
    end

    CA2[ContextAssembler] -->|reads working ctx| TC2 & BS2 & PO2
    CA2 -->|filtered query:\ntenant_id + source_type\n+ recency_weight gt 0.7| ltm
    CA2 -->|builds explicit context packet| TaskSchemaCtx[Task Schema\ncontext field]

    subgraph writes2 [Deliberate Writes - PostWorkflowWriter]
        PW[PostWorkflowWriter\nverified outcomes only]
        PW -->|source_type: incident| INC2
        PW -->|source_type: adr| ADR2
        PW -->|requires provenance\nworkflow_run_id + task_id| ltm
    end

    style writes2 fill:#e8f5e9
    style workingCtx fill:#e3f2fd
    style ltm fill:#fce4ec
```

**Strict separation rule:** `WorkingContextService` and `LongTermMemoryService` are separate classes. No method calls across. ContextAssembler is the only component that uses both.

---

## 14. Security Architecture

```mermaid
flowchart TB
    subgraph l1 [Layer 1 - Transport Security]
        TLS2[TLS 1.3\nexternal HTTPS]
        MTLS2[mTLS\nIstio service mesh\ninternal east-west]
    end

    subgraph l2 [Layer 2 - Identity]
        OIDC2[OIDC / SAML\nEntra ID / Okta / Cognito]
        JWT2[JWT validation\nauth-service\nshort-lived tokens]
    end

    subgraph l3 [Layer 3 - Human Authorization]
        RBAC3[rbac-service\nrole ↔ permission model\nwho can approve which gate]
        GE2[GateEnforcer\nnon-bypassable\nno bypass flag exists]
    end

    subgraph l4 [Layer 4 - Agent Authorization]
        OPA2[OPA - Open Policy Agent\npolicy-engine service]
        BUNDLE[per-tenant policy bundles\npolicy-as-code]
    end

    subgraph l5 [Layer 5 - Credential Security]
        VAULT2[HashiCorp Vault\nkv-v2, database, pki, transit]
        SS3[secrets-service\nonly service that touches Vault]
        SCOPE2[Tool scope ceiling\nread/write/admin enforced\nregardless of underlying key]
        TTL2[Short-lived tokens\nTTL 15 minutes per invocation]
    end

    subgraph l6 [Layer 6 - Data Isolation]
        RLS2[PostgreSQL RLS\ntenant_id on every table]
        KAFKA3[Kafka ACLs\nper-service per-topic]
        VNS2[pgvector tenant filter\nat storage layer not API]
        REDIS2[Redis keyspace\naep:{tenant_id}:* prefix]
    end

    l1 --> l2 --> l3 --> l4 --> l5 --> l6
```

**Three security controls — never merged (Constitution S1):**

| Control | Service | Governs |
|---------|---------|---------|
| RBAC | `rbac-service` | Which humans approve which gates |
| Policy Engine | `policy-engine` (OPA) | Which agent actions are permitted, regardless of triggering user |
| Secrets Vault | `secrets-service` + Vault | Credential issuance — no agent holds credentials |

---

## 15. Observability Architecture

```mermaid
flowchart LR
    subgraph allServices [All 16 Services - Auto-instrumented]
        SDK2[OpenTelemetry SDK\nPython auto-instrumentation]
        TRACES2[Distributed Traces\nspan per operation]
        METRICS2[Metrics\ncounters, histograms, gauges]
        LOGS2[Structured Logs\nJSON + trace_id + task_id]
        LLM[LLM Traces\nprompt, tokens, latency\nvia Langfuse SDK]
    end

    OTELC2[OpenTelemetry Collector\ncentralised pipeline\nbatching + sampling]

    SDK2 --> OTELC2

    subgraph backends2 [Telemetry Backends]
        TEMPO2[Grafana Tempo\ndistributed tracing\n30-day retention]
        PROM2[Prometheus\ntime-series metrics\n90-day retention]
        LOKI2[Grafana Loki\nlog aggregation\n30-day retention]
        LF2[Langfuse\nLLM observability\ntoken cost tracking]
        CLK3[ClickHouse\naudit analytics\n7-year retention]
    end

    OTELC2 --> TEMPO2 & PROM2 & LOKI2 & LF2
    OTELC2 --> CLK3

    subgraph dashboards2 [Grafana - 5 Dashboard Sets]
        ENG2[Engineer Dashboard\ntask tracing\nagent execution detail]
        LEAD2[Leadership Dashboard\nDORA metrics\ncycle time, deployment freq]
        GOV2[Governance Dashboard\ngate audit trail\nnamed approver report]
        OPS2[Operations Dashboard\ninfra health\nKafka lag, DB connections]
        COST2[Cost Dashboard\ninference spend by tenant\nmodel tier distribution]
    end

    TEMPO2 & PROM2 & LOKI2 --> ENG2 & LEAD2 & GOV2 & OPS2
    LF2 --> COST2
    CLK3 --> GOV2
```

### Key Platform Metrics

```
# Throughput
aep_tasks_total{tenant, workflow_type, state}
aep_workflows_total{tenant, workflow_type, terminal_state}

# Agent performance
aep_agent_execution_duration_seconds{agent_id, cost_class}
aep_agent_retries_total{agent_id, retry_tier}

# Gate metrics
aep_gate_wait_duration_seconds{gate_id, workflow_type}
aep_gate_decisions_total{gate_id, decision}

# Model cost
aep_model_tokens_total{tier, tenant, agent_id}
aep_model_cost_usd_total{tier, tenant}

# Infrastructure health
aep_kafka_consumer_lag{topic, consumer_group}
aep_db_connection_pool_used{service, pool}
aep_cache_hit_rate{service, cache_type}
```

---

## 16. Scalability Architecture

```mermaid
flowchart TB
    subgraph dim1 [Dimension 1 - More Engineers]
        AR5[agent-runtime\nstateless horizontal pods]
        KAFKA4[Kafka partitions\nparallelism by tenant_id]
        HPA3[HPA on Kafka consumer lag\nmaxReplicas: 200]
    end

    subgraph dim2 [Dimension 2 - More Agent Types]
        AREG2[agent-registry\nnew entry = new capability\nzero orchestrator changes]
        TL2[template-loader\nworkflow templates\nindependently versioned]
    end

    subgraph dim3 [Dimension 3 - More Tenants]
        NS6[Kafka namespace\npartitioned by tenant_id]
        RLS3[Postgres RLS\nper-tenant row filtering]
        VEC3[pgvector tenant_id\nstorage-layer isolation]
        QUOTA[Model Router quota\nper-tenant token limit]
    end

    subgraph targets [Scale Targets]
        P[Pilot: 10 workflows/day\n5 agents, 1 tenant]
        A[Alpha: 100/day\n20 agents, 5 tenants]
        B[Beta: 1,000/day\n50 agents, 20 tenants]
        E[Enterprise: 10,000/day\n200 agents, 100 tenants]
        G[GA: 100,000/day\n1000+ agents, 1000+ tenants]
    end
```

**Honest limit (Constitution AI2):** This architecture scales coordination capacity. Model quality is a separate investment. A weak model does not improve because the platform around it is well-architected.

---

## 17. High Availability Architecture

```mermaid
flowchart TB
    subgraph region [Production Region - 3 Availability Zones]
        subgraph az1 [AZ-1]
            S1A[orchestrator x2\nagent-runtime x5\nKafka broker 1]
        end
        subgraph az2 [AZ-2]
            S2A[orchestrator x2\nagent-runtime x5\nKafka broker 2]
        end
        subgraph az3 [AZ-3]
            S3A[orchestrator x1\nagent-runtime x5\nKafka broker 3]
        end

        subgraph multiAZData [Multi-AZ Data]
            PG4[(Aurora PostgreSQL\nWriter AZ-1\nReader AZ-2, AZ-3)]
            RD4[(Redis Cluster\n3 primary + 3 replica\nacross all AZs)]
            KZK[Kafka Kraft\ncontroller quorum\nleader election < 30s]
        end
    end

    subgraph ha [HA Guarantees]
        WF2[Workflow durability\ntask persisted before action\npod restart = resume not restart]
        GW2[Gateway HA\nKong CP + DP separated\nmulti-AZ DP nodes]
        VLT4[Vault HA\n3-node Raft cluster\nauto-unseal on restart]
    end
```

| Component | HA Strategy | RTO | RPO |
|-----------|-------------|-----|-----|
| All services | Deployment min 2 replicas per AZ, PDB | < 30s | 0 (stateless) |
| PostgreSQL | Aurora Multi-AZ, auto-failover | < 60s | < 5s |
| Redis | Cluster mode 3+3, Sentinel | < 30s | < 1s |
| Kafka | RF=3, min-ISR=2, 3 brokers | < 60s | 0 |
| pgvector | Streaming read replicas | < 30s | < 5s |
| ClickHouse | Keeper 3-node quorum | < 60s | < 5s |
| Vault | Raft 3-node HA, auto-unseal | < 30s | 0 |

---

## 18. Disaster Recovery Architecture

```mermaid
flowchart LR
    subgraph primary [Primary Region]
        subgraph activePrimary [Active Services]
            PSVC2[All 16 services\nfull capacity]
            PKF[Kafka - primary cluster]
            PPG[Aurora - writer]
            PVT[Vault - primary]
        end
    end

    subgraph secondary [Secondary Region - Warm Standby]
        subgraph warmStandby [Warm Standby]
            SSVC[All 16 services\n0 replicas - fast scale-up]
            SKF[Kafka MirrorMaker 2\nasync replication]
            SPG[Aurora - read replica\nfast-promote capable]
            SVT[Vault - DR replica\nauto-promote]
        end
    end

    subgraph failover [Failover Mechanism]
        DNS2[Route53 / Traffic Manager\nhealth check failover]
        FM[Automated DB failover\nAurora Global < 60s]
        GATE[Human approval gate\nfor full regional failover\nConstitution H2: non-bypassable]
    end

    primary -->|async replication| secondary
    DNS2 --> primary
    DNS2 -->|on failure| secondary
    GATE -->|approves| DNS2
```

### Backup Schedule

| Data Store | Backup Method | Retention | RTO |
|------------|--------------|-----------|-----|
| PostgreSQL | Continuous WAL + daily snapshot | 30 days | < 60s (Aurora) |
| ClickHouse | Daily cold export → S3 | 7 years (audit) | < 4 hours |
| pgvector | pg_dump + WAL archiving | 30 days | < 60s |
| Kafka | Cross-region MirrorMaker 2 | 30 days | 0 (replicated) |
| Vault | Auto-snapshot → encrypted S3 | 90 days | < 30s |
| Redis | RDB snapshot every 15 min | No persistence needed | Warm from DB |

---

## 19. API Architecture

```mermaid
flowchart TB
    subgraph clients [API Clients]
        WEBCLIENT[React Frontend\nREST + WebSocket]
        SDKCLIENT[Agent SDK\ngRPC internal]
        EXTCLIENT[External Integrations\nREST webhooks]
    end

    subgraph gateway [API Gateway - Kong]
        RT[Routing]
        AT[Auth validation\nJWT]
        RL[Rate limiting\nper-tenant]
        TF[Transform\nrequest/response]
    end

    subgraph apis [Service APIs]
        subgraph rest [REST APIs - OpenAPI 3.1]
            WFA[/api/v1/workflows]
            AGENTA[/api/v1/agents]
            TOOLA[/api/v1/tools]
            APPROVA[/api/v1/approvals]
            AUDITA[/api/v1/audit]
            MEMA[/api/v1/memory]
        end
        subgraph ws [WebSocket]
            WS2[/ws/workflows/{id}\nreal-time state updates]
            WSAPPR[/ws/approvals\npending gate notifications]
        end
        subgraph grpc [gRPC - internal services]
            AGENTGRPC[AgentRegistry.Resolve\nToolRegistry.Resolve]
            MEMGRPC[MemoryService.Query\nMemoryService.Write]
            POLICYGRPC[PolicyEngine.Check]
        end
    end

    WEBCLIENT --> gateway --> rest & ws
    SDKCLIENT --> grpc
    EXTCLIENT --> gateway
```

---

## 20. Multi-Tenancy Architecture

```mermaid
flowchart TB
    subgraph tenants [Multiple Tenants - One Platform Deployment]
        subgraph tenantA [Tenant A - FinTech Corp]
            TA_POLICY[gates: architecture + security required]
            TA_TOOLS[tools: github-prod + jira-tenant-a]
            TA_QUOTA[quota: 100k tokens/hour]
        end
        subgraph tenantB [Tenant B - HealthCare Org]
            TB_POLICY[gates: CAB + CSO required]
            TB_TOOLS[tools: azure-devops-b + confluence-b]
            TB_QUOTA[quota: 50k tokens/hour]
        end
        subgraph tenantC [Tenant C - Manufacturing]
            TC_POLICY[gates: tech lead only]
            TC_TOOLS[tools: gitlab-c + jira-c]
            TC_QUOTA[quota: 200k tokens/hour]
        end
    end

    subgraph isolation [3-Layer Isolation]
        subgraph layer1a [Layer 1 - Data]
            KPART[Kafka partitioned\nby tenant_id]
            RLS4[PostgreSQL RLS\ncurrent_setting tenant_id]
            VFILT[pgvector tenant_id\nstorage filter]
            RKEY[Redis keyspace\naep:{tenant_id}:*]
        end
        subgraph layer2a [Layer 2 - Policy]
            TPOL[Per-tenant gate config\nOPA bundle per tenant]
            TTOOLS[Per-tenant tool visibility]
            TAGENTS[Per-tenant agent visibility]
        end
        subgraph layer3a [Layer 3 - Resources]
            TQUOTA[Per-tenant model quota\nRedis token counter]
            TRATE[Per-tenant tool rate limit\nsliding window]
        end
    end

    tenants --> isolation
```

---

## 21. Workflow Engine Architecture

```mermaid
stateDiagram-v2
    [*] --> Scoped : WorkflowInitiated

    Scoped --> Architected : ApprovalGranted\n[scope gate - Product Owner]
    Scoped --> Scoped : ApprovalDenied\n[revision task created]

    Architected --> Implemented : ApprovalGranted\n[arch gate - Tech Lead]
    Architected --> Architected : ApprovalDenied\n[revision task]

    Implemented --> Tested : AgentCompleted\n[coding agent]
    Tested --> Scanned : AgentCompleted\n[test agent]
    Scanned --> Merged : ApprovalGranted\n[merge gate - Senior Eng]
    Merged --> Released : ApprovalGranted\n[release gate - Release Mgr]

    Implemented --> Failed : AgentFailed × 5
    Tested --> Failed : AgentFailed × 5
    Released --> RolledBack : RollbackTriggered
    Released --> [*]
    RolledBack --> [*]
    Failed --> [*]
```

### Workflow Template Structure

```
{
  workflow_type, version, initial_state, terminal_states,
  states: [
    {
      name, required_capability,
      gate: { id, strategy: "open-ended"|"time-boxed", sla_minutes, required_role },
      transitions_to
    }
  ],
  context_handoff: { state → [context_keys] },
  rollback_strategy: { pre_merge, post_release },
  success_criteria: [...]
}
```

---

## 22. Agent Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Registered : SDK registers agent\ncontract validated

    Registered --> Available : Health check passed\nagent-runtime loaded

    Available --> Dispatched : TaskCreated event\nmatched by capability

    Dispatched --> Executing : AgentStarted published\ntools resolved\ntokens issued

    Executing --> Completed : AgentCompleted published\nresult in output_schema

    Executing --> Failed : AgentFailed published\nerror_code + retry_count

    Failed --> Dispatched : Tier 1 retry\nretry_count lt 3

    Failed --> Compensating : Tier 2 saga\nretry_count 3-5

    Failed --> Escalated : Tier 3 human gate\nretry_count gt 5

    Completed --> Available : Ready for next task

    Compensating --> Available
    Escalated --> [*]
    Completed --> Deregistered : SDK deregisters\nrolling update
    Deregistered --> [*]
```

---

## 23. Tool Integration Architecture

```mermaid
flowchart LR
    subgraph agent [agent-runtime]
        REQ[Agent requests\ncreate-pull-request]
    end

    subgraph toolReg [tool-registry]
        CAP[capability lookup\ncreate-pull-request]
        RESOLVE[resolve to\ntenant tool config]
        NORM[response_normaliser\nvendor → common shape]
    end

    subgraph vault3 [secrets-service + Vault]
        TOKEN[short-lived token\nscoped to repo\nTTL 15 min]
    end

    subgraph vendors [Vendor APIs]
        GH2[GitHub API]
        ADO[Azure DevOps API]
        GL[GitLab API]
    end

    subgraph commonShape [Common Response Shape]
        PR[pr_id, pr_url, status, branch]
    end

    REQ --> CAP --> RESOLVE
    RESOLVE --> TOKEN
    TOKEN --> GH2
    TOKEN --> ADO
    TOKEN --> GL
    GH2 & ADO & GL --> NORM --> PR --> agent
```

**Tool Contract fields:** `tool_id · capability_tags · auth_strategy · scope · rate_limit_policy · response_normaliser · contract_version`

---

## 24. Model Routing Architecture

```mermaid
flowchart TB
    subgraph dispatch [Cost-Aware Dispatcher]
        COSTCLASS[Agent cost_class hint\nlow / medium / high]
        TASKMETA[Task metadata\nsecurity_critical flag\ncomplexity_score]
        TENQUOTA[Tenant quota check\nRedis token counter]
    end

    subgraph router [model-router service]
        CLASSIFY[TaskClassifier\nfinal tier decision]
        ROUTE[TierRouter\nroute to endpoint]
    end

    subgraph tiers [Model Tiers - endpoints are config not code]
        LOW[Low Tier\nroutine tasks\ntest scaffolding\ndocumentation]
        MED[Medium Tier\nfeature development\ncode review]
        HIGH[High Tier\narchitecture design\nsecurity critical\nincident root cause]
    end

    subgraph quota [Per-Tenant Quota Enforcement]
        QCHECK[Token counter in Redis\nsliding window 1h]
        QBACKP[Backpressure on exceed\ntask queued not dropped]
    end

    COSTCLASS & TASKMETA --> CLASSIFY
    CLASSIFY --> TENQUOTA --> ROUTE
    ROUTE --> LOW & MED & HIGH
    TENQUOTA --> QCHECK
    QCHECK --> QBACKP
```

---

## 25. SDK Architecture

```mermaid
flowchart TB
    subgraph agentSDK [aep-agent-sdk - Python Package]
        subgraph base [Base Classes]
            AGENT[Agent\nAbstract base class\nall agents inherit]
            CTX[AgentContext\ntyped context packet]
            RESULT[AgentResult\ntyped output]
        end

        subgraph capabilities [Auto-Inherited Capabilities]
            LOGCAP[logging\nstructured JSON\ntask_id + workflow_run_id]
            MEMCAP[memory\nworking context\nLTM query]
            EVCAP[events\nAgentStarted/Completed/Failed\ncorrect envelope]
            RETRYCAP[retry\nexponential backoff\nidempotency check]
            SECCAP[security\npolicy check\nscoped token]
            TOOLCAP[tool access\ncapability-based\nnot vendor-specific]
            METCAP[metrics\nhistogram per operation]
            CFGCAP[configuration\nper-tenant\nfrom config-service]
        end

        subgraph registration [Registry Integration]
            REG[AgentRegistration\ncontract validation\nheartbeat]
        end
    end

    subgraph usage [Usage Pattern]
        IMPL[class ReviewAgent\n    inherits Agent\n\n    async def execute\n        self.tools.invoke\n        self.memory.query\n        return AgentResult]
    end

    AGENT --> LOGCAP & MEMCAP & EVCAP & RETRYCAP & SECCAP & TOOLCAP & METCAP & CFGCAP
    AGENT --> REG
    IMPL --> AGENT
```

---

## Phase Execution Summary

| Phase | Deliverable | Key Acceptance Criterion |
|-------|-------------|--------------------------|
| **1** | Repository structure, service scaffolding, technology stack, ADRs, dev guidelines | CI green, service boundaries enforced |
| **2** | All 16 core platform microservices | Contract tests pass, integration suite green |
| **3** | Agent SDK + Tool SDK | Third-party agent registers in < 1 day |
| **4** | 15 specialist agents | All implement Agent Contract, idempotency verified |
| **5** | 8 workflow templates | End-to-end run with full audit trail |
| **6** | All database schemas + migrations | RLS verified, cross-tenant leakage = 0 |
| **7** | 11 external connectors | Tool Contract compliance, response normalisation |
| **8** | REST / gRPC / WebSocket APIs + OpenAPI | Contract tests, load tests |
| **9** | React dashboard (9 views) | Approval console blocks workflow |
| **10** | Docker, Compose, K8s, Helm, Terraform, CI/CD | Deploy to dev with one command |
| **11** | Full observability stack | 3 Grafana audiences from real runs |
| **12** | Unit, integration, contract, load, workflow, chaos | > 80% coverage, chaos: zero workflow loss |
| **13** | Architecture, Developer, Operator, API, SDK guides | Peer-reviewed, published |

---

## Document Relationships

| Document | Role |
|----------|------|
| [CONSTITUTION.md](../../CONSTITUTION.md) | Immutable principles — this diagram doc must not violate any |
| [ARCHITECTURE.md](../ARCHITECTURE.md) | Source architecture this document visualises |
| [DECISIONS.md](./DECISIONS.md) | ADRs explaining why each architectural choice was made |
| [CLAUDE.md](../CLAUDE.md) | Implementation rules derived from this architecture |
| [ROADMAP.md](../ROADMAP.md) | Delivery timeline for each architectural layer |
| [TASKS.md](../TASKS.md) | Engineering breakdown implementing each diagram |

---

*This is a living document. Every new architectural diagram belongs here. Update when containers, data flows, security controls, or deployment topology changes. Changes that conflict with CONSTITUTION.md require a Decision Record.*
