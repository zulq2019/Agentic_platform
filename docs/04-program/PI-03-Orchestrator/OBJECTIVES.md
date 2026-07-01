# PI-03 — Objectives

**Architecture baseline:** [ARCHITECTURE_BASELINE_V2.md](../../architecture/ARCHITECTURE_BASELINE_V2.md). Orchestrator implements the **Planner** role; **Provider** resolution by capability tag (not agent name).

## O1. Greenfield workflow runs end-to-end
A POST to `/api/v1/workflows` with a valid request body results in a complete workflow execution with all states traversed and a terminal state recorded.  
**Measure:** `test_greenfield_workflow_e2e.py` passes.

## O2. Gates block without approval_record
A state transition from `Implemented` to `Tested` that lacks an `approval_record` is rejected.  
**Measure:** `test_gate_enforcer_blocks.py` — transition returns 409 when no approval record.

## O3. Tier 2 saga compensation runs on repeated failure
An agent that fails 4 times triggers saga compensation events, not a simple retry.  
**Measure:** `test_saga_compensation.py` — `RollbackTriggered` published after 4th failure.

## O4. Tier 3 escalates to human gate
An agent that fails 6 times creates an `ApprovalRequested` event for on-call escalation.  
**Measure:** `test_tier3_escalation.py` — approval gate created, workflow paused.

## O5. Platform restart resumes mid-workflow
A workflow in state `Implemented` survives a full orchestrator restart and resumes from the same state.  
**Measure:** Chaos test — kill orchestrator pod, restart, verify workflow resumes.
