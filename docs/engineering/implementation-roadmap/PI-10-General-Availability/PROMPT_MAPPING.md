# PI-10-General-Availability — Prompt Mapping

> **Architecture Baseline v2.0:** [ARCHITECTURE_BASELINE_V2.md](../../../architecture/ARCHITECTURE_BASELINE_V2.md) · [PLATFORM_GLOSSARY.md](../../../architecture/PLATFORM_GLOSSARY.md)

> This file does not contain prompts.
> It maps each User Story to reusable commands in \`.ai/commands/\`.
> The prompt library lives in \`.ai/\`. This file is a reference index only.

---

## How to use this file

1. Identify the user story you are implementing
2. Find the matching command reference below
3. Open the linked \`.ai/commands/\` file
4. Follow the prompt instructions, substituting \\{placeholders}\\ with PI-10 context

---

## US-PI-10-01 — Core Functionality

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Release | ? \`.ai/commands/release-story.md\` |

**PI-10 context:** Deliverable = Terraform modules + K8s manifests + Helm chart + chaos test suite + GA release v1.0.0.

---

## US-PI-10-02 — Observability

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Performance Review | ? \`.ai/commands/performance-review.md\` |

**PI-10 context:** Full observability stack operational. 5 Grafana dashboard sets live for all audiences.

---

## US-PI-10-03 — Tenant Isolation

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Security Review | ? \`.ai/commands/security-review.md\` |

**PI-10 context:** Penetration test report: zero cross-tenant findings. DR drill: zero data loss.

---

## US-PI-10-04 — Security

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Security Review | ? \`.ai/commands/security-review.md\` |

**PI-10 context:** External pen test: zero critical/high findings. All CVEs remediated before GA tag.

---

## US-PI-10-05 — Developer Onboarding

| Activity | Command |
|----------|---------|
| Implement | ? \`.ai/commands/implement-story.md\` |
| Review | ? \`.ai/commands/review-story.md\` |
| Testing | ? \`.ai/commands/generate-tests.md\` |
| Documentation | ? \`.ai/commands/update-documentation.md\` |
| Release | ? \`.ai/commands/release-story.md\` |

**PI-10 context:** All five documentation guides peer-reviewed and published. Beta pilot: 2 external tenants live.

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
