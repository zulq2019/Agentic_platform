# PI-03 — Implementation Guide

## GateEnforcer — Non-Bypassable by Design

```python
# platform/orchestrator-service/src/domain/gate_enforcer.py

class GateEnforcer:
    """
    Blocks state transitions unless a valid approval_record exists.
    No bypass flag. No timeout auto-approve. Constitution H2.
    """
    async def check(self, task_id: UUID, gate_id: str) -> None:
        record = await self.approval_client.get_record(task_id, gate_id)
        if record is None:
            raise GateNotSatisfiedError(
                task_id=task_id,
                gate_id=gate_id,
                message="State transition refused: no approval_record present."
            )
        if record.decision != "approved":
            raise GateNotSatisfiedError(
                task_id=task_id,
                gate_id=gate_id,
                message=f"Gate denied by {record.approver}: {record.feedback}"
            )
        # Log to audit trail — every gate decision is named and timestamped
        self.logger.info(
            "gate_satisfied",
            task_id=str(task_id),
            gate_id=gate_id,
            approver=record.approver,
            decided_at=record.decided_at.isoformat(),
        )
```

## PlannerService — Orchestrator Core

```python
# platform/orchestrator-service/src/domain/planner.py

class PlannerService:
    async def plan(self, workflow_run: WorkflowRun) -> list[Task]:
        """
        Decomposes a workflow into an ordered list of tasks.
        Does NOT generate code, call LLMs, or execute tools.
        """
        template = await self.workflow_engine.get_template(
            workflow_run.workflow_type,
            workflow_run.workflow_template_version,
        )
        tasks = []
        for state in template.states:
            agent = await self.agent_selector.resolve(
                capability_tag=state.required_capability,
                tenant_id=workflow_run.tenant_id,
            )
            context = await self.context_assembler.build(
                workflow_run=workflow_run,
                state=state,
            )
            task = Task(
                workflow_run_id=workflow_run.workflow_run_id,
                tenant_id=workflow_run.tenant_id,
                assigned_agent_id=agent.agent_id,
                context=context,
                state="pending",
            )
            # Write-before-act: persist BEFORE publishing to Kafka
            await self.task_engine.persist(task)
            tasks.append(task)
        return tasks
```

## RetryCompensationManager — 3-Tier Recovery

```python
# platform/orchestrator-service/src/domain/retry_compensation_manager.py

class RetryCompensationManager:
    async def handle_failure(self, task: Task, error: AgentError) -> None:
        task.retry_count += 1
        await self.task_engine.update(task)

        if task.retry_count <= 3:
            # Tier 1: exponential backoff
            delay = (2 ** task.retry_count) + random.uniform(0, 1)
            await asyncio.sleep(delay)
            await self.kafka.publish(TaskCreated.from_task(task))

        elif task.retry_count <= 5:
            # Tier 2: saga compensation
            await self.kafka.publish(RollbackTriggered(
                task_id=task.task_id,
                workflow_run_id=task.workflow_run_id,
                reason=str(error),
            ))

        else:
            # Tier 3: human escalation — no auto-approve
            await self.kafka.publish(ApprovalRequested(
                task_id=task.task_id,
                gate_id="on-call-escalation",
                escalation_reason=str(error),
                retry_count=task.retry_count,
            ))
            await self.kafka.produce_to_dlq(task)
```
