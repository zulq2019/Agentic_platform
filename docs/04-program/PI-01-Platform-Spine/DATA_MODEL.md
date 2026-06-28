# PI-01 — Data Model

PI-01 establishes the database schema foundation. Full DDL lives in `platform/shared/migrations/`.

## Core Tables (implemented in PI-01)

### orchestrator.workflow_runs

```sql
CREATE TABLE orchestrator.workflow_runs (
    workflow_run_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id         TEXT NOT NULL,
    workflow_type     TEXT NOT NULL,
    workflow_template_version TEXT NOT NULL,
    current_state     TEXT NOT NULL,
    started_at        TIMESTAMPTZ DEFAULT now(),
    completed_at      TIMESTAMPTZ,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ DEFAULT now(),
    updated_at        TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE orchestrator.workflow_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orchestrator.workflow_runs
    USING (tenant_id = current_setting('app.current_tenant_id'));
CREATE INDEX idx_wfr_tenant_state ON orchestrator.workflow_runs (tenant_id, current_state);
```

### orchestrator.tasks

```sql
CREATE TABLE orchestrator.tasks (
    task_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_run_id   UUID NOT NULL REFERENCES orchestrator.workflow_runs(workflow_run_id),
    tenant_id         TEXT NOT NULL,
    assigned_agent_id TEXT,
    state             TEXT NOT NULL DEFAULT 'pending',
    context           JSONB NOT NULL DEFAULT '{}'::jsonb,
    retry_count       INT NOT NULL DEFAULT 0,
    approval_record   JSONB,
    model_tier        TEXT,
    created_at        TIMESTAMPTZ DEFAULT now(),
    updated_at        TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE orchestrator.tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orchestrator.tasks
    USING (tenant_id = current_setting('app.current_tenant_id'));
CREATE INDEX idx_tasks_wfr ON orchestrator.tasks (workflow_run_id, state);
CREATE INDEX idx_tasks_agent ON orchestrator.tasks (assigned_agent_id, state);
```

### agents.registrations

```sql
CREATE TABLE agents.registrations (
    agent_id            TEXT PRIMARY KEY,
    tenant_id           TEXT NOT NULL,
    capabilities        JSONB NOT NULL DEFAULT '[]'::jsonb,
    input_schema        TEXT NOT NULL,
    output_schema       TEXT NOT NULL,
    required_tools      JSONB NOT NULL DEFAULT '[]'::jsonb,
    cost_class          TEXT NOT NULL CHECK (cost_class IN ('low','medium','high')),
    approval_required   BOOLEAN NOT NULL DEFAULT false,
    idempotency_key_strategy TEXT NOT NULL,
    contract_version    TEXT NOT NULL,
    active              BOOLEAN NOT NULL DEFAULT true,
    registered_at       TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE agents.registrations ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON agents.registrations
    USING (tenant_id = current_setting('app.current_tenant_id'));
CREATE INDEX idx_agents_capabilities ON agents.registrations USING GIN (capabilities);
```

### memory.entries (pgvector)

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE memory.entries (
    memory_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      TEXT NOT NULL,
    source_type    TEXT NOT NULL CHECK (source_type IN ('standard','adr','incident','codebase')),
    content        TEXT NOT NULL,
    embedding      vector(1536),
    recency_weight FLOAT NOT NULL DEFAULT 1.0,
    provenance     JSONB NOT NULL,
    metadata       JSONB,
    created_at     TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE memory.entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON memory.entries
    USING (tenant_id = current_setting('app.current_tenant_id'));
CREATE INDEX ON memory.entries USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_memory_tenant_type ON memory.entries (tenant_id, source_type, recency_weight DESC);
```

## Redis Key Schema

```
aep:{tenant_id}:ctx:{task_id}           TTL 24h    Working context
aep:{tenant_id}:sess:{session_id}       TTL 8h     User session
aep:{tenant_id}:quota:{tier}:tokens     TTL 1h     Model quota window
aep:{tenant_id}:rl:{tool_id}:{min}      TTL 60s    Tool rate limit
aep:lock:{resource_id}                  TTL 30s    Distributed lock
```
