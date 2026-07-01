# PI-02 — Metadata Engine — METRICS

**Snapshot:** US-02.01 complete (1 July 2026)

| Metric | Value |
|--------|-------|
| Unit tests (US-02.01) | 13 |
| Integration tests (US-02.01) | 4 |
| Total tests (US-02.01) | 17 |
| CI job | `story_us_02_01` in `lint-and-test` |
| Test pass rate | 100% |
| `aep_meta` line coverage | 95% |
| `aep_meta` modules | 12 |
| Contract schemas (platform) | 1 (`platform-object` v1.0.0) |
| REST endpoints (metadata-engine) | 4 |
| DB tables (metadata schema) | 4 |
| Lines of domain code (approx.) | ~650 |

## Coverage target

≥ 80% on `aep_meta` for PI-02 gate — run:

```bash
pytest src/shared/aep_meta/tests --cov=aep_meta --cov-report=term-missing
```
