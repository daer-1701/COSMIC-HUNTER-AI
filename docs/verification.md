# Verificación de la base

Fecha: 2026-11-14. Windows / Python 3.13.0 / uv 0.12.3.

- `uv lock` y `uv sync --frozen`: completados; lockfile incluido.
- `uv run pytest -q`: 14 pruebas aprobadas de validación de consultas y contratos.
- `uv run ruff check .` y `uv run ruff format --check .`: aprobados.
- Exportación OpenAPI: completada. El contrato no contiene rutas futuras ficticias.
- `docker compose --env-file .env.example config --quiet`: aprobado.
- `.env`, FITS locales y `.venv` quedan excluidos por Git.

Aviso del entorno de pruebas: Starlette advierte que su uso de httpx está deprecado
en favor de httpx2. No afecta estas pruebas; revisar compatibilidad al actualizar el
cliente de pruebas.

No verificado: build/arranque Docker ni ejecución SQL, porque el daemon de Docker
Desktop no estaba disponible. El esquema requiere ejecutar el bootstrap en PostgreSQL
y validar restricciones antes de integrar persistencia. La CI incluye build del API,
pero no ha corrido en GitHub porque todavía no hay remoto.

No se probaron IRSA en vivo, FITS, detección, Gemini, frontend ni colas: no están
implementados. Las pruebas actuales validan la base arquitectónica, no exactitud
científica ni desempeño de la plataforma final.
