"""Exercise the published science handoff through HTTP without paid calls."""

import hashlib
import json
from pathlib import Path

import httpx
import pytest
from cosmic_ai.summary import build_evidence
from cosmic_api.main import app, get_archive_transport
from cosmic_api.settings import Settings, get_settings
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def published_client():
    settings = Settings(
        manifests_dir=ROOT / "data/manifests",
        previews_dir=ROOT / "apps/web/public/previews",
        cors_origins=("http://localhost:3000",),
    )
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


def test_published_pair_is_served_with_provenance_and_verified_pngs(published_client):
    manifest = json.loads((ROOT / "data/manifests/wise-0855.json").read_text())
    response = published_client.get("/v1/examples/wise-0855?detector=SPHEREx-D2")
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "cache"
    assert body["comparable"] is True
    assert body["coord_epoch"] == manifest["coord_epoch"]
    assert body["comparison_note"] == manifest["comparison_note"]
    assert len(body["observations"]) == 2
    for observation, frame in zip(body["observations"], manifest["frames"], strict=True):
        for key in ("obs_id", "mjd", "time_scale", "iso_time", "hdu", "sha256"):
            assert observation[key] == frame[key]
        preview = published_client.get(observation["preview_url"])
        assert preview.status_code == 200
        assert preview.headers["content-type"] == "image/png"
        expected = next(
            f.split(":", 1)[1] for f in frame["flags"] if f.startswith("preview-sha256:")
        )
        assert hashlib.sha256(preview.content).hexdigest() == expected
    evidence = " ".join(text for _, text in build_evidence(body))
    assert "Target motion and flux changes were not measured" in evidence
    assert "UTC" in evidence
    unavailable = published_client.get("/v1/examples/barnards-star").json()
    assert "manifest-not-ready" in unavailable["warnings"]
    assert published_client.post("/v1/examples/wise-0855/summary").status_code == 503


def test_archive_results_link_to_published_previews(published_client):
    # Synthetic provider response using the published IDs; no live archive claim.
    from test_live_search import votable

    manifest = json.loads((ROOT / "data/manifests/wise-0855.json").read_text())
    rows = "".join(
        f"<TR><TD>{f['obs_id']}</TD><TD>{f['id']}</TD>"
        f"<TD>{manifest['collection']}</TD><TD>{f['mjd']}</TD>"
        f"<TD>{f['detector']}</TD></TR>"
        for f in manifest["frames"]
    )
    fixture = votable(rows=rows)
    app.dependency_overrides[get_archive_transport] = lambda: httpx.MockTransport(
        lambda request: httpx.Response(
            200, content=fixture, headers={"content-type": "application/x-votable+xml"}
        )
    )
    response = published_client.post(
        "/v1/sky/search",
        json={"ra_deg": 133.795129, "dec_deg": -7.245147, "radius_deg": 0.02},
    )
    assert response.status_code == 200
    previews = [o["preview_url"] for o in response.json()["observations"] if o["preview_url"]]
    assert "/v1/frames/wise-0855-1" in previews
    assert "/v1/frames/wise-0855-2" in previews
    assert all(published_client.get(url).status_code == 200 for url in previews)
