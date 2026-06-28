# Blueprint: Tool SDK

**Status:** DEFERRED — Implemented in PI-05  
**Target PI:** PI-05-Tool-Registry (Sprint 19)

## Purpose

Python SDK enabling third parties to build new tool connectors without understanding the platform internals.

## Package Structure

```
sdk/aep-tool-sdk/
├── aep_tool_sdk/
│   ├── __init__.py
│   ├── tool.py             # Abstract Tool base class
│   ├── auth.py             # Auth strategy: OAuth2, PAT, APIKey, GitHubApp, ManagedIdentity
│   ├── normaliser.py       # Base normaliser + shape validators
│   ├── rate_limit.py       # Rate limit policy enforcement
│   ├── registry.py         # ToolRegistration model + ContractValidator
│   ├── scope.py            # Scope ceiling enforcement
│   └── errors.py           # ToolError hierarchy
├── pyproject.toml
└── README.md
```

## Key Design Constraints

- No vendor SDK imports in tool base class — only in concrete implementations
- Scope ceiling enforced by SDK, not by application code
- Every tool invocation fetches a fresh short-lived token via secrets-service
- Response normaliser is mandatory — cannot return raw vendor response

## Usage Example

```python
from aep_tool_sdk import Tool, ToolResult

class GitHubTool(Tool):
    async def invoke(self, capability: str, params: dict) -> ToolResult:
        if capability == "create-pull-request":
            return await self._create_pr(params)
        raise UnsupportedCapabilityError(capability)

    async def _create_pr(self, params: dict) -> ToolResult:
        token = await self.secrets.get_token(self.tool_id)  # TTL 15 min
        response = await github_api.create_pr(params, token)
        return self.normaliser.normalise("pull_request", response)
        # Returns: {"pr_id": ..., "pr_url": ..., "status": ..., "branch": ...}
```

## Tool Contract Fields

See `contracts/tool-contract.schema.json` for the full schema:
- `tool_id` — kebab-case, env-qualified
- `capability_tags` — what the tool can do
- `auth_strategy` — how credentials are obtained
- `scope` — read / write / admin (minimum required)
- `rate_limit_policy` — requests per minute per tenant
- `response_normaliser` — maps vendor shape to common shape
- `contract_version`
