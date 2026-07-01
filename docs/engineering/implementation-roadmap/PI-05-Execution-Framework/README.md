# PI-05 — Tool Registry

**Status:** `PLANNED`  
**Depends on:** PI-02 complete (ToolClient stub replaced)  
**Target:** Sprint 16–19 (weeks 31–38)  
**Architecture baseline:** [ARCHITECTURE_BASELINE_V2.md](../../../architecture/ARCHITECTURE_BASELINE_V2.md). Tool Registry is the **typed index for `connector` and `rest-api` Providers** (Provider Model v2).

## Architecture v2 alignment

| Field | Value |
|-------|-------|
| **Classification** | Renamed (conceptual) + Extended |
| **v2 concept** | Plugin Framework |
| **Report** | [ARCHITECTURE_ALIGNMENT_REPORT.md](../../architecture-alignment/ARCHITECTURE_ALIGNMENT_REPORT.md) |
| **Migration note** | tool-contract valid until Provider Contract unifies in PI-09 (G-02). |

---

## What This PI Delivers

- `tool-registry` resolves agent requests by capability tag to the correct vendor tool (**Provider** binding)
- `secrets-service` issues short-lived, scoped tokens per tool invocation (TTL 15 min)
- First 3 production tool connectors: `github-tool`, `jira-tool`, `confluence-tool`
- Every tool response is normalised to the common response shape (vendor-neutral)
- Tool scope ceiling enforced — a tool registered as `read` can never write
- Rate limiting per tool per tenant enforced via Redis sliding window

## Key Constitutional Constraints

- Agents request tools by CAPABILITY TAG, never by tool_id (AG4)
- No vendor SDK imports in agent code — tools are the abstraction layer (AP5)
- Credentials never in agent code — always via secrets-service (S2, SR1)
- Tool scope set to minimum required (SR2)
