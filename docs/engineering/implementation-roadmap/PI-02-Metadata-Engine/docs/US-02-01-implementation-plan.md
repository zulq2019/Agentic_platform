# US-02.01 — Platform Object Framework — Implementation Plan

**Story:** US-02.01  
**PI:** PI-02 Metadata Engine  
**Status:** In progress  
**Authority:** [PLATFORM_PRIMITIVES.md](../../../../architecture/PLATFORM_PRIMITIVES.md) §3 · [PLATFORM_CONTRACTS.md](../../../../architecture/PLATFORM_CONTRACTS.md) §4

---

## Objective

Implement the universal **Platform Object** abstraction — identity, metadata, configuration, lifecycle, versioning, relationships, dependencies, security, audit, metrics, health, and extension points — as a **generic, business-agnostic** library and contract.

---

## Architecture approach

| Layer | Location | Pattern |
|-------|----------|---------|
| Contract | `contracts/platform-object.schema.json` | JSON Schema Draft 2020-12 |
| Domain | `src/shared/aep_meta/aep_meta/domain/` | DDD aggregates + value objects |
| Application | `src/shared/aep_meta/aep_meta/application/` | Use cases, validation orchestration |
| Ports | `src/shared/aep_meta/aep_meta/domain/ports.py` | Hexagonal interfaces |
| Adapters | `src/shared/aep_meta/aep_meta/infrastructure/` | Schema validator, in-memory + Postgres repos |
| Service | `src/platform/services/metadata-engine/` | FastAPI REST host (thin adapter) |
| Persistence | `migrations/versions/006_platform_object_tables.py` | `metadata` schema, RLS |

**No business-specific logic** in domain or application layers.

---

## Deliverables mapping

| # | Deliverable | Implementation |
|---|-------------|----------------|
| 1 | Base model | `PlatformObject` aggregate |
| 2 | Interfaces | `ports.py` repository + audit + metrics |
| 3–11 | Sub-models | `identity`, `metadata`, `configuration`, `lifecycle`, `versioning`, `relationships`, `dependencies`, `security`, `observability` |
| 12 | Validation | `PlatformObjectValidator` + JSON Schema adapter |
| 13 | Unit tests | `src/shared/aep_meta/tests/` |
| 14 | Integration tests | `src/tests/integration/test_us_02_01_platform_object.py` |
| 15 | Diagrams | `docs/.../diagrams/platform-object-framework.md` |
| 16 | ADR | ADR-028 in `docs/architecture/ADR/DECISIONS.md` |
| 17 | Documentation | STATUS, CHANGELOG, METRICS, story updates |

---

## Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| PI-01 spine (`aep-common`, migrations, RLS helpers) | Complete | Required |
| `jsonschema` | In aep_common kafka extras | Schema validation |
| PostgreSQL `metadata` schema | New migration 006 | Persistence |
| `platform-object.schema.json` | This story | CI contract validation |

**No dependency** on agent-runtime, orchestrator, or Provider Contract (G-02) for US-02.01.

---

## Risks

| ID | Risk | Mitigation |
|----|------|------------|
| R1 | Schema too rigid for extensibility | `custom_metadata` + `additionalProperties` on annotation buckets |
| R2 | PI-02 docs still reference Agent Runtime | Update STATUS + US-02.01 only; broader doc refresh separate |
| R3 | Scope creep into publish/registry MVP | US-02.01 stops at framework + validate + persist API |
| R4 | Circular dependency false positives | Publish-time only; unit tests for DAG detection |

---

## Out of scope (US-02.01)

- Metadata Engine publish/registry index (later story)
- Provider Contract unification (PI-09 / G-02)
- Kafka events for lifecycle (interface only; emission in later story)
- UI / Builder UX

---

## Verification

```bash
pip install -e "src/shared/aep_meta[dev]" -e "src/shared/aep_common[health]"
ruff check src/shared/aep_meta src/platform/services/metadata-engine
pytest src/shared/aep_meta/tests src/tests/integration/test_us_02_01_platform_object.py -v
python scripts/validate_contract.py platform contracts/examples/sample-platform-object.json
```
