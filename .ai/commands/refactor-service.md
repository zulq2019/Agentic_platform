# refactor-service.md

**Command:** `refactor-service`  
**Version:** 1.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs — use when an existing service requires structural improvement without changing behaviour

---

## Purpose

Use this command to safely refactor an existing service to improve code quality, maintainability, or alignment with platform standards, without changing observable behaviour.

A refactor under this command must be provably behaviour-preserving. If existing tests do not exist, they must be written first. If the refactor changes the public API or event contracts, it is not a refactor — use `implement-story.md` with a new User Story.

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture | `ARCHITECTURE.md` | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| Implementation Guide | `docs/engineering/implementation-roadmap/{PI}/IMPLEMENTATION.md` | Mandatory |
| Existing service code | `src/{target_folder}/` | Mandatory |
| Existing test suite | `src/tests/` — all tests for this service | Mandatory |
| ADRs relevant to this service | `DECISIONS.md` | Mandatory |
| Refactor justification | Provided by engineer — what pattern is being fixed | Mandatory |

**Substitutions required:**

```
{PI}              = PI this service belongs to
{service_name}    = e.g. agent-registry-service
{target_folder}   = e.g. src/platform/registry/
{refactor_goal}   = e.g. extract repository pattern, remove N+1 queries, add DI
```

---

## Preconditions

- [ ] All existing tests pass before the refactor begins — baseline is green
- [ ] Coverage report for `{target_folder}` is available — no behaviour without test coverage
- [ ] The refactor goal is clearly stated and does not include new features
- [ ] Any behaviour not covered by tests is covered before refactoring starts
- [ ] No other work in progress in this service

---

## Execution Steps

### Step 1 — Establish the baseline

Before changing anything:

1. Run the full test suite: `pytest src/tests/ -k "{service_name}" -v`
2. Record coverage: `pytest --cov={target_folder} --cov-report=term`
3. Save baseline:
   ```
   Baseline tests:    N passing, 0 failing
   Baseline coverage: N%
   ```
4. If any tests are failing at baseline, STOP. Fix them before proceeding.
5. If coverage is below 80%, write tests to reach 80% before proceeding.

### Step 2 — Map the current structure

Read every file in `{target_folder}`. Produce a dependency map:

```
Module: {module_name}
  Imports: {list of dependencies}
  Exported: {list of public classes/functions}
  Callers: {list of modules that import this}
  Issues: {what specifically needs changing and why}
```

### Step 3 — Identify the refactor scope

From the dependency map, define the exact scope:

```
Files to be changed:    list
Files NOT to be changed: list
Public interfaces unchanged: confirm YES/NO
Event contracts unchanged:  confirm YES/NO
Database schema unchanged:  confirm YES/NO
```

If public interfaces, event contracts, or database schema will change, this is NOT a refactor. Stop and create a new User Story.

### Step 4 — Apply refactoring in atomic steps

Apply one logical change at a time. After each change:
1. Run affected tests: `pytest {affected_test_file} -v`
2. Tests must pass before the next change begins
3. Never accumulate multiple logical changes before testing

Approved refactoring patterns:

| Pattern | When to Apply |
|---------|--------------|
| Extract repository interface | Domain code imports ORM directly |
| Extract service interface | High coupling between layers |
| Replace `any` with typed Union | TypeScript code has untyped regions |
| Replace bare `except:` with typed exceptions | Error handling is too broad |
| Extract configuration to Pydantic Settings | Config values are hardcoded |
| Add structured logging | Raw `print()` or unstructured `logging` calls |
| Add OTEL tracing | Domain methods have no trace spans |
| Replace N+1 with eager load | ORM lazy loading inside loops |
| Extract constants to named enum | Magic strings or numbers in domain logic |
| Add Pydantic validation | Dict-based input not validated at boundaries |

Forbidden refactoring in this command:

- Changing public method signatures
- Changing Kafka topic names
- Changing database column names
- Changing API endpoint paths or response shapes
- Merging two services
- Splitting one service into two

### Step 5 — Verify behaviour preservation

After all changes:

1. Run the full test suite: `pytest src/tests/ -k "{service_name}" -v`
2. Confirm: same number of tests pass as baseline
3. Confirm: coverage is same or higher than baseline
4. Run integration tests: `pytest src/tests/integration/{service_name}/ -v`
5. Diff the public interface: `git diff main -- src/{target_folder}/api/`
   - The diff on `api/` must show ZERO changes to schemas or route signatures

### Step 6 — Update internal documentation

For every file changed, update its module docstring if the internal structure changed:
- Describe the new pattern used
- Reference the `IMPLEMENTATION.md` pattern it follows

Do not update `API_SPEC.md`, `SEQUENCE_DIAGRAMS.md`, or `DATA_MODEL.md` — those describe external behaviour which did not change.

### Step 7 — Produce the refactor report

```
## Refactor Report: {service_name}
Goal: {refactor_goal}

### Behaviour Preservation
Tests before: N passing
Tests after:  N passing
Coverage before: N%
Coverage after:  N%
Public interface diff: ZERO changes

### Changes Made
1. {file}: {what changed and why}
2. ...

### Patterns Applied
1. {pattern_name}: applied in {file} to address {specific issue}

### Patterns NOT Applied (deferred)
1. {pattern_name}: deferred because {reason}

### Summary
{one paragraph}
```

---

## Expected Outputs

| Artifact | Description |
|----------|-------------|
| Refactored service code | `src/{target_folder}/` — improved structure, same behaviour |
| Additional unit tests | Any tests written to reach 80% baseline |
| Refactor report | Evidence of behaviour preservation |
| Updated module docstrings | Internal documentation updated |

---

## Quality Gates

- [ ] All tests that passed before the refactor still pass after
- [ ] Coverage same or higher than baseline
- [ ] Public API schema unchanged — `git diff main -- api/` shows zero changes
- [ ] Event schemas unchanged
- [ ] Database queries produce same results
- [ ] Lint passes: `ruff check` and `black --check` exit 0
- [ ] Type check passes: `mypy --strict` exits 0

---

## Completion Checklist

```
[ ] Baseline established — all tests pass, coverage documented
[ ] Dependency map produced — structure understood
[ ] Refactor scope defined — public interface confirmed unchanged
[ ] Refactoring applied in atomic steps — test after each change
[ ] Behaviour preservation verified — same tests, same coverage
[ ] Internal documentation updated
[ ] Refactor report produced with evidence
[ ] No new features introduced
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Begin refactoring without a passing baseline
- Apply multiple logical changes without running tests between them
- Change a public method signature and call it a "refactor"
- Change a Kafka topic name or event type
- Change a database column name or index
- Change an API endpoint path or response schema
- Add new business features during a refactor
- Reduce test coverage during a refactor
- Merge two services or extract a new service without a User Story
- Modify `CONSTITUTION.md`, `ARCHITECTURE.md`, or PI documentation
- Accept a test failure as "expected during refactoring"
