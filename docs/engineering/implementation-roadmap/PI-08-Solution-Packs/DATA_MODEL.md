# PI-08-Solution-Packs — Data Model

## Overview
Enterprise introduces the following data stores. Full DDL is in platform/shared/migrations/.

## PostgreSQL Tables
All tables follow these invariants:
- RLS enabled immediately after CREATE TABLE
- tenant_id column NOT NULL on every table
- tenant_isolation policy: USING (tenant_id = current_setting('app.current_tenant_id'))
- Timestamps: created_at and updated_at TIMESTAMPTZ DEFAULT now()
- UUID primary keys: DEFAULT gen_random_uuid()

See DATA_MODEL in PI-01 for the foundational schema.
Enterprise-specific tables are defined in their respective migration files:
platform/shared/migrations/

## Redis Keys
All keys prefixed: aep:{tenant_id}:{service}:{resource_id}
TTL applied to all transient keys.

## Event Payloads
See contracts/event-envelope.schema.json for the envelope.
PI-specific payload shapes documented in the API_SPEC.md for this PI.
