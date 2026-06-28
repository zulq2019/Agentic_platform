# PI-08-Enterprise — Prompt Mapping

> This file does not contain prompts.
> It maps each User Story to reusable commands in \`.ai/commands/\`.
> The prompt library lives in \`.ai/\`. This file is a reference index only.

---

## How to use this file

1. Identify the user story you are implementing
2. Find the matching command reference below
3. Open the linked \`.ai/commands/\` file
4. Follow the prompt instructions, substituting \\{placeholders}\\ with PI-08 context

---

## US-PI-08-01 — Core Functionality

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |

**PI-08 context:** Deliverable = full 3-layer multi-tenancy + config-service + enterprise SSO + SCIM + SLA monitoring.

---

## US-PI-08-02 — Observability

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Performance Review | → \`.ai/commands/performance-review.md\` |

**PI-08 context:** Per-tenant SLA dashboard. Resource quota usage alerts at 80%.

---

## US-PI-08-03 — Tenant Isolation

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Security Review | → \`.ai/commands/security-review.md\` |

**PI-08 context:** 50 cross-tenant penetration attempts return zero rows. One codebase, no per-tenant forks.

---

## US-PI-08-04 — Security

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Security Review | → \`.ai/commands/security-review.md\` |

**PI-08 context:** SAML SSO + SCIM provisioning. Data residency controls per tenant region.

---

## US-PI-08-05 — Developer Onboarding

| Activity | Command |
|----------|---------|
| Implement | → \`.ai/commands/implement-story.md\` |
| Review | → \`.ai/commands/review-story.md\` |
| Testing | → \`.ai/commands/generate-tests.md\` |
| Documentation | → \`.ai/commands/update-documentation.md\` |

**PI-08 context:** New Fortune 500 tenant fully onboarded in under 15 minutes without code changes.

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
