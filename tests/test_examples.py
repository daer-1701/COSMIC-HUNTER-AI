import json

import pytest
from cosmic_api.catalog import EXAMPLES
from cosmic_api.main import app
from cosmic_api.settings import Settings, get_settings
from fastapi.testclient import TestClient

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
SEARCH = {"ra_deg": 133.795129, "dec_deg": -7.245147, "radius_deg": 0.02}


def frame(frame_id, mjd, preview_file=None, **extra):
    return {
        "id": frame_id,
        "obs_id": f"obs-{frame_id}",
        "mjd": mjd,
        "time_scale": "TDB",
        "iso_time": None,
        "detector": "D1",
        "band": None,
        "hdu": 1,
        "flags": [],
        "preview_file": preview_file,
        "sha256": None,
        **extra,
    }


def manifest(frames, **extra):
    return {
        "slug": "wise-0855",
        "name": "WISE 0855",
        "ra_deg": 133.795129,
        "dec_deg": -7.245147,
        "coord_source": "NASA Space Apps challenge statement",
        "coord_epoch": None,
        "collection": "spherex_dr1",
        "radius_deg": 0.02,
        "queried_at": "2026-11-14T16:00:00-04:00",
        "comparable": True,
        "comparison_note": "Same detector and collection.",
        "warnings": [],
        "frames": frames,
        **extra,
    }


@pytest.fixture
def workspace(tmp_path):
    settings = Settings(
        manifests_dir=tmp_path / "manifests",
        previews_dir=tmp_path / "previews",
        cors_origins=("http://localhost:3000",),
    )
    settings.manifests_dir.mkdir()
    settings.previews_dir.mkdir()
    app.dependency_overrides[get_settings] = lambda: settings
    yield settings
    app.dependency_overrides.clear()


@pytest.fixture
def client(workspace):
    return TestClient(app)


def write_manifest(settings, data, slug="wise-0855"):
    (settings.manifests_dir / f"{slug}.json").write_text(json.dumps(data), encoding="utf-8")


def assert_error(response, status_code):
    assert response.status_code == status_code
    body = response.json()
    assert isinstance(body["detail"], str) and body["detail"]
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_examples_without_manifests_are_marked_not_ready(client):
    response = client.get("/v1/examples")
    assert response.status_code == 200
    examples = response.json()
    assert [e["slug"] for e in examples] == list(EXAMPLES)
    for example in examples:
        assert example["source"] == "cache"
        assert example["observations"] == []
        assert example["query"] is None
        assert example["warnings"] == ["manifest-not-ready"]


def test_cached_manifest_returns_observations_in_time_order(client, workspace):
    (workspace.previews_dir / "wise-0855-1.png").write_bytes(PNG)
    write_manifest(
        workspace,
        manifest([frame("wise-0855-1", 60800.0, "wise-0855-1.png"), frame("wise-0855-2", 60990.5)]),
    )

    body = client.get("/v1/examples/wise-0855").json()

    assert body["source"] == "cache"
    assert body["queried_at"] == "2026-11-14T16:00:00-04:00"
    assert body["query"] == SEARCH | {"collection": "spherex_dr1"}
    assert body["comparable"] is True
    assert body["warnings"] == []
    assert [o["mjd"] for o in body["observations"]] == [60800.0, 60990.5]
    first, second = body["observations"]
    assert first["obs_id"] == "obs-wise-0855-1"
    assert first["preview_url"] == "/v1/frames/wise-0855-1"
    assert second["preview_url"] is None
    assert "access_url" not in first


def test_out_of_order_manifest_is_flagged_not_reordered(client, workspace):
    write_manifest(workspace, manifest([frame("b", 60990.0), frame("a", 60800.0)]))
    body = client.get("/v1/examples/wise-0855").json()
    assert [o["id"] for o in body["observations"]] == ["b", "a"]
    assert "frames-not-chronological" in body["warnings"]


@pytest.mark.parametrize(
    "data",
    [
        manifest([frame("a", 60800.0, access_url="https://example.org")]),
        manifest([], slug="r-draconis"),
        "{not json",
    ],
)
def test_invalid_manifest_is_reported_not_served(client, workspace, data):
    if isinstance(data, str):
        (workspace.manifests_dir / "wise-0855.json").write_text(data, encoding="utf-8")
    else:
        write_manifest(workspace, data)
    body = client.get("/v1/examples/wise-0855").json()
    assert body["observations"] == []
    assert body["warnings"] == ["manifest-invalid"]


def test_empty_manifest_warns(client, workspace):
    write_manifest(workspace, manifest([], comparable=False))
    body = client.get("/v1/examples/wise-0855").json()
    assert body["observations"] == []
    assert body["warnings"] == ["no-observations"]


def test_unknown_example_is_404(client):
    assert_error(client.get("/v1/examples/planet-x"), 404)


def test_frame_is_served_as_png(client, workspace):
    (workspace.previews_dir / "wise-0855-1.png").write_bytes(PNG)
    write_manifest(workspace, manifest([frame("wise-0855-1", 60800.0, "wise-0855-1.png")]))
    response = client.get("/v1/frames/wise-0855-1")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == PNG


@pytest.mark.parametrize("preview_file", [None, "missing.png", "../secret.png", "notes.txt"])
def test_frame_without_servable_png_is_404(client, workspace, preview_file):
    (workspace.manifests_dir.parent / "secret.png").write_bytes(PNG)
    (workspace.previews_dir / "notes.txt").write_text("not an image", encoding="utf-8")
    write_manifest(workspace, manifest([frame("wise-0855-1", 60800.0, preview_file)]))
    assert_error(client.get("/v1/frames/wise-0855-1"), 404)


def test_unknown_frame_is_404(client):
    assert_error(client.get("/v1/frames/nope"), 404)


@pytest.mark.parametrize(
    "change",
    [
        {"ra_deg": 360},
        {"dec_deg": -91},
        {"radius_deg": 0},
        {"radius_deg": 0.6},
        {"collection": "spherex_qr2"},
        {"url": "https://irsa.ipac.caltech.edu/SIA"},
        {"start_mjd": 60000},
    ],
)
def test_sky_search_rejects_invalid_requests(client, change):
    assert_error(client.post("/v1/sky/search", json=SEARCH | change), 422)


def test_cors_allows_only_the_web_origin(client):
    preflight = {"Access-Control-Request-Method": "POST"}
    allowed = client.options(
        "/v1/sky/search", headers=preflight | {"Origin": "http://localhost:3000"}
    )
    denied = client.options("/v1/sky/search", headers=preflight | {"Origin": "https://evil.test"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-origin" not in denied.headers
