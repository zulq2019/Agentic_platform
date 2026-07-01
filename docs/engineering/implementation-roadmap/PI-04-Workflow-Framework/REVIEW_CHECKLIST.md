# PI-04-Workflow-Framework — Review Checklist

## Architecture
- [ ] Code belongs to the correct service boundary
- [ ] No cross-boundary data access without event or registered API
- [ ] No specialist logic added to orchestrator-service
- [ ] tenant_id in all data queries

## Code Quality
- [ ] ruff check exits 0
- [ ] black --check exits 0
- [ ] mypy --strict exits 0
- [ ] No silent exception handling

## Events
- [ ] Every Kafka message validates against EventEnvelope
- [ ] Consumer commits offset only after successful processing
- [ ] Failures routed to DLQ, never silently dropped

## Security
- [ ] No hardcoded values
- [ ] Tool scope set to minimum required
- [ ] Input validated at service boundary

## Tests
- [ ] New unit tests cover new logic
- [ ] Integration test added for new cross-service flow
- [ ] Contract test updated if contracts changed

## Documentation
- [ ] PR description explains what and why
- [ ] .env.example updated
