---
name: pi-kickoff
description: |
  When the engineer types /pi-kickoff <PI_FOLDER> (e.g. /pi-kickoff PI-02-Agent-Runtime),
  execute a structured Program Increment kickoff: validate all PI documentation, assess
  infrastructure readiness, verify PI-01 handoff conditions, check dependency completion,
  produce a readiness verdict, and generate a sprint-ready execution checklist. This skill
  is the mandatory entry point before any implement-story command is run for a new PI.
  Produces PASS / FAIL / BLOCKED verdict with concrete remediation steps.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq
  file: read
---

# PI Kickoff

<purpose>
Structured Program Increment kickoff for the Agentic Engineering Platform. Validates
documentation completeness, dependency satisfaction, infrastructure readiness, and
contract integrity before any story implementation begins. A PI that fails kickoff
must not begin implementation. Engineers who skip kickoff ship to an unvalidated foundation.
</purpose>

---

## When To Activate

Trigger when the engineer types `/pi-kickoff` followed by a PI folder name.

```
/pi-kickoff PI-02-Agent-Runtime
/pi-kickoff PI-05-Tool-Registry
```

The PI folder must exist under `docs/04-program/`.

---

## Repository Context to Read

Read these documents before executing any checks. Do not re-output their contents.

```bash
# Platform authorities
cat CONSTITUTION.md
cat ARCHITECTURE.md
cat CLAUDE.md
cat DECISIONS.md
cat REPOSITORY_GUIDE.md

# Target PI — all 11 documents
cat docs/04-program/{PI}/README.md
cat docs/04-program/{PI}/OBJECTIVES.md
cat docs/04-program/{PI}/CAPABILITIES.md
cat docs/04-program/{PI}/USER_STORIES.md
cat docs/04-program/{PI}/ACCEPTANCE_CRITERIA.md
cat docs/04-program/{PI}/IMPLEMENTATION.md
cat docs/04-program/{PI}/PROMPT_MAPPING.md
cat docs/04-program/{PI}/SPRINT_PLAN.md
cat docs/04-program/{PI}/TESTING.md
cat docs/04-program/{PI}/RISKS.md
cat docs/04-program/{PI}/DEFINITION_OF_DONE.md

# Previous PI (to validate handoff)
cat docs/04-program/{PREVIOUS_PI}/README.md
cat docs/04-program/{PREVIOUS_PI}/DEFINITION_OF_DONE.md

# Contracts
ls contracts/
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
cat contracts/tool-contract.schema.json

# Current repository state
git log --oneline -10
git status
```

**Substitutions required:**

```
{PI}          = the PI folder name passed by the engineer, e.g. PI-02-Agent-Runtime
{PREVIOUS_PI} = the preceding PI, e.g. PI-01-Platform-Spine
{PI_NUMBER}   = numeric portion, e.g. 02
```

**Stop condition:** If `CONSTITUTION.md`, `ARCHITECTURE.md`, or the target PI's `README.md` cannot be read, stop and report. Kickoff cannot proceed.

---

## Preconditions

Verify before running any check:

- [ ] The PI folder `docs/04-program/{PI}/` exists
- [ ] The engineer has specified exactly one PI
- [ ] Git working tree is clean (`git status` shows no uncommitted changes in PI docs)

---

## Execution Workflow

Execute every check in order. Report findings as you go. Do not skip checks.

---

### Check 1 — Documentation Completeness

Verify that all 11 required documents exist in the PI folder:

```bash
ls docs/04-program/{PI}/
```

Expected files:
```
README.md
OBJECTIVES.md
CAPABILITIES.md
USER_STORIES.md
ACCEPTANCE_CRITERIA.md
IMPLEMENTATION.md
PROMPT_MAPPING.md
SPRINT_PLAN.md
TESTING.md
RISKS.md
DEFINITION_OF_DONE.md
```

For each missing file: **FAIL** — document the gap and what content it must contain.

For each present file, verify it is not empty and not a placeholder:

```bash
# Check for placeholder content
rg "TODO|TBD|PLACEHOLDER|Lorem ipsum|coming soon" docs/04-program/{PI}/ -i
```

If placeholder content found: **WARN** — list every file and line containing it.

---

### Check 2 — Objectives Validity

Read `OBJECTIVES.md`. For each objective:

- Does it have a measurable outcome? ("Measure:" line present)
- Is the measure a concrete command, metric, or test — not a subjective statement?
- Are there between 3 and 7 objectives? (Fewer = too vague, more = unfocused PI)

**Flag as FAIL when:**
- An objective has no `Measure:` line
- A measure is subjective ("works well", "feels stable")
- Fewer than 3 or more than 7 objectives defined

---

### Check 3 — User Stories Completeness

Read `USER_STORIES.md`. For every story:

- Follows the `As a / I want / so that` format
- References a specific capability (`Capability: CAP-XX`)
- References a sprint (`Sprint: N`)
- Has a corresponding entry in `ACCEPTANCE_CRITERIA.md`

```bash
# Count stories in USER_STORIES.md
rg "^### US-" docs/04-program/{PI}/USER_STORIES.md | wc -l

# Count stories in ACCEPTANCE_CRITERIA.md
rg "^## AC-" docs/04-program/{PI}/ACCEPTANCE_CRITERIA.md | wc -l
```

Every story ID in `USER_STORIES.md` must have a matching section in `ACCEPTANCE_CRITERIA.md`.

**Flag as FAIL when:**
- A story is missing from `ACCEPTANCE_CRITERIA.md`
- A story does not reference a capability
- A story does not reference a sprint

---

### Check 4 — Acceptance Criteria Quality

Read `ACCEPTANCE_CRITERIA.md`. For each criterion:

- Written in Given/When/Then format
- "Then" clause is testable — it describes observable behaviour, not intent
- No criterion duplicates another from the same story

**Flag as FAIL when:**
- A criterion is not in Given/When/Then format
- A "Then" clause is subjective or untestable (e.g. "Then the system works correctly")
- A story has zero criteria

---

### Check 5 — Sprint Plan Validity

Read `SPRINT_PLAN.md`. Verify:

- Number of sprints matches the PI duration in `README.md`
- Every User Story ID appears in at least one sprint
- Every sprint has a `Sprint Goal` statement
- Story point totals are within a reasonable team velocity range (typically 15–35 points per sprint)
- Dependencies between stories are respected — a story does not appear in a sprint before its dependency stories

```bash
# Extract all story IDs from sprint plan
rg "US-" docs/04-program/{PI}/SPRINT_PLAN.md | sort -u

# Cross-reference against USER_STORIES.md
rg "^### US-" docs/04-program/{PI}/USER_STORIES.md | sort -u
```

**Flag as FAIL when:**
- A User Story is not assigned to any sprint
- A sprint has no goal statement
- A dependency story appears after the story that depends on it

---

### Check 6 — Capability Coverage

Read `CAPABILITIES.md`. For each capability (CAP-XX):

- At least one User Story references this capability
- The capability has a technical contract defined (schemas, sequences, or data model)
- No capability is described as "TBD" or "to be defined"

```bash
# Find capabilities defined
rg "^## CAP-" docs/04-program/{PI}/CAPABILITIES.md

# Cross-reference against story capability fields
rg "Capability: CAP-" docs/04-program/{PI}/USER_STORIES.md
```

**Flag as FAIL when:**
- A capability has no User Stories assigned to it
- A capability section has no technical content (only a one-line description)

---

### Check 7 — Prompt Mapping Completeness

Read `PROMPT_MAPPING.md`. For every User Story in `USER_STORIES.md`:

- There is a corresponding section in `PROMPT_MAPPING.md`
- Each section maps to at minimum `implement-story.md` and `review-story.md`
- All referenced commands exist in `.ai/commands/`

```bash
# Verify commands exist
ls .ai/commands/
```

**Flag as FAIL when:**
- A story has no entry in `PROMPT_MAPPING.md`
- A referenced command file does not exist in `.ai/commands/`

---

### Check 8 — Risk Register

Read `RISKS.md`. Verify:

- At least 3 risks are documented (a PI with fewer than 3 risks is under-assessed)
- Every risk has: ID, description, likelihood, impact, and mitigation
- High-impact risks have a concrete mitigation — not "monitor and respond"

**Flag as WARN when:**
- Fewer than 3 risks documented
- A risk has no mitigation defined
- A high-impact risk mitigation is purely reactive

---

### Check 9 — Previous PI Handoff Verification

Read `{PREVIOUS_PI}/README.md` and `{PREVIOUS_PI}/DEFINITION_OF_DONE.md`.

Check `{PREVIOUS_PI}/README.md` for the status field:

```bash
rg "Status:" docs/04-program/{PREVIOUS_PI}/README.md
```

**For PI-01 (no previous PI):** skip this check — mark as N/A.

**For all other PIs:**

- Previous PI status must be `COMPLETE` or `CLOSED`
- The "Handoff to PI-{N}" section must exist in the previous PI's `README.md`
- Every item in the handoff requirements must be verifiable

Check current repository state against the handoff requirements:

```bash
# Verify handoff infrastructure claims from previous PI README
git log --oneline --all | head -20
ls src/
```

**Flag as BLOCKED when:**
- Previous PI status is not `COMPLETE` or `CLOSED`
- Handoff section is missing from previous PI README
- A handoff requirement references infrastructure that does not exist in `src/`

---

### Check 10 — Contract Integrity

Validate that every contract schema the PI references is present and valid:

```bash
python scripts/validate_contract.py contracts/
```

If `scripts/validate_contract.py` is unavailable:
```bash
python -c "
import json, sys
from pathlib import Path
for f in Path('contracts').glob('*.schema.json'):
    try:
        json.loads(f.read_text())
        print(f'OK: {f.name}')
    except json.JSONDecodeError as e:
        print(f'INVALID: {f.name} — {e}')
        sys.exit(1)
"
```

Check whether the PI introduces new events, agents, or tools that require a new or updated contract:

```bash
rg "new.*agent|register.*agent|new.*tool|new.*event.*type" docs/04-program/{PI}/CAPABILITIES.md -i
```

If new agents, tools, or event types are introduced: confirm their contract schemas exist or note that they must be created before implementation begins.

**Flag as FAIL when:**
- Any existing contract schema is invalid JSON
- A new agent or tool is described in CAPABILITIES.md but no contract schema exists
- A new event type is described with no envelope schema reference

---

### Check 11 — Architecture Alignment

Cross-reference `CAPABILITIES.md` against `ARCHITECTURE.md` and `CONSTITUTION.md`.

For each capability:
- The service it describes exists in `ARCHITECTURE.md`
- No capability describes agent-to-agent communication (Constitution A1)
- No capability places specialist logic in the orchestrator (Constitution A2)
- No capability describes direct inter-service HTTP calls (Constitution A4)

```bash
rg "calls.*agent|agent.*calls|direct.*http|http.*direct" docs/04-program/{PI}/CAPABILITIES.md -i
rg "orchestrator.*generat|orchestrator.*execut" docs/04-program/{PI}/CAPABILITIES.md -i
```

**Flag as FAIL when:**
- A capability describes a pattern that violates any Constitution principle

---

### Check 12 — Definition of Done Completeness

Read `DEFINITION_OF_DONE.md`. Verify:

- Story-Level Gate section is present and contains at minimum: architecture, code quality, database (if applicable), Kafka (if applicable), security, and documentation items
- PI-Level Gate section is present and contains at minimum: operational readiness, CI/CD, security, and PI handoff items
- All items are concrete and verifiable (no subjective criteria)

**Flag as FAIL when:**
- Either gate section is missing
- A gate item is not verifiable (subjective language)

---

## Review Lenses

After running all 12 checks, apply these cross-cutting lenses.

### Lens A — Implementation Readiness

Can an engineer pick up Sprint 1, Story 1 and begin implementation immediately?

- Are acceptance criteria specific enough to write a failing test?
- Does `IMPLEMENTATION.md` define the service scaffold pattern for this PI?
- Is `aep-common` listed as available for this PI's services?

**Flag as BLOCKED when:** An engineer cannot start Sprint 1, Story 1 without additional clarification.

### Lens B — Infrastructure Gap

Does the PI require infrastructure that does not yet exist?

Compare the infrastructure implied by `CAPABILITIES.md` against:
- What was delivered in the previous PI (check `{PREVIOUS_PI}/README.md`)
- What exists in `src/`

List every infrastructure gap with the sprint in which it must be resolved.

### Lens C — Scope Realism

Is the PI scope realistic for the sprint count?

Count total story points across all sprints in `SPRINT_PLAN.md`. Divide by number of sprints. Flag if any sprint exceeds 35 points (overloaded) or is below 10 points (underloaded).

Calculate: total stories ÷ sprints. If > 8 stories per sprint on average, flag as at-risk.

### Lens D — Dependency Risk

Which stories have external dependencies (on other PIs, on infrastructure, on contracts not yet created)?

List every external dependency and its owner. Flag any that are on the critical path of Sprint 1.

---

## Expected Outputs

The kickoff produces three artefacts:

### 1. Kickoff Report

Structured verdict document (see Output Format below).

### 2. Sprint 1 Execution Checklist

A concrete, ordered list of tasks to begin Sprint 1:

```
## Sprint 1 Execution Checklist — {PI} Sprint 1

Pre-implementation (complete before any code):
  [ ] {infrastructure_step_1}
  [ ] {infrastructure_step_2}
  [ ] {contract_step}

Story sequence (implement in this order):
  [ ] US-{N}.01 — {story_title}   → .ai/commands/implement-story.md
  [ ] US-{N}.02 — {story_title}   → .ai/commands/implement-story.md
  ...

Per-story review sequence (after each story):
  [ ] Run: /aep-review <PR_NUMBER>

Sprint completion gate:
  [ ] All Sprint 1 acceptance criteria verified
  [ ] Sprint 1 goal statement met
  [ ] DEFINITION_OF_DONE.md Story-Level Gate passed for each story
```

### 3. Infrastructure Readiness Matrix

```
## Infrastructure Readiness — {PI}

| Component | Required in PI | Required in Sprint | Status | Action |
|-----------|---------------|-------------------|--------|--------|
| PostgreSQL | Yes | Sprint 1 | EXISTS | Use PI-01 migration |
| Kafka topic: aep.X | Yes | Sprint 1 | MISSING | Create before US-N.01 |
| Redis key schema | Yes | Sprint 2 | EXISTS | Use PI-01 keyspace |
| ...

Blockers (must resolve before Sprint 1):
  1. {blocker}

Deferrals (safe to resolve later):
  1. {deferral}
```

---

## Completion Checklist

```
[ ] Check 1: All 11 documents present and non-empty
[ ] Check 2: Objectives have measurable outcomes
[ ] Check 3: Every story has acceptance criteria
[ ] Check 4: All AC in Given/When/Then format with testable Then clauses
[ ] Check 5: Sprint plan covers all stories with goals
[ ] Check 6: All capabilities have stories assigned
[ ] Check 7: Prompt mapping complete, all commands exist
[ ] Check 8: Risk register has at least 3 risks with mitigations
[ ] Check 9: Previous PI handoff verified (or N/A for PI-01)
[ ] Check 10: All contract schemas valid, new schemas identified
[ ] Check 11: Capabilities aligned with Architecture and Constitution
[ ] Check 12: Definition of Done has both gates, all items verifiable
[ ] Lens A: Sprint 1 Story 1 can be started immediately
[ ] Lens B: Infrastructure gaps documented
[ ] Lens C: Scope realism assessed
[ ] Lens D: Dependency risks on critical path identified
[ ] Kickoff report produced with PASS / FAIL / BLOCKED verdict
[ ] Sprint 1 Execution Checklist produced
[ ] Infrastructure Readiness Matrix produced
```

---

## Forbidden Actions

- Begin implementation for any story before the kickoff verdict is PASS
- Modify `CONSTITUTION.md`, `ARCHITECTURE.md`, or any PI document during kickoff
- Mark a PI as PASS when any Check has status FAIL or BLOCKED
- Invent findings not supported by the document content
- Skip a check because "it was probably done"
- Produce a kickoff report without a concrete Sprint 1 Execution Checklist
- Redesign any capability or architecture
- Add, remove, or merge User Stories during kickoff
- Approve infrastructure that is not required by the current PI's stories

---

## Output Format

```
## PI Kickoff Report: {PI}
Date: {YYYY-MM-DD}
Executed by: pi-kickoff skill

---

### Verdict: PASS | FAIL | BLOCKED

{One paragraph explaining the verdict and the primary reason.}

---

### Check Results

| Check | Status | Finding |
|-------|--------|---------|
| 1 Documentation Completeness | ✅ PASS / ❌ FAIL / ⚠️ WARN | {summary} |
| 2 Objectives Validity | ✅ / ❌ / ⚠️ | {summary} |
| 3 User Stories Completeness | ✅ / ❌ / ⚠️ | {summary} |
| 4 Acceptance Criteria Quality | ✅ / ❌ / ⚠️ | {summary} |
| 5 Sprint Plan Validity | ✅ / ❌ / ⚠️ | {summary} |
| 6 Capability Coverage | ✅ / ❌ / ⚠️ | {summary} |
| 7 Prompt Mapping Completeness | ✅ / ❌ / ⚠️ | {summary} |
| 8 Risk Register | ✅ / ❌ / ⚠️ | {summary} |
| 9 Previous PI Handoff | ✅ / ❌ / ⚠️ / N/A | {summary} |
| 10 Contract Integrity | ✅ / ❌ / ⚠️ | {summary} |
| 11 Architecture Alignment | ✅ / ❌ / ⚠️ | {summary} |
| 12 Definition of Done | ✅ / ❌ / ⚠️ | {summary} |

---

### Failures (must resolve before implementation begins)
{If none: "No failures."}

#### FAIL: {check_name}
**File:** {document}:{line}
**Finding:** {what is wrong}
**Why it matters:** {concrete consequence if not fixed}
**Fix:** {specific action required}

---

### Warnings (should resolve, not blocking)
{If none: "No warnings."}

#### WARN: {check_name}
**Finding:** {what is incomplete}
**Why it matters:** {risk if ignored}
**Recommendation:** {specific action}

---

### Blockers (previous PI not complete — cannot start)
{If none: "No blockers."}

#### BLOCKED: {reason}
**Evidence:** {what was checked}
**Required:** {what must be true before this PI can start}

---

### Lens Results

**Lens A — Implementation Readiness:** READY | NOT READY
{explanation}

**Lens B — Infrastructure Gaps:**
{list of gaps with sprint required by}

**Lens C — Scope Realism:** ON TRACK | AT RISK | OVERLOADED
Sprint averages: {N} points/sprint, {N} stories/sprint

**Lens D — Critical Path Dependencies:**
{list of Sprint 1 dependencies and their status}

---

### Sprint 1 Execution Checklist
{full checklist — see Expected Outputs}

---

### Infrastructure Readiness Matrix
{full matrix — see Expected Outputs}

---

### Recommended First Action
{One concrete sentence: exactly what the engineer should do next.}
```

---

## Merge Criteria

This skill does not produce a PR. It produces a kickoff verdict.

**Implementation may begin when:**
- Verdict is **PASS**
- All FAIL checks are resolved and re-verified
- Sprint 1 Execution Checklist is available
- Infrastructure gaps in Sprint 1 column are resolved

**Implementation must not begin when:**
- Verdict is **FAIL** — resolve all failures first
- Verdict is **BLOCKED** — previous PI must close first
- Any Check with status FAIL remains open
- A Sprint 1 blocker in the Infrastructure Readiness Matrix is unresolved
