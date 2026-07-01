---
name: next
description: |
  When the engineer types /next, /next PI-02, or /next current, discover repository
  context and determine the next executable engineering work item. This skill is the
  primary engineering entry point — it orchestrates existing skills (implement-story,
  review-story, generate-tests, security-review, performance-review, regression-review,
  release-story) and never writes production code. Repository-agnostic discovery with
  graceful degradation when documents are missing.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq
  file: read
---

## Phase 0 — Repository Discovery (mandatory)

**Execute before all other steps in this skill.** Repository-agnostic; reusable in any
software repository. Never hardcode repository names or folder structures. Never fail
because a document is missing — record `NOT FOUND` and continue with graceful degradation.

**Authority:** Full discovery procedure, bash patterns, and Discovery Record template:
[`.ai/skills/_shared/REPOSITORY_DISCOVERY.md`](../_shared/REPOSITORY_DISCOVERY.md).
If the relative path does not resolve, discover via glob: `**/skills/_shared/REPOSITORY_DISCOVERY.md`.

**Auto-detect and record:**

| Item | Action |
|------|--------|
| Repository type | Infer from manifests and layout |
| Architecture documents | Glob/search `ARCHITECTURE*.md`, `PLATFORM_*.md`, architecture doc trees |
| Platform constitutions | Discover `CONSTITUTION.md`, platform baseline docs — **load automatically if present** |
| Repository constitution | Discover `CLAUDE.md`, `REPOSITORY_GUIDE.md`, `AGENTS.md`, `CONTRIBUTING.md` |
| Engineering roadmap | Discover `ROADMAP.md`, `TASKS.md`, implementation-roadmap / program trees |
| Current PI | Active program folder (`PI-*` or discovered pattern) |
| Current Sprint | Active section in `SPRINT_PLAN.md` when present |
| Current Story | In Progress / next Planned from `STATUS.md` + story catalogues |
| STATUS.md | Nearest program status file |
| CHANGELOG.md | Root or discovered changelog |
| METRICS.md | Root or discovered metrics doc |
| README hierarchy | Root + nested `README.md` files |
| Skills library | `**/skills/**/SKILL.md` |
| Prompt library | Command libraries (`commands/`, `.ai/commands/`, etc.) |

**Before proceeding:** Emit a **Discovery Record** per the shared template. If Platform
Constitution documents exist, confirm they were loaded. Then continue to this skill's
existing steps unchanged.

---


# next

**Version:** 1.0 — Global engineering orchestrator  
**Authority:** Read-only orchestration. Never implements stories or writes production code.

<purpose>
Determine the next executable engineering work item for the current repository.
Discover architecture, program context, current PI/sprint/story, validate dependencies,
produce a high-level implementation plan (no code), recommend the correct downstream
skill, suggest STATUS updates, and render an Engineering Dashboard. This skill is the
engineer's primary entry point before invoking implement-story, review-story, or other
execution skills.
</purpose>

---

## When To Activate

Trigger when the engineer types `/next` with an optional scope argument.

```
/next
/next PI-02
/next current
/next PI-02-Metadata-Engine
```

| Input form | Resolution behaviour |
|------------|---------------------|
| No argument | Discover active PI from STATUS patterns, roadmap order, or most recently updated PI folder |
| PI shorthand (`PI-02`) | Resolve to matching PI folder via prefix search |
| Full PI folder name | Use directly if folder exists |
| `current` | Same as no argument — focus on in-progress work across the repository |

---

## Engineering Rules

- **Never write production code** — orchestration and recommendations only
- **Never invoke implement-story, review-story, or other execution skills automatically** — recommend the command for the engineer to run
- **Never fail because documents are missing** — note gaps and continue with available context
- **Never hardcode project names, paths, or technology stacks** — discover via search
- **Prefer recommending STATUS updates** over writing STATUS files unless the repository has an established read-only orchestrator pattern that explicitly permits STATUS writes
- **Repository agnostic** — adapt discovery to whatever structure exists
- **Architecture aware** — load v2 platform constitution when present

---

## Forbidden Actions

- Write or modify source code, tests, migrations, or configuration
- Run implement-story, review-story, generate-tests, security-review, performance-review, regression-review, or release-story inline
- Guess story IDs when resolution is ambiguous — list candidates and ask
- Block the dashboard because mandatory v2 docs are missing — degrade gracefully
- Provision infrastructure or create PRs
- Modify CONSTITUTION.md, ARCHITECTURE.md, or PI tracking documents (recommend updates only)

---

## Execution Flow (9 Steps)

Execute **all steps in order**. Produce the Engineering Dashboard at Step 9.

| Step | Name | Output |
|------|------|--------|
| 1 | Discover Repository | Repo identity, default branch, active branch, remote |
| 2 | Discover Architecture | Constitution, architecture docs, v2 platform docs (if present) |
| 3 | Discover Current Engineering Context | Roadmap, TASKS, ROADMAP, program folders |
| 4 | Discover Current Story | PI, Sprint, Story from STATUS/SPRINT_PLAN/USER_STORIES patterns |
| 5 | Validate Dependencies | Story, architecture, and capability dependencies |
| 6 | Produce Implementation Plan | High-level plan only — no code |
| 7 | Recommend Skill | Next command with rationale |
| 8 | Update STATUS | Recommendations for STATUS fields (do not write unless repo pattern allows) |
| 9 | Produce Engineering Dashboard | Required output template |

---

## Step 1 — Discover Repository

Establish baseline repository context. Use discovery — never assume layout.

```bash
# Repository identity
git remote -v 2>/dev/null || true
git branch --show-current 2>/dev/null || true
git status -sb 2>/dev/null || true

# Root-level engineering markers
ls -la 2>/dev/null | head -30
```

Record:
- Repository name (from remote URL or directory)
- Current branch and divergence from default branch
- Uncommitted changes (may indicate work in progress)
- Presence of common roots: `docs/`, `src/`, `contracts/`, `.ai/`

**Graceful degradation:** If not a git repo, note it and continue with filesystem discovery.

---

## Step 2 — Discover Architecture

Search for architecture and constitution documents. Load what exists; note what is missing.

### Discovery patterns (try all — use first match per category)

```bash
# Repository constitution
for f in CONSTITUTION.md CLAUDE.md README.md ARCHITECTURE.md; do
  [ -f "$f" ] && echo "FOUND: $f"
done

# Architecture docs
find docs/architecture -name "*.md" 2>/dev/null | head -20
find . -maxdepth 2 -name "ARCHITECTURE*.md" 2>/dev/null

# ADRs / decisions
find docs -path "*ADR*" -name "*.md" 2>/dev/null | head -10
find docs -name "DECISIONS.md" 2>/dev/null
```

### Architecture v2 platform constitution (load if present)

Attempt to read each file. If missing, note `NOT FOUND` and continue.

| Document | Typical path |
|----------|--------------|
| Platform Primitives | `docs/architecture/PLATFORM_PRIMITIVES.md` |
| Platform Contracts | `docs/architecture/PLATFORM_CONTRACTS.md` |
| Platform Meta Model | `docs/architecture/PLATFORM_META_MODEL.md` |
| Platform UX Model | `docs/architecture/PLATFORM_UX_MODEL.md` |
| Platform Glossary | `docs/architecture/PLATFORM_GLOSSARY.md` |
| Metadata-Driven Enterprise Platform | `docs/architecture/METADATA_DRIVEN_ENTERPRISE_PLATFORM.md` |
| Architecture Baseline v2 | `docs/architecture/ARCHITECTURE_BASELINE_V2.md` |

```bash
# v2 constitution batch check
for doc in PLATFORM_PRIMITIVES PLATFORM_CONTRACTS PLATFORM_META_MODEL PLATFORM_UX_MODEL \
           PLATFORM_GLOSSARY METADATA_DRIVEN_ENTERPRISE_PLATFORM ARCHITECTURE_BASELINE_V2; do
  find docs -name "${doc}.md" 2>/dev/null
done
```

**Output:** Architecture awareness level: `v2-full` | `v2-partial` | `v1-only` | `minimal`

---

## Step 3 — Discover Current Engineering Context

Locate engineering roadmap and program tracking. Search multiple conventions.

```bash
# Roadmap / program folders
find docs -type d \( -name "implementation-roadmap" -o -name "04-program" -o -name "engineering" \) 2>/dev/null

# Task and roadmap files
find . -maxdepth 3 \( -name "TASKS.md" -o -name "ROADMAP.md" -o -name "STATUS.md" \) 2>/dev/null

# PI folders (common patterns)
find docs -type d -name "PI-*" 2>/dev/null | head -20
ls docs/engineering/implementation-roadmap/ 2>/dev/null
ls docs/04-program/ 2>/dev/null
```

### PI folder resolution (when engineer passes `PI-02` or similar)

```bash
# Resolve PI shorthand to full folder name
ls docs/engineering/implementation-roadmap/ 2>/dev/null | rg "^{PI_SHORT}"
# Fallback: search any docs tree
find docs -type d -name "${PI_SHORT}*" 2>/dev/null
```

Record discovered PI folders and their key files:
- `README.md`, `OBJECTIVES.md`, `STATUS.md`, `SPRINT_PLAN.md`, `USER_STORIES.md`
- `CHANGELOG.md`, `METRICS.md` (if present)

**Graceful degradation:** If no PI structure exists, derive work items from `TASKS.md`, `ROADMAP.md`, or open issues via `gh issue list` when `gh` is available.

---

## Step 4 — Discover Current Story

Determine current PI, Sprint, and Story from status patterns.

### PI selection (when no argument provided)

Priority order:
1. PI with a story marked **In Progress** in any `STATUS.md`
2. PI with the most recent `CHANGELOG.md` or `STATUS.md` modification
3. First PI in roadmap order with **Planned** stories remaining
4. Engineer-supplied PI argument

### Story resolution algorithm

```bash
# Read STATUS.md for target PI
cat docs/engineering/implementation-roadmap/{PI}/STATUS.md 2>/dev/null

# Cross-reference sprint plan
cat docs/engineering/implementation-roadmap/{PI}/SPRINT_PLAN.md 2>/dev/null

# Story definitions
rg "^## US-" docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md 2>/dev/null
```

| STATUS pattern | Interpretation |
|----------------|----------------|
| **In Progress** (first occurrence) | Current story — likely mid-implementation |
| **Planned** (first after last **Complete**) | Next story to implement |
| **Blocked** | Blocked item — surface in dashboard |
| **Complete** (all stories) | PI complete — recommend next PI or release activity |

Also check git context for in-flight work:
```bash
git diff --stat HEAD 2>/dev/null
git log --oneline -5 2>/dev/null
gh pr list --author @me --state open 2>/dev/null || true
```

**Output:**
```
PI:           {PI folder or NOT FOUND}
Sprint:       {N or UNKNOWN}
Story ID:     {US-XX.YY or NOT FOUND}
Story title:  {title or UNKNOWN}
Story status: {In Progress | Planned | Complete | Blocked | UNKNOWN}
```

**STOP for disambiguation only** if multiple stories are In Progress across PIs and no PI argument was given. List candidates; do not guess.

---

## Step 5 — Validate Dependencies

Assess whether the current/next story can proceed. Check applicable dimensions only.

### Story dependencies

```bash
rg "{story_id}" docs/engineering/implementation-roadmap/{PI}/SPRINT_PLAN.md -A 10 2>/dev/null
rg "{story_id}" docs/engineering/implementation-roadmap/{PI}/STATUS.md 2>/dev/null
```

Verify prerequisite stories marked **Complete** in `STATUS.md`.

### Architecture / capability dependencies (when docs exist)

| Dimension | Where to check |
|-----------|----------------|
| Story prerequisites | `SPRINT_PLAN.md`, `STATUS.md` |
| Capability spec | `CAPABILITIES.md` |
| Acceptance criteria | `ACCEPTANCE_CRITERIA.md` |
| Contract schemas | `contracts/` |
| ADR conflicts | `docs/architecture/ADR/DECISIONS.md` or equivalent |

### Readiness signals from git / CI

```bash
# Open PR for current branch?
gh pr view 2>/dev/null || true

# CI status on open PR
gh pr checks 2>/dev/null || true
```

**Output:**
```
Dependencies:
  Story prerequisites:  {N satisfied / N blocked / UNKNOWN}
  Capability spec:        {EXISTS | MISSING | N/A}
  Acceptance criteria:    {EXISTS | MISSING | N/A}
  Contracts:              {N found | N/A}
  Open PR:                {YES #N | NO}
  Status:                 CLEAR | BLOCKED | UNKNOWN
```

---

## Step 6 — Produce Implementation Plan (High-Level, No Code)

Produce a planning summary for the identified story. **Do not write code.** This plan informs the engineer before they invoke `/implement-story`.

```
## Implementation Plan (Orchestrator Preview): {story_id} — {story_title}

### Objective
{one paragraph — what this story delivers}

### Scope boundaries
{what is in scope / explicitly out of scope for this story}

### Key deliverables
- {deliverable 1}
- {deliverable 2}

### Files/services likely touched
{discovered from IMPLEMENTATION.md, CAPABILITIES.md, or story text — or UNKNOWN}

### Dependencies to clear first
{list or NONE}

### Risks
{technical, dependency, or governance risks — or NONE identified}

### Estimated complexity
{S | M | L | XL} — {one-line justification}
```

If story is not yet ready (missing AC, blocked deps), state what must happen before implementation.

---

## Step 7 — Recommend Skill

Select the **single best next command** based on current state. Never run the skill — recommend only.

### Decision logic

| State | Recommended command |
|-------|----------------------|
| Story **Planned**, deps **CLEAR**, no implementation started | `/implement-story {story_id}` |
| Story **In Progress**, code incomplete, no open PR | `/implement-story {story_id}` (continue) |
| Implementation complete, tests missing or insufficient | `/generate-tests {story_id}` |
| Implementation complete, ready for pre-PR review | `/review-story {story_id}` |
| Open PR exists, not yet reviewed for regression | `/regression-review {pr_number}` |
| PR touches auth/secrets/data/tenant isolation | `/security-review {pr_number}` |
| PR has latency/throughput SLO concerns | `/performance-review {pr_number}` |
| All reviews pass, story marked complete, ready to merge | `/release-story {pr_number}` |
| Story **Blocked** | No implementation skill — list unblock actions |
| PI complete, no open stories | Recommend next PI kickoff or `/next {next_PI}` |
| No engineering docs found | Recommend creating roadmap or opening `TASKS.md` / issues |

### Workflow position reference

```
/next → implement-story → generate-tests → review-story
     → regression-review → security-review (if applicable)
     → performance-review (if applicable) → release-story
```

### Recommendation output

```
Recommended Next Command: /{skill} {argument}
Rationale: {why this command fits the current state}
Alternative: /{skill} {argument} — {when to use instead}
```

---

## Step 8 — Update STATUS (Recommendations Only)

**Default: recommend, do not write.** List what should change in tracking documents.

### Recommended STATUS updates

When story state implies a transition, output:

```
STATUS update recommendations (engineer or implement-story should apply):

  File:   docs/engineering/implementation-roadmap/{PI}/STATUS.md
  Field:  {story_id} status
  From:   {current}
  To:     {recommended}
  Reason: {why}

  File:   docs/engineering/implementation-roadmap/{PI}/CHANGELOG.md
  Action: {add entry when story completes — not yet}

  File:   docs/engineering/implementation-roadmap/{PI}/METRICS.md
  Action: {update test/coverage counts after implementation — not yet}
```

Only write STATUS files if the repository documents an explicit orchestrator-write pattern. Default is read-only.

---

## Step 9 — Produce Engineering Dashboard

**Required final output.** Use this exact structure:

```
## Engineering Dashboard

### Current Project
{repository name, branch, architecture awareness level}

### Current PI
{PI folder name, objectives summary or link, PI status}

### Current Sprint
{sprint number, sprint goal if known, stories in sprint}

### Current Story
{story_id, title, status, capability, sprint assignment}

### Dependencies
{prerequisite stories, capability deps, blocked items — or NONE}

### Risk
{top risks for current work — technical, dependency, governance — or LOW}

### Estimated Complexity (S/M/L/XL with justification)
{size} — {justification based on scope, deps, touch surface, unknowns}

### Recommended Next Command
/{skill} {argument}
{Rationale — one paragraph}

### Blocked Items
{list each blocked story/dependency with unblock action — or NONE}

### Overall Progress
{PI: N/M stories complete; Sprint: N/M complete; Open PRs: N; CI: passing/failing/unknown}
```

---

## Skill Orchestration Reference

This skill coordinates but does not execute:

| Skill | When to recommend |
|-------|-------------------|
| `implement-story` | Story planned or in progress, deps clear, needs implementation |
| `generate-tests` | Implementation done, test gap identified |
| `review-story` | Implementation complete, pre-PR peer review needed |
| `regression-review` | PR open, backward-compatibility audit needed |
| `security-review` | PR touches security-sensitive surfaces |
| `performance-review` | PR has performance SLO implications |
| `release-story` | All gates pass, ready for merge/release validation |

Invoke path for engineers:
```
/next                          # discover and recommend
/implement-story {story_id}    # execute recommended work
/next current                  # re-assess after work session
```

---

## Discovery Cheat Sheet

Use glob/search — never hardcode paths. Common locations:

| Category | Search patterns |
|----------|-----------------|
| Constitution | `CONSTITUTION.md`, `CLAUDE.md` |
| Architecture | `ARCHITECTURE.md`, `docs/architecture/**` |
| Roadmap | `TASKS.md`, `ROADMAP.md`, `docs/engineering/**`, `docs/04-program/**` |
| PI context | `docs/**/PI-*/STATUS.md`, `docs/**/PI-*/SPRINT_PLAN.md` |
| Stories | `**/USER_STORIES.md`, `**/STATUS.md` |
| Metrics | `**/METRICS.md`, `**/CHANGELOG.md` |
| Contracts | `contracts/*.schema.json` |
| Skills | `.ai/skills/*/SKILL.md`, `.ai/commands/*.md` |

---

## Quality Checklist

Before delivering the Engineering Dashboard, confirm:

- [ ] Repository discovered without hardcoded assumptions
- [ ] Architecture docs loaded or gaps noted
- [ ] PI/Sprint/Story resolved or disambiguation requested
- [ ] Dependencies assessed
- [ ] High-level plan produced (no code)
- [ ] Exactly one primary recommended command
- [ ] STATUS update recommendations listed (not written unless permitted)
- [ ] Engineering Dashboard uses required template
- [ ] No production code written or modified
