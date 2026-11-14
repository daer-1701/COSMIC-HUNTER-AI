# HTTP contracts

Executable source: Pydantic models and OpenAPI exported to
`packages/shared/openapi.json`. `/docs` and `/openapi.json` are available at startup.

## Implemented

| Method / route | Result |
| --- | --- |
| GET /health/live | 200: process alive; does not assert SQL/IRSA readiness |
| POST /v1/observations/query-plan | 200: IRSA URL, executed=false; 422: invalid input |

ICRS coordinates in degrees: 0 <= RA < 360, -90 <= Dec <= 90; radius (0, 0.5].
DR1 or QR3 collection. Optional time requires both MJD bounds using the scale required
by SIA2; confirm file semantics during import. Extra fields and nonfinite values are
rejected. This endpoint does not run external queries or persist evidence.

## Designed, not yet implemented

| Planned route | Planned contract |
| --- | --- |
| POST /v1/observation-searches | 202 + job_id and Location; bounded asynchronous search |
| GET /v1/observations | Opaque cursor + limit <= 100; region/epoch/collection filters |
| POST /v1/jobs | JWT + Idempotency-Key; inputs reference persisted IDs; 202 |
| GET /v1/jobs/{id} | Persisted state, progress, and errors by stage |
| GET /v1/candidates | Filters and cursor pagination |
| GET /v1/candidates/{id} | Detections, errors, motion, provenance, and review |
| GET /v1/candidates/{id}/evidence | Versioned manifest and temporary links |
| POST /v1/candidates/{id}/reviews | Reviewer JWT; 201 or 409 if already present |
| POST /v1/candidates/{id}/summary | JWT + budget limit; evidence required |

Before implementation, specify bodies and errors in OpenAPI and generate the TS client.
Planned errors with request_id: 401/403 authorization, 404 missing resource, 409 conflict,
422 validation, 429 quota, 502/503 provider errors; Retry-After where applicable.
Reusing Idempotency-Key with a different body must return 409. Document API messages
and descriptions in English.
