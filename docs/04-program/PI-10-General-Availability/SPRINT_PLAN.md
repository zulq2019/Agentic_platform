# PI-10 — Sprint Plan

## Sprint 39–40 (Days 381–400): Infrastructure as Code

| # | Task | Points |
|---|------|--------|
| 39.1 | Terraform AWS module: EKS + Aurora + MSK + ElastiCache | 5 |
| 39.2 | Terraform Azure module: AKS + Flexible Server + Event Hubs + Redis | 5 |
| 39.3 | Terraform HCP Vault module | 3 |
| 40.1 | K8s production manifests: HPA for all services | 3 |
| 40.2 | K8s PodDisruptionBudgets + ResourceQuotas | 2 |
| 40.3 | NetworkPolicy: deny-all default + explicit allow per pair | 3 |
| 40.4 | Helm chart: single-command deploy to new cluster | 3 |

---

## Sprint 41–42 (Days 401–420): Load + Chaos Testing

| # | Task | Points |
|---|------|--------|
| 41.1 | Load test: 10,000 workflows/day, 100 tenants (k6 or Locust) | 4 |
| 41.2 | Identify and resolve 3 bottlenecks from load test results | 4 |
| 41.3 | Tune HPA: agent-runtime scales to 200 pods under load | 2 |
| 42.1 | Chaos: kill orchestrator mid-workflow — workflow resumes | 3 |
| 42.2 | Chaos: kill Kafka broker — no message loss, consumers reconnect | 3 |
| 42.3 | Chaos: simulate AZ failure — traffic rerouted in < 60s | 3 |
| 42.4 | Chaos: PostgreSQL failover — Aurora promotes replica in < 60s | 3 |

---

## Sprint 43 (Days 421–430): Security + DR

| # | Task | Points |
|---|------|--------|
| 43.1 | External penetration test — fix all critical and high findings | 5 |
| 43.2 | DR drill: full cluster restore from backup | 3 |
| 43.3 | Verify RTO < 5 min for full cluster restore | 2 |
| 43.4 | Verify RPO < 60s for PostgreSQL, < 5s for Redis | 2 |

---

## Sprint 44 (Days 431–440): Documentation + Beta Pilot + GA

| # | Task | Points |
|---|------|--------|
| 44.1 | Architecture guide — peer-reviewed | 2 |
| 44.2 | Developer guide — peer-reviewed | 2 |
| 44.3 | Operator runbook — peer-reviewed | 2 |
| 44.4 | API reference — generated from OpenAPI, reviewed | 1 |
| 44.5 | SDK guide — peer-reviewed | 1 |
| 44.6 | Beta pilot: 2 external tenants, production data, 2-week observation | 3 |
| 44.7 | GA release: tag v1.0.0, publish release notes | 2 |

**Sprint Goal:** GA. All exit criteria met. First paying customers live.
