import json
import threading
from dataclasses import replace
from types import SimpleNamespace

import httpx
import pytest
from cosmic_ai.budget import BudgetExceeded, BudgetLedger
from cosmic_ai.summary import build_evidence, validate_summary
from cosmic_api import summaries
from cosmic_api.main import app, get_gemini_client_factory
from cosmic_api.settings import Settings, get_settings
from fastapi.testclient import TestClient
from google.genai import errors

GOOD_TEXT = (
    "WISE 0855 was observed by SPHEREx detector D1 at two epochs [E1] [E5] [E6]. "
    "This is a cached example [E2]; any change is apparent only [E3]."
)
USAGE = SimpleNamespace(prompt_token_count=500, candidates_token_count=80, thoughts_token_count=20)
EXPECTED_COST = (500 * 0.30 + 100 * 2.50) / 1_000_000


def frame(frame_id, mjd):
    return {
        "id": frame_id,
        "obs_id": f"obs-{frame_id}",
        "mjd": mjd,
        "time_scale": None,
        "iso_time": None,
        "detector": "D1",
        "band": None,
        "hdu": None,
        "flags": [],
        "preview_file": None,
        "sha256": None,
    }


def write_manifest(settings, slug="wise-0855", name="WISE 0855"):
    manifest = {
        "slug": slug,
        "name": name,
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
        "frames": [frame(f"{slug}-1", 60800.0), frame(f"{slug}-2", 60990.0)],
    }
    (settings.manifests_dir / f"{slug}.json").write_text(json.dumps(manifest), "utf-8")


class FakeGemini:
    """Stands in for google.genai.Client; never touches the network or spends money."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls: list[dict] = []
        self.models = self

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def reply(text=GOOD_TEXT, usage=USAGE):
    return SimpleNamespace(text=text, usage_metadata=usage)


@pytest.fixture
def settings(tmp_path):
    value = Settings(
        manifests_dir=tmp_path / "manifests",
        previews_dir=tmp_path / "previews",
        cors_origins=("http://localhost:3000",),
        gemini_enabled=True,
        gemini_api_key="test-key-not-real",
        gemini_model="gemini-3.5-flash-lite",
        gemini_budget_usd=4.0,
        gemini_input_usd_per_mtok=0.30,
        gemini_output_usd_per_mtok=2.50,
        state_dir=tmp_path / "state",
    )
    value.manifests_dir.mkdir()
    value.previews_dir.mkdir()
    summaries.summary_cache.clear()
    summaries.rate_limiter = summaries.RateLimiter()
    yield value
    app.dependency_overrides.clear()


def summarize(settings, gemini, slug="wise-0855"):
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_gemini_client_factory] = lambda: lambda _settings: gemini
    return TestClient(app).post(f"/v1/examples/{slug}/summary")


def ledger_file(settings):
    return json.loads((settings.state_dir / "gemini_budget.json").read_text("utf-8"))


def test_summary_cites_evidence_and_charges_real_usage(settings):
    write_manifest(settings)
    gemini = FakeGemini(reply())

    response = summarize(settings, gemini)

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == GOOD_TEXT
    assert body["cited"] == ["E1", "E2", "E3", "E5", "E6"]
    assert body["cached"] is False
    assert body["model"] == "gemini-3.5-flash-lite"
    assert "does not confirm" in body["disclaimer"]
    assert body["evidence"][0]["id"] == "E1"
    assert "WISE 0855" in body["evidence"][0]["text"]
    assert body["usage"]["cost_usd"] == pytest.approx(EXPECTED_COST)
    assert body["usage"]["budget_remaining_usd"] == pytest.approx(4.0 - EXPECTED_COST)
    assert ledger_file(settings)["spent_usd"] == pytest.approx(EXPECTED_COST)
    assert ledger_file(settings)["reservations"] == {}
    call = gemini.calls[0]
    assert call["model"] == "gemini-3.5-flash-lite"
    assert "[E5] Observation obs-wise-0855-1" in call["contents"]
    assert "test-key-not-real" not in response.text


def test_repeated_summary_is_served_from_cache_without_a_second_call(settings):
    write_manifest(settings)
    gemini = FakeGemini(reply())
    summarize(settings, gemini)
    again = summarize(settings, gemini)
    assert again.status_code == 200
    assert again.json()["cached"] is True
    assert len(gemini.calls) == 1


@pytest.mark.parametrize(
    "change, detail",
    [
        ({"gemini_enabled": False}, "disabled"),
        ({"gemini_api_key": ""}, "GEMINI_API_KEY"),
        ({"gemini_model": ""}, "GEMINI_MODEL"),
        ({"gemini_output_usd_per_mtok": 0.0}, "prices"),
        ({"gemini_budget_usd": 0.0}, "GEMINI_BUDGET_USD"),
    ],
)
def test_incomplete_configuration_is_503_without_a_call(settings, change, detail):
    write_manifest(settings)
    gemini = FakeGemini()
    response = summarize(replace(settings, **change), gemini)
    assert response.status_code == 503
    assert detail in response.json()["detail"]
    assert gemini.calls == []


def test_target_without_manifest_is_409(settings):
    response = summarize(settings, FakeGemini())
    assert response.status_code == 409


def test_unknown_target_is_404(settings):
    assert summarize(settings, FakeGemini(), slug="planet-x").status_code == 404


def test_exhausted_budget_is_429_without_a_call(settings):
    write_manifest(settings)
    gemini = FakeGemini(reply())
    response = summarize(replace(settings, gemini_budget_usd=0.000001), gemini)
    assert response.status_code == 429
    assert "budget exhausted" in response.json()["detail"]
    assert gemini.calls == []


@pytest.mark.parametrize(
    "text, problem",
    [
        ("WISE 0855 was observed twice.", "no evidence citations"),
        ("Observed twice [E1] [E99].", "unknown citations E99"),
        ("This is a new planet [E1].", "forbidden phrase 'new planet'"),
    ],
)
def test_unsupported_output_is_rejected_but_still_charged(settings, text, problem):
    write_manifest(settings)
    response = summarize(settings, FakeGemini(reply(text)))
    assert response.status_code == 502
    assert problem in response.json()["detail"]
    assert ledger_file(settings)["spent_usd"] == pytest.approx(EXPECTED_COST)


def test_provider_rejection_releases_the_reservation(settings):
    write_manifest(settings)
    rejected = errors.ClientError(400, {"error": {"code": 400, "message": "API key not valid"}})
    response = summarize(settings, FakeGemini(rejected))
    assert response.status_code == 502
    assert response.json()["detail"] == "Gemini rejected the request (HTTP 400)"
    assert ledger_file(settings) == {"spent_usd": 0.0, "reservations": {}, "calls": 0}


def test_unknown_provider_outcome_charges_the_reserved_maximum(settings):
    write_manifest(settings)
    response = summarize(settings, FakeGemini(ConnectionResetError("lost")))
    assert response.status_code == 502
    state = ledger_file(settings)
    assert state["reservations"] == {}
    assert state["spent_usd"] > EXPECTED_COST


def test_provider_timeout_is_504(settings):
    write_manifest(settings)
    response = summarize(settings, FakeGemini(httpx.ReadTimeout("slow")))
    assert response.status_code == 504


def test_rate_limit_is_429_with_retry_after(settings):
    write_manifest(settings)
    write_manifest(settings, slug="r-draconis", name="R Draconis")
    limited = replace(settings, gemini_max_calls_per_minute=1)
    gemini = FakeGemini(reply(), reply())
    assert summarize(limited, gemini).status_code == 200
    second = summarize(limited, gemini, slug="r-draconis")
    assert second.status_code == 429
    assert int(second.headers["Retry-After"]) >= 1
    assert len(gemini.calls) == 1


def test_ledger_reservations_never_exceed_the_limit_under_concurrency(tmp_path):
    ledger = BudgetLedger(tmp_path / "budget.json", limit_usd=4.0)
    granted = []

    def reserve():
        try:
            granted.append(ledger.reserve(0.3))
        except BudgetExceeded:
            pass

    threads = [threading.Thread(target=reserve) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(granted) == 13
    assert ledger.state().reserved_usd == pytest.approx(3.9)
    ledger.settle(granted[0], 0.1)
    assert ledger.state().spent_usd == pytest.approx(0.1)
    assert ledger.state().remaining_usd == pytest.approx(4.0 - 0.1 - 0.3 * 12)


def test_evidence_marks_cache_and_unverified_time_scale():
    example = {
        "slug": "wise-0855",
        "name": "WISE 0855",
        "query": {"ra_deg": 1, "dec_deg": 2, "radius_deg": 0.02, "collection": "spherex_dr1"},
        "queried_at": None,
        "comparable": False,
        "comparison_note": None,
        "warnings": ["manifest-not-ready"],
        "observations": [{"obs_id": "a", "detector": "D1", "mjd": 1.0, "time_scale": None}],
    }
    lines = dict(build_evidence(example))
    assert "not a live query" in lines["E2"]
    assert "unverified time scale" in lines["E5"]
    assert validate_summary("Fine [E1].", set(lines)) == []
