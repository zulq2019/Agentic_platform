# Repository Guide

**Agentic Engineering Platform**  
**Version:** 1.1 (Architecture v2.0 repository layout)  
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
├── docs/                   ← ALL documentation (four domains)
│   ├── architecture/       ← Ontology, contracts, ADR, reference architecture
│   ├── product/            ← Vision, roadmap, commercial model (customer-facing)
│   ├── engineering/        ← Implementation roadmap, release plan, alignment
│   ├── reference/          ← Blueprints, contracts index
│   └── migration/          ← Migration reports
├── contracts/              ← JSON Schema contracts (production deliverable)
├── workflows/              ← Workflow templates (production deliverable)
├── scripts/                ← CI and developer utility scripts
└── [root docs]             ← CONSTITUTION, ARCHITECTURE, CLAUDE (+ relocation stubs)
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

A folder inside `src/` is created **at the start of its PI**, not before. The blueprint in `docs/reference/blueprints/` describes what will go there. The PI plan in `docs/engineering/implementation-roadmap/` describes when and how.

**Empty code folders are forbidden.** If it exists in `src/`, it contains production code.

---

## 2. Documentation — `docs/`

**Rule: All documentation lives in `docs/` or as root-level reference documents. Never inline with source code except for `README.md` per service.**

```
docs/
├── architecture/           ← Platform ontology (v2.0)
│   ├── PLATFORM_*.md       ← Primitives, Contracts, Meta Model, UX, Glossary
│   ├── ARCHITECTURE_BASELINE_V2.md
│   ├── REFERENCE_ARCHITECTURE.md
│   └── ADR/DECISIONS.md
│
├── product/                ← Customer-facing
│   ├── VISION.md, ROADMAP.md
│   ├── COMMERCIAL_MODEL.md, MARKETPLACE.md, SOLUTION_PACKS.md
│   └── PRODUCT_*.md
│
├── engineering/              ← Internal execution (not customer-facing)
│   ├── implementation-roadmap/   ← PI-01 through PI-10
│   ├── release-plan.md
│   ├── architecture-alignment/
│   └── sprint-history/
│
├── reference/              ← Technical reference
│   └── blueprints/         ← Future capability designs
│
└── migration/              ← Migration plans and reports
```

**Restructure report:** [REPOSITORY_RESTRUCTURE_REPORT.md](REPOSITORY_RESTRUCTURE_REPORT.md)

Legacy paths `docs/04-program/` and `docs/05-blueprints/` contain redirect READMEs only.

### Root-level reference documents

These live at the root because they apply to the entire repository:

| File | Purpose | Mutable? |
|------|---------|----------|
| `CONSTITUTION.md` | Immutable engineering principles | No |
| `ARCHITECTURE.md` | Container topology and system structure | Living |
| `CLAUDE.md` | AI implementation rules | Living |
| `DECISIONS.md` | **Stub** → [docs/architecture/ADR/DECISIONS.md](docs/architecture/ADR/DECISIONS.md) | Append-only |
| `ROADMAP.md` | **Stub** → [docs/product/ROADMAP.md](docs/product/ROADMAP.md) | Living |
| `VISION.md` | **Stub** → [docs/product/VISION.md](docs/product/VISION.md) | Living |
| `TASKS.md` | Engineering work breakdown | Living |
| `README.md` | Repository index | Living |
| `REPOSITORY_GUIDE.md` | This file — onboarding | Living |
| `REPOSITORY_RESTRUCTURE_REPORT.md` | Docs v2 layout change log | Living |

### Where does my documentation go?

| I am writing... | Goes in |
|----------------|---------|
| Sprint plan, implementation guide for a PI | `docs/engineering/implementation-roadmap/PI-XX-*/` |
| AI prompt mapping for a PI | `docs/engineering/implementation-roadmap/PI-XX-.../PROMPT_MAPPING.md` |
| Reusable AI prompt commands | `.ai/commands/` |
| Design for a future component not yet built | `docs/reference/blueprints/{component}/BLUEPRINT.md` |
| Architecture diagram | `docs/architecture/REFERENCE_ARCHITECTURE.md` |
| Architectural decision record | `DECISIONS.md` |
| API spec for a service (generated) | Service `README.md` or OpenAPI under `src/` |
| Service-level README | `src/platform/{service}/README.md` |

---

## 3. AI Engineering Assets — `.ai/`

**Rule: `.ai/` is the single source of truth for all reusable AI prompts, templates, checklists, and reviewer configurations. Never scatter AI assets across the repo.**

**PI folders do not own prompts.** Each PI contains `PROMPT_MAPPING.md` — a reference index that maps each User Story to the reusable commands stored in `.ai/commands/`.

```
.ai/
├── commands/       ← Reusable AI prompt commands — the single prompt library
│                       One file per operation, referenced by every PI
│                       Example: implement-story.md, review-story.md,
│                                generate-tests.md, security-review.md,
│                                performance-review.md, update-documentation.md,
│                                release-story.md
│
├── templates/      ← Starting-point code and document templates for AI scaffolding
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

See `.ai/README.md` for the full prompt lifecycle, naming convention, and how engineers use the library.

### How PI folders reference prompts

Each PI contains `PROMPT_MAPPING.md` — not prompts themselves. The mapping file lists each User Story and links it to the relevant `.ai/commands/` files with PI-specific context.

One change to `.ai/commands/implement-story.md` improves all ten PIs simultaneously.

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
    ... (7 more — see docs/reference/blueprints/workflow-templates/BLUEPRINT.md)
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
- [ ] Read `docs/engineering/implementation-roadmap/PI-01-Platform-Core/README.md` — understand what is being built now
- [ ] Read `docs/engineering/implementation-roadmap/PI-01-Platform-Core/IMPLEMENTATION.md` — understand the code patterns
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
| What am I building this sprint? | `docs/engineering/implementation-roadmap/PI-0X-.../SPRINT_PLAN.md` |
| How do I implement X? | `docs/engineering/implementation-roadmap/PI-0X-.../IMPLEMENTATION.md` |
| What AI prompts should I use? | `.ai/commands/` (prompt library) and the current PI's `PROMPT_MAPPING.md` |
| What does a future component look like? | `docs/reference/blueprints/{component}/BLUEPRINT.md` |
| Why was this decision made? | `DECISIONS.md` |
| What is the full architecture diagram? | `docs/architecture/REFERENCE_ARCHITECTURE.md` |
