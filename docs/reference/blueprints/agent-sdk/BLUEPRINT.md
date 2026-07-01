# Blueprint: Agent SDK & Tool SDK

**Status:** DEFERRED — Agent SDK in PI-02, Tool SDK in PI-05  
**Target PI:** PI-02 (agent-sdk), PI-05 (tool-sdk)

## aep-agent-sdk

Python package providing the base class and auto-inherited capabilities for all agents.

```
sdk/aep-agent-sdk/
├── aep_sdk/
│   ├── __init__.py
│   ├── agent.py          # Abstract Agent base class
│   ├── context.py        # AgentContext (typed input)
│   ├── result.py         # AgentResult (typed output)
│   ├── tools.py          # ToolClient — capability-based requests
│   ├── memory.py         # MemoryClient — working context + LTM
│   ├── events.py         # EventClient — Kafka event publishing
│   ├── retry.py          # Exponential backoff + jitter
│   ├── security.py       # Policy check + scoped token from secrets-service
│   ├── metrics.py        # Auto Prometheus metrics per agent operation
│   ├── registry.py       # AgentRegistration model + ContractValidator
│   └── tracing.py        # OTEL auto-trace decorator
├── pyproject.toml
└── README.md             # Quickstart: new agent in 30 minutes
```

## aep-tool-sdk

Python package providing the base class for building new tool connectors.

```
sdk/aep-tool-sdk/
├── aep_tool_sdk/
│   ├── __init__.py
│   ├── tool.py           # Abstract Tool base class
│   ├── auth.py           # Auth strategy implementations
│   ├── normaliser.py     # Base response normaliser
│   ├── rate_limit.py     # Rate limit policy enforcement
│   ├── registry.py       # ToolRegistration model + ContractValidator
│   └── errors.py         # Tool-specific error hierarchy
├── pyproject.toml
└── README.md             # Quickstart: new connector in 2 hours
```

## Usage Example (Agent SDK)

```python
from aep_sdk import Agent, AgentContext, AgentResult

class MyAgent(Agent):
    async def execute(self) -> AgentResult:
        # Request a tool by capability tag — never by tool_id
        result = await self.tools.invoke(
            capability="create-pull-request",
            params={"title": "...", "branch": "..."}
        )
        return AgentResult(output={"pr_url": result.pr_url})
```

## Usage Example (Tool SDK)

```python
from aep_tool_sdk import Tool, ToolResult

class MyVendorTool(Tool):
    async def invoke(self, capability: str, params: dict) -> ToolResult:
        # Call vendor API with scoped token from secrets-service
        token = await self.secrets.get_token(self.tool_id)
        response = await self.vendor_client.call(capability, params, token)
        # Normalise to common shape
        return self.normaliser.normalise(capability, response)
```
