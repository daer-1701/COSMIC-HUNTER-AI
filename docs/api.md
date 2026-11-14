# HTTP contracts

Executable source: Pydantic models and OpenAPI exported to
`packages/shared/openapi.json`. `/docs` and `/openapi.json` are available at startup.

## Implemented

| Method / route | Result |
| --- | --- |
| GET /health/live | 200: process alive; does not assert SQL/IRSA readiness |
| POST /v1/observations/query-plan | 200: IRSA URL, executed=false; 422: invalid input |
| POST /v1/sky/search | 200: live IRSA SIA2 observations, source=live; 422; 502 IRSA failure; 504 after 25 s |
| GET /v1/examples, GET /v1/examples/{slug}?detector= | 200: cached manifests, source=cache; never contacts IRSA; 404 unknown slug |
| GET /v1/frames/{id} | 200 image/png from `apps/web/public/previews/`; 404 if missing |
| POST /v1/examples/{slug}/summary | 200: Gemini text citing evidence tags; 404; 409 no manifest; 429 budget/rate; 502 provider or rejected output; 503 disabled; 504 |

Search and example responses carry `detectors`: the distinct detector values in order of
first appearance, computed before any filter. `?detector=` keeps exact matches; an
unknown value returns 200 with an empty list and `unknown-detector`, not 404.

The summary endpoint is a paid call. It runs only when `GEMINI_ENABLED=true` and the
key, model, both token prices, and a positive `GEMINI_BUDGET_USD` are set; otherwise
503 names the missing setting. Before calling, it reserves the worst-case cost (UTF-8
byte length of the prompt as an input-token bound, plus `GEMINI_MAX_OUTPUT_TOKENS`) in
`data/state/gemini_budget.json`; no reservation, no call. Real usage is settled after the
call; provider 4xx releases the reservation, an unknown outcome is charged at the
reserved maximum. The model sees only numbered evidence lines from the cached manifest
and must cite them; text without citations, with unknown tags, or with discovery
phrases is rejected with 502 (and still charged). Identical evidence is served from an
in-process cache. The ledger lock is per process: run one API worker until the budget
moves to PostgreSQL. Summary text never changes measurements or comparability.

`/v1/sky/search` lists ObsCore rows only; it never downloads FITS or returns
`access_url`. Rows are sorted by `t_min` (MJD) and de-duplicated by publisher DID,
because one SPHEREx `obs_id` covers several detectors. `detector` copies
`energy_bandpassname` verbatim and `band` stays null: a detector is not a uniform band.
The VOTable does not declare a time scale, so `time_scale` is null, `iso_time` is the
calendar rendering of the MJD without a UTC suffix, and the response carries the
`time-scale-unverified` warning. An empty result is 200 with `no-observations`.
`preview_url` is set only when a cached manifest frame with the same `obs_id` and
`detector` has a PNG. One retry on a network failure or an IRSA 502/503/504; redirects are not followed;
responses above 32 MB are rejected.

ICRS coordinates in degrees: 0 <= RA < 360, -90 <= Dec <= 90; radius (0, 0.5].
DR1 or QR3 collection. Optional time requires both MJD bounds using the scale required
by SIA2; confirm file semantics during import. Extra fields and nonfinite values are
rejected. The query-plan endpoint does not run external queries; no endpoint persists
evidence.

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

## Published WISE 0855 integration

The repository now includes Mateo's DR1 D2 manifest and two PNG previews. Use
`GET /v1/examples/wise-0855?detector=SPHEREx-D2`, then request each observation's
`preview_url`. These are cached products, not fresh downloads. The response preserves
`coord_epoch`, and each cached observation exposes `hdu` and `sha256` (the original
FITS checksum, not the PNG checksum). Live observations leave those fields null.
Comparison notes and warnings must remain visible in the frontend: the supplied
checks support visual comparison but do not measure target motion or flux changes.
The other four examples remain not ready until their manifests are supplied.

`tests/test_published_example.py` checks the actual published PNG checksums and HTTP
routes, metadata, disabled Gemini behavior, and preview linking with a synthetic
archive response. It does not re-run the notebook or validate the original FITS.
