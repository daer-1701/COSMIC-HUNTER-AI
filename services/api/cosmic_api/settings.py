import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    manifests_dir: Path
    previews_dir: Path
    cors_origins: tuple[str, ...]


def get_settings() -> Settings:
    origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    return Settings(
        manifests_dir=Path(os.environ.get("MANIFESTS_DIR", REPO_ROOT / "data" / "manifests")),
        previews_dir=Path(
            os.environ.get("PREVIEWS_DIR", REPO_ROOT / "apps" / "web" / "public" / "previews")
        ),
        # A wildcard origin is never honoured; the browser client is an explicit list.
        cors_origins=tuple(o.strip() for o in origins if o.strip() and o.strip() != "*"),
    )
