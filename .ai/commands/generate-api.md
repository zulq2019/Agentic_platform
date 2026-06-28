# generate-api.md

**Command:** `generate-api`  
**Version:** 1.0  
**Library:** `.ai/commands/`  
**Applies to:** All PIs — use when a story requires a new REST API endpoint or gRPC method

---

## Purpose

Use this command to generate a production-ready API layer for a service: the route handler, request/response models, authentication middleware, input validation, error handling, and OpenAPI documentation.

This command does not generate business logic. It generates the API contract boundary that exposes domain logic to callers.

One execution = one logical API resource (e.g., `/agents`, `/tasks/{id}/approve`).

---

## Inputs

| Input | Location | Required |
|-------|----------|----------|
| Constitution | `CONSTITUTION.md` | Mandatory |
| Architecture — API Gateway section | `docs/artifacts/TECHNICAL_ARCHITECTURE.md` (Section 15) | Mandatory |
| AI implementation rules | `CLAUDE.md` | Mandatory |
| API Spec | `docs/04-program/{PI}/API_SPEC.md` — target endpoint | Mandatory |
| User Story | `docs/04-program/{PI}/USER_STORIES.md` — target story | Mandatory |
| Acceptance Criteria | `docs/04-program/{PI}/ACCEPTANCE_CRITERIA.md` | Mandatory |
| Implementation Guide | `docs/04-program/{PI}/IMPLEMENTATION.md` | Mandatory |
| Domain service interface | `src/{target_folder}/domain/{service}.py` | Mandatory |
| Existing auth middleware | `src/platform/gateway/` | Mandatory |

**Substitutions required:**

```
{PI}              = e.g. PI-03-Orchestrator
{story_id}        = e.g. US-PI-03-04
{resource}        = e.g. workflows
{http_method}     = GET | POST | PUT | DELETE | PATCH
{endpoint_path}   = e.g. /api/v1/workflows/{workflow_id}/approve
{service_name}    = e.g. workflow-service
{target_folder}   = e.g. src/platform/workflow/
```

---

## Preconditions

- [ ] The domain service interface (`domain/{service}.py`) exists
- [ ] Auth middleware is available in `src/platform/gateway/`
- [ ] The endpoint is specified in `docs/04-program/{PI}/API_SPEC.md`
- [ ] Request and response schemas are defined in the API spec

---

## Execution Steps

### Step 1 — Read the API spec

Read `docs/04-program/{PI}/API_SPEC.md` for the target endpoint. Extract:

```
Method:          {http_method}
Path:            {endpoint_path}
Auth:            Bearer token | API key | Internal only
Tenant scope:    extracted from auth context | explicit parameter
Request schema:  {field list with types and constraints}
Response schema: {field list with types}
Error codes:     {list of possible error responses}
SLO:             {p99 latency target}
```

### Step 2 — Define Pydantic models

Create request and response models in `src/{target_folder}/api/schemas.py`:

Rules:
- Every field has a type annotation
- Every field has a `Field(description="...")` for OpenAPI generation
- UUIDs use `uuid.UUID`, not `str`
- Timestamps use `datetime`, not `str`
- No optional fields that are actually required (use `Field(...)` for required)
- Enums use Python `enum.Enum`, not plain strings
- `tenant_id` is never accepted from the request body — always extracted from auth context

```python
class {Resource}CreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # reject unknown fields
    field_name: type = Field(..., description="...", min_length=1, max_length=255)

class {Resource}Response(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID  # included in response for client-side validation
    created_at: datetime
    ...
```

### Step 3 — Generate the route handler

Create the route in `src/{target_folder}/api/routes/{resource}.py`:

Template structure:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from aep_common.auth import get_verified_tenant_context, TenantContext
from aep_common.logging import get_logger
from aep_common.tracing import get_tracer

router = APIRouter(prefix="/api/v1/{resource}", tags=["{resource}"])
logger = get_logger(__name__)
tracer = get_tracer(__name__)

@router.{http_method}("{path_suffix}", response_model={Resource}Response, status_code=status.HTTP_{code})
async def {handler_name}(
    request: {Resource}CreateRequest,
    ctx: TenantContext = Depends(get_verified_tenant_context),
    service: {DomainService} = Depends(get_{domain_service}),
) -> {Resource}Response:
    with tracer.start_as_current_span("{handler_name}") as span:
        span.set_attribute("tenant_id", str(ctx.tenant_id))
        span.set_attribute("task_id", str(request.task_id) if hasattr(request, "task_id") else "")
        
        logger.info("{handler_name}.called", tenant_id=ctx.tenant_id)
        
        try:
            result = await service.{domain_method}(ctx.tenant_id, request)
            logger.info("{handler_name}.succeeded", tenant_id=ctx.tenant_id, resource_id=result.id)
            return {Resource}Response.model_validate(result)
        except {DomainError} as exc:
            logger.warning("{handler_name}.domain_error", error=str(exc), tenant_id=ctx.tenant_id)
            raise HTTPException(status_code=status.HTTP_{error_code}, detail=str(exc)) from exc
```

### Step 4 — Wire authentication

Verify that `get_verified_tenant_context` is used as a dependency on every endpoint. This middleware:
- Validates the Bearer token against `rbac-service`
- Extracts and validates `tenant_id`
- Populates `TenantContext` for the request lifetime
- Never trusts `tenant_id` from the request body

For internal-only endpoints (service-to-service):
- Use `get_verified_service_context` instead
- Validate the service identity header
- Reject any request without a valid service token

### Step 5 — Wire error handling

Map every domain exception to an HTTP status code in `src/{target_folder}/api/exception_handlers.py`:

```python
exception_map = {
    ResourceNotFoundError:       status.HTTP_404_NOT_FOUND,
    ResourceAlreadyExistsError:  status.HTTP_409_CONFLICT,
    ValidationError:             status.HTTP_422_UNPROCESSABLE_ENTITY,
    UnauthorizedError:           status.HTTP_403_FORBIDDEN,
    RateLimitExceededError:      status.HTTP_429_TOO_MANY_REQUESTS,
}
```

Never expose internal exception messages to API callers. Use safe error messages.

### Step 6 — Add rate limiting

Apply rate limiting to every public endpoint:
```python
@router.post("...", dependencies=[Depends(rate_limiter(requests=100, window_seconds=60))])
```

Rate limits are per-tenant, not per-IP.

### Step 7 — Generate OpenAPI annotations

Every endpoint must produce complete OpenAPI documentation:
- `summary`: one-line description
- `description`: detailed explanation including side effects
- `response_description`: what the 200 response represents
- `responses`: document every error code

### Step 8 — Write API tests

Generate tests in `src/tests/integration/{service_name}/test_api_{resource}.py`:

Required tests:
- Happy path: valid request returns expected response
- Missing auth: 401 returned
- Wrong tenant: 403 returned (cross-tenant access rejected)
- Invalid input: 422 returned with field-level errors
- Not found: 404 returned with correct error code
- Rate limit exceeded: 429 returned
- Domain error: correct HTTP status mapped from domain exception

---

## Expected Outputs

| Artifact | Location |
|----------|----------|
| Pydantic request/response models | `src/{target_folder}/api/schemas.py` |
| Route handler | `src/{target_folder}/api/routes/{resource}.py` |
| Exception handler map | `src/{target_folder}/api/exception_handlers.py` |
| API integration tests | `src/tests/integration/{service_name}/test_api_{resource}.py` |
| Updated API spec | `docs/04-program/{PI}/API_SPEC.md` |

---

## Quality Gates

- [ ] Every field in request model has `Field(description=...)` annotation
- [ ] `tenant_id` never accepted from request body
- [ ] Rate limiting applied to every public endpoint
- [ ] Every domain exception mapped to a specific HTTP status
- [ ] Internal error messages not exposed in HTTP responses
- [ ] OTEL span wraps every handler
- [ ] All required auth tests written and passing

---

## Completion Checklist

```
[ ] API spec read — endpoint requirements understood
[ ] Pydantic models created — all fields typed and annotated
[ ] Route handler generated — auth, tracing, error handling
[ ] Authentication middleware wired
[ ] Error handling wired — domain errors mapped to HTTP codes
[ ] Rate limiting applied
[ ] OpenAPI annotations complete
[ ] API integration tests written and passing
[ ] API spec updated in PI documentation
```

---

## Forbidden Actions

The AI executing this command must NEVER:

- Accept `tenant_id` from the request body
- Expose internal exception messages or stack traces to API callers
- Skip rate limiting on public endpoints
- Skip authentication on any endpoint
- Use plain `str` for UUIDs or timestamps
- Accept extra fields in the request model (`extra="forbid"` required)
- Call domain services directly without going through dependency injection
- Implement business logic inside route handlers
- Return different response shapes for success vs error
- Skip API documentation annotations
