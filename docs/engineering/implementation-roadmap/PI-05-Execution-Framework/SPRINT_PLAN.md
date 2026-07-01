# PI-05 — Sprint Plan

## Sprint 16 (Days 151–160): Tool Registry Core

| # | Task | Points |
|---|------|--------|
| 16.1 | Implement `tool-registry` POST /tools — register tool with contract validation | 3 |
| 16.2 | Implement `tool-registry` GET /tools?capability={tag} — resolve by capability | 3 |
| 16.3 | Implement scope ceiling enforcement (registered scope is maximum, regardless of token) | 3 |
| 16.4 | Implement rate limit check via Redis sliding window | 2 |
| 16.5 | Implement `secrets-service` Vault integration — dynamic secret issuance | 4 |

**Sprint Goal:** Tool registered, resolved by capability, scoped token issued.

---

## Sprint 17 (Days 161–170): github-tool Connector

| # | Task | Points |
|---|------|--------|
| 17.1 | Implement `github-tool` — create-pull-request capability | 3 |
| 17.2 | Implement `github-tool` — create-branch, commit-files capabilities | 3 |
| 17.3 | Implement response normaliser → `common-tool-responses.schema.json` PR shape | 2 |
| 17.4 | Implement idempotency: retry does not create duplicate PR | 3 |
| 17.5 | Tests: contract validation, scope enforcement, idempotency | 3 |

**Sprint Goal:** github-tool creates PRs idempotently with normalised response.

---

## Sprint 18 (Days 171–180): jira-tool + confluence-tool

| # | Task | Points |
|---|------|--------|
| 18.1 | Implement `jira-tool` — create-issue, update-issue, add-comment capabilities | 4 |
| 18.2 | Implement `confluence-tool` — create-page, update-page capabilities | 3 |
| 18.3 | Normalised responses for both tools | 2 |
| 18.4 | Multi-tenant tool config: same capability, different tenant credentials | 2 |

**Sprint Goal:** 3 production connectors operational across multiple tenants.

---

## Sprint 19 (Days 181–190): tool-sdk + PI-05 Close

| # | Task | Points |
|---|------|--------|
| 19.1 | Implement `aep-tool-sdk` — base class for building new connectors | 3 |
| 19.2 | Tool SDK documentation | 2 |
| 19.3 | Load test: 1,000 tool invocations/hour, rate limit triggers correctly | 2 |
| 19.4 | Security test: tool with `read` scope cannot perform write operations | 2 |
| 19.5 | PI-05 retrospective + PI-06 kick-off | 1 |

**Sprint Goal:** Tool SDK published. Security and rate limit tests pass.
