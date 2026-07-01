# Platform Contracts

JSON Schema definitions for every platform contract defined in Reference Architecture v1.0 Sections 6–10.

These schemas are the **validation authority** for Agent Registry, Tool Registry, Task Queue, Memory Store, and Event Bus implementations.

## Schemas

| Schema | RA Section | Purpose |
|--------|-----------|---------|
| [agent-contract.schema.json](./agent-contract.schema.json) | Section 6 | Specialist agent registration |
| [tool-contract.schema.json](./tool-contract.schema.json) | Section 7 | External system integration |
| [task-schema.schema.json](./task-schema.schema.json) | Section 8 | Orchestrator ↔ agent work unit |
| [memory-schema.schema.json](./memory-schema.schema.json) | Section 9 | Long-term memory entries |
| [event-envelope.schema.json](./event-envelope.schema.json) | Section 10 | Event Bus message envelope |
| [common-tool-responses.schema.json](./common-tool-responses.schema.json) | Section 7 | Normalised tool response shapes |
| [platform-object.schema.json](./platform-object.schema.json) | PLATFORM_PRIMITIVES §3 | Universal Platform Object envelope (v2) |

## Versioning

- Contract schemas use semantic versioning in `$id` and `contract_version` fields.
- **Patch:** Documentation or non-breaking constraint relaxation.
- **Minor:** Additive fields (optional only).
- **Major:** Breaking field changes — requires platform major version and ADR.

Current contract version: **1.0.0**

## Validation

Validate a document against a schema:

```bash
npx ajv-cli validate -s contracts/agent-contract.schema.json -d path/to/agent-registration.json --spec=draft2020
```

Or with Python:

```bash
pip install jsonschema
python scripts/validate_contract.py agent path/to/agent-registration.json
```

## Rules (from Constitution)

1. Agents MUST validate against `agent-contract.schema.json` at registration.
2. Tools MUST validate against `tool-contract.schema.json` at registration.
3. Tasks MUST validate against `task-schema.schema.json` before dispatch.
4. Memory writes MUST validate against `memory-schema.schema.json`.
5. Events MUST validate against `event-envelope.schema.json` before publish.
6. Tool responses MUST normalise to shapes in `common-tool-responses.schema.json`.

## Related Documents

- [ARCHITECTURE.md](../ARCHITECTURE.md) — system structure
- [docs/architecture/ARCHITECTURE_BASELINE_V2.md](../docs/architecture/ARCHITECTURE_BASELINE_V2.md) — implementation baseline
- [CLAUDE.md](../CLAUDE.md) — implementation rules
- [DECISIONS.md](../../docs/architecture/ADR/DECISIONS.md) — ADR-003, ADR-007, ADR-020

## Baseline v2 schema roadmap (PI-09)

| Planned schema | Purpose | Gap ID | Target PI |
|----------------|---------|--------|-----------|
| `provider-contract.schema.json` | Unified Provider registration (`ai-agent`, `connector`, etc.) | G-02 | PI-09 |
| `platform-object.schema.json` | Universal Platform Object envelope | G-05 | **PI-02 (US-02.01) — implemented** |
| `execution-profile.schema.json` | Execution Profile metadata | G-04 | PI-09 |

v1 schemas (`agent-contract`, `tool-contract`) remain valid until Provider Contract MINOR maps both kinds. See [ARCHITECTURE_CHANGELOG_V2.md](../docs/architecture/ARCHITECTURE_CHANGELOG_V2.md) migration guidance.
