# Foundation verification

Initial verification date: 2026-11-14. Windows / Python 3.13.0 / uv 0.12.3.
This records the initial setup checks, not the current state of external services.

- `uv lock` and `uv sync --frozen`: completed; lockfile included.
- `uv run pytest -q`: 14 passing query-validation and contract tests.
- `uv run ruff check .` and `uv run ruff format --check .`: passed.
- OpenAPI export: completed. The contract does not contain fictional future routes.
- `docker compose --env-file .env.example config --quiet`: passed.
- `.env`, local FITS files, and `.venv` are excluded from Git.

Test environment warning: Starlette deprecates its use of httpx in favor of httpx2.
This does not affect these tests; review compatibility when updating the test client.

Not verified during initial setup: Docker build/startup or SQL execution, because the
Docker Desktop daemon was unavailable. Run the bootstrap in PostgreSQL and validate
constraints before integrating persistence. CI includes the API image build; its
remote run was not verified during initial setup, when no remote was configured.

Live IRSA, FITS processing, detection, Gemini, frontend, and queues were not tested:
they are not implemented. Current tests validate the architecture foundation, not
scientific accuracy or final platform performance.
