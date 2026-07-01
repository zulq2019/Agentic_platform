# PI-06 — Engineering Agents

**Status:** `PLANNED`  
**Depends on:** PI-03 + PI-05 complete (orchestrator + tool registry operational)  
**Target:** Sprint 20–25 (weeks 39–50)  
**Architecture baseline:** [ARCHITECTURE_BASELINE_V2.md](../../architecture/ARCHITECTURE_BASELINE_V2.md). Specialist agents are **`ai-agent` Providers** registered via Agent Registry; tools resolved as **connector Providers** by capability tag.

## Architecture v2 alignment

| Field | Value |
|-------|-------|
| **Classification** | Extended |
| **v2 concept** | ai-agent Provider catalog |
| **Report** | [ARCHITECTURE_ALIGNMENT_REPORT.md](../../engineering/ARCHITECTURE_ALIGNMENT_REPORT.md) |
| **Migration note** | aep-agent-sdk unchanged. Execution Profile refs additive when PI-09 schema lands. |

---

## What This PI Delivers

All 15 specialist agents that power the platform's engineering workflows:

| Agent | Capability Tags | Cost Class |
|-------|----------------|-----------|
| `requirement-agent` | `analyses-requirements`, `produces-scope-document` | medium |
| `architecture-agent` | `designs-architecture`, `produces-adr` | high |
| `discovery-agent` | `discovers-codebase`, `maps-dependencies` | medium |
| `dependency-analysis-agent` | `analyses-dependencies`, `identifies-conflicts` | low |
| `backend-agent` | `generates-backend-code`, `creates-pull-request` | high |
| `frontend-agent` | `generates-frontend-code`, `creates-pull-request` | high |
| `testing-agent` | `generates-unit-tests`, `generates-integration-tests` | medium |
| `regression-agent` | `runs-regression-suite`, `reports-test-results` | low |
| `security-agent` | `scans-for-vulnerabilities`, `produces-security-report` | high |
| `performance-agent` | `runs-load-tests`, `produces-performance-report` | medium |
| `documentation-agent` | `generates-documentation`, `updates-confluence` | low |
| `review-agent` | `reviews-pull-request`, `posts-review-comments` | medium |
| `release-agent` | `creates-release`, `updates-changelog` | low |
| `migration-agent` | `plans-migration`, `generates-migration-scripts` | high |
| `root-cause-agent` | `analyses-incident`, `produces-rca-report` | high |

## Key Constraints

- Every agent inherits from `aep-agent-sdk` base Agent class
- Every agent passes contract validation before registration
- Every agent implements idempotency_key_strategy
- No agent imports a vendor SDK directly
- No agent calls another agent
