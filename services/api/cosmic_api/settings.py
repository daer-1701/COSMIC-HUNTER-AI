import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]

# Shell variables win over .env; a missing .env is fine.
load_dotenv(REPO_ROOT / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    manifests_dir: Path
    previews_dir: Path
    cors_origins: tuple[str, ...]
    irsa_timeout_seconds: float = 25.0
    gemini_enabled: bool = False
    gemini_api_key: str = ""
    gemini_model: str = ""
    gemini_budget_usd: float = 0.0
    gemini_input_usd_per_mtok: float = 0.0
    gemini_output_usd_per_mtok: float = 0.0
    gemini_max_output_tokens: int = 1024
    gemini_timeout_seconds: float = 30.0
    gemini_max_calls_per_minute: int = 10
    state_dir: Path = REPO_ROOT / "data" / "state"


def _float(name: str, default: str) -> float:
    return float(os.environ.get(name) or default)


def get_settings() -> Settings:
    origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    return Settings(
        manifests_dir=Path(os.environ.get("MANIFESTS_DIR", REPO_ROOT / "data" / "manifests")),
        previews_dir=Path(
            os.environ.get("PREVIEWS_DIR", REPO_ROOT / "apps" / "web" / "public" / "previews")
        ),
        # A wildcard origin is never honoured; the browser client is an explicit list.
        cors_origins=tuple(o.strip() for o in origins if o.strip() and o.strip() != "*"),
        irsa_timeout_seconds=_float("IRSA_TIMEOUT_SECONDS", "25"),
        gemini_enabled=os.environ.get("GEMINI_ENABLED", "false").strip().lower() == "true",
        gemini_api_key=os.environ.get("GEMINI_API_KEY", "").strip(),
        gemini_model=os.environ.get("GEMINI_MODEL", "").strip(),
        gemini_budget_usd=_float("GEMINI_BUDGET_USD", "0"),
        gemini_input_usd_per_mtok=_float("GEMINI_INPUT_USD_PER_MTOK", "0"),
        gemini_output_usd_per_mtok=_float("GEMINI_OUTPUT_USD_PER_MTOK", "0"),
        gemini_max_output_tokens=int(_float("GEMINI_MAX_OUTPUT_TOKENS", "1024")),
        gemini_timeout_seconds=_float("GEMINI_TIMEOUT_SECONDS", "30"),
        gemini_max_calls_per_minute=int(_float("GEMINI_MAX_CALLS_PER_MINUTE", "10")),
        state_dir=Path(os.environ.get("STATE_DIR", REPO_ROOT / "data" / "state")),
    )
