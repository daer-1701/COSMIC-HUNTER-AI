from urllib.parse import parse_qs, urlparse

import pytest
from cosmic_api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
REGION = {"ra_deg": 127.69, "dec_deg": -39.17, "radius_deg": 0.01}


def test_query_plan_is_explicitly_not_executed():
    response = client.post("/v1/observations/query-plan", json=REGION)
    assert response.status_code == 200
    result = response.json()
    assert result["executed"] is False
    params = parse_qs(urlparse(result["url"]).query)
    assert params["COLLECTION"] == ["spherex_dr1"]
    assert params["POS"] == ["CIRCLE 127.69 -39.17 0.01"]


@pytest.mark.parametrize(
    "change",
    [
        {"ra_deg": 360},
        {"dec_deg": -91},
        {"radius_deg": 0},
        {"radius_deg": 1},
        {"collection": "spherex_qr2"},
        {"start_mjd": 60000},
        {"start_mjd": 61000, "end_mjd": 60000},
        {"extra": "unexpected"},
    ],
)
def test_invalid_scientific_queries_are_rejected(change):
    assert client.post("/v1/observations/query-plan", json=REGION | change).status_code == 422


def test_mjd_interval_and_boundary_coordinates():
    response = client.post(
        "/v1/observations/query-plan",
        json={
            "ra_deg": 0,
            "dec_deg": 90,
            "radius_deg": 0.5,
            "collection": "spherex_qr3",
            "start_mjd": 60000,
            "end_mjd": 60001,
        },
    )
    assert response.status_code == 200
    assert parse_qs(urlparse(response.json()["url"]).query)["TIME"] == ["60000.0 60001.0"]
