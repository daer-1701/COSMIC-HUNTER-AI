"""SIA2 query construction; does not fetch, invent or validate archive results."""

import math
from urllib.parse import urlencode

SIA_ENDPOINT = "https://irsa.ipac.caltech.edu/SIA"
COLLECTIONS = frozenset({"spherex_dr1", "spherex_qr3"})


def build_sia_url(
    ra_deg: float,
    dec_deg: float,
    radius_deg: float,
    collection: str = "spherex_dr1",
    start_mjd: float | None = None,
    end_mjd: float | None = None,
) -> str:
    if not all(math.isfinite(v) for v in (ra_deg, dec_deg, radius_deg)):
        raise ValueError("Coordinates must be finite")
    if not (0 <= ra_deg < 360 and -90 <= dec_deg <= 90 and 0 < radius_deg <= 0.5):
        raise ValueError("Invalid ICRS region; radius must be in (0, 0.5] degrees")
    if collection not in COLLECTIONS:
        raise ValueError("Unsupported release/collection")
    params = {"COLLECTION": collection, "POS": f"CIRCLE {ra_deg} {dec_deg} {radius_deg}"}
    if (start_mjd is None) != (end_mjd is None):
        raise ValueError("Both time bounds are required")
    if start_mjd is not None:
        if not all(math.isfinite(v) for v in (start_mjd, end_mjd)):
            raise ValueError("Time bounds must be finite")
        if not 0 <= start_mjd <= end_mjd:
            raise ValueError("Invalid MJD interval")
        params["TIME"] = f"{start_mjd} {end_mjd}"
    return f"{SIA_ENDPOINT}?{urlencode(params)}"
