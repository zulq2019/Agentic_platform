# Blueprint: Frontend Dashboard

**Status:** DEFERRED — Implemented in PI-09  
**Target PI:** PI-09-Platform-UX

## Purpose

React-based web dashboard providing operational and governance visibility for all platform roles.

## 9 Views

| View | Route | Audience | Key Features |
|------|-------|----------|-------------|
| Workflow Monitor | /workflows | Engineers, PMs | Real-time state machine, current state highlighted, gate indicators |
| Approval Console | /approvals | Tech Leads, PMs, SREs, CSOs | Gate queue, artifact review, approve/deny with recorded feedback |
| Agent Registry | /agents | Platform Engineers | Browse registered agents, capabilities, health, registration form |
| Task Explorer | /tasks/{id} | Engineers | Context packet, retries, model tier, execution trace link |
| Audit Explorer | /audit | Compliance, Governance | Query ClickHouse audit log, filter by tenant/workflow/date, CSV export |
| Memory Explorer | /memory | Engineers | Browse LTM entries by source_type, search by embedding |
| Metrics Dashboard | /metrics | Engineering Leads, CTO | DORA metrics, cycle time, deployment frequency, LLM cost by tenant |
| Config Portal | /config | Tenant Admins | Per-tenant settings, tool visibility, feature flags, quota management |
| Developer Portal | /dev | External Developers | SDK docs, agent registration wizard, API explorer |

## Tech Stack

- React 18 + TypeScript
- TanStack Query (data fetching)
- TanStack Router (routing)
- Tailwind CSS + shadcn/ui
- Recharts (metrics visualisation)
- React Flow (workflow state machine diagram)
- WebSocket (real-time state updates)

## Directory Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── WorkflowMonitor/
│   │   ├── ApprovalConsole/
│   │   ├── AgentRegistry/
│   │   ├── TaskExplorer/
│   │   ├── AuditExplorer/
│   │   ├── MemoryExplorer/
│   │   ├── MetricsDashboard/
│   │   ├── ConfigPortal/
│   │   └── DeveloperPortal/
│   ├── components/
│   │   ├── WorkflowDiagram/
│   │   ├── GateIndicator/
│   │   └── shared/
│   ├── hooks/
│   ├── api/            # Generated from OpenAPI specs
│   └── App.tsx
├── package.json
└── Dockerfile
```

## Critical UX Requirements

- Approval Console MUST show the full artifact being approved (diff, report, etc.)
- Gate approval form MUST require feedback text — empty approval not permitted
- Workflow Monitor MUST show named approver and timestamp for every completed gate
- All views MUST be accessible — WCAG 2.1 AA
