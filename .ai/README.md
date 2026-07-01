# .ai — AI Prompt Library

**Agentic Engineering Platform**  
**Version:** 1.0  
**Audience:** Every engineer and AI assistant working in this repository  
**Authority:** [REPOSITORY_GUIDE.md](../REPOSITORY_GUIDE.md) · [CLAUDE.md](../CLAUDE.md)

---

> This folder is the single source of truth for all reusable AI engineering prompts.  
> PI folders reference this library. They do not own prompts.

---

## Purpose

The AI prompt library centralises every reusable prompt used to build this platform. Without it:

- Each PI owns its own prompts → duplication across 10 PIs
- Improving a prompt requires updating 10 files
- Engineering behaviour drifts across PIs as prompts diverge
- New engineers cannot find where prompts live

With this library:

- One prompt → referenced by all 10 PIs via `PROMPT_MAPPING.md`
- Improving a prompt improves all PIs simultaneously
- Consistent engineering behaviour across the entire platform lifecycle
- One obvious place to look for AI assistance

---

## Folder Responsibilities

```
.ai/
├── commands/       ← The prompt library. One file per engineering operation.
│
├── templates/      ← Starting-point scaffolds. AI uses these to generate new
│                     services, agents, tools, tests, and migrations.
│
├── checklists/     ← Structured pre-flight checks. AI runs these before
│                     declaring work done, raising a PR, or tagging a release.
│
└── reviewers/      ← AI reviewer configurations. Each reviewer has a defined
                      persona, scope, and output format.
```

### `commands/` — The prompt library

Each file defines one reusable engineering operation. A command file contains:

- **Purpose** — what this command does
- **When to use** — the trigger condition
- **Inputs** — what context to provide
- **Prompt body** — the reusable prompt text with `{placeholders}`
- **Expected output** — what well-formed output looks like
- **Constitutional constraints** — which CONSTITUTION.md principles apply

**Standard command set (populated at PI-01):**

| File | Operation |
|------|-----------|
| `implement-story.md` | Implement a User Story end-to-end (v4.0 — Architecture v2.0-aware) |
| `generate-tests.md` | Generate test suite for a story (v4.0 — Architecture v2.0-aware) |
| `review-story.md` | Review a completed story before PR (v2.0 — Architecture v2.0-aware) |
| `regression-review.md` | Backward-compatibility PR audit (v2.0 — Architecture v2.0-aware, 11 lenses) |
| `security-review.md` | Security-focused PR audit (v2.0 — Architecture v2.0-aware, 20 lenses) |
| `performance-review.md` | Latency, throughput, and resource usage review (v2.0 — Architecture v2.0-aware, 18 lenses) |
| `update-documentation.md` | Update service README, API spec, and ARCHITECTURE.md |
| `release-story.md` | Final release gate before merge (v2.0 — Architecture v2.0-aware, Pre-Release Verification + 11 lenses) |

### `templates/` — Scaffolding templates

Each file is a starting-point template an AI assistant uses when asked to scaffold something new. Templates prevent hallucinated structures and enforce conventions from day one.

**Planned templates (populated at PI-01 and PI-02):**

| File | What it scaffolds |
|------|------------------|
| `service-scaffold.py` | New FastAPI platform service (follows PI-01 IMPLEMENTATION.md pattern) |
| `agent-template.py` | New specialist agent (inherits from aep-agent-sdk Agent base class) |
| `tool-template.py` | New tool connector (inherits from aep-tool-sdk Tool base class) |
| `migration-template.py` | Alembic migration with RLS policy auto-applied |
| `test-unit-template.py` | Unit test file with standard structure and fixture patterns |
| `test-integration-template.py` | Integration test using Testcontainers |

### `checklists/` — Pre-flight checks

Each checklist is run by an AI assistant before a declared deliverable is considered complete. Checklists prevent common omissions that slip through code review.

**Planned checklists (populated at PI-01):**

| File | When it runs |
|------|-------------|
| `pre-commit.md` | Before every commit — lint, type check, no hardcoded secrets |
| `pre-merge.md` | Before merging a PR — tests pass, docs updated, constitutional compliance |
| `constitutional-compliance.md` | On any PR touching architecture boundaries — cross-reference with CONSTITUTION.md |
| `security.md` | On any PR touching auth, secrets, data access, or tenant isolation |
| `definition-of-done.md` | At PI story close — verifies all DoD criteria from DEFINITION_OF_DONE.md |

### `reviewers/` — AI reviewer personas

Each reviewer file configures an AI assistant to adopt a specific review perspective. Reviewers have defined scope, focus, and output format.

**Planned reviewers (populated at PI-02):**

| File | Persona | Focus |
|------|---------|-------|
| `constitution-reviewer.md` | Chief Architect | Verifies no CONSTITUTION.md principle is violated |
| `security-reviewer.md` | CISO | Credentials, RLS, scope ceiling, tenant isolation |
| `arch-reviewer.md` | Principal Engineer | Service boundaries, event contracts, dependency direction |
| `test-reviewer.md` | QA Lead | Coverage, edge cases, test naming, Testcontainers usage |
| `performance-reviewer.md` | SRE | Latency targets, Kafka lag, DB connection pools |

---

## Prompt Lifecycle

```
1. Need identified
   A recurring engineering task is performed manually more than twice
   → Candidate for a command

2. Draft
   Author writes the command file in .ai/commands/
   Peer reviews the prompt for correctness and completeness

3. Reference
   Affected PI folders update their PROMPT_MAPPING.md to reference the new command

4. Use
   Engineer opens the command file, substitutes {placeholders} with PI context,
   and uses it with their AI assistant

5. Improve
   Engineer identifies a problem with the prompt output
   → Opens a PR against the command file
   → All PIs benefit from the improvement immediately

6. Deprecate
   Command no longer needed (e.g., PI is complete, pattern replaced)
   → File kept with DEPRECATED header and explanation
   → Never deleted — audit trail preserved
```

---

## Naming Convention

| Asset type | Convention | Example |
|-----------|-----------|---------|
| Command | `verb-noun.md` | `implement-story.md`, `security-review.md` |
| Template | `noun-template.ext` | `agent-template.py`, `migration-template.py` |
| Checklist | `when-checklist.md` | `pre-commit.md`, `pre-merge.md` |
| Reviewer | `role-reviewer.md` | `security-reviewer.md`, `arch-reviewer.md` |

All names are **kebab-case**, **lowercase**, **descriptive**, and **action-oriented**.

---

## How Engineers Use This Library

### Step 1 — Find the right command

Open the relevant PI folder. Read `PROMPT_MAPPING.md`. Find the User Story you are working on. It lists the commands for each activity.

### Step 2 — Open the command file

```
.ai/commands/implement-story.md
```

Read the full command file. Understand the inputs it needs.

### Step 3 — Prepare your context

The command will have `{placeholders}` like:

```
{story_id}
{service_name}
{constitutional_constraints}
{acceptance_criteria}
```

Gather these from the PI's `USER_STORIES.md`, `ACCEPTANCE_CRITERIA.md`, and `IMPLEMENTATION.md`.

### Step 4 — Use with your AI assistant

Paste the filled-in prompt into your AI assistant (Claude, Cursor, Copilot).

### Step 5 — Feed back improvements

If the prompt produced poor output, improve the command file and raise a PR. Leave a comment explaining what failed and what you changed.

---

## How Prompts Evolve

Prompts are version-controlled code. They are reviewed, improved, and deprecated like any other asset.

| Action | How |
|--------|-----|
| Add a new command | Create file in `.ai/commands/`, update relevant `PROMPT_MAPPING.md` files |
| Improve a command | Open a PR with `fix(ai): improve {command-name}` |
| Deprecate a command | Add `> DEPRECATED: {reason}` header, do not delete |
| Add a new template | Create file in `.ai/templates/`, document in this README |
| Add a reviewer | Create file in `.ai/reviewers/`, document in this README |

**Never delete an asset from `.ai/`.** Deprecate with a header. History is preserved.

---

## Current Status

| Folder | Status | Populated in |
|--------|--------|-------------|
| `commands/` | Reserved — awaiting approval | PI-01 Sprint 1 |
| `templates/` | Reserved — awaiting approval | PI-01 Sprint 1 |
| `checklists/` | Reserved — awaiting approval | PI-01 Sprint 1 |
| `reviewers/` | Reserved — awaiting approval | PI-02 Sprint 5 |

See `docs/engineering/implementation-roadmap/PI-01-Platform-Core/SPRINT_PLAN.md` for the task that populates the initial command set.
