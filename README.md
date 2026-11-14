# Cosmic Hunter AI

Architecture foundation for investigating apparent motion in SPHEREx observations.
Prepared from the team's brief on November 14, 2026.

**Status: phase 1.** A runnable minimal API and tested contracts. There is no working
frontend, FITS downloader, detector, scientific result, or Gemini integration yet.
This is not a validated discovery tool.

## Local setup

Requirements: Git, Python 3.12 or 3.13, and [uv](https://docs.astral.sh/uv/).
From the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
uv sync --frozen
uv run uvicorn cosmic_api.main:app --reload --port 8000
```

Demo path: `uv sync` plus `uvicorn` is all you need. The API serves cached manifests
from `data/manifests/*.json` and PNG previews from `apps/web/public/previews/`.
No Docker, AWS, or Gemini keys are required; CORS allows `http://localhost:3000`.
Optional later: PostgreSQL and Redis via `docker compose`. S3 and Gemini are planned
and unused this weekend.

Interactive documentation: http://localhost:8000/docs.
`POST /v1/sky/search` queries IRSA live and lists SPHEREx observations in time order
(no FITS download). `GET /v1/examples/{slug}` serves cached manifests; a cached example
is not a live query. `POST /v1/observations/query-plan` only builds the IRSA SIA2 URL.

```json
{"ra_deg":127.69,"dec_deg":-39.17,"radius_deg":0.01,"collection":"spherex_dr1"}
```

Verification:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run python scripts/export_openapi.py
```

Optional, not needed for the demo: with Docker Desktop's Linux engine running,
`docker compose up --build`. This starts
the local API, PostgreSQL, and Redis; the current API does not use the database or
queue yet. SQL runs only when the PostgreSQL volume is first created. This is a local
development configuration. S3 and workers will be added with the processing pipeline.

## Repository

```text
apps/web/              Planned Next.js frontend and integration contract
services/api/          FastAPI and HTTP validation
services/astronomy/    IRSA query construction; future FITS/WCS processing
services/detection/    Reserved boundary for baseline and temporal association
services/ai/           Reserved boundary for classification and copilot
services/workers/      Reserved boundary for Celery orchestration
packages/shared/       Generated OpenAPI; future TypeScript client source
data/                 Local files excluded from Git; data policy
notebooks/             Future reproducible experiments
scripts/               Contract export
tests/                Query contracts and boundaries
docs/                 Architecture, science, API, and implementation plan
infrastructure/        Containers and initial SQL schema
```

Read the [architecture](docs/architecture.md), [data model](docs/data-model.md),
[API contracts](docs/api.md), [sources and requirements](docs/research.md),
[scientific validation](docs/science.md), and [remaining phases](docs/roadmap.md).
Separate directories do not mean all engines have been implemented.

## Working with Codex and Cursor

Shared instructions are in [AGENTS.md](AGENTS.md). Five repository skills live in
`.agents/skills/`, with scoped Cursor rules in `.cursor/rules/`. Read the
[skills and coordination guide](docs/agent-tooling.md) to activate them and divide
work without overwriting changes.

The [three-person project plan](docs/team-plan.md) assigns owners, tasks,
dependencies, and all 20 deliverables from the brief.

English is the default for documentation, agent instructions, code comments,
API messages, interface text, reports, and presentation materials.

## Git publication

The repository uses `main`. Inspect `git status` and existing remotes before following
the [publication guide](docs/git.md). No credentials, FITS files, or models belong in
Git. The team has not selected a distribution license; do not assume permission to
reuse project code.
