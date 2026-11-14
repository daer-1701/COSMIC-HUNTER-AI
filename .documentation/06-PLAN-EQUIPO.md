# Plan de ejecución — Eduardo, Julio y Mateo

Actualizado: 14 de noviembre de 2026, 11:00 America/La_Paz.

Este archivo es la orden de trabajo del fin de semana. Los tres lo leen entero antes de abrir su guía. Después cada uno sigue solo la suya:

- Mateo, datos y ciencia: [07-MATEO-DATOS.md](07-MATEO-DATOS.md)
- Julio, backend: [08-JULIO-BACKEND.md](08-JULIO-BACKEND.md)
- Eduardo, web y demo: [09-EDUARDO-WEB.md](09-EDUARDO-WEB.md)

El enunciado que hay que cubrir es el de NASA Space Apps, *Planet X and SPHEREx*: una web pública donde alguien escribe ascensión recta y declinación y ve las imágenes SPHEREx de esa zona en orden temporal, como un video corto. Hay que probarla con Barnard's Star, Epsilon Indi B, WISE 0855, RW Aurigae y R Draconis.

Esto no es el plan largo de `docs/team-plan.md`. Gemini, login, votos, detector automático, Celery, S3 y escaneo de todo el cielo quedan fuera de este fin de semana. Si sobra tiempo el domingo por la tarde, se anotan como siguiente paso. No se empiezan el sábado.

## Qué tiene que verse el domingo para cubrir el reto

Una persona que no programó el proyecto puede, sin ayuda y con la red caída después de la primera carga:

1. Abrir la web.
2. Pulsar uno de los cinco objetivos o escribir RA/Dec en grados.
3. Ver una lista de observaciones reales con fecha, colección y detector.
4. Pulsar play, pausar, avanzar y retroceder, y ver que la fecha cambia con el fotograma.
5. Leer de dónde salió cada imagen y qué no se puede afirmar.
6. Cambiar el tamaño de la región.
7. Filtrar por detector, porque SPHEREx observa en 102 bandas y seis detectores.
8. Ver dos épocas en parpadeo y, si Mateo la preparó, una resta de visualización.
9. Copiar una URL que reabre las mismas coordenadas.
10. Entender que un cambio en pantalla es un cambio aparente, no un planeta confirmado.

Si un objetivo no tiene dos épocas comparables, la web lo dice con una ficha honesta. Eso cumple el reto. Inventar una secuencia no lo cumple.

## Horario

Congelar funciones nuevas el domingo a las 15:00. Después solo se arregla la demo.

| Bloque | Mateo | Julio | Eduardo | Cierre juntos |
| --- | --- | --- | --- | --- |
| Sáb 11:30–13:00 | Primera consulta real de WISE 0855 | Endpoints con el manifiesto de ejemplo, sin IRSA todavía | App que reproduce ese manifiesto | Contrato de este archivo aceptado en el chat del equipo |
| Sáb 13:00–16:00 | Inventario del primer objetivo y dos recortes | `POST /v1/sky/search` vivo contra IRSA | Reproductor con pausa, teclado y estados vacíos | — |
| Sáb 16:00–19:00 | Manifiesto real del mejor objetivo | La API sirve esos fotogramas | La web deja los fixtures y usa la API | Un objetivo real se reproduce en el navegador |
| Sáb 19:00–22:00 | Fichas de los cinco objetivos | Caché de demo que arranca sin IRSA | Botones de los cinco, procedencia, URL | Demo de un minuto grabada como respaldo |
| Dom 09:00–12:00 | Resta de la mejor pareja, si las dos épocas alinean | Filtro por detector y radio en la búsqueda | Campo de visión, detector, parpadeo, resta | — |
| Dom 12:00–15:00 | Revisar cada frase científica de la interfaz | README de arranque y prueba en limpio | Textos en inglés, accesibilidad, ensayo | Recorrido completo sin consola abierta |
| Dom 15:00–17:00 | Ensayo: limita qué se afirma | Ensayo: API y caché | Ensayo: conduce la demo | Tres pasadas del guion. Subir lo que pida la plataforma |

Si a las 19:00 del sábado no hay un objetivo real en la web, se para todo lo opcional y los tres se quedan en ese único flujo hasta que funcione.

## Dueños

| Persona | Carpetas | No toca |
| --- | --- | --- |
| Mateo | `services/astronomy/`, `notebooks/`, `data/manifests/`, `docs/science.md` | `services/api/`, `apps/web/` |
| Julio | `services/api/`, `tests/`, `packages/shared/openapi.json` vía el script, `README.md`, `.env.example` | `apps/web/`, algoritmos de Mateo |
| Eduardo | `apps/web/` | Python, OpenAPI a mano, manifiestos científicos |

Ramas: `mateo/datos`, `julio/api`, `eduardo/web`. Nadie hace commit en `main` directo. Nadie reescribe el trabajo de otro. Un PR por bloque, con la frase de cierre de ese bloque.

La interfaz, los mensajes de la API, el README técnico y las fichas que se proyectan van en inglés. Este paquete `.documentation/` sigue en español para el equipo.

## Contrato congelado

Julio lo implementa. Eduardo lo consume. Mateo llena los manifiestos con estos nombres de campo y ningún otro. Si falta un dato del archivo, el valor es `null` y entra una advertencia. No se inventa el campo.

### Buscar

`POST /v1/sky/search`

```json
{
  "ra_deg": 133.795129,
  "dec_deg": -7.245147,
  "radius_deg": 0.02,
  "collection": "spherex_dr1"
}
```

Reglas ya vigentes en el código: RA en `[0, 360)`, Dec en `[-90, 90]`, radio en `(0, 0.5]`, colección `spherex_dr1` o `spherex_qr3`. Grados, ICRS. El radio de la demo se queda en `0.05` o menos para no pedir medios cielos.

Respuesta `200`:

```json
{
  "source": "live",
  "queried_at": "2026-11-14T16:00:00-04:00",
  "query": {
    "ra_deg": 133.795129,
    "dec_deg": -7.245147,
    "radius_deg": 0.02,
    "collection": "spherex_dr1"
  },
  "warnings": [],
  "observations": [
    {
      "id": "obs-1",
      "obs_id": "identificador del archivo",
      "mjd": 60800.0,
      "time_scale": "MJD tal como venga en la columna o la cabecera",
      "iso_time": "2025-06-01T00:00:00Z",
      "collection": "spherex_dr1",
      "detector": "nombre real del header",
      "band": null,
      "flags": [],
      "preview_url": "/v1/frames/obs-1"
    }
  ]
}
```

`source` es `live` o `cache`. `preview_url` es una ruta de nuestra API. El navegador no recibe `access_url` de IRSA ni descarga FITS.

Errores, siempre con `{"detail": "...", "request_id": "..."}`:

| Código | Cuándo |
| --- | --- |
| 422 | Coordenadas, radio o colección inválidos |
| 502 | IRSA no respondió, respondió mal o cortó a mitad |
| 504 | IRSA tardó más de 25 segundos |

Lista vacía es `200` con `observations: []` y una advertencia. No es un error. Un solo fotograma también es `200`.

### Fotograma

`GET /v1/frames/{id}` devuelve `image/png`. Si el id no existe, `404`.

### Ejemplos cacheados

`GET /v1/examples` devuelve los cinco objetivos. `GET /v1/examples/{slug}` devuelve el mismo objeto que la búsqueda, con `source: "cache"`. Slugs fijos:

| Slug | Nombre en pantalla |
| --- | --- |
| `barnards-star` | Barnard's Star |
| `epsilon-indi-b` | Epsilon Indi B |
| `wise-0855` | WISE 0855 |
| `rw-aurigae` | RW Aurigae |
| `r-draconis` | R Draconis |

El `GET` de un ejemplo responde aunque IRSA esté caído. Esa es la demo del escenario.

### Manifiesto que escribe Mateo

Un JSON por objetivo en `data/manifests/{slug}.json`. Esos JSON sí entran en Git. Los FITS no: `data/raw/` y `data/processed/` están ignorados.

```json
{
  "slug": "wise-0855",
  "name": "WISE 0855",
  "ra_deg": 133.795129,
  "dec_deg": -7.245147,
  "coord_source": "NASA Space Apps challenge statement",
  "coord_epoch": "sexagesimal publicado en el enunciado",
  "collection": "spherex_dr1",
  "radius_deg": 0.02,
  "queried_at": "2026-11-14T16:00:00-04:00",
  "comparable": false,
  "comparison_note": "por qué estas visitas se pueden o no se pueden animar juntas",
  "warnings": [],
  "frames": [
    {
      "id": "wise-0855-1",
      "obs_id": "copiado del archivo",
      "mjd": null,
      "time_scale": null,
      "iso_time": null,
      "detector": null,
      "band": null,
      "hdu": null,
      "flags": [],
      "preview_file": "wise-0855-1.png",
      "sha256": null
    }
  ]
}
```

`comparable: true` solo si hay al menos dos fotogramas del mismo detector, la misma colección, y Mateo revisó que no son el mismo reprocesado. Los PNG de esos frames viven en `apps/web/public/previews/` para que la demo cargue sin el API, y Julio los sirve también desde `GET /v1/frames/{id}`. Eduardo no genera esos PNG.

## WISE 0855, para arrancar ya

El enunciado da RA `08h55m10.831s`, Dec `-7d14m42.53s`. En grados, para el primer POST:

- RA = `15 * (8 + 55/60 + 10.831/3600)` = `133.795129`
- Dec = `-(7 + 14/60 + 42.53/3600)` = `-7.245147`

Mateo confirma la conversión con Astropy y guarda el código. Los otros cuatro objetivos no tienen coordenadas en el enunciado: Mateo las resuelve y anota la fuente. Nadie más escribe coordenadas de memoria.

## Qué suma puntos y qué se deja

El enunciado marca como opcionales, en este orden, porque se ven en tres minutos:

1. Campo de visión elegible. Domingo por la mañana. Eduardo lo pone en la URL; Julio lo aplica al radio.
2. Separar detectores. Es lo que esta misión tiene y WiseView no. El filtro sale de los valores reales que Mateo encuentre, no de una lista inventada.
3. Sumar o restar épocas. Una sola resta de la mejor pareja, hecha por Mateo, etiquetada como diferencia de previsualización estirada, no como fotometría.
4. Metadatos y flags en el panel de procedencia.
5. Coordenadas dentro de la URL: `/?ra=133.795129&dec=-7.245147&radius=0.02&target=wise-0855`.
6. Aladin Lite solo si el reproductor ya está cerrado el domingo antes de las 12:00. Sirve para situar el campo, no para reemplazar la secuencia SPHEREx.
7. Espectros y Gaia quedan fuera salvo que el flujo de arriba ya esté ensayado.

Actualizar a un release nuevo tiene que ser cambiar `collection` y repetir la consulta, no un catálogo pegado en el frontend.

## Guion de tres minutos

Eduardo conduce. Mateo corrige si una frase se pasa. Julio tiene la caché abierta por si la red falla.

| Tiempo | Qué se hace | Qué se dice |
| --- | --- | --- |
| 0:00–0:20 | Pantalla de inicio | SPHEREx mapea todo el cielo cada seis meses en 102 bandas. Nadie puede mirar eso a mano. |
| 0:20–0:45 | Clic en WISE 0855 | Escribimos coordenadas, o elegimos un objeto que el reto pide probar. |
| 0:45–1:30 | Play, pausa, un frame adelante | Cada frame es una visita real, con fecha y detector. El mismo detector, para no confundir una banda con un movimiento. |
| 1:30–2:05 | Procedencia y, si existe, la resta | Esto es un cambio aparente en la imagen. No es un descubrimiento confirmado. |
| 2:05–2:35 | Otro objetivo o una ficha sin épocas | Si no hay dos visitas comparables, la herramienta lo dice. No rellena el hueco. |
| 2:35–3:00 | URL copiada | Alguien puede reabrir este campo sin instalar nada. El siguiente paso sería más releases y una capa de catálogo. |

## Respaldo de escenario

Antes del sábado a las 22:00:

- La web reproduce los PNG de `public/previews/` si `GET /v1/examples/wise-0855` falla.
- Hay un video de un minuto del flujo real, grabado en el teléfono, por si el proyector no tiene red.
- `uv run pytest -q` pasa en la máquina de Julio.
- `npm run build` pasa en la máquina de Eduardo.

## Frases prohibidas en la demo y en la interfaz

Descubrimiento confirmado. Planeta nuevo. Movimiento medido, si nadie ajustó una trayectoria. Vacío de señal, para un pixel sin cobertura. La resta prueba un asteroide.

Frases que sí se usan: apparent change, review candidate, cached example queried on {fecha}, single epoch, incompatible detector.
