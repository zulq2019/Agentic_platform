#!/usr/bin/env python3
"""Upgrade implement-story SKILL.md to v6.0 — Architecture Decision Engine pipeline."""

from __future__ import annotations

import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / ".ai/skills/implement-story/SKILL.md"

ADE_MODE_A_B = """
## Phase 2 — Architecture Decision Engine — Mode A ("Should we build this?")

**Mandatory for every story. Executes immediately after Phase 1 (Architecture Discovery)
and before Phase 3 (Architecture Reuse). Uses `{story_ref}` from invocation; full story
context is confirmed in Phase 4.**

### Purpose (Evaluate Requirement)

Determine whether the requested capability **should be implemented at all**, or whether
it should be realized through existing Platform Primitives, metadata, configuration,
composition, workflows, policies, providers, or plugins.

This is an **Architecture Decision** — not an AI brainstorming step. Mode A answers:
**"Should this exist as new code?"**

### Quality principle

**Prefer:** Reuse, Configuration, Composition, Metadata  
**Over:** New Services, New Frameworks, Hardcoded Logic, New Microservices

### Discovery commands

```bash
find . \\( -iname 'PLATFORM_PRIMITIVES.md' -o -iname 'PLATFORM_META_MODEL.md' -o -iname 'PLATFORM_CONTRACTS.md' \\) ! -path '*/.git/*' 2>/dev/null
rg -i "{story_ref keywords}" docs/ src/ contracts/ --glob "*.md" --glob "*.py" --glob "*.json" 2>/dev/null | head -40
```

### Mode A — five mandatory questions

| # | Question | Evidence required |
|---|----------|-------------------|
| A1 | Does this **capability already exist**? | Services, APIs, providers, plugins, workflows, contracts, metadata |
| A2 | Can **metadata** solve it? | Platform Object model, config surfaces, tenant metadata |
| A3 | Can **configuration** solve it? | Feature flags, policy config, env-driven behaviour |
| A4 | Can **composition** of existing primitives solve it? | Registries, extension points, composed workflows |
| A5 | Does building this **violate Platform Primitives** or contracts? | `PLATFORM_PRIMITIVES.md`, `contracts/`, constitutional principles |

Per question output:

```
A{n}: {short label}
  Answer:     YES / NO / PARTIAL
  Evidence:   {paths, object names, or NONE}
```

### Mode A decision

| Outcome | Condition | Action |
|---------|-----------|--------|
| **CONTINUE** | A1–A4 show viable reuse/config/composition path **or** net-new build is justified without primitive violation; A5 = NO | Proceed to Phase 3 (Mode B) |
| **STOP — Architecture RFC** | No justified net-new path, reuse score for Mode A < 40, or A5 = YES without approved ADR | **STOP** — Architecture RFC (template in Phase 3); **no production code** |

When **STOP**, deliver RFC per Phase 3 template. Do not proceed to Phase 4+ until
engineer reviews RFC and approves a path forward.

### Mode A summary (required)

```
Architecture Decision Engine — Mode A:
  Story ref:              {story_ref}
  Should we build this?:  YES / NO / PARTIAL — {rationale}
  Existing capability:      {found / not found}
  Metadata path:          {viable / not viable}
  Configuration path:     {viable / not viable}
  Composition path:       {viable / not viable}
  Primitive compliance:   COMPLIANT / VIOLATION RISK
  Mode A decision:        CONTINUE / STOP — ARCHITECTURE RFC
```

---

## Phase 3 — Architecture Reuse (ADE Mode B — "How should we build it?")

**Mandatory when Mode A = CONTINUE. Executes before Phase 4 (Story Resolution).**

### Purpose (Reuse Analysis → Architecture Compliance → Decision)

If the capability must be built or extended, determine **how** using existing platform
building blocks. Mode B answers: **"How should we realize this with minimum new surface area?"**

### Mode B — six mandatory questions

| # | Question | Map to |
|---|----------|--------|
| B1 | Which **Platform Objects**? | Studios, Capabilities, Resources, Artifacts, metadata envelope |
| B2 | Which **Providers**? | Provider Framework, provider registry, adapters |
| B3 | Which **Workflows**? | Workflow templates, state machines, orchestration |
| B4 | Which **Policies**? | Policy Engine, RBAC, tenant policy configuration |
| B5 | Which **Execution Profiles**? | Runtime profiles, model routing boundaries |
| B6 | Which **APIs**? | Existing HTTP/event surfaces to extend vs new endpoints |

Per question output:

```
B{n}: {short label}
  Answer:     {specific names / NONE / NEW REQUIRED}
  Evidence:   {paths, contract names, service names}
  Reuse:      {what to reuse — or justification for new}
```

### Architecture Reuse Score (0–100)

| Score | Meaning |
|-------|---------|
| 80–100 | Fully realizable via existing objects, metadata, composition |
| 50–79 | Partial reuse — bounded new code within existing boundaries |
| 20–49 | Limited reuse — RFC recommended before planning |
| 0–19 | No viable reuse — **STOP** and RFC mandatory |

Score B1–B6: full reuse = ~17 pts each; partial = ~8; new required = 0. Round average.
A5 primitive violation caps maximum at 49.

### Combined ADE decision (Mode A + Mode B)

| Outcome | Condition | Action |
|---------|-----------|--------|
| **CONTINUE** | Mode A = CONTINUE, Reuse Score ≥ 50, primitive compliance OK | Proceed to Phase 4 — list reused Platform Objects in ADE Summary |
| **STOP — Architecture RFC** | Mode A STOP, Reuse Score < 50, or unresolved primitive/contract violation | **STOP** — RFC below; no Phase 9+ planning or code |

### Architecture RFC template (when STOP)

Write to `docs/architecture/rfc/RFC-{story_id}-{slug}.md` or deliver inline:

```
## Architecture RFC: {story_id or story_ref} — {title}

### Business Requirement
### Problem Statement
### Existing Platform Capabilities
### Gap Analysis
### Alternative Solutions
### Recommended Architecture
### Affected Platform Objects
### Risks
### Migration Strategy
### Recommendation
```

### Architecture Decision Engine — Summary (required)

Produce after Phase 2 + Phase 3 for every story:

```
Architecture Decision Engine Summary:
  Story ref:                    {story_ref}
  Mode A — Should we build?:    {YES/NO/PARTIAL + decision}
  Mode B — How to build:        {reuse map from B1–B6}
  Architecture Reuse Score:     {0-100} — {justification}
  Configuration vs Code:        CONFIGURATION / CODE / HYBRID
  Composition Recommendation:   {what to compose — or NONE}
  Platform Objects Reused:      {list — or NONE}
  Architecture Compliance:      COMPLIANT / VIOLATION RISK
  Final Recommendation:         CONTINUE / STOP — ARCHITECTURE RFC REQUIRED
```

Include in progress reports:

```
ADE:               {CONTINUE / STOP — RFC}
Reuse Score:       {0-100}
```

**Only if ADE = CONTINUE** may the pipeline proceed to Story Resolution, Risk Assessment,
Dependencies, Implementation Plan, Approval, and Implementation.

---

"""

# Phase header renames (order matters — longer patterns first)
HEADER_RENAMES = [
    (r"## Phase 12 — Completion", "## Phase 15 — Completion"),
    (r"## Phase 11 — Documentation", "## Phase 14 — Documentation"),
    (r"## Phase 10 — Engineering Reviews", "## Phase 13 — Engineering Reviews"),
    (r"## Phase 9 — Testing", "## Phase 12 — Testing"),
    (r"## Phase 8 — Implementation", "## Phase 11 — Implementation"),
    (r"## Phase 7 — Implementation Planning", "## Phase 9 — Implementation Plan"),
    (
        r"## Phase 5 \(Preserved\) — Architecture Validation",
        "## Phase 8 — Architecture Validation",
    ),
    (
        r"## Phase 4 \(Preserved\) — Infrastructure Assessment",
        "## Phase 7 — Infrastructure Assessment",
    ),
    (r"## Phase 6 — Dependency Analysis", "## Phase 7 — Dependencies"),
    (r"## Phase 5 — Risk Based Approval", "## Phase 10 — Approval"),
    (r"## Phase 4 — Architecture Impact Analysis", "## Phase 6 — Risk Assessment"),
    (r"## Phase 2 \(Preserved\) — Story Readiness", "## Phase 5 — Story Readiness"),
    (r"## Phase 3 — Story Resolution", "## Phase 4 — Story Resolution"),
    (r"## Phase 2 — Architecture Context", "## Phase 1 — Architecture Discovery"),
    (
        r"## Phase 1 — Repository Discovery",
        "## Phase 1 — Repository Discovery (skill extension)",
    ),
]

# Fix duplicate Phase 7 — Infrastructure should be 7a or renumber
# After renames: Dependencies becomes Phase 7, Infrastructure also Phase 7 - conflict!
# Adjust: Dependencies = 7, Infrastructure = 7 (merge) - I'll rename Infrastructure to subsection

HEADER_RENAMES_FIXED = [
    (r"## Phase 12 — Completion", "## Phase 15 — Completion"),
    (r"## Phase 11 — Documentation", "## Phase 14 — Documentation"),
    (r"## Phase 10 — Engineering Reviews", "## Phase 13 — Engineering Reviews"),
    (r"## Phase 9 — Testing", "## Phase 12 — Testing"),
    (r"## Phase 8 — Implementation", "## Phase 11 — Implementation"),
    (r"## Phase 7 — Implementation Planning", "## Phase 9 — Implementation Plan"),
    (
        r"## Phase 5 \(Preserved\) — Architecture Validation",
        "## Phase 8 — Architecture Validation",
    ),
    (
        r"## Phase 4 \(Preserved\) — Infrastructure Assessment",
        "## Phase 7b — Infrastructure Assessment",
    ),
    (r"## Phase 6 — Dependency Analysis", "## Phase 7 — Dependencies"),
    (r"## Phase 5 — Risk Based Approval", "## Phase 10 — Approval"),
    (r"## Phase 4 — Architecture Impact Analysis", "## Phase 6 — Risk Assessment"),
    (r"## Phase 2 \(Preserved\) — Story Readiness", "## Phase 5 — Story Readiness"),
    (r"## Phase 3 — Story Resolution", "## Phase 4 — Story Resolution"),
    (r"## Phase 2 — Architecture Context", "## Phase 1 — Architecture Discovery"),
]

PHASE_5A_PATTERN = re.compile(
    r"## Phase 5A — Architecture Think Mode.*?(?=\n## Phase 6 — Dependency Analysis)",
    re.DOTALL,
)

APPROVAL_INSERT = """
**Approval executes after Phase 9 (Implementation Plan) and before Phase 11 (Implementation).**
Phase 6 classifies risk; Phase 10 enforces the approval gate immediately before coding.

"""


def main() -> None:
    text = SKILL.read_text(encoding="utf-8")

    # Frontmatter description
    text = text.replace(
        "runs mandatory Architecture Think Mode",
        "runs mandatory Architecture Decision Engine (ADE)",
    )
    text = text.replace(
        "**Version:** 5.1 — Enterprise Principal Engineer implementation engine",
        "**Version:** 6.0 — Enterprise Principal Engineer implementation engine",
    )
    text = text.replace(
        "**Backward compatible:** All invocation forms unchanged from v4.0 and v5.0.",
        "**Backward compatible:** All invocation forms unchanged from v4.0, v5.0, and v5.1.",
    )

    # Remove old Phase 5A
    text = PHASE_5A_PATTERN.sub("", text)

    # Insert ADE after Architecture Discovery (formerly Phase 2)
    marker = "## Phase 1 — Architecture Discovery"
    if marker not in text:
        marker = "## Phase 2 — Architecture Context"
    idx = text.find(marker)
    if idx == -1:
        raise SystemExit("Architecture Discovery section not found")
    # Find end of Phase 1 section (next ## Phase)
    next_phase = text.find("\n## Phase ", idx + len(marker))
    if next_phase == -1:
        raise SystemExit("Could not find end of Architecture Discovery")
    text = text[:next_phase] + ADE_MODE_A_B + text[next_phase:]

    # Rename headers
    for old, new in HEADER_RENAMES_FIXED:
        text = re.sub(old, new, text)

    # Pipeline section replacement
    old_pipeline = re.search(
        r"## Enterprise Execution Pipeline — 12 Phases.*?(?=\n## Step mapping)",
        text,
        re.DOTALL,
    )
    new_pipeline = """## Mature Execution Pipeline (v6.0)

Execute **all phases in order**. Do not write production code until Phase 9
(Implementation Plan) is complete, Phase 10 (Approval) gates are satisfied, and
the Architecture Decision Engine (Phases 2–3) returns **CONTINUE**.

```
Repository Discovery (Phase 0 + Phase 1 extension)
        ↓
Architecture Discovery (Phase 1)
        ↓
Architecture Decision Engine — Mode A: "Should we build this?" (Phase 2)
        ↓
Architecture Reuse — Mode B: "How should we build it?" (Phase 3)
        ↓
Story Resolution (Phase 4)
        ↓
Story Readiness & Capability (Phase 5)
        ↓
Risk Assessment (Phase 6)
        ↓
Dependencies (Phase 7) → Infrastructure Assessment (Phase 7b)
        ↓
Architecture Validation (Phase 8)
        ↓
Implementation Plan (Phase 9)
        ↓
Approval (Phase 10)
        ↓
Implementation (Phase 11)
        ↓
Testing (Phase 12)
        ↓
Reviews (Phase 13)
        ↓
Documentation (Phase 14)
        ↓
Completion (Phase 15)
```

### Phase mapping — v6.0 ↔ v5.1

| v6 Phase | Name | v5.1 equivalent |
|----------|------|-----------------|
| 0 | Repository Discovery (common) | Phase 0 prepend |
| 1 | Architecture Discovery | Phase 2 |
| 2 | ADE Mode A — Should we build? | Phase 5A (questions A1–A5) |
| 3 | ADE Mode B — Architecture Reuse | Phase 5A (questions B1–B6) |
| 4 | Story Resolution | Phase 3 |
| 5 | Story Readiness & Capability | Phase 2 preserved |
| 6 | Risk Assessment | Phase 4 impact analysis |
| 7 | Dependencies | Phase 6 |
| 7b | Infrastructure Assessment | Phase 4 preserved |
| 8 | Architecture Validation | Phase 5 preserved |
| 9 | Implementation Plan | Phase 7 |
| 10 | Approval | Phase 5 risk gates (before code) |
| 11 | Implementation | Phase 8 |
| 12 | Testing | Phase 9 |
| 13 | Reviews | Phase 10 |
| 14 | Documentation | Phase 11 |
| 15 | Completion | Phase 12 |

"""
    if old_pipeline:
        text = text[: old_pipeline.start()] + new_pipeline + text[old_pipeline.end() :]

    # Global terminology
    replacements = [
        ("Think Mode:", "ADE:"),
        ("Think Mode ", "Architecture Decision Engine "),
        ("Architecture Think Mode", "Architecture Decision Engine"),
        (
            "Phase 5A (Architecture Think Mode)",
            "Phases 2–3 (Architecture Decision Engine)",
        ),
        ("Phase 5A (Think Mode CONTINUE)", "ADE CONTINUE (Phases 2–3)"),
        ("Phase 5A (Think Mode)", "ADE (Phases 2–3)"),
        ("Phase 5A", "ADE (Phases 2–3)"),
        ("before Phase 5A", "before ADE (Phases 2–3)"),
        ("Phase 5A decision", "ADE decision"),
        (
            "Think Mode Reuse (from Phase 5A)",
            "Architecture Reuse (from ADE Phases 2–3)",
        ),
        ("Think Mode Summary", "Architecture Decision Engine Summary"),
        ("Reuse Score:", "Reuse Score:"),
        ("proceed to Phase 5A", "proceed to Phase 2 (ADE Mode A)"),
        ("Skip Phase 5A", "Skip ADE (Phases 2–3)"),
        (
            "Always run Architecture Think Mode (Phase 5A)",
            "Always run Architecture Decision Engine (Phases 2–3)",
        ),
        (
            "completing Phases 1–7, passing Phase 5A (Think Mode CONTINUE), and satisfying\nPhase 5 approval gates",
            "completing Phases 1–9, passing ADE CONTINUE (Phases 2–3), and satisfying\nPhase 10 approval gates",
        ),
        (
            "Do not continue to Phase 4 until Status = READY.",
            "Do not continue to Phase 6 until Status = READY.",
        ),
        (
            "Do not proceed to Phase 8 (Implementation)",
            "Do not proceed to Phase 11 (Implementation)",
        ),
        (
            "Only begin coding after Phase 5A CONTINUE and Phase 5",
            "Only begin coding after ADE CONTINUE and Phase 10",
        ),
        (
            "Phase 5\napproval requirements are satisfied and Phase 5A (Think Mode) decision = CONTINUE",
            "Phase 10 approval requirements are satisfied and ADE decision = CONTINUE",
        ),
        ("Phase 12 handoff", "Phase 15 handoff"),
        (
            "all Phase 10 reviews pass and Phase 11 documentation",
            "all Phase 13 reviews pass and Phase 14 documentation",
        ),
        ("### Review verdicts (Phase 10)", "### Review verdicts (Phase 13)"),
        (
            "Do not proceed to Phase 12 with any unmet item.",
            "Do not proceed to Phase 15 with any unmet item.",
        ),
        (
            "| **LOW** | **Auto-continue** — proceed to Phase 2 (ADE Mode A) without pause |",
            "| **LOW** | **Auto-continue** — record risk; Approval (Phase 10) auto-continues after plan |",
        ),
    ]
    for old, new in replacements:
        text = text.replace(old, new)

    # Phase 1 repository note
    text = text.replace(
        "## Phase 1 — Repository Discovery (skill extension)",
        "## Phase 1 — Repository Discovery (skill extension)\n\n> **Note:** Common Phase 0 (prepended) runs first. This phase extends discovery with story-specific targets.\n",
    )

    # Risk assessment merges impact + note about approval timing
    text = text.replace(
        "## Phase 6 — Risk Assessment (NEW)",
        "## Phase 6 — Risk Assessment\n\n**Classify story risk after Story Readiness. Principal Engineer behaviour required.**\n",
    )

    text = text.replace(
        "## Phase 10 — Approval (NEW)\n\n**Gate implementation based on Phase 4 classification. No code until gates pass.**",
        "## Phase 10 — Approval\n\n**Gate implementation based on Phase 6 risk classification. Executes after Phase 9 (Implementation Plan). No code until gates pass.**",
    )

    SKILL.write_text(text, encoding="utf-8")
    print(f"Updated {SKILL}")


if __name__ == "__main__":
    main()
