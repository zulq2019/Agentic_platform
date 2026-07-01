---
name: regression-review
description: |
  When the engineer types /regression-review <PR_NUMBER> or /regression-review <GitHub PR URL>,
  fetch the PR diff and perform a Principal Engineer level regression assessment across 11
  compatibility dimensions. This skill asks "did this break anything that was already working?"
  — a dedicated backward-compatibility audit separate from aep-review (which asks "is this
  correct?"). Classifies every changed file into a compatibility zone, then executes 11 lenses
  in order: Blast Radius → Contract Compatibility → API Compatibility → Event/Kafka Compatibility →
  Database Schema Compatibility → Infrastructure Compatibility → Workflow Compatibility →
  Agent Compatibility → Tool Compatibility → SDK Compatibility → Backward Compatibility Summary.
  Produces a Blast Radius Map, per-lens findings with file:line citations and concrete fixes,
  a Regression Risk table, and a merge verdict. A single Critical finding in any lens forces
  REQUEST CHANGES regardless of all other results. Never approve a PR with an unresolved
  regression.
allowed-tools: |
  bash: gh, git, grep, rg, python, jq
  file: read
---

# AEP Regression Review

<purpose>
Detect regressions introduced by a Pull Request across 11 compatibility dimensions. This skill
is dedicated to backward compatibility and blast radius analysis. Where aep-review asks
"is this new code correct?", regression-review asks "did this break anything that was already
working?". Both skills must pass independently before a PR may merge. A PR can be architecturally
correct per aep-review and still introduce regressions in shared interfaces, event schemas,
database migrations, or workflow state machines. Only this skill catches those.

Review only the diff — never invent regressions not traceable to changed code. Every finding
must cite an exact file:line from the diff and explain the concrete runtime failure that would
result.
</purpose>

---

## When To Activate

Trigger when the engineer types `/regression-review` followed by a PR number or GitHub PR URL.

```
/regression-review 42
/regression-review https://github.com/org/Agentic_platform/pull/42
```

**Run after aep-review PASSES or in parallel with it.** Both must pass before merge.

**Mandatory for any PR that touches:**
- `src/shared/` or `aep-common/` — shared libraries with platform-wide blast radius
- `contracts/` — agent, tool, task, memory, or event envelope schemas
- `workflows/` — workflow state machine templates
- API endpoints (path, method, request/response schema)
- Kafka topic or schema definitions
- Database migrations (Alembic versions)
- Agent registrations or the Agent Registry
- Tool registrations or the Tool Registry
- `sdks/` — public SDK interfaces

---

## Step 1 — Fetch PR Metadata and Diff

```bash
# Fetch PR metadata
gh pr view <NUMBER> --json \
  title,body,author,baseRefName,headRefName,additions,deletions,changedFiles,labels,milestone

# Fetch the full diff
gh pr diff <NUMBER>

# Fetch file-level change summary
gh pr diff <NUMBER> --name-status

# Fetch line-level statistics per file
gh pr diff <NUMBER> --numstat
```

Extract and record before proceeding:

```
PR #:           {number}
Title:          {title}
Author:         {author}
Base branch:    {base}
Head branch:    {head}
Files changed:  {N}
Additions:      +{N}
Deletions:      -{N}
```

**Classify every changed file into a compatibility zone:**

| Zone | Path Pattern | Blast Radius |
|------|-------------|--------------|
| Zone S | `src/shared/`, `aep-common/` | HIGHEST — every service imports this |
| Zone C | `contracts/` | HIGH — all producers and consumers |
| Zone W | `workflows/` | HIGH — all in-flight workflow runs |
| Zone A | `src/platform/agent-runtime/`, agent registrations | HIGH — all orchestrated tasks |
| Zone T | `src/platform/tool-registry/`, tool registrations | HIGH — all tool-dependent agents |
| Zone K | Kafka topic/schema definitions, producers, consumers | CRITICAL — sole IPC path |
| Zone D | Database migrations (`alembic/versions/`) | CRITICAL — applied before code |
| Zone I | Docker Compose, K8s manifests, GitHub Actions, `.env` | HIGH — all environments |
| Zone SDK | `sdks/` | HIGH — external consumers |
| Zone API | API route files, request/response schemas | HIGH — UI, SDK, external callers |

Record the zone classification for every file. This drives which lenses are mandatory.

**Stop condition:** If `gh` cannot fetch the diff, stop and report. Review cannot proceed
without the full diff.

---

## Step 2 — Load Reference Documents

Read these documents as regression context. Do not re-output their contents. They are the
authoritative baselines this PR is measured against.

```bash
# Platform authorities — the baseline to regress against
cat CONSTITUTION.md
cat ARCHITECTURE.md
cat DECISIONS.md

# All contract schemas — current baselines
ls contracts/
cat contracts/event-envelope.schema.json
cat contracts/agent-contract.schema.json
cat contracts/tool-contract.schema.json
cat contracts/task-schema.schema.json
cat contracts/memory-schema.schema.json

# Contract examples — must remain valid after the change
ls contracts/examples/ 2>/dev/null && cat contracts/examples/*.json

# All workflow templates — current state machines
ls workflows/
cat workflows/*.json

# PI capability map — agent/tool registry context
cat docs/engineering/implementation-roadmap/{PI}/CAPABILITIES.md
```

**Stop condition:** If `CONSTITUTION.md` or `ARCHITECTURE.md` or the `contracts/` directory
cannot be read, stop and report. Regression review cannot proceed without these baselines.

---

## Step 3 — Execute Regression Lenses

Execute every applicable lens in this exact order. "Applicable" means: the PR contains at
least one file in the corresponding zone. A lens with no applicable files produces an automatic
PASS — record it as N/A in the results table. Do not skip lenses for Zone S, Zone K, or
Zone D changes — these are always mandatory when files are present.

Priority is top-down: a Critical in Lens 1 is not superseded by a clean result in Lens 11.

---

### Lens 1 — Blast Radius Assessment

**Applies to: Zone S (src/shared/, aep-common/). Highest priority — execute first.**

**Why it matters:** A single change to `aep-common` breaks every service simultaneously in
production. There is no partial rollout. A renamed function, removed export, or changed return
type silently fails in every importer at the moment the deployment lands.

For every file changed in Zone S:

**Step 1.1 — Map all downstream importers:**

```bash
# Find every Python file that imports the changed module
rg "from aep_common\.|import aep_common" src/ --include="*.py" -l

# Find every TypeScript file that imports the changed module
rg "from.*aep-common|require.*aep-common" src/ --include="*.ts" -l

# Find every service that depends on the shared package
rg "aep-common" requirements*.txt pyproject.toml package.json -l
```

Record: `{changed_module} → {N} downstream importers across {M} services`

**Step 1.2 — Interface diff analysis:** For each changed function, class, or exported symbol:

```bash
# Show exactly what changed at the interface level
git diff HEAD~1 <changed_file> | grep "^[+-]" | grep -E "^[+-](def |class |async def |export )"
```

Flag any of the following as **Critical**:
- Renamed function, method, or class used by downstream importers
- Removed exported symbol
- Changed function signature (new required parameter, removed parameter, reordered parameters)
- Changed return type
- Changed exception type raised (callers catching the old exception will miss the new one)
- Changed default value in shared configuration that alters runtime behaviour

Flag as **Major**:
- New optional parameter that changes behaviour when absent vs present
- Changed logging format in shared logger (breaks log-parsing pipelines)
- Changed metric name in shared instrumentation (breaks Grafana dashboards)

**Step 1.3 — Verify each importer still compiles against the new interface:**

```bash
# For each importer file identified in Step 1.1, grep for usages of the changed symbol
rg "{changed_symbol}" {importer_file} --context 3
```

Confirm: the importer's call site is still compatible with the new signature.

**Flag as Critical when:**
- Any downstream importer calls a symbol that has been renamed or removed
- Any downstream importer passes arguments in an order that no longer matches the new signature
- A shared config default is changed in a way that silently alters every service's behaviour

---

### Lens 2 — Contract Compatibility

**Applies to: Zone C (contracts/). Always mandatory for contract directory changes.**

**Why it matters:** The event envelope, agent contract, tool contract, task schema, and memory
schema are the platform's only stable interfaces between services. A breaking contract change
causes all producers, consumers, and validators to fail at runtime with opaque deserialization
errors — not at deployment, but when the first message flows through the system.

**Step 2.1 — Classify each contract change:**

For every changed file in `contracts/`:

| Change type | Classification |
|------------|---------------|
| Adding optional field with a JSON Schema default | Non-breaking ✅ |
| Adding required field (no default) | Breaking 🔴 |
| Removing any field | Breaking 🔴 |
| Renaming a field | Breaking 🔴 |
| Changing a field's type | Breaking 🔴 |
| Making an optional field required | Breaking 🔴 |
| Tightening a validation constraint (shorter maxLength, narrower enum) | Breaking 🔴 |
| Loosening a validation constraint | Non-breaking ✅ |
| Changing `schema_version` value | Required on any breaking change ✅ |

**Step 2.2 — Run contract validation script:**

```bash
python scripts/validate_contract.py contracts/
# Expected: exit 0. Any non-zero exit is Critical.
```

**Step 2.3 — Validate existing examples against the updated schema:**

```bash
# Every example in contracts/examples/ must still validate after the change
for f in contracts/examples/*.json; do
  python -c "
import json, jsonschema
schema = json.load(open('contracts/event-envelope.schema.json'))
instance = json.load(open('$f'))
jsonschema.validate(instance, schema)
print('PASS:', '$f')
"
done
```

Any example that fails validation after the change is a Critical finding.

**Step 2.4 — Schema version check:**

```bash
git diff HEAD~1 contracts/ | grep "schema_version"
```

If the diff makes any breaking contract change (Step 2.1 classification = Breaking) but does
NOT increment `schema_version`, flag Critical.

**Step 2.5 — ADR check for breaking changes:**

```bash
rg "ADR-" DECISIONS.md | tail -5
```

Every breaking contract change must be accompanied by a Decision Record. If no new ADR is
referenced in the PR body or `DECISIONS.md` was not updated, flag Major.

**Flag as Critical when:**
- Any breaking contract change present in the diff (see table above)
- `validate_contract.py` exits non-zero
- Any existing example in `contracts/examples/` fails validation against the new schema
- Breaking change with no `schema_version` increment

**Flag as Major when:**
- Breaking change with no ADR
- New required field has no corresponding documentation update

---

### Lens 3 — API Compatibility

**Applies to: Zone API (API route files, request/response Pydantic schemas).**

**Why it matters:** API consumers — the UI, the SDK, and any external caller — are not deployed
atomically with the backend service. A breaking API change causes live callers to fail with
404s, 422s, or silent data loss immediately upon backend deployment.

**Step 3.1 — Detect changed endpoints:**

```bash
# Find all changed route definitions
git diff HEAD~1 <changed_api_files> | grep -E "^[+-].*(@app\.|@router\.|path=|route=)"

# Detect path changes
git diff HEAD~1 <changed_api_files> | grep "^[+-].*\"/api/"
```

For each changed endpoint, record: HTTP method, path, before, after.

**Step 3.2 — Breaking change matrix:**

| Change | Breaking? | Failure scenario |
|--------|-----------|-----------------|
| Path renamed or removed | Breaking 🔴 | Existing callers get 404 |
| New required request field | Breaking 🔴 | Existing callers get 422 |
| Request field type narrowed | Breaking 🔴 | Existing valid payloads rejected |
| Response field removed | Breaking 🔴 | Callers depending on that field crash |
| Response field type changed | Breaking 🔴 | Callers deserialise into wrong type |
| HTTP method changed | Breaking 🔴 | Existing callers get 405 |
| Success status code changed (200→201) | Breaking 🟠 | Callers checking exact code fail |
| Error code changed (409→422) | Breaking 🟠 | Callers handling old code miss it |
| Pagination strategy changed | Breaking 🔴 | Cursor pagination callers break |
| New optional request field | Non-breaking ✅ | |
| New optional response field | Non-breaking ✅ | |

**Step 3.3 — API versioning check:**

```bash
git diff HEAD~1 <changed_api_files> | grep "api/v"
```

If any Breaking change (Step 3.2 matrix) is present: does the endpoint path increment from
`/api/v1/` to `/api/v2/`? If not, flag Critical — breaking API change without version increment.

**Step 3.4 — Deprecation check:**

```bash
rg "deprecated|x-deprecated|DeprecationWarning" -- <changed_files>
```

If an endpoint is being removed rather than versioned: is a deprecation notice present in the
prior version's response headers and documented in the PR? If not, flag Major.

**Flag as Critical when:**
- Breaking API change with no API version increment
- Endpoint path changed or removed with no redirect or version path

**Flag as Major when:**
- Response field removed without deprecation notice
- Error code changed without updating caller error-handling documentation
- Pagination strategy changed (cursor → offset or vice versa) without migration guide

---

### Lens 4 — Event/Kafka Compatibility

**Applies to: Zone K (Kafka producers, consumers, topic definitions, event schema files).**

**Why it matters:** Kafka is the sole inter-service communication path on this platform
(Constitution A4). A broken event format does not fail at deployment — it fails when the first
message is produced or consumed after deployment. At that point, every downstream consumer
stops processing, in-flight messages accumulate in the topic, and the platform stalls silently.
Kafka offset and partition key changes additionally cause message loss or incorrect ordering
for all in-flight messages at the time of deployment.

**Step 4.1 — Detect all Kafka changes in the diff:**

```bash
# Topic name changes
git diff HEAD~1 <changed_files> | grep -E "^[+-].*topic.*=" 

# Event type string changes
git diff HEAD~1 <changed_files> | grep -E "^[+-].*event_type.*="

# Consumer group ID changes
git diff HEAD~1 <changed_files> | grep -E "^[+-].*group_id.*="

# Partition key changes
git diff HEAD~1 <changed_files> | grep -E "^[+-].*partition_key|key=.*tenant"

# Producer acks setting
git diff HEAD~1 <changed_files> | grep -E "^[+-].*acks="

# Schema changes in event payload
git diff HEAD~1 <changed_files> | grep -E "^[+-].*(class.*Event|@dataclass|BaseModel)"
```

**Step 4.2 — Breaking change assessment per category:**

**Topic name:**
```bash
git diff HEAD~1 -- <topic_definition_files> | grep "^[+-].*topic_name\|TOPIC_NAME\|TOPIC ="
```
Any topic name change is Breaking: all consumers subscribed to the old name stop receiving
messages. Producers publishing to the old name have no consumers.

**Event type string:**
```bash
git diff HEAD~1 -- <changed_files> | grep "^[+-].*\"event_type\"\|event_type ="
```
Any `event_type` string change is Breaking: consumers filtering on event type stop matching.
In-flight messages with the old event type are ignored.

**Envelope required fields:**
```bash
rg "event_id|event_type|schema_version|emitted_by|tenant_id|task_id|workflow_run_id|timestamp|payload" \
  -- <changed_producer_files>
```
Any removal of a required envelope field is Critical: all consumers will fail deserialization
or schema validation on every message.

**Payload schema (breaking changes only):**

| Payload change | Breaking? |
|---------------|-----------|
| Required field removed | Breaking 🔴 |
| Field type changed | Breaking 🔴 |
| Field renamed | Breaking 🔴 |
| New required field (no default) | Breaking 🔴 |
| New optional field with default | Non-breaking ✅ |

**Partition key:**
```bash
git diff HEAD~1 -- <changed_files> | grep "partition_key\|key=tenant"
```
Any partition key change causes ordering violations for in-flight messages: messages published
before the change land on different partitions than messages published after. Consumers relying
on ordering guarantees will process events out of order.

**Consumer group ID:**
```bash
git diff HEAD~1 -- <changed_files> | grep "group_id"
```
A consumer group ID change causes the consumer to reset to the earliest or latest offset —
either reprocessing all historical messages (duplicate side effects) or skipping all messages
produced since the change (message loss).

**Flag as Critical when:**
- Topic name changed
- Event type string changed
- Any required envelope field removed from a producer
- Payload field removed or type changed
- Consumer group ID changed

**Flag as Major when:**
- Partition key changed (ordering regression)
- `acks` setting reduced from `all` to `1` or `0` (durability regression)
- New required payload field added without a migration plan for existing consumers

---

### Lens 5 — Database Schema Compatibility

**Applies to: Zone D (Alembic migration files in `alembic/versions/`).**

**Why it matters:** Database migrations are applied to the production database before the
new application code is deployed. This means the migration runs against live data and the
live application simultaneously. A migration that adds a NOT NULL column with no default
immediately breaks every existing row and crashes all running application instances. A
migration that removes a column breaks all application code still reading that column before
the new code is deployed. There is no fast rollback — you must write and run a second migration.

**Step 5.1 — Parse every new migration file in the diff:**

```bash
# Find new migration files
gh pr diff <NUMBER> --name-status | grep "^A.*alembic/versions/"

# Read each migration
cat <migration_file>
```

**Step 5.2 — NOT NULL without default check:**

```bash
rg "nullable=False|NOT NULL" -- <migration_files>
rg "server_default\|default=" -- <migration_files>
```

For every `NOT NULL` column addition: is there a `server_default` or `default` value? If not,
the migration will fail on any existing row and any running application instance will crash the
moment it tries to INSERT without the new column.

**Step 5.3 — Removed column live reference check:**

```bash
# Extract removed column names from the migration
git diff HEAD~1 <migration_file> | grep "^+.*op\.drop_column" | grep -oP "\"[^\"]+\"" | tail -1

# Check if the application still references the removed column
rg "{removed_column_name}" src/ --include="*.py" -l
```

If any application file still references a column being dropped by this migration, flag Critical.
The migration will succeed but the application will crash on first use of that column.

**Step 5.4 — Column rename check:**

```bash
rg "op\.alter_column\|op\.drop_column.*op\.add_column" -- <migration_files>
```

Any column rename (drop + add, or `alter_column` with new_column_name) breaks all queries
using the old name. Check every ORM model and raw SQL query referencing the old name.

**Step 5.5 — Type change safety:**

```bash
rg "op\.alter_column" -- <migration_files>
```

For each `alter_column`: does the new type accept all values that exist in the column? A type
narrowing (e.g. `TEXT → VARCHAR(50)`) silently truncates values longer than 50 characters.
A type change that is not natively castable (e.g. `TEXT → INTEGER`) will fail for any
non-numeric row.

**Step 5.6 — Index removal check:**

```bash
rg "op\.drop_index" -- <migration_files>
```

For each removed index: run this check:
```bash
# Is the index used in a hot-path query?
rg "{index_name}\|{indexed_column}" src/ --include="*.py" -l
```

Removing an index used by a hot-path query degrades to a full table scan — no immediate crash,
but a production performance regression that may cause timeouts under load.

**Step 5.7 — RLS policy check:**

```bash
rg "op\.execute.*POLICY\|DROP POLICY\|ALTER POLICY" -- <migration_files>
```

Any migration that alters or removes an RLS policy is a tenant isolation regression.
Cross-reference `CONSTITUTION.md` principle MT1. Flag Critical.

**Step 5.8 — Reversibility check:**

```bash
rg "def downgrade" -- <migration_files>
```

Every migration must have a `downgrade()` function with a correct reversal. An empty
`pass` body is not acceptable — it is equivalent to having no rollback path.

```bash
# Verify downgrade is not empty
python -c "
import ast, sys
with open('$migration_file') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'downgrade':
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            print('FAIL: downgrade() is empty — no rollback path')
            sys.exit(1)
        else:
            print('PASS: downgrade() has content')
"
```

**Flag as Critical when:**
- NOT NULL column added with no `server_default` or `default`
- Application code still references a column being dropped by this migration
- Column renamed and application code still uses the old name
- RLS policy removed or weakened
- `downgrade()` function absent or empty

**Flag as Major when:**
- Type change that may truncate or fail for existing data
- Index removed that is used by a hot-path query
- Migration is not idempotent (unsafe to run twice)

**Flag as Minor when:**
- Missing index on a column that will be queried frequently at scale (not yet a hot path)
- `downgrade()` exists but does not reverse the `upgrade()` completely

---

### Lens 6 — Infrastructure Compatibility

**Applies to: Zone I (Docker Compose, Kubernetes manifests, GitHub Actions workflows, environment variable files).**

**Why it matters:** Infrastructure changes are applied across all environments simultaneously
and cannot be feature-flagged. A renamed environment variable breaks every deployment that
has not yet been updated with the new name. A changed service port breaks every caller using
the hardcoded old port. A removed CI step removes a quality gate that was previously protecting
the main branch.

**Step 6.1 — Environment variable changes:**

```bash
# Find renamed or removed environment variables
git diff HEAD~1 -- <env_files> .env.example docker-compose*.yml \
  .github/workflows/*.yml | grep "^[+-].*[A-Z_]\{4,\}="
```

For each renamed or removed environment variable:
```bash
# Check if the old name is still referenced anywhere in the codebase
rg "{OLD_VAR_NAME}" src/ infra/ --include="*.py" --include="*.yml" --include="*.yaml" -l
```

Any live reference to an env var being renamed or removed is Breaking: the service will start
but fail at the first code path that reads the variable.

**Step 6.2 — Service port changes:**

```bash
git diff HEAD~1 -- docker-compose*.yml infra/k8s/ | grep "^[+-].*port"
```

For each changed port:
```bash
# Check all callers using the old port
rg "{old_port}" src/ infra/ --include="*.py" --include="*.yml" -l
```

**Step 6.3 — Container image changes:**

```bash
git diff HEAD~1 -- docker-compose*.yml infra/k8s/ | grep "^[+-].*image:"
```

For each changed image tag: is the new tag confirmed to not introduce breaking changes in its
own changelog? At minimum, flag for manual verification if the tag is `latest` or unpinned.

**Step 6.4 — Resource limit reductions:**

```bash
git diff HEAD~1 -- infra/k8s/ | grep "^[+-].*\(cpu\|memory\):"
```

Any resource limit reduction below the service's observed P99 usage is a latency regression.
Flag for verification against observed metrics.

**Step 6.5 — Health check path changes:**

```bash
git diff HEAD~1 -- infra/k8s/ | grep "^[+-].*\(livenessProbe\|readinessProbe\|path:\)"
```

Any changed health check path that does not exist in the new code version causes the pod to
fail readiness checks and never receive traffic — equivalent to a deployment failure.

**Step 6.6 — CI quality gate removal:**

```bash
git diff HEAD~1 -- .github/workflows/ | grep "^-.*\(step\|run\|uses\):"
```

For each removed CI step: was it providing a quality gate (lint, test, security scan, contract
validation)? A removed quality gate is a regression in the platform's safety net.

**Flag as Critical when:**
- Required environment variable renamed with live references to the old name
- Service port changed with live references to the old port
- Health check path changed to a path that does not exist in the new code

**Flag as Major when:**
- CI quality gate (lint, test, security scan) removed
- Resource limit reduced without evidence it is safe at observed load
- Unpinned (`latest`) container image tag introduced

**Flag as Minor when:**
- Environment variable renamed but no live references found (future-safe to document)
- Resource request (not limit) reduced

---

### Lens 7 — Workflow Compatibility

**Applies to: Zone W (files in `workflows/`).**

**Why it matters:** Workflow runs are long-lived. A single workflow run may span hours or days.
When a workflow template is updated, in-flight runs do not automatically migrate to the new
template — they continue executing on the state machine definition that was active when they
started. Removing a state or transition from the template does not affect those in-flight runs
immediately. However, if the platform reloads workflow templates on restart or state transition,
in-flight runs may suddenly find their current state or next transition missing from the new
template, causing them to stall or crash.

**Step 7.1 — State machine diff:**

```bash
git diff HEAD~1 -- workflows/*.json | jq 'keys'
```

For each changed workflow template:

```bash
# Extract state names before and after
git show HEAD~1:workflows/{template}.json | jq '[.states[].name]'
git show HEAD:workflows/{template}.json | jq '[.states[].name]'
```

Find: states present in the old template but absent in the new template. These are removed
states. Any workflow run currently in a removed state will be unable to proceed.

**Step 7.2 — Transition diff:**

```bash
# Extract transitions before and after
git show HEAD~1:workflows/{template}.json | jq '[.states[].transitions[].event]'
git show HEAD:workflows/{template}.json | jq '[.states[].transitions[].event]'
```

Find: transitions present in the old template but absent in the new template. Any workflow
run that was about to take a removed transition will stall indefinitely.

**Step 7.3 — Agent capability tag changes in workflow:**

```bash
git diff HEAD~1 -- workflows/*.json | grep "capability_tag\|agent_capability"
```

If a task step's required capability tag is changed: are there agents registered with the
new tag? If not, in-flight tasks dispatched after the template change will be orphaned.

```bash
# Verify new capability tag has at least one registered agent
rg "{new_capability_tag}" src/ --include="*.py" --include="*.json" -l
```

**Step 7.4 — Gate condition changes:**

```bash
git diff HEAD~1 -- workflows/*.json | grep "gate\|approval\|condition"
```

Any gate condition change affects in-flight runs currently waiting at that gate. A gate that
previously required one approver now requiring two will re-block runs that already received
one approval.

**Step 7.5 — Template version check:**

```bash
git diff HEAD~1 -- workflows/*.json | grep "version\|template_version"
```

Any change to a workflow template **must** increment the template version. New workflow runs
pick up the new version. In-flight runs continue on the version they started with. If the
template version is not incremented, there is no way to distinguish old-version from new-version
runs in the audit log.

**Flag as Critical when:**
- State removed or renamed in the template
- Transition removed in the template

**Flag as Major when:**
- Agent capability tag changed with no registered agent for the new tag
- Template version not incremented on any structural change
- Gate condition changed affecting in-flight runs

**Flag as Minor when:**
- Non-structural metadata change (description, label) without version bump
- Agent capability tag changed and new tag is registered

---

### Lens 8 — Agent Compatibility

**Applies to: Zone A (agent registration files, `agent-runtime`, agent contract changes).**

**Why it matters:** Agents are discovered by the orchestrator via capability tags in the
Agent Registry. The orchestrator does not know about specific agents — it knows only
about capabilities. A changed `agent_id` breaks any orchestrator reference that uses
the ID directly. A removed capability tag means no tasks with that required capability
will ever be routed. A changed input schema means the orchestrator passes task context
that the agent can no longer parse.

**Step 8.1 — Agent registration diff:**

```bash
git diff HEAD~1 -- <agent_registration_files> | grep "^[+-].*\(agent_id\|capabilities\|input_schema\|output_schema\|cost_class\|idempotency_key_strategy\)"
```

**Step 8.2 — Per-field breaking change assessment:**

**`agent_id` change:**
```bash
git diff HEAD~1 -- <files> | grep "^[+-].*agent_id"
```
If `agent_id` is changed: search for all references to the old ID.
```bash
rg "{old_agent_id}" src/ workflows/ --include="*.py" --include="*.json" -l
```
Any reference to the old ID will produce agent-not-found errors at dispatch time.

**Capability tag removal:**
```bash
# Tags present before but absent after
# Extract before set and after set and diff
```
A removed capability tag orphans any task that requires it. Check workflows and orchestrator
dispatch logic for references to the removed tag.

**`input_schema` change (new required field):**
```bash
git diff HEAD~1 -- <agent_registration_files> | grep -A 20 "input_schema"
```
If a new required field is added to `input_schema`: all callers passing the old input shape
will receive schema validation errors at agent runtime entry.

**`output_schema` change (field removal):**
```bash
git diff HEAD~1 -- <agent_registration_files> | grep -A 20 "output_schema"
```
If a field is removed from `output_schema`: any downstream consumer parsing the agent's output
(orchestrator, next agent in workflow, event subscriber) will fail to find the field.

**`cost_class` change:**
```bash
git diff HEAD~1 -- <files> | grep "^[+-].*cost_class"
```
A cost_class change alters model tier routing. An increase may cause budget overruns. A
decrease may route tasks to a model tier that cannot handle the task complexity.

**`idempotency_key_strategy` change:**
```bash
git diff HEAD~1 -- <files> | grep "^[+-].*idempotency_key_strategy"
```
A changed idempotency key strategy means in-flight retries compute a different key. The agent
may execute a side effect twice: once for the original request (with the old key) and once for
the retry (with the new key). This can create duplicate pull requests, duplicate commits, or
duplicate database records.

**Flag as Critical when:**
- `agent_id` changed with live references to the old ID
- Capability tag removed with tasks in workflows requiring it
- `idempotency_key_strategy` changed (duplicate side-effect risk for in-flight retries)

**Flag as Major when:**
- New required field in `input_schema` without updating all callers
- Field removed from `output_schema` with downstream consumers depending on it
- `cost_class` increased without documented justification

---

### Lens 9 — Tool Compatibility

**Applies to: Zone T (tool registration files, Tool Registry changes).**

**Why it matters:** Tools are discovered by agents via capability tags. An agent never references
a specific tool by ID — it requests a capability and the Tool Registry resolves the tool.
A changed `tool_id`, removed capability tag, or changed response schema breaks the agent's
ability to invoke the tool or parse its response — silently, because the agent calls the tool
at task execution time, not at registration time.

**Step 9.1 — Tool registration diff:**

```bash
git diff HEAD~1 -- <tool_registration_files> | grep "^[+-].*\(tool_id\|capabilities\|response_schema\|scope\|auth_type\)"
```

**Step 9.2 — Per-field breaking change assessment:**

**`tool_id` change:**
```bash
rg "{old_tool_id}" src/ --include="*.py" --include="*.json" -l
```
Any agent hardcoding the old `tool_id` (a violation of AG4, but may exist) will fail at
tool lookup time.

**Capability tag removal:**
```bash
# Find agents that request the removed capability
rg "{removed_capability_tag}" src/ --include="*.py" -l
```
Agents requesting a removed capability tag receive `ToolNotFound` at execution time.

**Response schema change:**
```bash
git diff HEAD~1 -- <tool_registration_files> | grep -A 30 "response_schema"
```
Any field removed from the response schema — or type-changed — breaks all agents parsing
the tool response. The agent's response normaliser will fail or silently return `None` for
the missing field.

**Scope reduction:**
```bash
git diff HEAD~1 -- <tool_registration_files> | grep "^[+-].*scope"
```
A scope reduction (e.g. `write → read`) causes authorization failures for agents that rely
on the write permission. The tool call succeeds at dispatch but the external API returns 403.
This is a silent regression — the agent may retry indefinitely.

**Flag as Critical when:**
- `tool_id` changed with live references to the old ID
- Scope reduced from `write` or `admin` to `read` with agents requiring write access

**Flag as Major when:**
- Capability tag removed with registered agents requesting it
- Response schema field removed with agents parsing that field

**Flag as Minor when:**
- `tool_id` changed with no live references (clean rename with no consumers)
- Response schema field added (non-breaking, but verify normaliser handles unknown fields)

---

### Lens 10 — SDK Compatibility

**Applies to: Zone SDK (files in `sdks/`).**

**Why it matters:** SDK consumers are external and cannot be updated atomically with the
platform. An SDK breaking change silently fails for all consumers who have not yet upgraded.
Unlike internal services (which are all deployed together), SDK consumers on their own
release cycle may be running the old interface for weeks after the platform has changed.

**Step 10.1 — Public interface diff:**

```bash
# Identify public methods changed or removed
git diff HEAD~1 -- sdks/ | grep "^[+-].*\(def \|async def \|class \|export \)" | grep -v "^---\|^+++"

# Identify type changes
git diff HEAD~1 -- sdks/ | grep "^[+-].*\(: str\|: int\|: bool\|: List\|: Dict\|: Optional\)"
```

**Step 10.2 — Breaking change classification:**

| SDK Change | Breaking? |
|-----------|-----------|
| Public method removed | Breaking 🔴 |
| Public method renamed | Breaking 🔴 |
| Required parameter added | Breaking 🔴 |
| Parameter removed | Breaking 🔴 |
| Parameter reordered | Breaking 🔴 |
| Return type changed | Breaking 🔴 |
| Exception type changed | Breaking 🔴 |
| New optional parameter with default | Non-breaking ✅ |
| New method added | Non-breaking ✅ |
| Internal private method changed | Non-breaking ✅ |

**Step 10.3 — SDK version check:**

```bash
git diff HEAD~1 -- sdks/*/pyproject.toml sdks/*/package.json | grep "^[+-].*version"
```

Any breaking change (Step 10.2 = Breaking) requires a major version increment (semver: `1.x.x →
2.0.0`). Any non-breaking addition requires a minor version increment (`1.0.x → 1.1.0`). If
a breaking change is present with no version increment, all consumers will silently break on
package update.

**Step 10.4 — Changelog check:**

```bash
cat sdks/*/CHANGELOG.md | head -20
```

Every SDK change must have a CHANGELOG entry. Missing entry is Major.

**Flag as Critical when:**
- Public method removed or renamed with no major version increment
- Required parameter added or removed with no major version increment
- Return type changed with no major version increment

**Flag as Major when:**
- Breaking change present with no CHANGELOG entry
- SDK version not incremented on any change

**Flag as Minor when:**
- Internal private method changed (no consumer impact, but note for maintainability)
- CHANGELOG entry missing for a non-breaking addition

---

### Lens 11 — Backward Compatibility Summary

**Applies to: all PRs. Always execute last.**

**Why it matters:** The individual lenses assess specific dimensions in isolation. This lens
synthesises a holistic backward compatibility verdict that a release manager or team lead can
act on immediately.

**Step 11.1 — Aggregate findings across all lenses:**

Count findings by severity for each lens. Note which lenses found breaking changes.

**Step 11.2 — Migration path assessment:**

For every breaking change found across all lenses: is there a documented migration path in the
PR body? A migration path must state:
1. What consumers or services are affected
2. What they must do to migrate (update a call site, update a config, subscribe to new topic)
3. What the window is for migration (is the old interface maintained in parallel temporarily?)

**Step 11.3 — Deployment risk assessment:**

Identify whether any breaking change requires a coordinated multi-service deployment:
- Database migration + application code = deploy migration first, then application
- Kafka schema change + producer + consumer = must coordinate producer and consumer deployment
- API breaking change + client = must coordinate API and client deployment

**Verdict classification:**

| Verdict | Condition |
|---------|-----------|
| FULLY COMPATIBLE | No breaking changes found in any lens across all zones |
| COMPATIBLE WITH MIGRATION | Breaking changes exist, but a documented migration path is present in the PR and all affected consumers are identified |
| BREAKING — REQUIRES VERSIONING | Breaking changes exist with no documented migration path, or migration path exists but affected consumers are not all identified |

---

## Step 4 — Produce the Review Output

```
## Regression Review: PR #{N} — {title}
Author: {author} | {additions}+ {deletions}- | {files_changed} files

---

### Blast Radius Map
Zone S (shared):      {files or NONE} → {N} downstream importers across {M} services
Zone C (contracts):   {files or NONE} → breaking | non-breaking | N/A
Zone W (workflows):   {files or NONE} → {N} templates changed, {M} states affected
Zone A (agents):      {files or NONE} → {N} registrations changed
Zone T (tools):       {files or NONE} → {N} registrations changed
Zone K (kafka):       {files or NONE} → breaking | non-breaking | N/A
Zone D (database):    {files or NONE} → {migration_file}: safe | risky | breaking
Zone I (infra):       {files or NONE} → {N} env vars changed, {M} ports changed
Zone SDK (sdk):       {files or NONE} → breaking | non-breaking | N/A
Zone API (api):       {files or NONE} → breaking | non-breaking | N/A

---

### Critical 🔴
{file/path.py}:{line} — {what breaks}
  Why it matters: {concrete runtime failure scenario — what fails, when, how}
  Fix: {specific action required — not general advice}

---

### Major 🟠
{file/path.py}:{line} — {what breaks}
  Why it matters: {impact}
  Fix: {specific action required}

---

### Minor 🟡
{file/path.py}:{line} — {what to note}
  Fix: {specific action or acknowledgement}

---

### Regression Risk
| Dimension       | Risk | Detail |
|-----------------|------|--------|
| Blast Radius    | HIGH / MED / LOW / N/A | {N} downstream importers affected across {M} services |
| Contract        | HIGH / MED / LOW / N/A | breaking / non-breaking / N/A |
| API             | HIGH / MED / LOW / N/A | {N} endpoints changed, {M} breaking |
| Events/Kafka    | HIGH / MED / LOW / N/A | {topic/schema change summary} |
| Database        | HIGH / MED / LOW / N/A | {migration safety summary} |
| Infrastructure  | HIGH / MED / LOW / N/A | {env var / port / CI change summary} |
| Workflow        | HIGH / MED / LOW / N/A | {state machine change summary} |
| Agent           | HIGH / MED / LOW / N/A | {registration change summary} |
| Tool            | HIGH / MED / LOW / N/A | {registration change summary} |
| SDK             | HIGH / MED / LOW / N/A | {interface change summary} |
| Backward Compat | FULLY COMPATIBLE / COMPATIBLE WITH MIGRATION / BREAKING — REQUIRES VERSIONING |

---

### Lens Results
| Lens | Status | Summary |
|------|--------|---------|
| 1 Blast Radius        | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary or "No Zone S files changed"} |
| 2 Contract            | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary or "No contract files changed"} |
| 3 API                 | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary} |
| 4 Events/Kafka        | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary} |
| 5 Database            | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary} |
| 6 Infrastructure      | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary} |
| 7 Workflow            | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary} |
| 8 Agent               | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary} |
| 9 Tool                | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary} |
| 10 SDK                | ✅ PASS / ⚠️ WARN / ❌ FAIL / N/A | {summary} |
| 11 Backward Compat    | ✅ FULLY COMPATIBLE / ⚠️ WITH MIGRATION / ❌ BREAKING | {verdict} |

---

### Merge Recommendation
{1-2 sentences. State what must change before merge, the coordinated deployment steps required
if any, or confirm the PR introduces no regressions.}

### Verdict
APPROVE — no regressions detected
REQUEST CHANGES — regressions found: {list blocking findings}
NEEDS DISCUSSION — potential regressions requiring team decision: {list}
```

---

## Mandatory Verdict Rules

**`REQUEST CHANGES`** — required when any of the following are true, regardless of all other
lens results:

- Any Critical finding in any lens
- Breaking contract change without `schema_version` increment (Lens 2)
- Breaking API change without API version increment (Lens 3)
- Kafka topic name changed (Lens 4)
- Kafka event_type string changed (Lens 4)
- Database migration adds NOT NULL column with no default (Lens 5)
- Database migration drops column still referenced in application code (Lens 5)
- Database migration has no `downgrade()` or empty `downgrade()` (Lens 5)
- RLS policy removed or weakened in a migration (Lens 5)
- Workflow state removed or renamed (Lens 7)
- `agent_id` changed with live references to the old ID (Lens 8)
- `idempotency_key_strategy` changed (Lens 8)
- SDK public method removed/renamed with no major version increment (Lens 10)
- Zone S importer call site broken by changed interface (Lens 1)

**`NEEDS DISCUSSION`** — required when:

- Breaking change is present and a migration path is documented but the migration is complex,
  risky, or requires a coordinated multi-service deployment window
- Workflow template change affects long-running in-flight workflow runs (state exists but
  behaviour changes significantly)
- Tool scope reduction that may affect existing agents (scope is confirmed reduced, but no
  agents confirmed broken yet)
- Kafka partition key change (ordering regression risk that requires team assessment of
  in-flight message volume)
- Cost_class increase on a high-throughput agent (budget impact requires explicit sign-off)

**`APPROVE`** — only when:

- All Critical and Major findings are resolved or acknowledged with explicit team sign-off
- Backward Compatibility verdict is FULLY COMPATIBLE or COMPATIBLE WITH MIGRATION with a
  documented, low-risk migration path
- No Constitution or contract violations

---

## Review Rules

1. Review only the PR diff — do not invent regressions not traceable to changed code
2. This skill reviews regressions only — do not flag code correctness, style, or new-feature
   quality issues (those belong to aep-review)
3. Every finding must cite an exact `file:line` from the diff
4. Every finding must explain the concrete runtime failure scenario, not just what changed
5. Every finding must have a specific, actionable fix — not general advice
6. A finding is not a regression unless it breaks something that was already working — new
   functionality that is incomplete is a correctness issue, not a regression
7. Never accept "it's unlikely to affect callers" without evidence from grep or rg
8. Never treat a breaking contract change as anything less than Critical
9. Never skip the blast radius grep for Zone S changes — always run the importer scan
10. Never skip the database migration safety checks — these are the highest deployment risk
11. If a lens has no applicable files (zone not present in PR), record it as N/A — do not
    skip it silently
12. Maximum 20 findings total — prioritise by severity (Critical first), then by blast radius
    (Zone S > Zone K > Zone D > others), then by concreteness of failure scenario

---

## Completion Checklist

Before producing the output, verify:

- [ ] All applicable lenses executed (N/A recorded for lenses with no zone files)
- [ ] Blast Radius Map produced with importer counts for every Zone S file
- [ ] Regression Risk table complete for all 11 dimensions
- [ ] Every Critical finding has a concrete runtime failure scenario and a specific fix
- [ ] Backward Compatibility verdict stated (FULLY COMPATIBLE / COMPATIBLE WITH MIGRATION / BREAKING)
- [ ] Verdict is consistent with Mandatory Verdict Rules
- [ ] No style, correctness, or new-feature findings included (regression only)

---

## Relationship to aep-review

| Skill | Question it answers | When to run |
|-------|--------------------|----|
| aep-review | Is this new code correct, complete, and architecturally sound? | All PRs |
| regression-review | Did this change break anything that was already working? | PRs touching shared zones (S, C, W, A, T, K, D, I, SDK, API) |

Both skills must PASS before merge. They are complementary, not redundant. A PR may pass
aep-review (new code is correct) and fail regression-review (it broke a downstream importer).
A PR may pass regression-review (no backward-compatibility regressions) and fail aep-review
(the new code itself is incomplete or architecturally wrong).
