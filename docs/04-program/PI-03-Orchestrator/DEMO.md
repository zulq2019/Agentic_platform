# PI-03-Orchestrator — Demo Script

**Audience:** Engineering team, PI stakeholders
**Duration:** 20 minutes
**Prerequisites:** Platform deployed to dev cluster with PI-01 through PI-03 active.

## Scene 1 — Happy Path (8 min)
Demonstrate the primary use case of Orchestrator end-to-end.
Walk through the key user story: trigger ? execute ? result.
Show the Grafana dashboard updating in real time.

## Scene 2 — Tenant Isolation (4 min)
Show that tenant A's data is invisible to tenant B.
Attempt a cross-tenant read — show it returns zero rows.
Talking point: "Isolation is enforced at the storage layer, not in application code."

## Scene 3 — Failure Recovery (4 min)
Simulate a failure scenario (kill a pod, invalid input, etc.)
Show the system recovers gracefully: retry, escalation, or error message.

## Scene 4 — Observability (4 min)
Open Grafana — show traces, metrics, and logs from this PI's services.
Show a distributed trace spanning multiple services.
Talking point: "Every operation is observable from day one."

## PI Close
- Summarise what was delivered
- Show PI-03 acceptance criteria — all green
- Preview PI-4 objectives
