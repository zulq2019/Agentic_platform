# PI-01 — Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R01 | Kafka KRaft mode instability in local Docker | Medium | High | Pin Kafka version; test on CI matrix; fallback to ZK-mode if blocked |
| R02 | Docker Compose resource exhaustion on developer machines (< 16 GB RAM) | High | Medium | Add resource limits to compose; document minimum machine spec |
| R03 | Alembic migration conflicts from parallel branches | Medium | Medium | One migration file per feature branch; squash before merge |
| R04 | RLS policy applied to table but not to new tables added later | Low | High | CI check: every table in `information_schema.tables` has a corresponding RLS policy |
| R05 | CI pipeline exceeds 8-minute target due to Docker build time | Medium | Medium | Parallelise builds; use GitHub Actions matrix; layer cache in registry |
| R06 | `aep-common` becomes a monolith with too many responsibilities | Low | High | Enforce module boundaries; each module is independently importable |
| R07 | Team velocity underestimated — PI-01 overruns into PI-02 time | Medium | Medium | Descope `cd-dev.yml` to PI-01 hardening if needed; CI is the critical path |
