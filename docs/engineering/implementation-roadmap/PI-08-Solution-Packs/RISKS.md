# PI-08-Solution-Packs — Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R01 | Upstream PI dependency not complete when this PI starts | Medium | High | Agree hard handoff criteria; do not start until all handoff conditions met |
| R02 | Integration complexity underestimated | Medium | Medium | Timebox integration spikes to 2 days; descope to stub if blocked |
| R03 | New team members unfamiliar with event-driven patterns | Medium | Medium | Pair programming for first week; review CLAUDE.md AR1-AR6 |
| R04 | Cross-tenant data leakage discovered late | Low | High | Run tenancy tests from Sprint 1 of this PI, not at the end |
| R05 | CI pipeline time grows beyond 8 minutes as more services added | High | Medium | Parallelise CI jobs; cache Docker layers; split slow tests into separate workflow |
| R06 | Vendor API rate limits or breaking changes in tool connectors | Medium | Medium | Mock all vendor APIs in tests; never test against production APIs in CI |
