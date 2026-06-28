# PI-01 — Testing Strategy

## Test Pyramid for Platform Spine

```
                    [E2E - 2%]
                 make dev-up → all green
              [Integration - 18%]
           Kafka round-trip · DB RLS · CI pipeline
        [Unit - 80%]
     aep-common modules · health routes · schema validation
```

## Unit Tests

| Test File | What It Covers | Pass Criteria |
|-----------|----------------|---------------|
| `tests/common/test_logging.py` | Structured log fields present | task_id, workflow_run_id, tenant_id in output |
| `tests/common/test_kafka_envelope.py` | Envelope validation | Missing field raises ValidationError |
| `tests/common/test_health.py` | Health endpoints | 200 live, 503 ready when dep down |
| `tests/common/test_errors.py` | Exception hierarchy | All error types serialisable to JSON |
| `tests/common/test_security.py` | JWT decode + tenant_id | Correct tenant extracted, invalid token raises 401 |
| `tests/db/test_migrations.py` | Migration idempotency | `make migrate` runs twice with no error |

## Integration Tests

| Test File | What It Covers |
|-----------|----------------|
| `tests/integration/test_kafka_round_trip.py` | Produce → consume → ack with envelope validation |
| `tests/integration/test_rls_isolation.py` | Cross-tenant query returns 0 rows |
| `tests/integration/test_health_all_services.py` | All 16 `/health/ready` return 200 |
| `tests/integration/test_kafka_topology.py` | All 11 topics + ACLs correct |

## Contract Validation Tests

Run automatically in CI:

```bash
python scripts/validate_contract.py contracts/
# Must exit 0 — validates all *.schema.json files against metaschema
# Validates contracts/examples/*.json against their parent schemas
```

## Security Tests

| Check | Tool | Threshold |
|-------|------|-----------|
| Container image vulnerabilities | Trivy | Zero critical, zero high |
| Python dependency CVEs | pip-audit | Zero critical |
| Hardcoded secrets | detect-secrets | Zero findings |

## Performance Baseline (recorded at PI-01 close)

```
make dev-up time-to-healthy: < 60s
make migrate execution time: < 30s
CI pipeline duration: < 8 min
/health/live p99 latency: < 20ms
```
