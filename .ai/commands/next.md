# next.md

**Command:** `next`  
**Version:** 1.0 — Global engineering orchestrator  
**Skill authority:** `.ai/skills/next/SKILL.md` (full pipeline)  
**Applies to:** All repositories using the `.ai` prompt library

---

## Purpose

Use this command to determine the **next executable engineering work item**. This is the engineer's primary entry point before invoking implementation or review skills.

`/next` discovers repository context, architecture documents, current PI/sprint/story, validates dependencies, produces a high-level implementation plan (no code), recommends the correct downstream skill, suggests STATUS updates, and renders an **Engineering Dashboard**.

**This command never writes production code.** It orchestrates existing skills:

`implement-story` · `review-story` · `generate-tests` · `security-review` · `performance-review` · `regression-review` · `release-story`

See `.ai/skills/next/SKILL.md` for the complete authoritative workflow.

### Invocation

```
/next
/next PI-02
/next current
/next PI-02-Metadata-Engine
```

| Input | Behaviour |
|-------|-----------|
| No argument | Discover active PI and next work item |
| PI shorthand (`PI-02`) | Scope discovery to that PI |
| Full PI folder name | Scope discovery to that folder |
| `current` | Focus on in-progress work |

---

## Execution Pipeline (9 Steps)

| Step | Action |
|------|--------|
| 1 | Discover Repository — git context, branch, engineering markers |
| 2 | Discover Architecture — constitution, ARCHITECTURE.md, v2 platform docs (if present) |
| 3 | Discover Current Engineering Context — roadmap, TASKS, ROADMAP, PI folders |
| 4 | Discover Current Story — PI, Sprint, Story from STATUS/SPRINT_PLAN patterns |
| 5 | Validate Dependencies — story, capability, architecture prerequisites |
| 6 | Produce Implementation Plan — high-level only, no code |
| 7 | Recommend Skill — single best next command with rationale |
| 8 | Update STATUS — recommend field updates (do not write by default) |
| 9 | Produce Engineering Dashboard — required output template |

---

## Discovery (Repository Agnostic)

Automatically discover via glob/search. **Never fail because documents are missing.**

| Category | Search patterns |
|----------|-----------------|
| Constitution | `CONSTITUTION.md`, `CLAUDE.md`, `README.md` |
| Architecture | `ARCHITECTURE.md`, `docs/architecture/**` |
| v2 platform docs | `PLATFORM_PRIMITIVES.md`, `PLATFORM_CONTRACTS.md`, `PLATFORM_META_MODEL.md`, `PLATFORM_UX_MODEL.md`, `PLATFORM_GLOSSARY.md`, `METADATA_DRIVEN_ENTERPRISE_PLATFORM.md`, `ARCHITECTURE_BASELINE_V2.md` |
| Roadmap | `TASKS.md`, `ROADMAP.md`, `docs/engineering/**`, `docs/04-program/**` |
| PI context | `**/PI-*/STATUS.md`, `**/PI-*/SPRINT_PLAN.md`, `**/PI-*/USER_STORIES.md` |
| Tracking | `**/CHANGELOG.md`, `**/METRICS.md` |

If v2 constitution docs are absent, continue with whatever repository standards exist.

---

## Skill Recommendation Logic

| State | Recommended command |
|-------|-------------------|
| Story Planned, deps clear | `/implement-story {story_id}` |
| Implementation in progress | `/implement-story {story_id}` |
| Code complete, tests missing | `/generate-tests {story_id}` |
| Ready for pre-PR review | `/review-story {story_id}` |
| Open PR, regression check needed | `/regression-review {pr}` |
| PR touches security surfaces | `/security-review {pr}` |
| PR has performance SLOs | `/performance-review {pr}` |
| All gates pass, ready to merge | `/release-story {pr}` |

### Workflow position

```
/next → implement-story → generate-tests → review-story
     → regression-review → security-review → performance-review → release-story
```

---

## Required Output — Engineering Dashboard

```
## Engineering Dashboard

### Current Project
### Current PI
### Current Sprint
### Current Story
### Dependencies
### Risk
### Estimated Complexity (S/M/L/XL with justification)
### Recommended Next Command
### Blocked Items
### Overall Progress
```

---

## Engineering Rules

- Never write production code or modify source files
- Never auto-invoke downstream skills — recommend only
- Never hardcode project names or technology stacks
- Prefer recommending STATUS updates over writing STATUS files
- Stop for disambiguation when multiple in-progress stories exist across PIs
- Degrade gracefully when documents are missing

---

## Forbidden Actions

- Implement stories or generate production code
- Run implement-story, review-story, or other execution skills inline
- Modify CONSTITUTION.md, ARCHITECTURE.md, or PI tracking documents
- Guess ambiguous story IDs without listing candidates
- Block the dashboard because v2 docs are missing
- Create PRs, provision infrastructure, or commit code

---

## Completion Checklist

```
[ ] Repository and branch context discovered
[ ] Architecture docs loaded or gaps noted
[ ] PI / Sprint / Story resolved
[ ] Dependencies validated
[ ] High-level implementation plan produced (no code)
[ ] Single primary command recommended with rationale
[ ] STATUS update recommendations listed
[ ] Engineering Dashboard produced with required template
[ ] No production code written or modified
```
