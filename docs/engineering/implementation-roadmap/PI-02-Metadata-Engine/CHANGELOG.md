# PI-02 — Metadata Engine — CHANGELOG

## [0.1.0] — 2026-07-01

### Added (US-02.01)

- `contracts/platform-object.schema.json` v1.0.0 — universal Platform Object envelope
- `contracts/examples/sample-platform-object.json` — reference capability object
- `aep_meta` shared library — domain models, lifecycle FSM, validation, ports
- `metadata-engine` service — REST API for register, get, list, lifecycle transitions
- Alembic migration `006_platform_object_tables` — `metadata` schema with RLS
- ADR-028 — Platform Object framework in `aep_meta`
- 12 automated tests (unit + API integration)

### Notes

- Postgres repository adapter deferred to next story; in-memory repository used at runtime
- PI README still references legacy Agent Runtime scope — rename tracked separately
