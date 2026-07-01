# Repository Discovery — Common Phase 0

**Used by:** Every engineering skill under `.ai/skills/`  
**Mode:** Read-only discovery unless the invoking skill explicitly permits writes  
**Rules:** Never hardcode repository names. Never hardcode folder structures. Graceful degradation when any item is absent.

---

## Purpose

Establish a consistent **Discovery Record** before skill-specific work begins. Skills remain reusable across any software repository while automatically loading richer context when platform or program documents exist.

---

## Step 0.1 — Repository identity

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
git branch --show-current 2>/dev/null
git log -1 --format='%H %s %ci' 2>/dev/null
git remote -v 2>/dev/null | head -3
```

Record: root path, current branch, latest commit, default remote (if any).

---

## Step 0.2 — Repository type

Infer from discovered manifests and layout (do not assume a single stack):

```bash
# Discover manifests — any match informs repo type
find . -maxdepth 4 \( -name 'package.json' -o -name 'pyproject.toml' -o -name 'go.mod' \
  -o -name 'Cargo.toml' -o -name 'pom.xml' -o -name 'build.gradle*' \) \
  ! -path '*/node_modules/*' ! -path '*/.git/*' 2>/dev/null | head -20

find . -maxdepth 3 \( -name 'Dockerfile' -o -name 'docker-compose*.yml' -o -name 'docker-compose*.yaml' \) \
  ! -path '*/.git/*' 2>/dev/null | head -15

find . -maxdepth 2 -path '*/.github/workflows/*' \( -name '*.yml' -o -name '*.yaml' \) 2>/dev/null | head -10
```

Classify as one or more of: monorepo, polyglot, library, service, platform, docs-only, unknown — based on evidence only.

---

## Step 0.3 — Architecture documents

```bash
find . \( -iname 'ARCHITECTURE*.md' -o -iname 'PLATFORM_*.md' -o -iname '*ARCHITECTURE_BASELINE*' \) \
  ! -path '*/.git/*' ! -path '*/node_modules/*' 2>/dev/null | head -40

find . -path '*/docs/*' \( -iname '*architecture*' -o -iname 'ADR' -o -iname 'adr' \) \
  -name '*.md' ! -path '*/.git/*' 2>/dev/null | head -40
```

Record each path found. Read top-level architecture index files when present.

---

## Step 0.4 — Platform constitutions (load if present)

Discover — do not assume paths:

```bash
find . -maxdepth 5 \( -iname 'CONSTITUTION.md' -o -iname 'PLATFORM_META_MODEL.md' \
  -o -iname 'PLATFORM_CONTRACTS.md' -o -iname 'PLATFORM_PRIMITIVES.md' \
  -o -iname 'PLATFORM_UX_MODEL.md' -o -iname 'ARCHITECTURE_BASELINE*.md' \) \
  ! -path '*/.git/*' 2>/dev/null | head -30
```

**If any Platform Constitution documents exist:** read them (or their executive summaries) and list loaded files in the Discovery Record.

**If none exist:** set `Platform constitutions: NOT FOUND` and continue — do not fail.

---

## Step 0.5 — Repository constitution

```bash
find . -maxdepth 4 \( -iname 'CLAUDE.md' -o -iname 'REPOSITORY_GUIDE.md' -o -iname 'AGENTS.md' \
  -o -iname 'CONTRIBUTING.md' -o -iname 'DECISIONS.md' \) ! -path '*/.git/*' 2>/dev/null | head -20
```

Load the primary repository engineering guide when found (prefer `REPOSITORY_GUIDE.md` or `CLAUDE.md` if multiple exist — note precedence in Discovery Record).

---

## Step 0.6 — Engineering roadmap

```bash
find . \( -iname 'ROADMAP.md' -o -iname 'TASKS.md' -o -iname 'IMPLEMENTATION_ROADMAP.md' \) \
  ! -path '*/.git/*' 2>/dev/null | head -15

find . -path '*/implementation-roadmap/*' -name '*.md' ! -path '*/.git/*' 2>/dev/null | head -30
find . -path '*/04-program/*' -name '*.md' ! -path '*/.git/*' 2>/dev/null | head -20
```

Record roadmap roots and PI/program folder patterns discovered.

---

## Step 0.7 — Current PI, Sprint, Story

Discover program folders dynamically (examples of patterns — search, do not assume):

```bash
find . -type d \( -iname 'PI-*' -o -iname '*program*' -o -path '*/implementation-roadmap/*' \) \
  ! -path '*/.git/*' 2>/dev/null | head -30

find . \( -iname 'STATUS.md' -o -iname 'SPRINT_PLAN.md' -o -iname 'USER_STORIES.md' \
  -o -iname 'ACCEPTANCE_CRITERIA.md' \) ! -path '*/.git/*' 2>/dev/null | head -40
```

**Current PI:** folder with active `STATUS.md` (In Progress stories) or most recently modified program docs.

**Current Sprint:** section marked active in `SPRINT_PLAN.md` when present.

**Current Story:** first **In Progress** in `STATUS.md` / `USER_STORIES.md`; else first **Planned** after last **Complete**.

If undetermined: `NOT FOUND` — do not guess IDs.

---

## Step 0.8 — STATUS, CHANGELOG, METRICS

```bash
find . -iname 'STATUS.md' ! -path '*/.git/*' 2>/dev/null | head -20
find . -iname 'CHANGELOG.md' ! -path '*/.git/*' 2>/dev/null | head -10
find . -iname 'METRICS.md' ! -path '*/.git/*' 2>/dev/null | head -10
```

Prefer root `CHANGELOG.md` / `METRICS.md` when multiple exist; note all paths.

---

## Step 0.9 — README hierarchy

```bash
find . -iname 'README.md' ! -path '*/.git/*' ! -path '*/node_modules/*' 2>/dev/null | head -40
```

Record root README and significant nested READMEs (depth ≤ 4). Note inconsistencies if root README contradicts a repository guide.

---

## Step 0.10 — Skills library

```bash
find . -path '*/skills/*' -name 'SKILL.md' ! -path '*/.git/*' 2>/dev/null | head -40
find . -path '*/.ai/skills/*' -name 'SKILL.md' 2>/dev/null | head -20
find . -path '*/.cursor/skills/*' -name 'SKILL.md' 2>/dev/null | head -20
```

Record skill roots and count.

---

## Step 0.11 — Prompt library

```bash
find . -path '*/commands/*' -name '*.md' ! -path '*/.git/*' 2>/dev/null | head -40
find . -path '*/.ai/commands/*' -name '*.md' 2>/dev/null | head -20
find . -path '*/.cursor/commands/*' -name '*.md' 2>/dev/null | head -20
```

Record command/prompt roots and count.

---

## Discovery Record template

Emit this (filled) before leaving Phase 0:

```markdown
### Discovery Record

| Item | Status | Location / notes |
|------|--------|------------------|
| Repository type | {inferred} | {evidence} |
| Architecture documents | FOUND / NOT FOUND | {paths} |
| Platform constitutions | LOADED / NOT FOUND | {paths read} |
| Repository constitution | FOUND / NOT FOUND | {path} |
| Engineering roadmap | FOUND / NOT FOUND | {paths} |
| Current PI | {id or NOT FOUND} | {folder} |
| Current Sprint | {name or NOT FOUND} | {source file} |
| Current Story | {id or NOT FOUND} | {source file} |
| STATUS.md | FOUND / NOT FOUND | {path} |
| CHANGELOG.md | FOUND / NOT FOUND | {path} |
| METRICS.md | FOUND / NOT FOUND | {path} |
| README hierarchy | {count} files | {root + notables} |
| Skills library | {count} skills | {root path} |
| Prompt library | {count} commands | {root path} |
| Discovery confidence | HIGH / MEDIUM / LOW | {one line} |
```

---

## Forbidden in Phase 0

- Hardcoding organisation, product, or repository names
- Assuming `docs/04-program/{PI}/` or any fixed tree exists
- Stopping the parent skill when documents are missing
- Modifying files (unless the parent skill explicitly allows writes after discovery)
