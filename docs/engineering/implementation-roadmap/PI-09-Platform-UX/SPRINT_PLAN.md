# PI-09 — Sprint Plan

## Sprint 34–35 (Days 331–350): REST APIs + WebSocket

| # | Task | Points |
|---|------|--------|
| 34.1 | Full OpenAPI 3.1 spec for all 16 services | 4 |
| 34.2 | `POST /api/v1/workflows` — trigger workflow | 3 |
| 34.3 | `GET /api/v1/workflows/{id}` — workflow state | 2 |
| 34.4 | `GET /api/v1/tasks/{id}` — task detail | 2 |
| 34.5 | `POST /api/v1/approvals/{task_id}` — submit gate decision | 3 |
| 35.1 | WebSocket `/ws/workflows/{id}` — real-time state updates | 3 |
| 35.2 | WebSocket `/ws/approvals` — pending gate notifications | 2 |

---

## Sprint 36–37 (Days 351–370): React Dashboard

| # | Task | Points |
|---|------|--------|
| 36.1 | Scaffold React app with routing, auth, and tenant context | 3 |
| 36.2 | Workflow Monitor view — real-time state machine visual | 4 |
| 36.3 | Approval Console — gate queue + decision form | 4 |
| 37.1 | Agent Registry view — browse + register agents | 3 |
| 37.2 | Audit Explorer — ClickHouse query UI | 3 |
| 37.3 | Metrics Dashboard — DORA + cost charts | 3 |
| 37.4 | Task Explorer, Memory Explorer, Config Portal | 4 |

---

## Sprint 38 (Days 371–380): CLI + SDK Docs + PI-09 Close

| # | Task | Points |
|---|------|--------|
| 38.1 | `aep` CLI — trigger workflow, get status, approve gate, tail logs | 4 |
| 38.2 | SDK documentation website — quickstart, API reference | 3 |
| 38.3 | Developer portal — self-service agent registration flow | 2 |
| 38.4 | UX test: external developer builds + registers new agent in < 1 hour | 2 |
| 38.5 | PI-09 retrospective + PI-10 kick-off | 1 |
