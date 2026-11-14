"""Run with uv run python scripts/export_openapi.py."""

import json
from pathlib import Path

from cosmic_api.main import app

target = Path(__file__).resolve().parents[1] / "packages/shared/openapi.json"
target.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
