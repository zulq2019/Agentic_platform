# PI-09-Platform-UX — Prompt Mapping

> This file does not contain prompts.
> It maps each User Story to reusable commands in \`.ai/commands/\`.
> The prompt library lives in \`.ai/\`. This file is a reference index only.

---

## How to use this file

1. Identify the user story you are implementing
2. Find the matching command reference below
3. Open the linked \`.ai/commands/\` file
4. Follow the prompt instructions, substituting \\{placeholders}\\ with PI-09 context

---

## US-PI-09-01 — Core Functionality

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |

**PI-09 context:** Deliverable = React dashboard (9 views) + REST/WebSocket APIs + CLI tool + SDK docs site.

---

## US-PI-09-02 — Observability

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Performance Review | ? \`.ai/commands/performance-review.md\` |

**PI-09 context:** Frontend performance: p99 page load < 2s. WebSocket reconnect transparent to user.

---

## US-PI-09-03 — Tenant Isolation

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Security Review | ? \`.ai/commands/security-review.md\` |

**PI-09 context:** Dashboard shows only current tenant's data. Tenant context enforced in all API calls.

---

## US-PI-09-04 — Security

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Security Review | ? \`.ai/commands/security-review.md\` |

**PI-09 context:** All API endpoints require JWT. CSRF protection on form submissions. WCAG 2.1 AA.

---

## US-PI-09-05 — Developer Onboarding

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Documentation | ? \`.ai/commands/update-documentation.md\` |

**PI-09 context:** External developer builds and registers new agent end-to-end using developer portal in under 1 hour.

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
