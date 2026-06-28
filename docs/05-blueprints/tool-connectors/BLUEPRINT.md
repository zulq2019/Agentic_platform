# Blueprint: 11 Tool Connectors

**Status:** DEFERRED — 3 connectors in PI-05, remaining 8 in PI-06/PI-07  
**Target PI:** PI-05 (github, jira, confluence) → PI-06 (sonarqube, snyk, ci/cd tools) → PI-07 (infra tools)

## Purpose

This blueprint documents all 11 external tool connectors, their capability tags, required scopes, and response normalisation contracts.

## Tool Inventory

| Tool ID | Capability Tags | Auth Strategy | Scope | Delivered In |
|---------|----------------|--------------|-------|-------------|
| `github-prod` | `create-branch`, `commit-files`, `create-pull-request`, `create-release`, `read-repository` | GitHub App | write | PI-05 |
| `jira-tenant-{id}` | `create-issue`, `update-issue`, `add-comment`, `read-issue` | OAuth2 | write | PI-05 |
| `confluence-tenant-{id}` | `create-page`, `update-page`, `read-page` | OAuth2 | write | PI-05 |
| `azure-devops-{id}` | `create-branch`, `commit-files`, `create-pull-request`, `trigger-pipeline` | PAT | write | PI-06 |
| `gitlab-{id}` | `create-branch`, `commit-files`, `create-pull-request` | OAuth2 | write | PI-06 |
| `sonarqube-{id}` | `trigger-security-scan`, `read-scan-results` | API key | read | PI-06 |
| `snyk-{id}` | `trigger-security-scan`, `read-scan-results` | API key | read | PI-06 |
| `terraform-{id}` | `plan-infrastructure`, `apply-infrastructure` | Service principal | write | PI-07 |
| `kubernetes-{id}` | `deploy-workload`, `get-workload-status` | Service account | write | PI-07 |
| `azure-{id}` | `provision-resource`, `read-resource-status` | Managed identity | write | PI-07 |
| `aws-{id}` | `provision-resource`, `read-resource-status` | IAM role | write | PI-07 |

## Directory Structure (created per PI)

```
tools/
├── github-tool/          # PI-05
├── jira-tool/            # PI-05
├── confluence-tool/      # PI-05
├── azure-devops-tool/    # PI-06
├── gitlab-tool/          # PI-06
├── sonarqube-tool/       # PI-06
├── snyk-tool/            # PI-06
├── terraform-tool/       # PI-07
├── kubernetes-tool/      # PI-07
├── azure-tool/           # PI-07
└── aws-tool/             # PI-07
```

## Tool Directory Structure

```
tools/{tool-name}/
├── {tool_name}.tool.py     # Implements Tool Contract
├── registration.json        # Tool Contract (validated against tool-contract.schema.json)
├── normaliser.py            # Maps vendor response → common-tool-responses.schema.json shape
├── rate_limit_policy.json
├── tests/
│   ├── test_contract.py
│   ├── test_normaliser.py   # Vendor shape → common shape
│   ├── test_scope.py        # Cannot exceed registered scope
│   └── test_idempotency.py
└── pyproject.toml
```

## Common Response Shapes

All tools normalise responses to shapes defined in `contracts/common-tool-responses.schema.json`:
- `pull_request`: pr_id, pr_url, status, branch, title
- `issue`: issue_id, issue_url, status, title, assignee
- `test_report`: passed, failed, skipped, coverage, report_url
- `security_report`: critical, high, medium, low, report_url
- `deployment`: deployment_id, status, url, version

## Key Design Rules

- Tool scope is the CEILING — never elevated at runtime
- Credentials always via secrets-service (never in tool code)
- Response normaliser is required — agents never parse vendor-specific shapes
- Rate limit policy defined per tool per tenant
- All tool operations are idempotent where possible
