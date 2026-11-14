from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ObservationQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    ra_deg: float = Field(ge=0, lt=360, description="ICRS right ascension in degrees")
    dec_deg: float = Field(ge=-90, le=90, description="ICRS declination in degrees")
    radius_deg: float = Field(gt=0, le=0.5)
    collection: Literal["spherex_dr1", "spherex_qr3"] = "spherex_dr1"
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
