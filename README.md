# Agentic Engineering Platform

**Version:** 1.0 · **Date:** 27 June 2026

Vendor-neutral, reusable blueprint for multi-agent software engineering — Greenfield and Brownfield, built to scale to thousands of engineers.

---

## Repository Structure

```
agentic-engineering-platform/
├── CONSTITUTION.md          # Immutable principles (NEVER violate)
├── VISION.md                # Product vision, personas, market, 5-year roadmap
├── ARCHITECTURE.md          # C4 diagrams, contracts, deployment, data flow
├── ROADMAP.md               # MVP → Alpha → Beta → Enterprise → GA
├── TASKS.md                 # Engineering work breakdown
├── CLAUDE.md                # AI-assisted implementation rules
├── DECISIONS.md             # Architectural Decision Records (24 ADRs)
├── contracts/               # JSON Schema contract definitions
│   ├── agent-contract.schema.json
│   ├── tool-contract.schema.json
│   ├── task-schema.schema.json
│   ├── memory-schema.schema.json
│   ├── event-envelope.schema.json
│   ├── common-tool-responses.schema.json
│   ├── examples/
│   └── README.md
├── workflows/               # Versioned workflow templates
│   └── greenfield-v1.0.0.json
├── scripts/
│   └── validate_contract.py
├── requirements-dev.txt
└── docs/reference/          # Source reference architecture (local)
```

---

## Read Order for New Contributors

1. [CONSTITUTION.md](./CONSTITUTION.md) — what MUST NEVER be violated
2. [VISION.md](./VISION.md) — why the platform exists
3. [ARCHITECTURE.md](./ARCHITECTURE.md) — how it is structured
4. [DECISIONS.md](./DECISIONS.md) — why specific choices were made
5. [contracts/README.md](./contracts/README.md) — contract schemas and validation
6. [CLAUDE.md](./CLAUDE.md) — how to implement correctly
7. [ROADMAP.md](./ROADMAP.md) — when things get built
8. [TASKS.md](./TASKS.md) — what to build next

---

## Source of Truth Hierarchy

| Document | Role | Mutable? |
|----------|------|----------|
| Reference Architecture v1.0 (`.docx`) | Original blueprint | No — reference only |
| [CONSTITUTION.md](./CONSTITUTION.md) | Immutable engineering philosophy | Only via Decision Record |
| [DECISIONS.md](./DECISIONS.md) | Recorded architectural decisions | Append-only (supersede, don't edit) |
| [contracts/](./contracts/) | Machine-readable contract validation | Versioned (semver) |
| All other documents | Living implementation guidance | Yes |

---

## Quick Start

### Local development (PI-01)

Prerequisites: **Git**, **Docker Desktop**, **Python 3.12+**

```bash
git clone https://github.com/zulq2019/Agentic_platform.git
cd Agentic_platform
pip install -e "src/shared/aep_common[health,kafka]" pytest pytest-asyncio httpx
make dev-up
```

`make dev-up` starts all 16 platform services plus Postgres (pgvector), Redis, Kafka, OTEL Collector, Prometheus, and Grafana. Host-side Kafka scripts use **`localhost:9094`** (containers use `kafka:9092`). It then verifies:

- All 16 `/health/live` endpoints return HTTP 200 within 60 seconds
- Kafka topics provisioned (`scripts/verify_kafka_topology.py` exits 0)
- Prometheus (`http://localhost:9090`), Grafana (`http://localhost:3001`), and OTEL Collector are healthy

| URL | Purpose |
|-----|---------|
| http://localhost:8080/health/live | API Gateway |
| http://localhost:8001–8015/health/live | Platform services |
| http://localhost:9090 | Prometheus metrics |
| http://localhost:3001 | Grafana (admin / admin — local dev only) |
| http://localhost:4317 | OTEL Collector (gRPC) |
| http://localhost:9094 | Kafka (host access; containers use `kafka:9092`) |

Stop the stack: `make dev-down`  
Tail logs: `make dev-logs`  
Re-check health: `make dev-status`

### Validate a contract

```bash
pip install -r requirements-dev.txt
python scripts/validate_contract.py agent contracts/examples/coding-agent-registration.json
```

### Six Constitutional Invariants

1. Agents never call agents
2. Orchestrator plans, never executes
3. New agents plug in, never patch in
4. Humans approve, agents propose
5. Every decision is reconstructable
6. Vendor-neutral by construction

---

## Document Index

| File | Description |
|------|-------------|
| [CONSTITUTION.md](./CONSTITUTION.md) | Platform constitution (83 principles) |
| [VISION.md](./VISION.md) | Product vision, personas, competitive landscape |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | C4, deployment, event model, security, memory |
| [ROADMAP.md](./ROADMAP.md) | MVP through GA, milestones, risks |
| [TASKS.md](./TASKS.md) | 12 epics, ~520 person-days |
| [CLAUDE.md](./CLAUDE.md) | AI implementation rules, forbidden patterns |
| [DECISIONS.md](./DECISIONS.md) | 24 ADRs |

---

*Derived from Agentic Engineering Platform Reference Architecture v1.0*
