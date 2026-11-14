---
name: cosmic-api-contracts
description: Create or update Cosmic Hunter AI FastAPI/Pydantic contracts, Celery jobs, PostgreSQL persistence, or Gemini controls with explicit boundaries, traceability, and consistent OpenAPI clients.
---

# Scientific backend contracts

Read docs/api.md, docs/architecture.md, and the affected code. For persistence, also
read docs/data-model.md and the current SQL. Do not expose routes that suggest real
processing when only placeholders exist. A query plan returns executed=false.
Write schemas, descriptions, errors, and documentation in English.

## HTTP and schemas

Define units, coordinate frame, time scale, bounds, and extra-field policy in Pydantic.
Reject nonfinite values and incomplete/reversed intervals. Paginate queries and bound
radius/time/volume according to measured capacity. Document implemented responses and
errors. Avoid HTTP 200 responses with failures hidden in the body. Do not expose keys,
internal traces, or private provider responses to the browser.

Move heavy processing to jobs with inputs referencing persisted IDs. Distinguish 202
acceptance from final results. Bind Idempotency-Key to body/configuration: the same
key with a different request is a conflict. Authorize reads/writes per resource before
persisting or delivering private artifacts.

## State and persistence

SQL owns state; Redis is not the sole evidence of progress. Resolve job creation/enqueue
atomicity with an outbox or another explicit mechanism. Design for repeated delivery,
partial writes, bounded retries, and cancellation before enabling workers. Produce
immutable results per run/configuration. Do not serialize FITS through the broker.
Evolve schemas through migrations; the current bootstrap only initializes a new database.
Verify constraints and transactions against real PostgreSQL before claiming they work.

## Gemini, when implemented by the task

Backend only, with persisted evidence and model/prices checked against official Google
documentation. Atomically reserve maximum cost before calling; account for tokens,
concurrency, retries, and calls with unknown outcomes. No reservation means no call.
Use offline tests for cache, quotas, and budget; paid tests require authorization.
Verify evidence references in responses. Do not change measurements or discovery
states based on model text.

## Verification

Add acceptance/rejection and provider-failure tests appropriate to the change.
Regenerate with `uv run python scripts/export_openapi.py`, inspect the diff, and run
Ruff/pytest as specified in AGENTS.md. Do not manually edit the generated contract.
Report operational routes and distinguish unit tests from real integration checks.
