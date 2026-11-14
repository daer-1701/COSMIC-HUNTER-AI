"""Cached challenge targets read from data/manifests; never contacts IRSA."""

import logging
from pathlib import Path

from pydantic import ValidationError

from cosmic_api.schemas import (
    ExampleResponse,
    Manifest,
    ManifestFrame,
    Observation,
    SkySearchQuery,
)
from cosmic_api.settings import Settings

logger = logging.getLogger("cosmic_api")

EXAMPLES: dict[str, str] = {
    "barnards-star": "Barnard's Star",
    "epsilon-indi-b": "Epsilon Indi B",
    "wise-0855": "WISE 0855",
    "rw-aurigae": "RW Aurigae",
    "r-draconis": "R Draconis",
}


def load_manifest(slug: str, settings: Settings) -> tuple[Manifest | None, str | None]:
    """Return the manifest, or None with the warning that explains why it is missing."""
    path = settings.manifests_dir / f"{slug}.json"
    if not path.is_file():
        return None, "manifest-not-ready"
    try:
        manifest = Manifest.model_validate_json(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValidationError) as exc:
        logger.warning("Rejected manifest %s: %s", path.name, exc)
        return None, "manifest-invalid"
    if manifest.slug != slug:
        logger.warning("Manifest %s declares slug %s", path.name, manifest.slug)
        return None, "manifest-invalid"
    return manifest, None


def preview_path(frame: ManifestFrame, settings: Settings) -> Path | None:
    name = frame.preview_file
    if not name or "/" in name or "\\" in name or not name.lower().endswith(".png"):
        return None
    path = settings.previews_dir / name
    return path if path.is_file() else None


def build_example(slug: str, settings: Settings) -> ExampleResponse:
    manifest, warning = load_manifest(slug, settings)
    if manifest is None:
        return ExampleResponse(
            slug=slug, name=EXAMPLES[slug], queried_at=None, query=None, warnings=[warning]
        )

    observations = [
        Observation(
            id=frame.id,
            obs_id=frame.obs_id,
            mjd=frame.mjd,
            time_scale=frame.time_scale,
            iso_time=frame.iso_time,
            collection=manifest.collection,
            detector=frame.detector,
            band=frame.band,
            flags=frame.flags,
            preview_url=f"/v1/frames/{frame.id}" if preview_path(frame, settings) else None,
        )
        for frame in manifest.frames
    ]
    warnings = list(manifest.warnings)
    if not observations:
        warnings.append("no-observations")
    times = [o.mjd for o in observations if o.mjd is not None]
    if any(later < earlier for earlier, later in zip(times, times[1:], strict=False)):
        warnings.append("frames-not-chronological")

    return ExampleResponse(
        slug=slug,
        name=manifest.name,
        queried_at=manifest.queried_at,
        query=SkySearchQuery(
            ra_deg=manifest.ra_deg,
            dec_deg=manifest.dec_deg,
            radius_deg=manifest.radius_deg,
            collection=manifest.collection,
        ),
        coord_source=manifest.coord_source,
        comparable=manifest.comparable,
        comparison_note=manifest.comparison_note,
        warnings=warnings,
        observations=observations,
    )


def preview_index(collection: str, settings: Settings) -> dict[tuple[str, str], str]:
    """Map (obs_id, detector) to a cached frame id whose PNG exists, for live results."""
    index: dict[tuple[str, str], str] = {}
    for slug in EXAMPLES:
        manifest, _ = load_manifest(slug, settings)
        if manifest is None or manifest.collection != collection:
            continue
        for frame in manifest.frames:
            if frame.obs_id and frame.detector and preview_path(frame, settings):
                index.setdefault((frame.obs_id, frame.detector), frame.id)
    return index


def find_frame_preview(frame_id: str, settings: Settings) -> Path | None:
    for slug in EXAMPLES:
        manifest, _ = load_manifest(slug, settings)
        if manifest is None:
            continue
        for frame in manifest.frames:
            if frame.id == frame_id:
                return preview_path(frame, settings)
    return None
