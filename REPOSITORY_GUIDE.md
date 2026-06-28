# Repository Guide

**Agentic Engineering Platform**  
**Version:** 1.0  
**Audience:** Every engineer, AI assistant, and contributor working in this repository  
**Authority:** [CONSTITUTION.md](CONSTITUTION.md) · [CLAUDE.md](CLAUDE.md) · [ARCHITECTURE.md](ARCHITECTURE.md)

---

> Read this guide before writing a single line of code.  
> It answers: where does my code go, where does my documentation go, and where do AI assets live?

---

## Repository at a Glance

```
agentic-engineering-platform/
│
├── src/                    ← ALL production code lives here. Nowhere else.
├── .ai/                    ← AI engineering assets (prompts, templates, checklists)
├── docs/                   ← ALL documentation lives here
│   ├── 04-program/         ← Engineering execution plans (PI-01 → PI-10)
│   ├── 05-blueprints/      ← Future capability designs
│   ├── artifacts/          ← Architecture diagrams
│   └── reference/          ← Source reference architecture
├── contracts/              ← JSON Schema contracts (production deliverable)
├── workflows/              ← Workflow templates (production deliverable)
├── scripts/                ← CI and developer utility scripts
└── [root docs]             ← CONSTITUTION, ARCHITECTURE, CLAUDE, DECISIONS, etc.
```

---

## 1. Source Code — `src/`

**Rule: No implementation code exists outside `src/`. No exceptions.**

```
src/
├── platform/               ← The 16 platform microservices
│   ├── gateway/            ← API Gateway (Go + Echo) — request routing, rate limiting, TLS
│   ├── orchestrator/       ← Orchestrator Service — planner, gate enforcer, dispatcher
│   ├── workflow/           ← Workflow Engine — state machine templates and transitions
│   ├── task/               ← Task Engine — durable task persistence and scheduling
│   ├── runtime/            ← Agent Runtime — agent execution host
│   ├── registry/           ← Agent Registry + Tool Registry + Model Router
│   └── services/           ← All remaining platform services:
│                               auth-service, rbac-service, approval-service,
│                               memory-service, audit-service, secrets-service,
│                               policy-engine, config-service
│
├── sdk/                    ← Developer SDKs
│   │                           aep-agent-sdk — base class all agents inherit
│   │                           aep-tool-sdk  — base class for tool connectors
│
├── agents/                 ← 15 specialist agents
│   │                           Each agent inherits from aep-agent-sdk.
│   │                           One directory per agent: {agent-name}.agent.py + registration.json
│
├── tools/                  ← 11 external tool connectors
│   │                           Each connector inherits from aep-tool-sdk.
│   │                           One directory per tool: {tool-name}.tool.py + registration.json
│
├── shared/                 ← Shared code imported across platform services
│   │                           aep-common: logging, health, kafka, schemas, tracing, errors
│
└── tests/                  ← All tests
        unit/               ← Unit tests, mirroring src/ structure
        integration/        ← Cross-service integration tests
        contract/           ← Agent and tool contract validation tests
        load/               ← k6 / Locust load test scripts
        chaos/              ← Chaos engineering test scenarios
```

### Which folder does my code go in?

| I am building... | Goes in |
|-----------------|---------|
| API Gateway, ingress routing | `src/platform/gateway/` |
| Orchestrator, planner, gate enforcer | `src/platform/orchestrator/` |
| Workflow state machine | `src/platform/workflow/` |
| Task persistence and scheduling | `src/platform/task/` |
| Agent execution host | `src/platform/runtime/` |
| Agent Registry, Tool Registry, Model Router | `src/platform/registry/` |
| Auth, RBAC, Approval, Memory, Audit, Secrets, Policy, Config | `src/platform/services/` |
| Agent SDK base class | `src/sdk/` |
| Tool SDK base class | `src/sdk/` |
| A specialist agent | `src/agents/` |
| A tool connector | `src/tools/` |
| Shared utility (logging, kafka, health) | `src/shared/` |
| Any test | `src/tests/` |

### When is a `src/` folder created?

A folder inside `src/` is created **at the start of its PI**, not before. The blueprint in `docs/05-blueprints/` describes what will go there. The PI plan in `docs/04-program/` describes when and how.

**Empty code folders are forbidden.** If it exists in `src/`, it contains production code.

---

## 2. Documentation — `docs/`

**Rule: All documentation lives in `docs/` or as root-level reference documents. Never inline with source code except for `README.md` per service.**

```
docs/
├── 04-program/             ← Engineering execution plans
│   └── PI-01 through PI-10
│       Each PI contains 16 documents:
│       README, OBJECTIVES, FEATURES, USER_STORIES,
│       ACCEPTANCE_CRITERIA, IMPLEMENTATION, PROMPTS,
│       SPRINT_PLAN, TESTING, RISKS, DEFINITION_OF_DONE,
│       API_SPEC, SEQUENCE_DIAGRAMS, DATA_MODEL,
│       REVIEW_CHECKLIST, DEMO
│
├── 05-blueprints/          ← Future capability designs (replaces empty code folders)
│   └── {capability}/BLUEPRINT.md
│       platform-services, agent-runtime, specialist-agents,
│       tool-connectors, agent-sdk, tool-sdk, frontend-dashboard,
│       infra-terraform, infra-kubernetes, observability-stack,
│       workflow-templates
│
├── artifacts/              ← Architecture diagrams
│   └── TECHNICAL_ARCHITECTURE.md  ← 25 architecture diagrams, all styles
│
├── reference/              ← Source reference architecture (read-only)
│   └── *.docx
│
└── MIGRATION_PLAN.md       ← Repository reorganisation rationale
```

### Root-level reference documents

These live at the root because they apply to the entire repository:

| File | Purpose | Mutable? |
|------|---------|----------|
| `CONSTITUTION.md` | Immutable engineering principles | No |
| `ARCHITECTURE.md` | Long-term system architecture | Living |
| `CLAUDE.md` | AI implementation rules | Living |
| `DECISIONS.md` | ADR repository | Append-only |
| `ROADMAP.md` | Delivery phases | Living |
| `TASKS.md` | Engineering work breakdown | Living |
| `VISION.md` | Product vision | Living |
| `README.md` | Repository index | Living |
| `REPOSITORY_GUIDE.md` | This file — onboarding | Living |

### Where does my documentation go?

| I am writing... | Goes in |
|----------------|---------|
| Sprint plan, implementation guide, AI prompts for a PI | `docs/04-program/PI-XX-*/` |
| Design for a future component not yet built | `docs/05-blueprints/{component}/BLUEPRINT.md` |
| Architecture diagram | `docs/artifacts/TECHNICAL_ARCHITECTURE.md` |
| Architectural decision record | `DECISIONS.md` |
| API spec for a service (generated) | `docs/artifacts/` or service `README.md` |
| Service-level README | `src/platform/{service}/README.md` |

---

## 3. AI Engineering Assets — `.ai/`

**Rule: All AI assistant assets — prompts, templates, checklists, reviewer configurations — live in `.ai/`. Never scattered across the repo.**

```
.ai/
├── commands/       ← Reusable AI prompt commands (slash commands, macros)
│                       Example: /implement-agent, /write-migration, /review-pr
│
├── templates/      ← Code and document templates for AI to use as starting points
│                       Example: agent-template.py, service-scaffold.py,
│                                migration-template.py, test-template.py
│
├── checklists/     ← Structured checklists AI runs before declaring work done
│                       Example: pre-commit.md, pre-merge.md,
│                                constitutional-compliance.md, security.md
│
└── reviewers/      ← AI reviewer configurations and personas
                        Example: security-reviewer.md, arch-reviewer.md,
                                 constitution-reviewer.md
```

`.ai/` is populated progressively during PI-01 and PI-02. Do not create files there without a clear prompt or checklist to put in them.

---

## 4. Contracts — `contracts/`

**Rule: JSON Schema contracts are production deliverables. They are validated in CI on every pull request.**

```
contracts/
├── agent-contract.schema.json      ← Every agent must satisfy this
├── tool-contract.schema.json       ← Every tool must satisfy this
├── task-schema.schema.json         ← Task structure between orchestrator and agents
├── memory-schema.schema.json       ← Long-term memory entry structure
├── event-envelope.schema.json      ← Every Kafka message must satisfy this
├── common-tool-responses.schema.json  ← Normalised tool response shapes
├── examples/
│   └── coding-agent-registration.json
└── README.md
```

Never modify a contract schema without:
1. Bumping the `contract_version`
2. Creating an ADR in `DECISIONS.md`
3. Updating all implementations that reference it

---

## 5. Workflow Templates — `workflows/`

**Rule: Workflow templates are production deliverables. Never modify an existing template. Create a new version instead.**

```
workflows/
└── greenfield-v1.0.0.json      ← Complete and operational
    brownfield-v1.0.0.json      ← Planned (PI-05)
    defect-resolution-v1.0.0.json
    ... (7 more — see docs/05-blueprints/workflow-templates/BLUEPRINT.md)
```

---

## 6. Utility Scripts — `scripts/`

Developer and CI utility scripts. Not application code.

```
scripts/
└── validate_contract.py    ← Validates all contracts/ schemas. Runs in CI.
```

Add scripts here when they support CI, developer workflow, or operational tasks.

---

## Onboarding Checklist for New Engineers

Before writing your first line of code:

- [ ] Read `CONSTITUTION.md` — understand what can never be violated
- [ ] Read `CLAUDE.md` — understand coding standards and forbidden patterns
- [ ] Read `ARCHITECTURE.md` — understand the system you are building
- [ ] Read `docs/04-program/PI-01-Platform-Spine/README.md` — understand what is being built now
- [ ] Read `docs/04-program/PI-01-Platform-Spine/IMPLEMENTATION.md` — understand the code patterns
- [ ] Run `make dev-up` (once PI-01 is complete) — verify your local environment
- [ ] Run `python scripts/validate_contract.py contracts/` — verify contracts pass

---

## Golden Rules — Never Forget

| Rule | Why |
|------|-----|
| All code in `src/` | Nothing is lost, nothing is scattered |
| All docs in `docs/` or root | Single source of truth for every decision |
| All AI assets in `.ai/` | Reusable, reviewable, version-controlled |
| No empty code folders | An empty folder lies about what is built |
| No vendor SDK imports in agent code | Tools abstract all vendors |
| No agent calls another agent | Events only — Constitution A1 |
| No credentials in code | Always `process.env` / environment variables |
| Every table has RLS | Tenant isolation at the storage layer |
| Every Kafka message uses EventEnvelope | Consistency across all event flows |
| No gate bypass exists | Human approval is non-negotiable — Constitution H2 |

---

## Getting Help

| Question | Where to look |
|----------|--------------|
| What are the platform principles? | `CONSTITUTION.md` |
| How does the system work? | `ARCHITECTURE.md` |
| What am I building this sprint? | `docs/04-program/PI-0X-.../SPRINT_PLAN.md` |
| How do I implement X? | `docs/04-program/PI-0X-.../IMPLEMENTATION.md` |
| What AI prompts should I use? | `docs/04-program/PI-0X-.../PROMPTS.md` and `.ai/commands/` |
| What does a future component look like? | `docs/05-blueprints/{component}/BLUEPRINT.md` |
| Why was this decision made? | `DECISIONS.md` |
| What is the full architecture diagram? | `docs/artifacts/TECHNICAL_ARCHITECTURE.md` |
