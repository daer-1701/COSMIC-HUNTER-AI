# Cosmic Hunter AI

Base de arquitectura para investigar movimiento aparente en observaciones SPHEREx.
Preparada a partir del brief del equipo, el 14 de noviembre de 2026.

**Estado: fase 1.** API mínima ejecutable y contratos probados. Todavía no hay
frontend funcional, descarga de FITS, detector, resultados científicos ni llamadas a Gemini.
No constituye una herramienta de descubrimiento validada.

## Inicio local

Requisitos: Git, Python 3.12 o 3.13 y [uv](https://docs.astral.sh/uv/).
Desde la raíz, en PowerShell:

```powershell
Copy-Item .env.example .env
uv sync --frozen
uv run uvicorn cosmic_api.main:app --reload
```

Documentación interactiva: http://localhost:8000/docs.
`POST /v1/observations/query-plan` construye una URL SIA2 de IRSA; no ejecuta la consulta.

```json
{"ra_deg":127.69,"dec_deg":-39.17,"radius_deg":0.01,"collection":"spherex_dr1"}
```

Verificación:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run python scripts/export_openapi.py
```

Docker Desktop con motor Linux: `docker compose up --build`. Incluye API,
PostgreSQL y Redis locales; la API de esta fase no utiliza aún la base ni la cola.
El SQL se aplica solo al crear el volumen PostgreSQL por primera vez.
No es una configuración de producción. S3 y workers se incorporarán con el pipeline.

## Repositorio

```text
apps/web/              Next.js previsto; contrato de integración
services/api/          FastAPI y validación HTTP
services/astronomy/    construcción de consultas IRSA; futuro FITS/WCS
services/detection/    límite reservado para baseline y asociación temporal
services/ai/           límite reservado para clasificación/copiloto
services/workers/      límite reservado para orquestación Celery
packages/shared/       OpenAPI generado, fuente del cliente TypeScript futuro
data/                 archivos locales ignorados; política de datos
notebooks/            experimentos reproducibles futuros
scripts/              exportación de contratos
tests/                contratos y límites de consultas
docs/                 arquitectura, ciencia, API y plan
infrastructure/       contenedores y esquema SQL inicial
```

Lee [arquitectura](docs/architecture.md), [modelo de datos](docs/data-model.md),
[contratos](docs/api.md), [fuentes y requisitos](docs/research.md),
[validación científica](docs/science.md) y [fases pendientes](docs/roadmap.md).
La separación de carpetas no implica que todos los motores estén implementados.

## Trabajar con Codex y Cursor

Las instrucciones compartidas están en [AGENTS.md](AGENTS.md). Hay cinco skills
del repositorio en `.agents/skills/` y reglas por módulo en `.cursor/rules/`.
Lee la [guía de skills y coordinación](docs/agent-tooling.md) para activarlas y
repartir trabajo entre ambos editores sin sobrescribir cambios.

## Subir a Git

El repositorio local se inicializa en `main`; no se configura un remoto sin una URL.
Revisa `git status` y sigue [la guía de publicación](docs/git.md).
No se incluyen credenciales, FITS ni modelos. La licencia de distribución sigue
pendiente de decisión del equipo; no asumir permiso de reutilización del código.
