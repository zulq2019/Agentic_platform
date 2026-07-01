# Blueprint: Workflow Templates (7 remaining)

**Status:** DEFERRED — greenfield-v1.0.0.json complete, 7 templates in PI-05/PI-06  
**Target PI:** PI-05 (defect-resolution, feature-enhancement) → PI-06 (remaining 5)

## Current State

`workflows/greenfield-v1.0.0.json` — complete and operational.

## Remaining 7 Templates

| Template | States | Key Gates | Delivered In |
|----------|--------|-----------|-------------|
| `brownfield-v1.0.0.json` | Scoped → Discovered → Architected → Implemented → Tested → Scanned → Merged → Released | Arch gate, Merge gate, Release gate | PI-05 |
| `defect-resolution-v1.0.0.json` | Root-Cause-Identified → Fix-Implemented → Regression-Tested → Hotfix-Merged → Deployed | SRE gate, Release gate | PI-05 |
| `feature-enhancement-v1.0.0.json` | Scoped → Implemented → Tested → Reviewed → Merged | Tech Lead gate | PI-06 |
| `security-remediation-v1.0.0.json` | Vulnerability-Identified → Remediated → Verified → Closed | CSO gate | PI-06 |
| `technical-debt-v1.0.0.json` | Assessed → Refactored → Tested → Merged | Senior Eng gate | PI-06 |
| `migration-v1.0.0.json` | Planned → Script-Generated → Staged → Production-Applied | DBA gate, CAB gate | PI-06 |
| `release-management-v1.0.0.json` | Release-Staged → Release-Tested → Candidate-Approved → Released | Release Manager gate, CAB gate | PI-06 |

## Template Schema

Each template follows the schema established in `workflows/greenfield-v1.0.0.json`:

```json
{
  "workflow_type": "...",
  "version": "1.0.0",
  "initial_state": "...",
  "terminal_states": ["Released", "Failed", "RolledBack"],
  "states": [
    {
      "name": "Scoped",
      "required_capability": "analyses-requirements",
      "gate": {
        "id": "scope-gate",
        "strategy": "open-ended",
        "required_role": "product-owner"
      },
      "transitions_to": "Implemented"
    }
  ],
  "context_handoff": {},
  "rollback_strategy": {},
  "success_criteria": []
}
```

## Versioning Policy

- New workflow version = new file (brownfield-v1.1.0.json)
- Existing runs on old template are never migrated automatically
- Template versions are immutable once a workflow run references them
