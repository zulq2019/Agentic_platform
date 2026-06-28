# PI-01 — Demo Script

**Audience:** Engineering team, stakeholders  
**Duration:** 15 minutes  
**Prerequisites:** `make dev-up` running

---

## Scene 1 — All Services Alive (3 min)

1. Open terminal. Run `make dev-up`.
2. Wait for all 16 services to show green.
3. Open Grafana at `http://localhost:3000` → Service Health Dashboard.
4. **Talking point:** "Every service we will build for the next 6 months starts from this foundation. No surprises — every service looks the same."

---

## Scene 2 — Event Bus Operational (3 min)

1. Run `python scripts/verify_kafka_topology.py`.
2. Show output: all 11 topics + DLQ confirmed.
3. Produce a test event manually:
   ```bash
   python scripts/produce_test_event.py --topic aep.task.created --tenant tenant-demo
   ```
4. Show it consumed by the test consumer with full envelope parsed.
5. **Talking point:** "Every event that flows through this system — every agent action, every human decision — goes through this bus in this exact format."

---

## Scene 3 — Database with RLS (3 min)

1. Connect to PostgreSQL:
   ```bash
   make db-shell
   ```
2. Set tenant context and query:
   ```sql
   SET app.current_tenant_id = 'tenant-a';
   SELECT COUNT(*) FROM orchestrator.workflow_runs; -- returns 0 (only tenant-a rows)
   SET app.current_tenant_id = 'tenant-b';
   SELECT COUNT(*) FROM orchestrator.workflow_runs; -- returns different count
   ```
3. **Talking point:** "Multi-tenancy is enforced at the database layer. Even if a bug in application code forgot to filter by tenant, the database refuses to return another tenant's data."

---

## Scene 4 — CI Pipeline (3 min)

1. Open GitHub Actions on the repo.
2. Show last passing CI run: lint → unit tests → contract validation → build.
3. Show the duration — under 8 minutes.
4. **Talking point:** "Every pull request gets this feedback. We catch contract violations, missing tests, and security issues before they reach the main branch."

---

## Wrap-up (3 min)

- PI-01 is the invisible foundation. No user-visible features — but the platform is now buildable.
- PI-02 starts next sprint: the Agent Runtime and first working event flow.
- Questions?
