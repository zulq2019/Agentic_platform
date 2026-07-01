# Blueprint: Agent Runtime & SDK

**Status:** DEFERRED — Implemented in PI-02  
**Target PI:** PI-02-Metadata-Engine

## Purpose

This blueprint describes the agent execution architecture and the `aep-agent-sdk` Python package that all specialist agents inherit from.

## Components

### agent-runtime service
- Kafka consumer for `aep.task.created`
- AgentLoader — dynamic import and contract validation
- AgentExecutor — runs the agent lifecycle
- IdempotencyKeyResolver — prevents duplicate side effects
- 3-tier retry (Tier 1: exponential backoff)

### agent-registry service
- POST /agents — register agent with contract validation
- GET /agents?capability={tag} — capability-based discovery
- Redis capability index for fast lookup

### model-router service
- Routes tasks to low/medium/high model tiers based on cost_class
- Per-tenant token quota enforcement via Redis

### aep-agent-sdk (Python package)
```
sdk/aep-agent-sdk/
└── aep_sdk/
    ├── agent.py          # Abstract base Agent class
    ├── context.py        # AgentContext type
    ├── result.py         # AgentResult type
    ├── tools.py          # ToolClient — by capability tag
    ├── memory.py         # MemoryClient — working + LTM
    ├── events.py         # EventClient — publishes AgentStarted/Completed/Failed
    ├── retry.py          # Exponential backoff + jitter
    ├── security.py       # Policy check + scoped token
    ├── metrics.py        # Auto-metrics per agent operation
    ├── registry.py       # AgentRegistration model + validator
    └── tracing.py        # Auto-trace every agent method
```

## Key Design Decisions

- Agents NEVER call other agents directly (Constitution A1)
- Model selection is in model-router, NOT in agent code (Constitution MI3)
- No vendor SDK imports in agent code — tools abstract all vendors (Constitution AP5)
- SDK auto-instruments every agent — zero observability boilerplate for agent authors

## Agent Contract Requirements

Every agent must declare:
- `agent_id` (kebab-case)
- `capabilities` (verb-noun tags)
- `input_schema` (JSON Schema string)
- `output_schema` (JSON Schema string)
- `required_tools` (capability tags, not tool IDs)
- `cost_class` (low / medium / high)
- `idempotency_key_strategy`

See `contracts/agent-contract.schema.json` for the authoritative schema.

## Reference Implementation

`agents/echo-agent/` — a minimal reference agent demonstrating all SDK features.
Created at the start of PI-02. Every new agent follows this pattern.
