# Blueprint: 15 Specialist Agents

**Status:** DEFERRED — Implemented in PI-06  
**Target PI:** PI-06-Studio-Framework  
**Depends on:** PI-03 (Orchestrator) + PI-05 (Tool Registry) complete

## Purpose

This blueprint documents all 15 specialist agents, their capabilities, required tools, and cost classification.

## Agent Inventory

| Agent ID | Capabilities | Required Tools | Cost Class | Approval Required |
|----------|-------------|----------------|-----------|------------------|
| `requirement-agent` | `analyses-requirements`, `produces-scope-document` | `create-issue`, `update-issue` | medium | false |
| `architecture-agent` | `designs-architecture`, `produces-adr` | `create-page`, `create-issue` | high | true |
| `discovery-agent` | `discovers-codebase`, `maps-dependencies` | `read-repository`, `read-files` | medium | false |
| `dependency-analysis-agent` | `analyses-dependencies`, `identifies-conflicts` | `read-repository` | low | false |
| `backend-agent` | `generates-backend-code`, `creates-pull-request` | `create-branch`, `commit-files`, `create-pull-request` | high | false |
| `frontend-agent` | `generates-frontend-code`, `creates-pull-request` | `create-branch`, `commit-files`, `create-pull-request` | high | false |
| `testing-agent` | `generates-unit-tests`, `generates-integration-tests` | `create-branch`, `commit-files` | medium | false |
| `regression-agent` | `runs-regression-suite`, `reports-test-results` | `trigger-pipeline`, `read-test-results` | low | false |
| `security-agent` | `scans-for-vulnerabilities`, `produces-security-report` | `trigger-security-scan`, `read-scan-results` | high | true |
| `performance-agent` | `runs-load-tests`, `produces-performance-report` | `trigger-load-test`, `read-test-results` | medium | false |
| `documentation-agent` | `generates-documentation`, `updates-confluence` | `create-page`, `update-page` | low | false |
| `review-agent` | `reviews-pull-request`, `posts-review-comments` | `read-pull-request`, `create-review-comment` | medium | false |
| `release-agent` | `creates-release`, `updates-changelog` | `create-release`, `update-page` | low | true |
| `migration-agent` | `plans-migration`, `generates-migration-scripts` | `read-repository`, `create-branch`, `commit-files` | high | true |
| `root-cause-agent` | `analyses-incident`, `produces-rca-report` | `read-logs`, `read-metrics`, `create-page` | high | true |

## Directory Structure (created in PI-06)

```
agents/
├── echo-agent/           # Reference implementation (created PI-02)
├── requirement-agent/    # Sprint 20
├── architecture-agent/   # Sprint 20
├── discovery-agent/      # Sprint 21
├── dependency-analysis-agent/ # Sprint 21
├── backend-agent/        # Sprint 22
├── frontend-agent/       # Sprint 22
├── testing-agent/        # Sprint 23
├── regression-agent/     # Sprint 23
├── security-agent/       # Sprint 24
├── performance-agent/    # Sprint 24
├── review-agent/         # Sprint 24
├── release-agent/        # Sprint 24
├── documentation-agent/  # Sprint 25
├── migration-agent/      # Sprint 25
└── root-cause-agent/     # Sprint 25
```

## Agent Directory Structure

Each agent follows this layout:
```
agents/{agent-name}/
├── {agent_name}.agent.py   # Inherits from aep_sdk.Agent
├── registration.json        # Agent Contract (validated against agent-contract.schema.json)
├── prompts/
│   └── system_prompt.txt    # LLM system prompt
├── tests/
│   ├── test_contract.py     # Contract validation
│   ├── test_idempotency.py  # Retry does not duplicate side effects
│   └── test_tool_resolution.py # Tool resolved by capability, not ID
└── pyproject.toml
```

## Idempotency Strategy Per Agent

| Agent | Idempotency Key Strategy |
|-------|------------------------|
| `backend-agent` | `task_id + branch_name` |
| `testing-agent` | `task_id + test_suite_name` |
| `release-agent` | `task_id + release_tag` |
| All others | `task_id` (sufficient for their operations) |
