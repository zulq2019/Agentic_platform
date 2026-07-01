# Studio Overview

**Status:** Living document  
**Version:** 1.0  
**Last updated:** 29 June 2026

---

Each **Studio** is an independently valuable product module on the Engineering Platform. Studios run in parallel in production; delivery still follows PI sequencing in [docs/engineering/implementation-roadmap/](../engineering/implementation-roadmap/).

---

## Platform Core

**Primary users:** Platform engineers, SRE, integration architects

**Value:** Reliable, event-mediated infrastructure so every Studio can register agents and tools, run workflows, and enforce policy without bespoke plumbing.

**Key outcomes (via PIs):** All services healthy ([PI-01](../engineering/implementation-roadmap/PI-01-Platform-Core/README.md)), agents execute tasks ([PI-02](../engineering/implementation-roadmap/PI-02-Metadata-Engine/README.md)), workflows orchestrate end-to-end ([PI-03](../engineering/implementation-roadmap/PI-03-Provider-Framework/README.md)), memory layers operational ([PI-04](../engineering/implementation-roadmap/PI-04-Workflow-Framework/README.md)).

**Detail:** [PLATFORM_CORE.md](./PLATFORM_CORE.md)

---

## Requirements Studio

**Primary users:** Product owners, business analysts, engineering leads

**Value:** Turn intent into traceable scope — user stories, acceptance criteria, and scope documents linked to workflow runs.

**Agents (planned):** `requirement-agent` — capability tags `analyses-requirements`, `produces-scope-document` ([PI-06](../engineering/implementation-roadmap/PI-06-Studio-Framework/README.md))

**Typical workflows:** Greenfield scope gate, brownfield discovery intake

**Consumes Platform Core:** Workflow Engine, Memory Service (context), Tool Registry (e.g. issue tracker)

---

## Architecture Studio

**Primary users:** Solution architects, principal engineers

**Value:** Design decisions, ADRs, codebase discovery, and dependency intelligence before implementation.

**Agents (planned):** `architecture-agent`, `discovery-agent`, `dependency-analysis-agent` ([PI-06](../engineering/implementation-roadmap/PI-06-Studio-Framework/README.md))

**Typical workflows:** Architected state, brownfield mapping, ADR publication

**Consumes Platform Core:** Memory Service (project context), Event Bus, Audit

---

## Development Studio

**Primary users:** Software engineers, full-stack developers

**Value:** AI-assisted implementation — backend/frontend code, PRs, and schema migrations with human gates.

**Agents (planned):** `backend-agent`, `frontend-agent`, `migration-agent`, `review-agent`, `documentation-agent` ([PI-06](../engineering/implementation-roadmap/PI-06-Studio-Framework/README.md))

**Typical workflows:** Greenfield / brownfield implementation states through merge gate

**Consumes Platform Core:** Model Router, Tool Registry (source control), Agent Runtime, Task Engine

---

## Testing Studio

**Primary users:** QA engineers, SDETs, CI owners

**Value:** Generated and executed tests, regression signals, and quality evidence for gates.

**Agents (planned):** `testing-agent`, `regression-agent`, `performance-agent` ([PI-06](../engineering/implementation-roadmap/PI-06-Studio-Framework/README.md))

**Typical workflows:** Tested state, regression on defect resolution paths

**Consumes Platform Core:** Tool Registry (CI/CD, Katalon, etc.), Workflow Engine, Audit

---

## Security Studio

**Primary users:** AppSec, security champions, compliance officers

**Value:** Vulnerability scanning, security reports, and policy-enforced security gates.

**Agents (planned):** `security-agent` ([PI-06](../engineering/implementation-roadmap/PI-06-Studio-Framework/README.md))

**Typical workflows:** Security review gates, release hardening

**Consumes Platform Core:** Policy Engine, Tool Registry (security scanners), Audit

---

## Release Studio

**Primary users:** Release managers, DevOps leads

**Value:** Controlled promotion — changelog, release artifacts, deployment orchestration with approval checkpoints.

**Agents (planned):** `release-agent` ([PI-06](../engineering/implementation-roadmap/PI-06-Studio-Framework/README.md))

**Typical workflows:** Release and deploy states in workflow templates ([workflows/](../../workflows/))

**Consumes Platform Core:** Workflow Engine, Approval service, Tool Registry (CI/CD)

---

## Engineering Operations

**Primary users:** SRE, incident commanders, platform operations

**Value:** Incident analysis, root-cause workflows, operational runbooks, and platform reliability programmes.

**Agents (planned):** `root-cause-agent` ([PI-06](../engineering/implementation-roadmap/PI-06-Studio-Framework/README.md))

**PI contributions:** Governance dashboards ([PI-07](../engineering/implementation-roadmap/PI-07-Platform-Services/README.md)), enterprise SLAs ([PI-08](../engineering/implementation-roadmap/PI-08-Solution-Packs/README.md)), GA hardening ([PI-10](../engineering/implementation-roadmap/PI-10-General-Availability/README.md))

**Consumes Platform Core:** Audit, Observability, Event Bus, Workflow Engine

---

## AI Operations

**Primary users:** ML platform teams, FinOps, agent owners

**Value:** Model tier routing, per-tenant quotas, cost visibility, and agent lifecycle governance.

**PI contributions:** Model Router behaviour ([PI-02](../engineering/implementation-roadmap/PI-02-Metadata-Engine/README.md)), enterprise quotas ([PI-08](../engineering/implementation-roadmap/PI-08-Solution-Packs/README.md))

**Consumes Platform Core:** Model Router, Agent Registry, Configuration, Observability (cost metrics)

---

## Integration Marketplace

**Primary users:** Integration engineers, partner teams, tool vendors

**Value:** Discoverable, scoped, tenant-safe connectors — register once, resolve by capability tag everywhere.

**PI contribution:** [PI-05 Tool Registry](../engineering/implementation-roadmap/PI-05-Execution-Framework/README.md) — Tool Contract, Secrets Vault integration, response normalisation

**Future programme:** Enterprise marketplace and full integration framework are **not** in PI-05 scope — see [FUTURE_CAPABILITIES.md](./FUTURE_CAPABILITIES.md) (FC-INT-01, FC-INT-02).

**Consumes Platform Core:** Tool Registry, Secrets, Policy Engine, Event Bus

**Examples:** GitHub, Jira, Katalon, CI/CD, Confluence (see [PI-05 FEATURES](../engineering/implementation-roadmap/PI-05-Execution-Framework/FEATURES.md))

---

## Administration

**Primary users:** Tenant admins, compliance officers, identity teams

**Value:** Identity, RBAC, policy-as-code, immutable audit, and tenant configuration.

**PI contributions:** [PI-07 Governance](../engineering/implementation-roadmap/PI-07-Platform-Services/README.md), [PI-08 Enterprise](../engineering/implementation-roadmap/PI-08-Solution-Packs/README.md) (SSO, SCIM, config-service)

**Consumes Platform Core:** Auth, RBAC, Policy Engine, Audit, Secrets, Configuration

---

## Observability

**Primary users:** SRE, engineering managers, all Studio operators

**Value:** Unified health, traces, metrics, and dashboards across every Studio and Core service.

**PI contributions:** Baseline stack ([PI-01](../engineering/implementation-roadmap/PI-01-Platform-Core/README.md), US-01.02), Grafana views ([PI-09](../engineering/implementation-roadmap/PI-09-Platform-UX/README.md) Metrics Dashboard)

**Note:** Observability is **cross-cutting** — it is a product domain for packaging and UX, not a replacement for the Observability container in [ARCHITECTURE.md](../../ARCHITECTURE.md).

---

## Developer Experience (Cross-Studio Shell)

[PI-09 Developer Experience](../engineering/implementation-roadmap/PI-09-Platform-UX/README.md) delivers the **unified shell** — dashboard, CLI (`aep`), SDK docs, and APIs — that surfaces every Studio. Product-wise, PI-09 maps to **all Studios** as the experience layer; implementation remains a single PI.

| Dashboard view | Primary Studio |
|----------------|----------------|
| Workflow Designer | All (orchestration) |
| Agent Registry | AI Operations + each Studio's agents |
| Workflow Monitor | Engineering Operations |
| Task Explorer | All |
| Audit Explorer | Administration |
| Memory Explorer | Architecture + Requirements |
| Approval Console | Administration + Release |
| Metrics Dashboard | Observability |
| Config Portal | Administration |
