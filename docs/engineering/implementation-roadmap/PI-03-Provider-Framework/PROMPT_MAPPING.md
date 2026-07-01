# PI-03-Provider-Framework — Prompt Mapping

> **Architecture Baseline v2.0:** Orchestrator = **Planner**; resolve **Providers** by capability tag. See [ARCHITECTURE_BASELINE_V2.md](../../../architecture/ARCHITECTURE_BASELINE_V2.md).

> This file does not contain prompts.
> It maps each User Story to reusable commands in \`.ai/commands/\`.
> The prompt library lives in \`.ai/\`. This file is a reference index only.

---

## How to use this file

1. Identify the user story you are implementing
2. Find the matching command reference below
3. Open the linked \`.ai/commands/\` file
4. Follow the prompt instructions, substituting \\{placeholders}\\ with PI-03 context

---

## US-PI-03-01 — Core Functionality

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |

**PI-03 context:** Deliverable = orchestrator-service, workflow-engine, task-engine, approval-service. Gate enforcement non-bypassable.

---

## US-PI-03-02 — Observability

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Performance Review | ? \`.ai/commands/performance-review.md\` |

**PI-03 context:** Distributed traces span orchestrator ? agent-runtime ? audit-service.

---

## US-PI-03-03 — Tenant Isolation

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Security Review | ? \`.ai/commands/security-review.md\` |

**PI-03 context:** workflow_runs and tasks tables RLS-enforced. No cross-tenant workflow visibility.

---

## US-PI-03-04 — Security

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Security Review | ? \`.ai/commands/security-review.md\` |

**PI-03 context:** Gate enforcer has no bypass flag. Approval records are signed and immutable.

---

## US-PI-03-05 — Developer Onboarding

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Documentation | ? \`.ai/commands/update-documentation.md\` |

**PI-03 context:** New developer triggers a full greenfield workflow end-to-end within 2 hours.

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
