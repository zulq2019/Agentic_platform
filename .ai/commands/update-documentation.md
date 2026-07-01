# update-documentation.md

**Command:** `update-documentation`  
**Version:** 1.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs, all sprints — run after every story that changes public contracts, APIs, events, or architecture

---

## Purpose

Use this command to update all documentation affected by a completed implementation.

Documentation is a first-class deliverable. Code that is not documented is incomplete. This command identifies every documentation artifact that must be updated, produces the updates, and verifies nothing was missed.

Run this command after `implement-story.md` and before raising a PR.

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture | `ARCHITECTURE.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` (Documentation Rules section) | Mandatory |
| Changed files | `git diff main` | Mandatory |
| User Story | `docs/engineering/implementation-roadmap/{PI}/USER_STORIES.md` — implemented story | Mandatory |
| API Spec | `docs/engineering/implementation-roadmap/{PI}/API_SPEC.md` | If story produces/modifies API |
| Data Model | `docs/engineering/implementation-roadmap/{PI}/DATA_MODEL.md` | If story touches schema |
| Sequence Diagrams | `docs/engineering/implementation-roadmap/{PI}/SEQUENCE_DIAGRAMS.md` | If story changes a flow |
| ADR log | `DECISIONS.md` | If story involved an architectural decision |
| Architecture diagrams | `docs/architecture/REFERENCE_ARCHITECTURE.md` | If service boundaries changed |
| `.env.example` | Service root | If new environment variables introduced |

**Substitutions required:**

```
{PI}          = e.g. PI-04-Workflow-Framework
{story_id}    = e.g. US-PI-04-02
{service_name} = e.g. memory-store-service
```

---

## Preconditions

- [ ] Implementation is complete and all tests pass
- [ ] Review via `review-story.md` is complete with PASS verdict
- [ ] `git diff main` is available showing all changes

---

## Execution Steps

### Step 1 — Identify what changed

Categorise every changed file from `git diff main`:

```
Category A — Public API changed:
  New or modified endpoints
  Request/response schema changes
  New error codes introduced

Category B — Events changed:
  New Kafka topic introduced
  Existing event schema modified
  New event type published or consumed

Category C — Data model changed:
  New table or collection
  New column or field
  Index added or removed
  Migration file added

Category D — Configuration changed:
  New environment variable
  Default value changed
  New Kubernetes resource limit

Category E — Architecture boundary changed:
  New service introduced
  Service moved to different container
  New inter-service interaction added

Category F — Agent or tool changed:
  New agent registered
  New tool registered
  Agent capability tags modified
```

### Step 2 — Update API spec (if Category A)

Update `docs/engineering/implementation-roadmap/{PI}/API_SPEC.md`:
- Add documentation for every new endpoint
- Update request/response schema for every modified endpoint
- Document every new error code with HTTP status, error code string, and description
- Update the changelog at the bottom of the file with the story ID and version

Format every endpoint as:
```markdown
### POST /api/v1/{resource}

**Purpose:** One-sentence description.  
**Auth:** Bearer token required | API key required | Internal only  
**Tenant scope:** Request scoped to `tenant_id` from auth context

**Request:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|

**Response (200):**
| Field | Type | Description |
|-------|------|-------------|

**Error Responses:**
| Code | HTTP Status | Description |
|------|-------------|-------------|
```

### Step 3 — Update event catalogue (if Category B)

Update `docs/engineering/implementation-roadmap/{PI}/SEQUENCE_DIAGRAMS.md` if a new event flow was introduced.

Also update the Event Catalogue in `docs/architecture/REFERENCE_ARCHITECTURE.md` (Section 8):
- Add the new topic and its schema reference
- Add the new event type and its producer/consumer mapping

### Step 4 — Update data model (if Category C)

Update `docs/engineering/implementation-roadmap/{PI}/DATA_MODEL.md`:
- Add ERD entry for new tables
- Document every new column with type, constraints, and purpose
- Document the migration file that introduces the change
- If the data model affects another PI, cross-reference it

### Step 5 — Update environment variable documentation (if Category D)

Update `.env.example` in the service directory:
- Add every new environment variable with a safe example value and description comment
- Use this format:
  ```
  # Description of what this variable does and where to get the value
  VARIABLE_NAME=example-safe-value
  ```

Update `REPOSITORY_GUIDE.md` if a new platform-wide environment variable was introduced.

### Step 6 — Update architecture documentation (if Category E)

If a service boundary changed:
- Update `ARCHITECTURE.md` — the C4 diagrams and service descriptions
- Update `docs/architecture/REFERENCE_ARCHITECTURE.md` — relevant diagram section
- Create a new ADR in `DECISIONS.md` explaining the decision

ADR format:
```markdown
## ADR-{NNN}: {Short Title}
**Date:** {YYYY-MM-DD}  
**Status:** Accepted  
**Author:** {engineer}

### Context
What problem was being solved?

### Decision
What was decided?

### Consequences
What are the effects of this decision?
### Constitutional Principles Applied
List applicable CONSTITUTION.md principle IDs.
```

### Step 7 — Update agent/tool registry documentation (if Category F)

If a new agent or tool was registered:
- Add it to `ARCHITECTURE.md` — the Agent Registry section or Tool Registry section
- Document its capability tags, cost class, and supported operations
- If the tool has a new scope, document the approval that granted it

### Step 8 — Verify completeness

Produce a documentation update summary:

```
## Documentation Update Summary: {story_id}

### Updated Documents
1. {document} — {what changed}
2. ...

### No Update Required
1. {document} — {reason}

### New Documents Created
1. {document} — {purpose}

### ADRs Created
ADR-{NNN}: {title} — {one line summary}
```

---

## Expected Outputs

| Artifact | When Required |
|----------|--------------|
| Updated API spec | Any endpoint added or changed |
| Updated sequence diagrams | Any event flow changed |
| Updated data model | Any schema changed |
| Updated `.env.example` | Any new environment variable |
| Updated `ARCHITECTURE.md` | Any service boundary change |
| New ADR in `DECISIONS.md` | Any architectural decision made |
| Updated REFERENCE_ARCHITECTURE.md | Any event catalogue or diagram change |
| Documentation update summary | Always |

---

## Quality Gates

- [ ] Every new API endpoint is documented in API_SPEC.md
- [ ] Every new Kafka event type appears in the event catalogue
- [ ] Every new environment variable appears in `.env.example`
- [ ] Every new database table appears in DATA_MODEL.md
- [ ] Every architectural decision has an ADR
- [ ] No documentation references an old service name or removed endpoint
- [ ] Cross-references between PI documents are valid

---

## Completion Checklist

```
[ ] Changed files categorised — API, events, data, config, architecture, agents/tools
[ ] API spec updated (if applicable)
[ ] Event catalogue updated (if applicable)
[ ] Data model updated (if applicable)
[ ] .env.example updated (if applicable)
[ ] ARCHITECTURE.md updated (if applicable)
[ ] ADR created (if architectural decision was made)
[ ] REFERENCE_ARCHITECTURE.md updated (if applicable)
[ ] Documentation update summary produced
[ ] No broken cross-references introduced
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Skip documentation because "it is obvious from the code"
- Modify the Constitution in documentation updates
- Remove documentation for features that still exist
- Create documentation for features that were not implemented
- Merge RBAC, Policy, and Secrets into a single documentation section
- Accept a new endpoint without documentation as "temporary"
- Create a new ADR for a decision that was already documented
- Modify documentation to match an implementation that violates the Constitution
- Use future tense in API documentation — document only what was implemented
