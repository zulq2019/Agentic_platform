# PI-02 — Objectives

**Architecture baseline:** [ARCHITECTURE_BASELINE_V2.md](../../../architecture/ARCHITECTURE_BASELINE_V2.md). Agent Runtime hosts **`ai-agent` Providers**; model routing evolves to **Execution Profile** resolution (gap G-04).

## O1. Agent executes a task end-to-end
A `TaskCreated` event on Kafka causes an agent to execute and publish `AgentCompleted` with a result.  
**Measure:** Integration test `test_task_lifecycle.py` passes.

## O2. Agents discovered by capability, not by name
The orchestrator (stub) requests an agent with capability `generates-unit-tests` and receives the correct agent without knowing its ID.  
**Measure:** `test_capability_resolution.py` passes with two agents sharing a capability.

## O3. Model routing respects cost_class (Execution Profile path)
A `cost_class: low` task routes to the low-tier model endpoint; `cost_class: high` routes to high-tier. **v2 target:** route via Active Execution Profile preferred model; cost_class remains compatibility hint until Profile schema lands (PI-09).  
**Measure:** `test_model_routing.py` — correct endpoint returned for each cost class.

## O4. Tier 1 retry recovers transient failures
An agent that fails on first attempt with a transient error retries with exponential backoff and succeeds on second attempt.  
**Measure:** `test_retry_tier1.py` — AgentCompleted published on retry, not AgentFailed.

## O5. SDK enables a new agent in under 1 hour
A developer with the SDK docs can write, register, and run a new agent from scratch in under 1 hour.  
**Measure:** Timed developer trial on sprint 8 demo day.
