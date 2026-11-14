import logging
import math
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import httpx
from cosmic_ai.budget import BudgetExceeded
from cosmic_ai.summary import (
    Prices,
    ProviderTimeout,
    SummaryError,
    build_evidence,
    generate_summary,
    render_prompt,
)
from cosmic_astronomy.irsa import build_sia_url
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from cosmic_api import summaries
from cosmic_api.catalog import (
    EXAMPLES,
    build_example,
    distinct_detectors,
    find_frame_preview,
    preview_index,
)
from cosmic_api.live_search import ArchiveError, build_observations, fetch_votable, parse_votable
from cosmic_api.schemas import (
    ErrorResponse,
    EvidenceLine,
    ExampleResponse,
    ObservationQuery,
    QueryPlan,
    SearchResponse,
    SkySearchQuery,
    SummaryResponse,
    SummaryUsage,
)
from cosmic_api.settings import Settings, get_settings

logger = logging.getLogger("cosmic_api")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    for name in ("cosmic_api", "cosmic_ai"):
        logging.getLogger(name).addHandler(handler)
        logging.getLogger(name).setLevel(logging.INFO)

SettingsDep = Annotated[Settings, Depends(get_settings)]
DEMO_TIMEZONE = timezone(timedelta(hours=-4))


def get_archive_transport() -> httpx.BaseTransport | None:
    """Default network transport; tests override it so no request leaves the process."""
    return None


def get_gemini_client_factory() -> Callable[[Settings], Any]:
    """The client is built only after the configuration gate; tests override this."""
    return summaries.get_gemini_client


TransportDep = Annotated[httpx.BaseTransport | None, Depends(get_archive_transport)]
GeminiFactoryDep = Annotated[Callable[[Settings], Any], Depends(get_gemini_client_factory)]


def error_responses(*codes: int) -> dict[int | str, dict]:
    return {code: {"model": ErrorResponse} for code in codes}


app = FastAPI(
    title="Cosmic Hunter AI",
    version="0.1.0",
    description="Architecture foundation. No detection or discovery claims.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(get_settings().cors_origins),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Request-ID"],
)


@app.middleware("http")
async def assign_request_id(request: Request, call_next):
    request.state.request_id = uuid.uuid4().hex
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    logger.info(
        "%s %s status=%d source=%s ms=%.0f",
        request.method,
        request.url.path,
        response.status_code,
        getattr(request.state, "source", "-"),
        (time.perf_counter() - started) * 1000,
    )
    return response


def error_response(request: Request, status_code: int, detail: str, headers=None) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None) or uuid.uuid4().hex
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "request_id": request_id},
        headers={**(headers or {}), "X-Request-ID": request_id},
    )


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return error_response(request, exc.status_code, str(exc.detail), exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    detail = "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}" for error in exc.errors()
    )
    return error_response(request, 422, detail or "Invalid request")


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return error_response(request, 500, "Internal server error")


@app.get("/health/live", tags=["operations"])
def liveness() -> dict[str, str]:
    """Process liveness only; does not assert database/archive readiness."""
    return {"status": "ok", "stage": "architecture-foundation"}


@app.post(
    "/v1/observations/query-plan",
    response_model=QueryPlan,
    responses=error_responses(422),
    tags=["observations"],
)
def observation_query_plan(query: ObservationQuery) -> QueryPlan:
    return QueryPlan(url=build_sia_url(**query.model_dump()))


@app.post(
    "/v1/sky/search",
    response_model=SearchResponse,
    responses=error_responses(422, 502, 504),
    tags=["observations"],
)
def sky_search(
    query: SkySearchQuery, settings: SettingsDep, transport: TransportDep, request: Request
) -> SearchResponse:
    """Live SPHEREx search against IRSA SIA2; lists observations, never downloads FITS."""
    request.state.source = "live"
    queried_at = datetime.now(DEMO_TIMEZONE).replace(microsecond=0)
    url = build_sia_url(**query.model_dump())
    try:
        rows, table_warnings = parse_votable(
            fetch_votable(url, settings.irsa_timeout_seconds, transport)
        )
    except ArchiveError as exc:
        logger.warning("search source=live status=%d detail=%s", exc.status_code, exc.detail)
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    observations, row_warnings = build_observations(
        rows, query.collection, preview_index(query.collection, settings)
    )
    logger.info("search source=live status=200 observations=%d", len(observations))
    return SearchResponse(
        source="live",
        queried_at=queried_at,
        query=query,
        warnings=table_warnings + row_warnings,
        detectors=distinct_detectors(observations),
        observations=observations,
    )


@app.get("/v1/examples", response_model=list[ExampleResponse], tags=["examples"])
def list_examples(settings: SettingsDep, request: Request) -> list[ExampleResponse]:
    """The five challenge targets from cached manifests; never queries IRSA."""
    request.state.source = "cache"
    return [build_example(slug, settings) for slug in EXAMPLES]


@app.get(
    "/v1/examples/{slug}",
    response_model=ExampleResponse,
    responses=error_responses(404),
    tags=["examples"],
)
def get_example(
    slug: str,
    settings: SettingsDep,
    request: Request,
    detector: Annotated[
        str | None, Query(description="Keep only frames with this exact detector value")
    ] = None,
) -> ExampleResponse:
    request.state.source = "cache"
    if slug not in EXAMPLES:
        raise HTTPException(status_code=404, detail="Unknown example")
    return build_example(slug, settings, detector)


@app.post(
    "/v1/examples/{slug}/summary",
    response_model=SummaryResponse,
    responses=error_responses(404, 409, 429, 502, 503, 504),
    tags=["examples"],
)
def summarize_example(
    slug: str, settings: SettingsDep, make_client: GeminiFactoryDep, request: Request
) -> SummaryResponse:
    """Gemini explains the cached manifest of one target, citing numbered evidence.

    Paid call: runs only when GEMINI_ENABLED=true, prices and a USD budget are set, and
    the worst-case cost fits in the remaining budget. Output never changes any result.
    """
    request.state.source = "gemini"
    if slug not in EXAMPLES:
        raise HTTPException(status_code=404, detail="Unknown example")
    if reason := summaries.missing_configuration(settings):
        raise HTTPException(status_code=503, detail=reason)

    example = build_example(slug, settings)
    if example.query is None:
        raise HTTPException(status_code=409, detail="No cached evidence for this target yet")
    evidence = build_evidence(example.model_dump(mode="json"))
    evidence_lines = [EvidenceLine(id=tag, text=text) for tag, text in evidence]
    ledger = summaries.get_ledger(
        settings.state_dir / "gemini_budget.json", settings.gemini_budget_usd
    )
    key = summaries.cache_key(slug, settings.gemini_model, render_prompt(evidence))
    if (cached := summaries.summary_cache.get(key)) is not None:
        return cached.model_copy(update={"cached": True})

    if wait := summaries.rate_limiter.acquire(settings.gemini_max_calls_per_minute):
        raise HTTPException(
            status_code=429,
            detail="Too many Gemini summaries; try again shortly",
            headers={"Retry-After": str(math.ceil(wait))},
        )
    try:
        result = generate_summary(
            evidence,
            client=make_client(settings),
            model=settings.gemini_model,
            prices=Prices(settings.gemini_input_usd_per_mtok, settings.gemini_output_usd_per_mtok),
            ledger=ledger,
            max_output_tokens=settings.gemini_max_output_tokens,
        )
    except BudgetExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except ProviderTimeout as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except SummaryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    response = SummaryResponse(
        slug=slug,
        model=settings.gemini_model,
        generated_at=datetime.now(DEMO_TIMEZONE).replace(microsecond=0),
        cached=False,
        text=result.text,
        cited=result.cited,
        evidence=evidence_lines,
        usage=SummaryUsage(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=round(result.cost_usd, 6),
            budget_remaining_usd=round(ledger.state().remaining_usd, 6),
        ),
    )
    summaries.summary_cache[key] = response
    return response


@app.get(
    "/v1/frames/{frame_id}",
    response_class=FileResponse,
    responses={200: {"content": {"image/png": {}}}, **error_responses(404)},
    tags=["frames"],
)
def get_frame(frame_id: str, settings: SettingsDep) -> FileResponse:
    path = find_frame_preview(frame_id, settings)
    if path is None:
        raise HTTPException(status_code=404, detail="Frame not found")
    return FileResponse(path, media_type="image/png")
