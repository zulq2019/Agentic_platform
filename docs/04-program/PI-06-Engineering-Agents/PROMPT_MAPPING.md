# PI-06-Engineering-Agents — Prompt Mapping

> **Architecture Baseline v2.0:** [ARCHITECTURE_BASELINE_V2.md](../../architecture/ARCHITECTURE_BASELINE_V2.md) · [PLATFORM_GLOSSARY.md](../../architecture/PLATFORM_GLOSSARY.md)

> This file does not contain prompts.
> It maps each User Story to reusable commands in \`.ai/commands/\`.
> The prompt library lives in \`.ai/\`. This file is a reference index only.

---

## How to use this file

1. Identify the user story you are implementing
2. Find the matching command reference below
3. Open the linked \`.ai/commands/\` file
4. Follow the prompt instructions, substituting \\{placeholders}\\ with PI-06 context

---

## US-PI-06-01 — Core Functionality

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |

**PI-06 context:** Deliverable = all 15 specialist agents as `ai-agent` Providers. Each implements Agent Contract (maps to Provider Contract G-02) and idempotency strategy.

---

## US-PI-06-02 — Observability

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Performance Review | → \`.ai/commands/performance-review.md\` |

**PI-06 context:** Per-agent execution duration and retry count tracked. Langfuse LLM observability wired.

---

## US-PI-06-03 — Tenant Isolation

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Security Review | → \`.ai/commands/security-review.md\` |

**PI-06 context:** All agent context packets are tenant-scoped. No cross-tenant memory or tool access.

---

## US-PI-06-04 — Security

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Security Review | → \`.ai/commands/security-review.md\` |

**PI-06 context:** No agent imports vendor SDK directly. No agent calls another agent.

---

## US-PI-06-05 — Developer Onboarding

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Documentation | → \`.ai/commands/update-documentation.md\` |

**PI-06 context:** Third-party developer registers a new specialist agent in under 1 day using the SDK and BLUEPRINT.md.

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
