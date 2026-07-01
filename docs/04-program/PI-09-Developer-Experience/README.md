# PI-09 — Developer Experience

**Status:** `PLANNED`  
**Depends on:** PI-06 complete (all agents operational), PI-07 complete (auth + RBAC)  
**Target:** Sprint 34–38 (weeks 67–76)  
**Architecture baseline:** [ARCHITECTURE_BASELINE_V2.md](../../architecture/ARCHITECTURE_BASELINE_V2.md). Delivers **Platform Builders**, **Object Explorer**, and **Metadata Engine MVP** per [PLATFORM_UX_MODEL.md](../../architecture/PLATFORM_UX_MODEL.md).

## Architecture v2 alignment

| Field | Value |
|-------|-------|
| **Classification** | Renamed (conceptual) + Extended |
| **v2 concept** | Platform UX Framework |
| **Report** | [ARCHITECTURE_ALIGNMENT_REPORT.md](../../engineering/ARCHITECTURE_ALIGNMENT_REPORT.md) |
| **Migration note** | Critical path for G-01, G-02, G-05, G-07. Add ME/Builder stories at sprint planning — do not renumber existing stories. |

---

## What This PI Delivers

- React dashboard with operational views aligned to **Platform Object UX** (Object Inspector tabs)
- **Platform Builders** — Workflow, Provider, Policy, Execution Profile designers (metadata output)
- **Object Explorer** — global Platform Object catalogue
- Full REST API surface (OpenAPI 3.1 — all services)
- WebSocket real-time workflow state streaming
- gRPC internal APIs (AgentRegistry, ToolRegistry, MemoryService)
- SDK documentation website (quickstart, API reference, tutorials)
- Developer portal — self-service **Provider** registration (Provider Builder)
- CLI tool — `aep` — for developers to trigger workflows, inspect state, tail logs
- **Metadata Engine MVP** — publish, validate, registry index (see baseline gap G-01)

## 9 Dashboard Views

| View | Purpose |
|------|---------|
| Workflow Designer | Create and trigger workflows |
| Agent Registry | Browse, register, and monitor **Providers** (`ai-agent` kind) |
| Workflow Monitor | Real-time workflow state with gate indicators |
| Task Explorer | Drill into any task's context, retries, and result |
| Audit Explorer | Query the immutable audit log |
| Memory Explorer | Browse and search long-term memory |
| Approval Console | Review and decide on pending gates |
| Metrics Dashboard | DORA metrics, cost, performance |
| Config Portal | Per-tenant settings and feature flags |
