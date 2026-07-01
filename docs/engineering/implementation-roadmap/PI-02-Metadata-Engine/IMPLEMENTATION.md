# PI-02 — Implementation Guide

## agent-registry Service

```python
# platform/agent-registry/src/domain/registry.py

class AgentRegistryService:
    async def register(self, registration: AgentRegistration) -> str:
        """Validate contract, store in DB, cache capabilities in Redis."""
        ContractValidator().validate(registration)
        await self.db.upsert_agent(registration)
        await self.cache.index_capabilities(registration.agent_id, registration.capabilities)
        return registration.agent_id

    async def resolve(self, capability_tag: str, tenant_id: str) -> list[AgentRegistration]:
        """Query by capability tag — never by agent_id."""
        cached = await self.cache.get_by_capability(capability_tag, tenant_id)
        if cached:
            return cached
        return await self.db.query_by_capability(capability_tag, tenant_id)
```

## aep-agent-sdk Base Class

```python
# sdk/aep-agent-sdk/aep_sdk/agent.py

from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, context: AgentContext):
        self.context = context
        self.tools = ToolClient(context)
        self.memory = MemoryClient(context)
        self.events = EventClient(context)
        self.logger = get_logger(self.__class__.__name__).bind(
            task_id=context.task_id,
            workflow_run_id=context.workflow_run_id,
            tenant_id=context.tenant_id,
        )

    @abstractmethod
    async def execute(self) -> AgentResult:
        """Implement agent logic here. Return AgentResult."""
        ...

    async def run(self) -> AgentResult:
        """Called by AgentExecutor. Do not override."""
        await self.events.publish_started()
        try:
            result = await self.execute()
            await self.events.publish_completed(result)
            return result
        except Exception as e:
            await self.events.publish_failed(e)
            raise
```

## Agent Contract Validation

```python
# sdk/aep-agent-sdk/aep_sdk/registry.py

class AgentRegistration(BaseModel):
    agent_id: str                      # kebab-case
    capabilities: list[str]            # verb-noun tags
    input_schema: str                  # JSON Schema string
    output_schema: str                 # JSON Schema string
    required_tools: list[str]          # capability tags
    cost_class: Literal["low", "medium", "high"]
    approval_required: bool
    idempotency_key_strategy: str
    contract_version: str = "1.0"
    # FORBIDDEN: model_name — never in contract (MI3)
```

## model-router Tier Logic

```python
# platform/model-router/src/domain/router.py

TIER_CONFIG = {
    "low":    {"endpoint_env": "MODEL_TIER_LOW_ENDPOINT"},
    "medium": {"endpoint_env": "MODEL_TIER_MEDIUM_ENDPOINT"},
    "high":   {"endpoint_env": "MODEL_TIER_HIGH_ENDPOINT"},
}

class ModelRouter:
    async def route(self, cost_class: str, tenant_id: str) -> ModelEndpoint:
        await self.quota_enforcer.check(tenant_id, cost_class)
        endpoint = os.environ[TIER_CONFIG[cost_class]["endpoint_env"]]
        return ModelEndpoint(url=endpoint, tenant_id=tenant_id)
```
