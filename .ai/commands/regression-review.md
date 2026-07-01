# regression-review.md

**Command:** `regression-review`  
**Version:** 2.0 — Architecture v2.0-aware  
**Skill authority:** `.ai/skills/regression-review/SKILL.md` (full pipeline)  
**Applies to:** All PIs, all sprints — mandatory on PRs touching shared zones, contracts, metadata, workflows, APIs, Kafka, migrations, registries, or SDKs

---

## Purpose

Use this command to perform a Principal Engineer level backward-compatibility and blast-radius audit of a pull request.

This command asks **"did this break anything that was already working?"** — distinct from `aep-review` (correctness) and complementary to `security-review` / `performance-review`. Architecture v2.0 extensions automatically identify Platform Object impact, generate Regression Scope across platform surfaces, produce a Regression Matrix (dimensions × risk × test coverage), and recommend automation to close coverage gaps.

**Lenses 1–11 are preserved unchanged.** v2.0 adds Steps 1b, 2b, and extended output sections — not new lenses.

### Invocation (unchanged)

```
/regression-review 42
/regression-review https://github.com/org/Agentic_platform/pull/42
```

See `.ai/skills/regression-review/SKILL.md` for the complete authoritative workflow.

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Platform primitives | `docs/architecture/PLATFORM_PRIMITIVES.md` | When Zone S, C, or M present |
| Platform contracts | `docs/architecture/PLATFORM_CONTRACTS.md` | When Zone S, C, or M present |
| Meta model | `docs/architecture/PLATFORM_META_MODEL.md` | When Zone S, C, or M present |
| UX model | `docs/architecture/PLATFORM_UX_MODEL.md` | When Zone S, C, or M present |
| Glossary | `docs/architecture/PLATFORM_GLOSSARY.md` | When Zone S, C, or M present |
| Metadata-driven architecture | `docs/architecture/METADATA_DRIVEN_ENTERPRISE_PLATFORM.md` | When Zone S, C, or M present |
| Architecture baseline v2 | `docs/architecture/ARCHITECTURE_BASELINE_V2.md` | When Zone S, C, or M present |
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture | `ARCHITECTURE.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| ADRs | `docs/architecture/ADR/DECISIONS.md` | Mandatory |
| Contract schemas | `contracts/` (including `platform-object.schema.json`) | Mandatory |
| PR diff | `gh pr diff <NUMBER>` | Mandatory |
| Contract validation | `python scripts/validate_contract.py contracts/` | When `contracts/` changed |
| PI capability map | `docs/engineering/implementation-roadmap/{PI}/CAPABILITIES.md` | When agents/tools changed |

**Substitutions required:**

```
{pr_number}   = GitHub pull request number
{PI}          = PI folder from PR body or branch context
```

---

## Preconditions

- [ ] PR is open and diff is fetchable via `gh pr diff`
- [ ] `CONSTITUTION.md` and `ARCHITECTURE.md` are readable
- [ ] `contracts/` directory is readable
- [ ] Platform constitution docs readable if PR touches Zone S, Zone C, or Zone M

---

## Execution Steps

### Step 1 — Fetch PR metadata and classify compatibility zones

See `.ai/skills/regression-review/SKILL.md` Step 1. Classify every changed file into compatibility zones (S, C, W, A, T, K, D, I, SDK, API, M). Set `load_platform_constitution = true` when Zone S, C, or M files are present.

### Step 1b — Platform Object impact identification (Architecture v2.0)

When `load_platform_constitution = true`, execute before Lens 1. Identify Platform Object schema, lifecycle FSM, `aep_meta`, and primitive-type impact. See skill Step 1b.

### Step 2 — Load reference documents

Load repository constitution always. Load platform constitution when `load_platform_constitution = true`. See skill Step 2.

### Step 2b — Regression scope generation (Architecture v2.0)

Map changed files to impacted surfaces: Capabilities, Providers, Policies, Execution Profiles, Marketplace, Registries, Metadata Engine, Workflow Engine, Platform APIs. See skill Step 2b.

### Step 3 — Execute 11 regression lenses (preserved)

Execute in order — do not skip or reorder:

1. Blast Radius (Zone S, Zone M)
2. Contract Compatibility (Zone C)
3. API Compatibility (Zone API)
4. Event/Kafka Compatibility (Zone K)
5. Database Schema Compatibility (Zone D)
6. Infrastructure Compatibility (Zone I)
7. Workflow Compatibility (Zone W)
8. Agent Compatibility (Zone A)
9. Tool Compatibility (Zone T)
10. SDK Compatibility (Zone SDK)
11. Backward Compatibility Summary (all PRs)

### Step 4 — Produce regression review report

```
## Regression Review: PR #{N} — {title}

### Blast Radius Map
{zone classification with importer counts}

### Platform Object Impact (Architecture v2.0)
{Step 1b output or N/A}

### Regression Scope (Architecture v2.0)
{9-surface affected/N/A table}

### Regression Matrix (Architecture v2.0)
{dimensions × risk × test coverage required}

### Automation Coverage Recommendations
{Priority 1–3 test automation items}

### Critical / Major / Minor Findings
{file:line findings with runtime failure scenario and fix}

### Regression Risk
{11-lens risk table}

### Lens Results
{11-lens status table}

### Merge Recommendation
{1-2 sentences}

### Verdict
APPROVE | REQUEST CHANGES | NEEDS DISCUSSION
```

---

## Architecture v2.0 Regression Surfaces

| Surface | Typical path signals |
|---------|------------------------|
| Capabilities | Capability tags, `object_type: capability` |
| Providers | Provider framework, `object_type: provider` |
| Policies | `policy-engine/`, `object_type: policy` |
| Execution Profiles | `execution_profile`, profile schema handlers |
| Marketplace | `marketplace/`, `solution_pack`, install flows |
| Registries | `agent-registry/`, `tool-registry/`, registrations |
| Metadata Engine | `aep_meta/`, `metadata-engine/`, `platform-object.schema.json` |
| Workflow Engine | `workflows/`, orchestrator workflow handlers |
| Platform APIs | `/api/v1/`, route and schema files |

---

## Expected Outputs

| Artifact | Description |
|----------|-------------|
| Regression review report | Structured report with verdict, 11-lens summary, v2.0 scope and matrix |
| Regression Matrix | Dimensions × risk × test coverage gaps |
| Automation recommendations | Priority 1–3 test automation to close coverage gaps |

---

## Quality Gates

- [ ] Platform constitution loaded when Zone S, C, or M present
- [ ] Platform Object impact assessed before Lens 1 when triggered
- [ ] Regression Scope produced for all affected v2.0 surfaces
- [ ] All 11 lenses executed (or N/A documented)
- [ ] Regression Matrix complete for every affected surface
- [ ] Automation Coverage Recommendations produced
- [ ] No Critical finding unresolved
- [ ] Verdict consistent with Mandatory Verdict Rules in skill

---

## Completion Checklist

```
[ ] PR diff fetched and compatibility zones classified
[ ] Platform Object impact assessed (Step 1b) when triggered
[ ] Platform constitution loaded when triggered (Step 2)
[ ] Regression Scope generated (Step 2b)
[ ] Lenses 1–11 executed (or N/A documented)
[ ] Regression Matrix produced
[ ] Automation Coverage Recommendations produced
[ ] Mandatory Verdict Rules applied
[ ] Verdict issued (APPROVE | REQUEST CHANGES | NEEDS DISCUSSION)
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Skip platform constitution loading when Zone S, C, or M files are present
- Replace or reorder the 11 regression lenses
- Change invocation syntax (`/regression-review <PR_NUMBER>` or PR URL only)
- Invent regressions not traceable to changed code in the diff
- Approve a PR with an unresolved Critical finding in any lens
- Mark a Regression Scope surface AFFECTED without a Regression Matrix row
- Approve a HIGH-risk matrix row with zero test coverage and no Priority 1 automation recommendation
- Include style, correctness, or new-feature findings (those belong to aep-review)
- Treat a breaking contract or Platform Object change as anything less than Critical
