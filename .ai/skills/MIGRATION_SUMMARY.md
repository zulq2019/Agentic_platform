# Migration Summary — pi-kickoff → implement-story

**Date:** 2026-06-28  
**Author:** Chief Platform Engineer  
**Status:** Complete

---

## What Was Merged from pi-kickoff into implement-story

The following readiness checks from `pi-kickoff` were extracted and embedded as
dedicated phases inside `implement-story`. Each check now fires per-story rather
than per-PI, giving engineers immediate, story-scoped feedback without requiring
a separate PI-level ceremony.

| pi-kickoff Check | implement-story Phase | Notes |
|------------------|-----------------------|-------|
| Check 3 — User Stories Completeness | Phase 2 — Story Readiness | Scoped to the single story being implemented |
| Check 4 — Acceptance Criteria Quality | Phase 2 — Story Readiness | Given/When/Then validation + testable Then clause check |
| Check 6 — Capability Coverage | Phase 2 — Capability Validation | Verifies CAP-XX section exists and has technical content |
| Check 10 — Contract Integrity | Phase 3 — Dependency Validation | Contract schema existence check for this story's schemas |
| Check 11 — Architecture Alignment | Phase 5 — Architecture Validation | Full Constitution A/H/S/MI principle sweep before any code |
| Lens A — Implementation Readiness | Phase 2 — Story Readiness | "Can an engineer start immediately?" gate |
| Lens B — Infrastructure Gap | Phase 4 — Infrastructure Assessment | Per-story infrastructure table, written to INFRASTRUCTURE.md |
| Lens D — Dependency Risk | Phase 3 — Dependency Validation | Story-level dependency check against SPRINT_PLAN.md |

---

## What Was Removed (PM-Only Concerns)

The following checks were present in pi-kickoff but are **not** in implement-story
because they are program-management concerns that belong in a planning ceremony,
not in a story implementation workflow.

| pi-kickoff Check | Reason for Removal |
|------------------|--------------------|
| Check 1 — Documentation Completeness (all 11 docs) | PI-level gate; not meaningful per story |
| Check 2 — Objectives Validity | PI objectives review; no story-level equivalent |
| Check 5 — Sprint Plan Validity | Velocity and sprint goal validation; PM responsibility |
| Check 7 — Prompt Mapping Completeness | PI setup concern; assume mapping is correct by the time a story is picked up |
| Check 8 — Risk Register | Risk management is a PI-level and PI-planning concern |
| Check 9 — Previous PI Handoff Verification | Cross-PI governance; not relevant inside a story implementation |
| Check 12 — Definition of Done Completeness | DoD structure validation is a PI kickoff concern; implement-story consumes the DoD, not validates it |
| Lens C — Scope Realism (velocity/story points) | Agile planning metric; no place in a coding workflow |
| Sprint 1 Execution Checklist | Sprint planning output; generated once at PI start |
| Infrastructure Readiness Matrix (PI-wide) | PI-wide view; implement-story produces per-story rows in INFRASTRUCTURE.md |
| Kickoff Report (PASS/FAIL/BLOCKED verdict) | PI-level artefact; not applicable per story |

---

## New Workflow Order

```
implement-story → generate-tests → regression-review → aep-review
    → security-review (optional) → performance-review (optional) → release-story
```

`implement-story` is now the **single implementation entry point**. There is no
mandatory pre-flight skill. Engineers type `/implement-story <story_id>` and the
skill self-validates readiness before proceeding.

---

## Why implement-story Is Now the Single Implementation Entry Point

### Before this migration

Engineers were expected to run:
1. `/pi-kickoff <PI_FOLDER>` — once per PI, validates 12 checks + 4 lenses
2. `/implement-story <story_id>` — per story, begins immediately after kickoff passes

This created two problems:
- **Temporal gap:** A PI could pass kickoff but individual stories could become stale
  (dependency stories incomplete, capability sections revised, new ADRs added) before
  implementation began. The kickoff verdict offered false confidence.
- **Cognitive overhead:** Engineers had to remember to run a separate command before
  every new sprint. In practice, kickoff was often skipped for mid-PI stories.

### After this migration

`implement-story` now validates everything it needs at invocation time:

- **Phase 2** catches story format, AC quality, and capability completeness the moment
  the engineer invokes the skill — not days or weeks earlier at PI kickoff.
- **Phase 3** checks whether dependency stories are actually complete in the sprint
  plan, not just planned.
- **Phase 5** re-checks Architecture and Constitution alignment against the current
  state of `DECISIONS.md` — catching any ADR added after PI start.

The result is a single, self-contained command that never assumes the PI setup is
still valid. Every invocation is an independent readiness assertion.

---

## Files Deleted

| Location | Path | Action |
|----------|------|--------|
| AEP repository | `.ai/skills/pi-kickoff/SKILL.md` | Deleted |
| Global Claude skills | `~/.claude/skills/skills/pi-kickoff/SKILL.md` | Deleted |
| Global Cursor skills | `~/.cursor/skills-cursor/pi-kickoff/SKILL.md` | Deleted (if existed) |

---

## Files Created / Updated

| Location | Path | Action |
|----------|------|--------|
| AEP repository | `.ai/skills/implement-story/SKILL.md` | Created |
| Global Claude skills | `~/.claude/skills/skills/implement-story/SKILL.md` | Installed |
| Global Cursor skills | `~/.cursor/skills-cursor/implement-story/SKILL.md` | Installed |
| AEP repository | `.ai/skills/MIGRATION_SUMMARY.md` | Created (this file) |
