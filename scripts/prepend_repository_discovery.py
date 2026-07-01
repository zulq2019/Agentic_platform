#!/usr/bin/env python3
"""Prepend Phase 0 — Repository Discovery to all engineering SKILL.md files."""

from __future__ import annotations

from pathlib import Path

PHASE_0 = """
## Phase 0 — Repository Discovery (mandatory)

**Execute before all other steps in this skill.** Repository-agnostic; reusable in any
software repository. Never hardcode repository names or folder structures. Never fail
because a document is missing — record `NOT FOUND` and continue with graceful degradation.

**Authority:** Full discovery procedure, bash patterns, and Discovery Record template:
[`.ai/skills/_shared/REPOSITORY_DISCOVERY.md`](../_shared/REPOSITORY_DISCOVERY.md).
If the relative path does not resolve, discover via glob: `**/skills/_shared/REPOSITORY_DISCOVERY.md`.

**Auto-detect and record:**

| Item | Action |
|------|--------|
| Repository type | Infer from manifests and layout |
| Architecture documents | Glob/search `ARCHITECTURE*.md`, `PLATFORM_*.md`, architecture doc trees |
| Platform constitutions | Discover `CONSTITUTION.md`, platform baseline docs — **load automatically if present** |
| Repository constitution | Discover `CLAUDE.md`, `REPOSITORY_GUIDE.md`, `AGENTS.md`, `CONTRIBUTING.md` |
| Engineering roadmap | Discover `ROADMAP.md`, `TASKS.md`, implementation-roadmap / program trees |
| Current PI | Active program folder (`PI-*` or discovered pattern) |
| Current Sprint | Active section in `SPRINT_PLAN.md` when present |
| Current Story | In Progress / next Planned from `STATUS.md` + story catalogues |
| STATUS.md | Nearest program status file |
| CHANGELOG.md | Root or discovered changelog |
| METRICS.md | Root or discovered metrics doc |
| README hierarchy | Root + nested `README.md` files |
| Skills library | `**/skills/**/SKILL.md` |
| Prompt library | Command libraries (`commands/`, `.ai/commands/`, etc.) |

**Before proceeding:** Emit a **Discovery Record** per the shared template. If Platform
Constitution documents exist, confirm they were loaded. Then continue to this skill's
existing steps unchanged.

---

"""

MARKER = "## Phase 0 — Repository Discovery (mandatory)"
SKILLS_DIR = Path(__file__).resolve().parents[1] / ".ai" / "skills"


def prepend_phase_0(skill_path: Path) -> bool:
    text = skill_path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    if not text.startswith("---"):
        raise ValueError(f"Missing frontmatter: {skill_path}")
    end = text.find("\n---\n", 3)
    if end == -1:
        raise ValueError(f"Could not find frontmatter end: {skill_path}")
    insert_at = end + len("\n---\n")
    updated = text[:insert_at] + PHASE_0 + text[insert_at:]
    skill_path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    updated = []
    skipped = []
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        if skill_md.parent.name.startswith("_"):
            continue
        if prepend_phase_0(skill_md):
            updated.append(skill_md.relative_to(SKILLS_DIR.parent.parent))
        else:
            skipped.append(skill_md.name)
    print(f"Updated {len(updated)} skills:")
    for p in updated:
        print(f"  + {p}")
    if skipped:
        print(f"Skipped (already has Phase 0): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
