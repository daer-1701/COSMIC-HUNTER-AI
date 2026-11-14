# Contratos HTTP

Fuente ejecutable: modelos Pydantic y OpenAPI exportado a
`packages/shared/openapi.json`. `/docs` y `/openapi.json` disponibles al arrancar.

## Implementado

| Método / ruta | Resultado |
| --- | --- |
| GET /health/live | 200: proceso vivo; no indica preparación de SQL/IRSA |
| POST /v1/observations/query-plan | 200: URL IRSA, executed=false; 422: entrada inválida |

Coordenadas ICRS en grados: 0 ≤ RA < 360, −90 ≤ Dec ≤ 90; radio (0, 0.5].
Colección DR1 o QR3. Tiempo opcional: ambos límites MJD, escala que exige SIA2;
confirmar semántica del archivo al importar. No se aceptan campos extra o no finitos.
No se ejecutan consultas externas ni se guarda evidencia con este endpoint.

## Diseñado, pendiente de implementar

| Ruta prevista | Contrato previsto |
| --- | --- |
| POST /v1/observation-searches | 202 + job_id y Location; búsqueda acotada asíncrona |
| GET /v1/observations | cursor opaco + limit ≤ 100; filtros región/época/colección |
| POST /v1/jobs | JWT + Idempotency-Key; entradas por IDs persistidos; 202 |
| GET /v1/jobs/{id} | estado persistido, progreso, errores por etapa |
| GET /v1/candidates | filtros y paginación por cursor |
| GET /v1/candidates/{id} | detecciones, errores, movimiento, procedencia, revisión |
| GET /v1/candidates/{id}/evidence | manifiesto versionado + enlaces temporales |
| POST /v1/candidates/{id}/reviews | JWT reviewer; 201 o 409 si ya existe |
| POST /v1/candidates/{id}/summary | JWT + límite presupuesto; evidencia obligatoria |

Antes de implementar: especificar cuerpos y errores en OpenAPI, generar cliente TS.
Errores previstos con request_id: 401/403 autorización, 404 ausente, 409 conflicto,
422 validación, 429 cuota, 502/503 proveedor; Retry-After cuando aplique.
Reutilizar Idempotency-Key con cuerpo distinto debe devolver 409.
