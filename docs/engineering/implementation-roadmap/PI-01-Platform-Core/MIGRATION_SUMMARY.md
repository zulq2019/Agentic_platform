# PI-01 — Documentation Migration Summary

**Date:** 2026-06-28  
**Author:** Platform Engineering Lead  
**Scope:** PI-01-Platform-Core documentation restructuring

---

## Why This Change Was Made

The original 16-file structure was designed for maximum coverage. In practice, it created four problems:

1. **Scattered intent.** A developer had to open 5 files to understand what one capability does: FEATURES.md for what it is, API_SPEC.md for its contract, DATA_MODEL.md for its schema, SEQUENCE_DIAGRAMS.md for its flow, and IMPLEMENTATION.md for how to build it. The first four are all *about the same thing* — the capability — and should live together.

2. **Duplicate acceptance criteria.** USER_STORIES.md contained inline `**Acceptance:**` lines that duplicated content already in ACCEPTANCE_CRITERIA.md. Any update required editing two places.

3. **Orphaned review content.** REVIEW_CHECKLIST.md contained checklist items that should have been part of DEFINITION_OF_DONE.md. Having both files meant engineers had two different checklists for the same quality gate, causing inconsistency.

4. **Operational artefacts in documentation.** DEMO.md was a runbook for a 15-minute demo. It is execution context, not engineering documentation. It created noise when reading the PI documents as a set.

The new structure collapses these overlaps into a minimal, coherent 11-file set.

---

## What Was Merged

### FEATURES.md → CAPABILITIES.md (new file)

FEATURES.md described what each feature delivers. That content is now the backbone of CAPABILITIES.md, with the following additions merged in:

| Source file | Content moved into CAPABILITIES.md |
|-------------|-------------------------------------|
| `API_SPEC.md` | Standard endpoint contracts (health, metrics, info, EventEnvelope) moved under CAP-01 |
| `SEQUENCE_DIAGRAMS.md` | Service startup sequence → under CAP-01; Kafka round-trip → under CAP-04; DB migration sequence → under CAP-05 |
| `DATA_MODEL.md` | Full DDL for all core tables, Redis key schema → under CAP-05 |

Each capability section in CAPABILITIES.md is now self-contained: what it is, what it produces, its technical contracts, and its key behaviour sequences are all in one place.

### REVIEW_CHECKLIST.md → DEFINITION_OF_DONE.md

REVIEW_CHECKLIST.md was a PR-level checklist. DEFINITION_OF_DONE.md was a PI-level completion gate. These were two separate documents describing two levels of the same quality bar. They are now merged into one document with two clearly labelled gates:

- **Story-Level Gate** — used on every PR (was REVIEW_CHECKLIST.md)
- **PI-Level Gate** — used at PI close (was the original DEFINITION_OF_DONE.md)

Engineers now have one document to consult for "what does done mean".

---

## What Was Removed

| File | Why removed |
|------|-------------|
| `FEATURES.md` | All content absorbed into `CAPABILITIES.md` |
| `API_SPEC.md` | Contracts moved into the relevant capability sections of `CAPABILITIES.md` |
| `SEQUENCE_DIAGRAMS.md` | Diagrams moved into the relevant capability sections of `CAPABILITIES.md` |
| `DATA_MODEL.md` | Schema DDL moved into CAP-05 of `CAPABILITIES.md` |
| `REVIEW_CHECKLIST.md` | Checklists absorbed into the Story-Level Gate section of `DEFINITION_OF_DONE.md` |
| `DEMO.md` | Demo scripts are operational content, not engineering documentation. Acceptance criteria already capture the same scenarios in testable form. |

**No information was lost.** Every meaningful piece of content from the removed files exists in the new structure. The deletions removed duplication and format overhead, not information.

---

## What Changed in Retained Files

| File | Change made |
|------|-------------|
| `README.md` | Added document index table mapping each file to its purpose; added capability column to the "What Is Being Built" table |
| `USER_STORIES.md` | Removed inline `**Acceptance:**` lines from each story; added `Capability:` and `Sprint:` cross-reference fields |
| `DEFINITION_OF_DONE.md` | Expanded with Story-Level Gate section (absorbed from REVIEW_CHECKLIST.md); restructured PI-Level Gate for clarity |

`OBJECTIVES.md`, `ACCEPTANCE_CRITERIA.md`, `IMPLEMENTATION.md`, `PROMPT_MAPPING.md`, `SPRINT_PLAN.md`, `TESTING.md`, and `RISKS.md` are **unchanged** — they were already focused and non-duplicative.

---

## What Became Simpler

| Before | After |
|--------|-------|
| 16 files | 11 files |
| "Where is the EventEnvelope schema?" → 3 files had partial answers | → 1 place: CAPABILITIES.md CAP-02 |
| "What does done mean?" → 2 files (REVIEW_CHECKLIST.md + DEFINITION_OF_DONE.md) | → 1 file: DEFINITION_OF_DONE.md |
| "What are the acceptance criteria for US-01.04?" → 2 files (USER_STORIES.md inline + ACCEPTANCE_CRITERIA.md) | → 1 file: ACCEPTANCE_CRITERIA.md |
| Capability understanding required 5 files | → 1 file: CAPABILITIES.md |

---

## The PI-01 Template

This 11-file structure is now the canonical template for all future PIs. When creating PI-02 through PI-10, each should follow this layout:

```
{PI-XX}/
├── README.md              PI overview, status, document index, handoff requirements
├── OBJECTIVES.md          Measurable outcomes — what success looks like
├── CAPABILITIES.md        What is built — features, contracts, schemas, sequences, data model
├── USER_STORIES.md        Stories only — who, what, why; one story per section
├── ACCEPTANCE_CRITERIA.md Given/When/Then per story; one section per story
├── IMPLEMENTATION.md      Tech stack, patterns, code conventions, examples
├── PROMPT_MAPPING.md      Story → .ai/commands/ mapping; PI-specific context per story
├── SPRINT_PLAN.md         Sprint-by-sprint task breakdown with owners and points
├── TESTING.md             Test pyramid, test files, security baseline, NFR baselines
├── RISKS.md               Risk register: ID, description, likelihood, impact, mitigation
└── DEFINITION_OF_DONE.md  Story-level gate + PI-level gate — single source of truth
```

### Rules for future PI documents

| Document | Contains | Does NOT contain |
|----------|---------|-----------------|
| `CAPABILITIES.md` | What, why, technical contracts, schemas, sequences | Stories, acceptance criteria, task breakdown |
| `USER_STORIES.md` | As a / I want / so that; capability + sprint reference | Acceptance criteria, implementation detail |
| `ACCEPTANCE_CRITERIA.md` | Given/When/Then per story | Implementation approach |
| `IMPLEMENTATION.md` | Tech decisions, code patterns, examples | Stories, acceptance criteria |
| `PROMPT_MAPPING.md` | Story → command mapping + PI-specific context | Actual prompt text (that lives in `.ai/commands/`) |
| `DEFINITION_OF_DONE.md` | Story-level PR gate + PI-level completion gate | Retrospective notes, demo scripts |

---

## Files Not Touched by This Migration

- All PI-02 through PI-10 documents — these will be refactored in a separate pass using PI-01 as the template
- `.ai/commands/` — the Engineering Command Library is separate from PI documentation
- `CONSTITUTION.md`, `ARCHITECTURE.md`, `CLAUDE.md`, `ROADMAP.md`, `TASKS.md` — root documents are not part of PI documentation
- `contracts/`, `workflows/`, `scripts/` — implementation artefacts, not documentation
