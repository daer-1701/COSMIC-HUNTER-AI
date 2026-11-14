"""Live SPHEREx search against IRSA SIA2. Reads ObsCore rows; never downloads FITS."""

import logging
import math
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from urllib.parse import urlsplit

import httpx

from cosmic_api.schemas import Observation

logger = logging.getLogger("cosmic_api")

IRSA_HOST = "irsa.ipac.caltech.edu"
MAX_RESPONSE_BYTES = 32 * 1024 * 1024
MJD_EPOCH = datetime(1858, 11, 17)
EXPECTED_COLUMNS = ("obs_id", "obs_publisher_did", "obs_collection", "t_min", "energy_bandpassname")
UNSAFE_ID_CHARS = re.compile(r"[^A-Za-z0-9_.-]+")


class ArchiveError(Exception):
    """IRSA failed; carries the HTTP status our API answers with (502 or 504)."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def fetch_votable(
    url: str, timeout_s: float, transport: httpx.BaseTransport | None = None
) -> bytes:
    """GET an IRSA URL within a total deadline, retrying once on a network failure."""
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname != IRSA_HOST:
        raise ValueError("Only https://irsa.ipac.caltech.edu URLs may be fetched")

    deadline = time.monotonic() + timeout_s
    for attempt in (1, 2):
        try:
            return _get(url, deadline, transport)
        except httpx.TimeoutException as exc:
            raise ArchiveError(504, f"IRSA did not respond within {timeout_s:g} seconds") from exc
        except httpx.TransportError as exc:
            logger.warning("IRSA network failure (attempt %d): %s", attempt, exc)
            if attempt == 2 or deadline - time.monotonic() <= 0:
                raise ArchiveError(502, "Could not reach IRSA") from exc
    raise AssertionError("unreachable")


def _get(url: str, deadline: float, transport: httpx.BaseTransport | None) -> bytes:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise httpx.ReadTimeout("deadline exceeded before request")
    with httpx.Client(timeout=remaining, follow_redirects=False, transport=transport) as client:
        with client.stream("GET", url) as response:
            if response.status_code != 200:
                logger.warning("IRSA answered HTTP %d for %s", response.status_code, url)
                raise ArchiveError(502, f"IRSA returned HTTP {response.status_code}")
            content_type = response.headers.get("content-type", "")
            if "xml" not in content_type:
                logger.warning("IRSA answered content-type %r", content_type)
                raise ArchiveError(502, "IRSA returned a response that is not a VOTable")
            chunks: list[bytes] = []
            size = 0
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > MAX_RESPONSE_BYTES:
                    raise ArchiveError(502, "IRSA response too large; use a smaller radius_deg")
                if time.monotonic() > deadline:
                    raise httpx.ReadTimeout("deadline exceeded while reading")
                chunks.append(chunk)
            return b"".join(chunks)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element if _local(child.tag) == name]


def parse_votable(data: bytes) -> tuple[list[dict[str, str | None]], list[str]]:
    """Return the result rows keyed by FIELD name, plus warnings about the table itself."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ArchiveError(502, "IRSA returned a malformed VOTable") from exc
    if _local(root.tag) != "VOTABLE":
        raise ArchiveError(502, "IRSA returned a response that is not a VOTable")

    resources = _children(root, "RESOURCE")
    results = next((r for r in resources if r.get("type") == "results"), None)
    if results is None:
        results = next((r for r in resources if _children(r, "TABLE")), None)
    if results is None:
        raise ArchiveError(502, "IRSA VOTable has no result table")

    warnings: list[str] = []
    for info in _children(results, "INFO") + _children(root, "INFO"):
        if info.get("name") != "QUERY_STATUS":
            continue
        status = (info.get("value") or "").upper()
        if status == "ERROR":
            message = " ".join((info.text or "").split())[:200] or "no message"
            raise ArchiveError(502, f"IRSA query error: {message}")
        if status == "OVERFLOW":
            warnings.append("results-truncated")

    tables = _children(results, "TABLE")
    if not tables:
        return [], warnings
    table = tables[0]
    names = [field.get("name") or "" for field in _children(table, "FIELD")]
    if any(column not in names for column in EXPECTED_COLUMNS):
        warnings.append("columns-unverified")

    rows: list[dict[str, str | None]] = []
    for data_element in _children(table, "DATA"):
        tabledata = _children(data_element, "TABLEDATA")
        if not tabledata:
            raise ArchiveError(502, "Unsupported VOTable serialization from IRSA")
        for tr in _children(tabledata[0], "TR"):
            cells = [(td.text or "").strip() or None for td in _children(tr, "TD")]
            rows.append(dict(zip(names, cells, strict=False)))
    return rows, warnings


def _mjd(value: str | None) -> float | None:
    try:
        mjd = float(value) if value is not None else None
    except ValueError:
        return None
    return mjd if mjd is not None and math.isfinite(mjd) else None


def _calendar_time(mjd: float | None) -> str | None:
    """Calendar rendering of the MJD in the archive's own time scale, so no UTC suffix."""
    if mjd is None:
        return None
    return (MJD_EPOCH + timedelta(days=mjd)).isoformat(timespec="seconds")


def build_observations(
    rows: list[dict[str, str | None]],
    collection: str,
    previews: dict[tuple[str, str], str],
) -> tuple[list[Observation], list[str]]:
    """Turn ObsCore rows into contract observations, sorted by time and de-duplicated.

    One SPHEREx obs_id covers several detectors, so identity is the publisher DID
    (obs_id plus detector), not obs_id alone.
    """
    warnings: list[str] = []
    seen: set[str] = set()
    duplicates = 0
    foreign = 0
    observations: list[Observation] = []

    for row in rows:
        row_collection = row.get("obs_collection")
        if row_collection is not None and row_collection != collection:
            foreign += 1
            continue
        obs_id = row.get("obs_id")
        detector = row.get("energy_bandpassname")
        key = row.get("obs_publisher_did") or f"{obs_id}/{detector}"
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)

        frame_id = UNSAFE_ID_CHARS.sub("-", "-".join(p for p in (obs_id, detector) if p))
        mjd = _mjd(row.get("t_min"))
        preview_id = previews.get((obs_id, detector)) if obs_id and detector else None
        observations.append(
            Observation(
                id=frame_id or f"row-{len(observations) + 1}",
                obs_id=obs_id,
                mjd=mjd,
                time_scale=None,
                iso_time=_calendar_time(mjd),
                collection=collection,
                detector=detector,
                band=None,
                flags=[],
                preview_url=f"/v1/frames/{preview_id}" if preview_id else None,
            )
        )

    observations.sort(key=lambda o: (o.mjd is None, o.mjd or 0.0, o.detector or ""))
    if duplicates:
        logger.info("Removed %d duplicate IRSA rows", duplicates)
        warnings.append("duplicate-rows-removed")
    if foreign:
        warnings.append("unexpected-collection-rows-skipped")
    if any(o.mjd is None for o in observations):
        warnings.append("missing-time")
    if observations:
        # The SIA2 VOTable publishes t_min in MJD without declaring a time scale.
        warnings.append("time-scale-unverified")
    else:
        warnings.append("no-observations")
    return observations, warnings
