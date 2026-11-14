from cosmic_astronomy.irsa import build_sia_url
from fastapi import FastAPI

from cosmic_api.schemas import ObservationQuery, QueryPlan

app = FastAPI(
    title="Cosmic Hunter AI",
    version="0.1.0",
    description="Architecture foundation. No detection or discovery claims.",
)


@app.get("/health/live", tags=["operations"])
def liveness() -> dict[str, str]:
    """Process liveness only; does not assert database/archive readiness."""
    return {"status": "ok", "stage": "architecture-foundation"}


@app.post("/v1/observations/query-plan", response_model=QueryPlan, tags=["observations"])
def observation_query_plan(query: ObservationQuery) -> QueryPlan:
    return QueryPlan(url=build_sia_url(**query.model_dump()))
