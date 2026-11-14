import logging
import uuid
from typing import Annotated

from cosmic_astronomy.irsa import build_sia_url
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from cosmic_api.catalog import EXAMPLES, build_example, find_frame_preview
from cosmic_api.schemas import (
    ErrorResponse,
    ExampleResponse,
    ObservationQuery,
    QueryPlan,
    SearchResponse,
    SkySearchQuery,
)
from cosmic_api.settings import Settings, get_settings

logger = logging.getLogger("cosmic_api")

SettingsDep = Annotated[Settings, Depends(get_settings)]


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
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
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
    responses=error_responses(422, 501, 502, 504),
    tags=["observations"],
)
def sky_search(query: SkySearchQuery) -> SearchResponse:
    """Live SPHEREx search against IRSA. Not wired yet: always 501 after validation."""
    raise HTTPException(status_code=501, detail="live search not wired")


@app.get("/v1/examples", response_model=list[ExampleResponse], tags=["examples"])
def list_examples(settings: SettingsDep) -> list[ExampleResponse]:
    """The five challenge targets from cached manifests; never queries IRSA."""
    return [build_example(slug, settings) for slug in EXAMPLES]


@app.get(
    "/v1/examples/{slug}",
    response_model=ExampleResponse,
    responses=error_responses(404),
    tags=["examples"],
)
def get_example(slug: str, settings: SettingsDep) -> ExampleResponse:
    if slug not in EXAMPLES:
        raise HTTPException(status_code=404, detail="Unknown example")
    return build_example(slug, settings)


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
