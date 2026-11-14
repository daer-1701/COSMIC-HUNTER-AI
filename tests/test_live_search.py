import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from cosmic_api.live_search import fetch_votable, parse_votable
from cosmic_api.main import app, get_archive_transport
from cosmic_api.settings import Settings, get_settings
from fastapi.testclient import TestClient

FIXTURE = (Path(__file__).parent / "fixtures" / "irsa_sia_spherex_dr1_wise0855.xml").read_bytes()
VOTABLE = {"content-type": "application/x-votable+xml"}
SEARCH = {"ra_deg": 133.795129, "dec_deg": -7.245147, "radius_deg": 0.02}
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def votable(status="OK", message="", rows=""):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<VOTABLE version="1.3" xmlns="http://www.ivoa.net/xml/VOTable/v1.3">
  <RESOURCE type="results">
    <INFO name="QUERY_STATUS" value="{status}">{message}</INFO>
    <TABLE>
      <FIELD name="obs_id" datatype="char" arraysize="*"/>
      <FIELD name="obs_publisher_did" datatype="char" arraysize="*"/>
      <FIELD name="obs_collection" datatype="char" arraysize="*"/>
      <FIELD name="t_min" datatype="double" unit="d"/>
      <FIELD name="energy_bandpassname" datatype="char" arraysize="*"/>
      <DATA><TABLEDATA>{rows}</TABLEDATA></DATA>
    </TABLE>
  </RESOURCE>
</VOTABLE>""".encode()


class Archive:
    """Scripted IRSA stand-in; records every request so tests can assert on them."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture
def workspace(tmp_path):
    settings = Settings(
        manifests_dir=tmp_path / "manifests",
        previews_dir=tmp_path / "previews",
        cors_origins=("http://localhost:3000",),
        irsa_timeout_seconds=5,
    )
    settings.manifests_dir.mkdir()
    settings.previews_dir.mkdir()
    app.dependency_overrides[get_settings] = lambda: settings
    yield settings
    app.dependency_overrides.clear()


def search_with(*responses, body=None):
    archive = Archive(*responses)
    app.dependency_overrides[get_archive_transport] = lambda: httpx.MockTransport(archive)
    response = TestClient(app).post("/v1/sky/search", json=body or SEARCH)
    return response, archive


def assert_error(response, status_code):
    assert response.status_code == status_code
    body = response.json()
    assert isinstance(body["detail"], str) and body["detail"]
    assert body["request_id"] == response.headers["X-Request-ID"]
    return body["detail"]


def test_live_search_parses_real_irsa_rows_in_time_order(workspace):
    response, archive = search_with(httpx.Response(200, headers=VOTABLE, content=FIXTURE))

    assert response.status_code == 200
    body = response.json()
    request_url = urlsplit(str(archive.requests[0].url))
    assert (request_url.scheme, request_url.hostname, request_url.path) == (
        "https",
        "irsa.ipac.caltech.edu",
        "/SIA",
    )
    assert parse_qs(request_url.query)["POS"] == ["CIRCLE 133.795129 -7.245147 0.02"]
    assert body["source"] == "live"
    assert body["queried_at"].endswith("-04:00")
    assert body["query"] == SEARCH | {"collection": "spherex_dr1"}

    observations = body["observations"]
    assert [(o["obs_id"], o["detector"], o["mjd"]) for o in observations] == [
        ("2025W19_1B_0116_1", "SPHEREx-D3", 60800.700028),
        ("2025W19_1B_0116_1", "SPHEREx-D6", 60800.700028),
        ("2025W46_2A_0214_4", "SPHEREx-D3", 60993.509586),
        ("2026W20_1A_1166_1", "SPHEREx-D2", 61174.287218),
    ]
    first = observations[0]
    assert first["id"] == "2025W19_1B_0116_1-SPHEREx-D3"
    assert first["time_scale"] is None
    assert first["iso_time"] == "2025-05-05T16:48:02"
    assert first["band"] is None
    assert first["preview_url"] is None
    assert all("access_url" not in o for o in observations)
    assert "irsa.ipac.caltech.edu/ibe" not in response.text
    assert body["warnings"] == ["duplicate-rows-removed", "time-scale-unverified"]


def test_live_row_links_to_cached_png_with_same_obs_id_and_detector(workspace):
    (workspace.previews_dir / "wise-0855-1.png").write_bytes(PNG)
    manifest = {
        "slug": "wise-0855",
        "name": "WISE 0855",
        "ra_deg": 133.795129,
        "dec_deg": -7.245147,
        "coord_source": None,
        "coord_epoch": None,
        "collection": "spherex_dr1",
        "radius_deg": 0.02,
        "queried_at": None,
        "comparable": False,
        "comparison_note": None,
        "frames": [
            {
                "id": "wise-0855-1",
                "obs_id": "2025W46_2A_0214_4",
                "mjd": 60993.509586,
                "time_scale": None,
                "iso_time": None,
                "detector": "SPHEREx-D3",
                "band": None,
                "hdu": None,
                "flags": [],
                "preview_file": "wise-0855-1.png",
                "sha256": None,
            }
        ],
    }
    (workspace.manifests_dir / "wise-0855.json").write_text(json.dumps(manifest), "utf-8")

    response, _ = search_with(httpx.Response(200, headers=VOTABLE, content=FIXTURE))

    previews = {o["obs_id"]: o["preview_url"] for o in response.json()["observations"]}
    assert previews["2025W46_2A_0214_4"] == "/v1/frames/wise-0855-1"
    assert previews["2026W20_1A_1166_1"] is None


def test_empty_result_is_200_with_warning(workspace):
    response, _ = search_with(httpx.Response(200, headers=VOTABLE, content=votable()))
    assert response.status_code == 200
    assert response.json()["observations"] == []
    assert response.json()["warnings"] == ["no-observations"]


def test_overflow_is_flagged_as_truncated(workspace):
    row = "<TR><TD>a</TD><TD>did-a</TD><TD>spherex_dr1</TD><TD>60800.5</TD><TD>D1</TD></TR>"
    content = votable(status="OVERFLOW", rows=row)
    response, _ = search_with(httpx.Response(200, headers=VOTABLE, content=content))
    assert response.status_code == 200
    assert "results-truncated" in response.json()["warnings"]


def test_network_failure_is_retried_once(workspace):
    response, archive = search_with(
        httpx.ConnectError("connection reset"),
        httpx.Response(200, headers=VOTABLE, content=FIXTURE),
    )
    assert response.status_code == 200
    assert len(archive.requests) == 2


def test_repeated_network_failure_is_502(workspace):
    response, archive = search_with(httpx.ConnectError("down"), httpx.ConnectError("down"))
    assert assert_error(response, 502) == "Could not reach IRSA"
    assert len(archive.requests) == 2


def test_timeout_is_504_without_retry(workspace):
    response, archive = search_with(httpx.ReadTimeout("slow"))
    assert "did not respond" in assert_error(response, 504)
    assert len(archive.requests) == 1


def test_html_error_page_is_502_and_not_forwarded(workspace):
    page = "<html><body><h1>Internal Server Error</h1></body></html>"
    response, _ = search_with(
        httpx.Response(500, headers={"content-type": "text/html"}, content=page)
    )
    assert assert_error(response, 502) == "IRSA returned HTTP 500"
    assert "<html" not in response.text


def test_non_votable_success_is_502(workspace):
    response, _ = search_with(
        httpx.Response(200, headers={"content-type": "text/html"}, content="<html></html>")
    )
    assert assert_error(response, 502) == "IRSA returned a response that is not a VOTable"


def test_redirect_is_not_followed(workspace):
    response, archive = search_with(
        httpx.Response(302, headers={"location": "https://evil.test/SIA"}),
    )
    assert assert_error(response, 502) == "IRSA returned HTTP 302"
    assert len(archive.requests) == 1


def test_query_error_status_is_502(workspace):
    content = votable(status="ERROR", message="Collection unavailable")
    response, _ = search_with(httpx.Response(200, headers=VOTABLE, content=content))
    assert assert_error(response, 502) == "IRSA query error: Collection unavailable"


def test_truncated_xml_is_502(workspace):
    response, _ = search_with(httpx.Response(200, headers=VOTABLE, content=FIXTURE[:4000]))
    assert assert_error(response, 502) == "IRSA returned a malformed VOTable"


def test_failed_search_leaves_cached_examples_available(workspace):
    search_with(httpx.ConnectError("down"), httpx.ConnectError("down"))
    response = TestClient(app).get("/v1/examples/wise-0855")
    assert response.status_code == 200
    assert response.json()["source"] == "cache"


def test_client_cannot_supply_an_archive_url(workspace):
    body = SEARCH | {"url": "https://evil.test/SIA"}
    response, archive = search_with(body=body)
    assert_error(response, 422)
    assert archive.requests == []


@pytest.mark.parametrize(
    "url",
    [
        "http://irsa.ipac.caltech.edu/SIA?COLLECTION=spherex_dr1",
        "https://evil.test/SIA",
        "https://irsa.ipac.caltech.edu.evil.test/SIA",
    ],
)
def test_fetch_rejects_anything_but_https_irsa(url):
    def fail(request):
        raise AssertionError("no request may be sent")

    with pytest.raises(ValueError):
        fetch_votable(url, 5, httpx.MockTransport(fail))


def test_binary_serialization_is_rejected():
    content = votable().replace(b"<TABLEDATA></TABLEDATA>", b"<BINARY/>")
    with pytest.raises(Exception, match="Unsupported VOTable serialization"):
        parse_votable(content)
