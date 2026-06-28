# PI-04-Memory — Prompt Mapping

> This file does not contain prompts.
> It maps each User Story to reusable commands in \`.ai/commands/\`.
> The prompt library lives in \`.ai/\`. This file is a reference index only.

---

## How to use this file

1. Identify the user story you are implementing
2. Find the matching command reference below
3. Open the linked \`.ai/commands/\` file
4. Follow the prompt instructions, substituting \\{placeholders}\\ with PI-04 context

---

## US-PI-04-01 — Core Functionality

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |

**PI-04 context:** Deliverable = memory-service with working context (Redis) and LTM (pgvector). Two separate service layers.

---

## US-PI-04-02 — Observability

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Performance Review | → \`.ai/commands/performance-review.md\` |

**PI-04 context:** Memory query latency tracked as histogram. LTM write events published to audit.

---

## US-PI-04-03 — Tenant Isolation

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Security Review | → \`.ai/commands/security-review.md\` |

**PI-04 context:** pgvector queries always filter by tenant_id at storage layer. Cross-tenant vector search blocked.

---

## US-PI-04-04 — Security

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Security Review | → \`.ai/commands/security-review.md\` |

**PI-04 context:** No agent writes to LTM directly. Only PostWorkflowWriter. Provenance required on every LTM write.

---

## US-PI-04-05 — Developer Onboarding

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Documentation | → \`.ai/commands/update-documentation.md\` |

**PI-04 context:** Memory API documented with examples for working context read/write and LTM filtered query.

---

## Standard Commands (all stories)

Every story in every PI maps to at minimum these four commands:

| Activity | Command | When to use |
|----------|---------|-------------|
| Implement | \`.ai/commands/implement-story.md\` | Before writing the first line |
| Review | \`.ai/commands/review-story.md\` | Before raising a PR |
| Generate Tests | \`.ai/commands/generate-tests.md\` | Alongside or after implementation |
| Security Review | \`.ai/commands/security-review.md\` | On every story touching auth, secrets, or data |

Additional commands used when applicable:

| Activity | Command | When to use |
|----------|---------|-------------|
| Performance Review | \`.ai/commands/performance-review.md\` | Stories with latency or throughput targets |
| Documentation | \`.ai/commands/update-documentation.md\` | Stories producing a new API or public interface |
| Release | \`.ai/commands/release-story.md\` | End-of-PI release stories only |
