from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Collection = Literal["spherex_dr1", "spherex_qr3"]
ExampleSlug = Literal["barnards-star", "epsilon-indi-b", "wise-0855", "rw-aurigae", "r-draconis"]


class ObservationQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    ra_deg: float = Field(ge=0, lt=360, description="ICRS right ascension in degrees")
    dec_deg: float = Field(ge=-90, le=90, description="ICRS declination in degrees")
    radius_deg: float = Field(gt=0, le=0.5)
    collection: Collection = "spherex_dr1"
    start_mjd: float | None = Field(default=None, ge=0)
    end_mjd: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_interval(self):
        if (self.start_mjd is None) != (self.end_mjd is None):
            raise ValueError("Provide both start_mjd and end_mjd, or neither")
        if self.start_mjd is not None and self.end_mjd < self.start_mjd:
            raise ValueError("end_mjd must be >= start_mjd")
        return self


class QueryPlan(BaseModel):
    archive: Literal["IRSA"] = "IRSA"
    url: str
    executed: Literal[False] = False
    warning: str = "Query plan only; no observations have been downloaded or validated."


class ErrorResponse(BaseModel):
    detail: str
    request_id: str


class SkySearchQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    ra_deg: float = Field(ge=0, lt=360, description="ICRS right ascension in degrees")
    dec_deg: float = Field(ge=-90, le=90, description="ICRS declination in degrees")
    radius_deg: float = Field(gt=0, le=0.5, description="Cone radius in degrees")
    collection: Collection = "spherex_dr1"


class Observation(BaseModel):
    id: str = Field(description="Stable identifier used by /v1/frames/{id}")
    obs_id: str | None = Field(description="Archive observation identifier, copied verbatim")
    mjd: float | None = Field(description="Observation time as published; scale in time_scale")
    time_scale: str | None
    iso_time: str | None
    collection: Collection
    detector: str | None
    band: str | None
    flags: list[str] = Field(default_factory=list)
    preview_url: str | None = Field(description="API path to a PNG preview, or null if none")
    hdu: int | None = Field(default=None, description="Original FITS HDU from the cached manifest")
    sha256: str | None = Field(
        default=None, description="Original FITS SHA-256, not the PNG checksum"
    )


class SearchResponse(BaseModel):
    source: Literal["live", "cache"]
    queried_at: datetime
    query: SkySearchQuery
    warnings: list[str] = Field(default_factory=list)
    detectors: list[str] = Field(
        default_factory=list,
        description="Distinct detector values in order of first appearance, before filtering",
    )
    observations: list[Observation] = Field(default_factory=list)


class ExampleResponse(SearchResponse):
    """A cached search for one of the challenge targets; never a live archive query."""

    source: Literal["cache"] = "cache"
    slug: ExampleSlug
    name: str
    queried_at: datetime | None = Field(description="When the cached archive query was made")
    query: SkySearchQuery | None = Field(description="Null until the target manifest exists")
    coord_source: str | None = None
    coord_epoch: str | None = None
    comparable: bool | None = Field(
        default=None, description="Whether at least two frames can be animated together"
    )
    comparison_note: str | None = None


class EvidenceLine(BaseModel):
    id: str = Field(description="Tag cited in the summary text, e.g. E1")
    text: str


class SummaryUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    cost_usd: float
    budget_remaining_usd: float


class SummaryResponse(BaseModel):
    """Gemini's plain-language explanation of a cached target's evidence. Not a measurement."""

    slug: ExampleSlug
    model: str
    generated_at: datetime
    cached: bool = Field(description="True when served from the in-process summary cache")
    text: str
    cited: list[str]
    evidence: list[EvidenceLine]
    usage: SummaryUsage
    disclaimer: str = (
        "AI-generated explanation of archive metadata. It does not confirm any object or motion."
    )


class ManifestFrame(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    obs_id: str | None
    mjd: float | None
    time_scale: str | None
    iso_time: str | None
    detector: str | None
    band: str | None
    hdu: int | None
    flags: list[str] = Field(default_factory=list)
    preview_file: str | None
    sha256: str | None


class Manifest(BaseModel):
    """On-disk contract for data/manifests/{slug}.json, written by the data pipeline."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    slug: ExampleSlug
    name: str
    ra_deg: float = Field(ge=0, lt=360)
    dec_deg: float = Field(ge=-90, le=90)
    coord_source: str | None
    coord_epoch: str | None
    collection: Collection
    radius_deg: float = Field(gt=0, le=0.5)
    queried_at: datetime | None
    comparable: bool
    comparison_note: str | None
    warnings: list[str] = Field(default_factory=list)
    frames: list[ManifestFrame] = Field(default_factory=list)
