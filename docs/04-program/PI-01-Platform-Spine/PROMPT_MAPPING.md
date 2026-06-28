# PI-01 — Prompt Mapping

> This file does not contain prompts.
> It maps each User Story to reusable commands in `.ai/commands/`.
> The prompt library lives in `.ai/`. This file is a reference index only.

---

## How to use this file

1. Identify the user story you are implementing
2. Find the matching command reference below
3. Open the linked `.ai/commands/` file
4. Follow the prompt instructions, substituting `{placeholders}` with PI-01 context

---

## US-01.01 — Service Bootstrap

| Activity | Command |
|----------|---------|
| Implement | → `.ai/commands/implement-story.md` |
| Review | → `.ai/commands/review-story.md` |
| Testing | → `.ai/commands/generate-tests.md` |
| Security Review | → `.ai/commands/security-review.md` |
| Documentation | → `.ai/commands/update-documentation.md` |

**PI-01 context:** Service = all 16 platform services. Scaffold pattern defined in `IMPLEMENTATION.md`.

---

## US-01.02 — Local Developer Environment

| Activity | Command |
|----------|---------|
| Implement | → `.ai/commands/implement-story.md` |
| Review | → `.ai/commands/review-story.md` |
| Testing | → `.ai/commands/generate-tests.md` |
| Documentation | → `.ai/commands/update-documentation.md` |

**PI-01 context:** Deliverable = `docker-compose.yml` + `Makefile`. Target: `make dev-up` in < 5 min.

---

## US-01.03 — Event Bus Ready

| Activity | Command |
|----------|---------|
| Implement | → `.ai/commands/implement-story.md` |
| Review | → `.ai/commands/review-story.md` |
| Testing | → `.ai/commands/generate-tests.md` |
| Security Review | → `.ai/commands/security-review.md` |
| Documentation | → `.ai/commands/update-documentation.md` |

**PI-01 context:** Deliverable = Kafka topic provisioning script. Schema in `ARCHITECTURE.md` Event Flow section.

---

## US-01.04 — Database Migrated

| Activity | Command |
|----------|---------|
| Implement | → `.ai/commands/implement-story.md` |
| Review | → `.ai/commands/review-story.md` |
| Testing | → `.ai/commands/generate-tests.md` |
| Security Review | → `.ai/commands/security-review.md` |
| Documentation | → `.ai/commands/update-documentation.md` |

**PI-01 context:** Deliverable = Alembic migrations + RLS policies. Schema in `DATA_MODEL.md`.

---

## US-01.05 — CI Feedback

| Activity | Command |
|----------|---------|
| Implement | → `.ai/commands/implement-story.md` |
| Review | → `.ai/commands/review-story.md` |
| Testing | → `.ai/commands/generate-tests.md` |
| Security Review | → `.ai/commands/security-review.md` |
| Documentation | → `.ai/commands/update-documentation.md` |
| Release | → `.ai/commands/release-story.md` |

**PI-01 context:** Deliverable = `.github/workflows/ci.yml`. Target: < 8 min pipeline.

---

## US-01.06 — Shared Logging

| Activity | Command |
|----------|---------|
| Implement | → `.ai/commands/implement-story.md` |
| Review | → `.ai/commands/review-story.md` |
| Testing | → `.ai/commands/generate-tests.md` |
| Documentation | → `.ai/commands/update-documentation.md` |

**PI-01 context:** Deliverable = `src/shared/aep_common/logging.py`. Uses structlog.

---

## US-01.07 — Observability Baseline

| Activity | Command |
|----------|---------|
| Implement | → `.ai/commands/implement-story.md` |
| Review | → `.ai/commands/review-story.md` |
| Testing | → `.ai/commands/generate-tests.md` |
| Performance Review | → `.ai/commands/performance-review.md` |
| Documentation | → `.ai/commands/update-documentation.md` |

**PI-01 context:** Deliverable = OTEL collector config + Prometheus scrape + Grafana health dashboard.

---

## Standard Commands (all stories)

Every story in every PI maps to at minimum these four commands:

| Activity | Command | When to use |
|----------|---------|-------------|
| Implement | `.ai/commands/implement-story.md` | Before writing the first line |
| Review | `.ai/commands/review-story.md` | Before raising a PR |
| Generate Tests | `.ai/commands/generate-tests.md` | Alongside or after implementation |
| Security Review | `.ai/commands/security-review.md` | On every story touching auth, secrets, or data |

Additional commands used when applicable:

| Activity | Command | When to use |
|----------|---------|-------------|
| Performance Review | `.ai/commands/performance-review.md` | Stories with latency or throughput targets |
| Documentation | `.ai/commands/update-documentation.md` | Stories producing a new API or public interface |
| Release | `.ai/commands/release-story.md` | End-of-PI release stories only |
