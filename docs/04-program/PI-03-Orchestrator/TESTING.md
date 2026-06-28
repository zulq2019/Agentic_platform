# PI-03-Orchestrator — Testing Strategy

## Test Pyramid

Unit tests (= 80% coverage on all new code) ? Integration tests (cross-service flows) ? Contract tests ? Security scan.

## Unit Tests
- All domain logic in Orchestrator has unit tests
- Edge cases: empty input, invalid tenant, Kafka unavailable
- All tests hermetic — no external dependencies

## Integration Tests
- Cross-service event flows verified end-to-end
- Database RLS isolation confirmed
- Kafka round-trip: produce ? consume ? ack

## Contract Tests
- All agents/tools registered in this PI pass contract validation
- python scripts/validate_contract.py exits 0

## Security Tests
| Check | Tool | Threshold |
|-------|------|-----------|
| Container CVEs | Trivy | 0 critical, 0 high |
| Python deps | pip-audit | 0 critical |
| Secrets | detect-secrets | 0 findings |

## Performance Baseline
All API endpoints: p99 < 200ms under normal load.
Document baseline metrics at PI close in DEMO.md.
