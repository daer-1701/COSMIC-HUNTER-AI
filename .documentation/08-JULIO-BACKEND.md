# Julio — backend

Tu resultado del domingo: una API que busca en IRSA, devuelve observaciones con fechas y sirve PNG, y que sigue respondiendo los cinco ejemplos cuando IRSA está caído. Eduardo programa contra el contrato de [06-PLAN-EQUIPO.md](06-PLAN-EQUIPO.md) desde el sábado al mediodía. Tú no cambias esos campos sin un mensaje previo a los dos.

Lo que ya existe y no hay que romper:

- `GET /health/live`
- `POST /v1/observations/query-plan`, que arma la URL y responde `executed: false`

Ese endpoint se queda. La búsqueda de verdad es otra ruta, para no mentir en la que ya dice que no consulta el archivo.

## Qué es solo tuyo

- `services/api/cosmic_api/`
- `tests/`
- `packages/shared/openapi.json`, solo regenerado con `uv run python scripts/export_openapi.py`
- `README.md` y `.env.example` cuando cambie el arranque
- CORS y el tiempo máximo de la llamada a IRSA

No edites el notebook de Mateo ni los componentes de Eduardo. Si falta un dato científico, el campo va en `null` con una advertencia. No completes tú el detector mirando un blog.

## Arranque

```powershell
Copy-Item .env.example .env
uv sync --frozen
uv run uvicorn cosmic_api.main:app --reload --port 8000
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
```

La documentación interactiva queda en `http://localhost:8000/docs`. CORS tiene que permitir `http://localhost:3000`. No uses `*`.

Postgres, Redis y Docker no son necesarios para la demo. No los levantes salvo que el flujo en disco ya funcione y sobre la tarde del domingo. El estado de la demo es el JSON de `data/manifests/` más los PNG.

Dependencias: `httpx` está en el grupo de desarrollo. Para llamar a IRSA desde la API, añádelo a las dependencias del proyecto y regenera el lock con uv. Astropy y PyVO viven en el extra `astronomy`. El proceso de la API puede llamar a las funciones de Mateo en `cosmic_astronomy` cuando él las deje en `search.py`. Hasta ese momento, lee los JSON.

Límite de la llamada externa: 25 segundos, un reintento si el fallo es de red, y después `504` o `502` según la tabla del plan de equipo. Tamaño máximo de descarga de un FITS: 80 MB. Rechaza cualquier URL que no sea `https` y cuyo host no sea `irsa.ipac.caltech.edu`. El cliente de la web no envía URLs.

## Bloque 1 — sábado 11:30 a 13:00. Contrato visible, datos de mentira controlados

Eduardo necesita pegarle a la API ya, antes de que Mateo tenga FITS.

1. Modelos Pydantic nuevos en `services/api/cosmic_api/schemas.py` para el cuerpo de búsqueda y la respuesta del plan de equipo. `extra="forbid"`, igual que `ObservationQuery`.
2. `GET /v1/examples` y `GET /v1/examples/{slug}` leen `data/manifests/{slug}.json`. Si la carpeta está vacía, responde los cinco slugs con `observations: []`, `source: "cache"` y la advertencia `manifest-not-ready`. Así Eduardo distingue «Mateo no ha entregado» de «IRSA vacío».
3. `GET /v1/frames/{id}` busca el `id` dentro de los manifiestos y devuelve el PNG desde `apps/web/public/previews/{preview_file}`. Si no está, `404`.
4. `POST /v1/sky/search` en este bloque puede devolver `501` con el detalle `live search not wired` **solo hasta las 16:00**. A las 16:00 tiene que estar vivo o devolver un error real de IRSA. No dejes el 501 para el domingo.
5. Tests con `TestClient`: 422 de coordenadas, 404 de frame, y un manifiesto temporal en `tmp_path` que devuelve dos observaciones ordenadas por `mjd`. No hace falta red.
6. Regenera OpenAPI y mira el diff. No edites el JSON a mano.

Manda a Eduardo la lista de rutas en cuanto `/docs` las muestre. Manda a Mateo la confirmación de que su JSON de ejemplo, cuando exista, se lee sin transformar los nombres.

## Bloque 2 — sábado 13:00 a 16:00. Búsqueda viva

`POST /v1/sky/search` ejecuta la consulta.

1. Construye la URL con `build_sia_url`. No armes otra query a mano.
2. Haz el GET a IRSA con el timeout de 25 segundos.
3. Parsea el VOTable con lo que Mateo haya confirmado. Si a las 14:00 todavía no te pasó `colnames`, parsea solo las columnas que veas y pon `null` en el resto, con una advertencia `columns-unverified`. No bloquees el endpoint esperando el parser perfecto.
4. Ordena por tiempo ascendente. Quita filas repetidas por `obs_id` y anótalo en `warnings`.
5. No pongas `access_url` en la respuesta.
6. `preview_url` apunta a `/v1/frames/{id}` solo cuando el PNG ya existe. Si la fila es real pero aún no hay imagen, `preview_url` es `null`. Eduardo mostrará la fila igual, sin hueco negro disfrazado de cielo.
7. `source` es `live` y `queried_at` es la hora de esta llamada, con offset `-04:00`.
8. Tests: XML o VOTable mínimo guardado en `tests/fixtures/`, sin red. Un test de host rechazado si alguien intenta pasar una URL. El POST no acepta un campo `url`.

Si IRSA responde un error HTML, eso es `502`, con el estado HTTP del proveedor en el log y un `detail` corto en inglés. No reenvíes el HTML al navegador.

## Bloque 3 — sábado 16:00 a 19:00. El objetivo de Mateo se sirve

Cuando llegue `data/manifests/wise-0855.json` y los PNG:

1. `GET /v1/examples/wise-0855` devuelve ese manifiesto traducido al objeto de búsqueda, `source: "cache"`.
2. Cada frame con PNG responde `200` y `Content-Type: image/png`.
3. El orden de `observations` es el del archivo, que ya viene cronológico. No reordenes «para que se vea mejor».
4. Añade un test que carga ese JSON real si está en el repo. Si Mateo aún no lo commiteó, el test se salta con una razón explícita, no falla en silencio.
5. Prueba desde otra terminal:

```powershell
uv run pytest -q
Invoke-RestMethod http://localhost:8000/v1/examples/wise-0855 | ConvertTo-Json -Depth 6
```

Eduardo cambia su base URL a `http://localhost:8000`. Quédate en esa integración hasta que el play del navegador muestre la fecha del primer y del segundo frame. Si el CORS falla, lo ves tú en el log, no Eduardo adivinando.

## Bloque 4 — sábado 19:00 a 22:00. Caché de escenario

1. Los cinco `GET /v1/examples/{slug}` responden sin abrir un socket a IRSA. Compruébalo apagando la red o apuntando el host de IRSA a un valor inválido solo en un test.
2. Una búsqueda live fallida no borra la caché.
3. Log en consola: hora, ruta, status, y si el origen fue live o cache. Sin volcar FITS ni headers enteros.
4. Actualiza el README raíz: cómo levantar la API, cómo probar un ejemplo, y la frase de que la caché no es una consulta en vivo. Coordiná con Eduardo para no editar el README a la vez; tú tienes la prioridad en ese archivo, él te pasa el párrafo de la web.
5. `.env.example` gana `IRSA_TIMEOUT_SECONDS=25` y `CORS_ORIGINS=http://localhost:3000` si hiciste falta configurarlos. Sin secretos.

Graba con Eduardo el video de un minuto cuando este bloque cierre. Si la grabación espera a que «quede más lindo», no hay respaldo.

## Domingo 09:00 a 12:00. Radio y detector

1. El radio que manda Eduardo en el POST es el que viaja a IRSA, dentro de `(0, 0.5]`. Si manda más, `422`.
2. Query opcional `detector` en `GET /v1/examples/{slug}?detector=`. Filtra en memoria sobre el manifiesto. Si el valor no existe, lista vacía y advertencia `unknown-detector`, no un 404 del objetivo entero.
3. No filtres detectores en el frontend por tu cuenta: la lista de valores sale de los frames. Puedes añadir en la respuesta de ejemplos un arreglo `detectors` con los valores distintos, en el orden en que aparecen. Avisa a Eduardo si lo añades.
4. La resta de Mateo, si llega como un frame más con flag `display-difference`, se sirve como cualquier PNG. No la metas dentro de la secuencia temporal por defecto: en el manifiesto puede vivir en el array, y Eduardo la muestra aparte. Si hace falta un campo `role` con valores `epoch` o `difference`, añádelo el domingo a las 09:30 y regenera OpenAPI en ese momento, no después de que Eduardo haya cableado el player.

## Domingo 12:00 a 15:00. Limpio

En una terminal nueva, desde cero:

```powershell
uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run python scripts/export_openapi.py
uv run uvicorn cosmic_api.main:app --port 8000
```

Recorre con el navegador, o con `Invoke-RestMethod`, los cinco slugs, un POST inválido y un POST del campo de WISE 0855. Anota en el README qué comando se corrió y si el POST live respondió. Si live falla en ese momento, la demo usa caché y el README lo dice.

No abras Gemini, no añadas usuarios, no conectes Celery.

## Definition of done

- `/docs` muestra search, examples y frames.
- Los tests cubren 422, 404, manifiesto cacheado, URL de IRSA rechazada como entrada del cliente, y live parseado desde un fixture local.
- Con IRSA inalcanzable, los cinco ejemplos siguen respondiendo.
- `executed: false` del query-plan antiguo sigue igual.
- OpenAPI regenerado, sin edición manual.
- Eduardo puede dejar el frontend en `npm run build` apuntando a tu API sin un proxy improvisado de última hora.

## Si te atascas

| Situación | Qué haces |
| --- | --- |
| VOTable distinto al tutorial | Guarda el archivo en `tests/fixtures/` y parsea las columnas que existan |
| La descarga del FITS tarda más que el demo | No la hagas en el request del play. El play solo lee PNG ya hechos por Mateo |
| Eduardo pide un campo nuevo | Dilo en el chat, cambia Pydantic, regenera OpenAPI, y él actualiza el cliente. No dupliques el tipo en TypeScript a mano |
| Quieres Postgres porque el esquema ya está en `infrastructure/db/` | Después del domingo 15:00, y solo si la caché en JSON ya está ensayada |
| El puerto 8000 está ocupado | Usa 8000 igual y mata el proceso viejo. Eduardo va a tener esa URL escrita |
