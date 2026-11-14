# Cosmic Hunter web

Next.js application for the SPHEREx explorer. Interface text is English.

The browser calls the API at `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`).
Run the web app on port 3000 so the API CORS rule applies. Types in `src/lib/schema.d.ts`
are generated from the OpenAPI document; do not edit that file by hand.

`POST /v1/sky/search` runs a live IRSA search. `GET /v1/examples` serves cached targets
and does not call IRSA. A missing `preview_url` stays text. Timestamps with a null
`time_scale` are shown as published, not as UTC. `POST /v1/examples/{slug}/summary`
returns 503 as “AI summary unavailable” when the model is off.

## Run

From the repository root, start the API:

```powershell
uv run uvicorn cosmic_api.main:app --reload --port 8000
```

From `apps/web`:

```powershell
npm install
npm run generate:api
npm test
npm run dev
```

Open http://localhost:3000. Search from Explore submits the real query plan. Compare,
candidates, review, and copilot stay empty until those endpoints exist.

Aladin Lite is loaded from the `aladin-lite` package when a valid ICRS position is
entered. The public CDS script path returned 404 during implementation. The map
is a DSS context view, not a SPHEREx exposure. Plotly loads only if measurement
points are passed to the trajectory chart. The current pages pass none.

## Checks

```powershell
npm test
npm run lint
npm run build
```
