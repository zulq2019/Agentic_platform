# PI-06 — Sprint Plan

## Sprint 20–21 (Days 191–210): Greenfield Agents

| Agent | Sprint | Key Capability |
|-------|--------|----------------|
| `requirement-agent` | 20 | Analyses PRD, produces scope document |
| `architecture-agent` | 20 | Designs system architecture, produces ADR |
| `discovery-agent` | 21 | Reads codebase via tool, maps structure |
| `dependency-analysis-agent` | 21 | Analyses package deps, flags conflicts |

**Sprint Goal:** Greenfield workflow agents 1–4 complete with contract tests.

---

## Sprint 22–23 (Days 211–230): Development Agents

| Agent | Sprint | Key Capability |
|-------|--------|----------------|
| `backend-agent` | 22 | Generates backend code, creates PR via tool |
| `frontend-agent` | 22 | Generates frontend components, creates PR |
| `testing-agent` | 23 | Generates unit + integration tests |
| `regression-agent` | 23 | Runs test suite, reports results |

**Sprint Goal:** Code generation agents create real PRs in a test repository.

---

## Sprint 24 (Days 231–240): Quality + Release Agents

| Agent | Key Capability |
|-------|----------------|
| `security-agent` | Triggers Snyk/SonarQube via tool, produces report |
| `performance-agent` | Triggers load test, parses results |
| `review-agent` | Reviews PR diff, posts comments via tool |
| `release-agent` | Creates GitHub release, updates changelog |

---

## Sprint 25 (Days 241–250): Specialist + PI-06 Close

| Agent | Key Capability |
|-------|----------------|
| `documentation-agent` | Generates docs, pushes to Confluence via tool |
| `migration-agent` | Plans and generates DB migration scripts |
| `root-cause-agent` | Analyses incident timeline, produces RCA |

- End-to-end greenfield workflow with all 15 agents
- All 15 agents: idempotency verified, contract tests passing
- PI-06 retrospective
