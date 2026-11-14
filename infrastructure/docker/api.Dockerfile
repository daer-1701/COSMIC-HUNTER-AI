FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
COPY services ./services
RUN uv sync --frozen --no-dev
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "cosmic_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
