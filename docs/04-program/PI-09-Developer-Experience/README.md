# PI-09 — Developer Experience

**Status:** `PLANNED`  
**Depends on:** PI-06 complete (all agents operational), PI-07 complete (auth + RBAC)  
**Target:** Sprint 34–38 (weeks 67–76)

## What This PI Delivers

- React dashboard with 9 operational views
- Full REST API surface (OpenAPI 3.1 — all services)
- WebSocket real-time workflow state streaming
- gRPC internal APIs (AgentRegistry, ToolRegistry, MemoryService)
- SDK documentation website (quickstart, API reference, tutorials)
- Developer portal — self-service agent + tool registration
- CLI tool — `aep` — for developers to trigger workflows, inspect state, tail logs

## 9 Dashboard Views

| View | Purpose |
|------|---------|
| Workflow Designer | Create and trigger workflows |
| Agent Registry | Browse, register, and monitor agents |
| Workflow Monitor | Real-time workflow state with gate indicators |
| Task Explorer | Drill into any task's context, retries, and result |
| Audit Explorer | Query the immutable audit log |
| Memory Explorer | Browse and search long-term memory |
| Approval Console | Review and decide on pending gates |
| Metrics Dashboard | DORA metrics, cost, performance |
| Config Portal | Per-tenant settings and feature flags |
