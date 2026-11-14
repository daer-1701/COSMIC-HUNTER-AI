# Eduardo — web y demo

Tu resultado del domingo: una persona abre la web, elige un objetivo o escribe coordenadas, y ve la secuencia con fechas, procedencia y límites. Tú conduces los tres minutos. Mateo revisa las frases. Julio mantiene la API.

La interfaz va en inglés. Este archivo va en español. No calcules posiciones, tiempos ni restas en el navegador: muestra lo que la API y los manifiestos ya traen.

Lee [06-PLAN-EQUIPO.md](06-PLAN-EQUIPO.md) antes de crear componentes. El contrato de allí es la única forma de los datos.

## Qué es solo tuyo

`apps/web/`. Hoy solo hay un README. No está instalado Next.js.

No edites Python ni `packages/shared/openapi.json`. No generes PNG científicos. Si un frame no tiene `preview_url`, muestra la fila con su fecha y el texto `Preview not available`. No pongas una foto de relleno.

## Bloque 1 — sábado 11:30 a 13:00. App que ya se puede clickear

Node 20 o superior. Desde `apps/web`, el directorio no está vacío por el README. Muévelo a `README.plan.md`, crea la app y vuelve a dejar una nota corta en `README.md` de cómo se arranca.

```powershell
cd apps\web
node --version
npx create-next-app@latest . --ts --tailwind --eslint --app --src-dir --use-npm --no-import-alias
```

Si el asistente pregunta router, dile que sí a App Router, no a Turbopack si duda, y no a `src/` si el comando ya lo fijó. Lo que importa: TypeScript, Tailwind, App Router, sin carpeta `pages/`.

Dependencia de datos remotos:

```powershell
npm install @tanstack/react-query
```

No instales Plotly, Aladin, shadcn ni un cliente OpenAPI generado en este bloque. El player no los necesita.

Pantalla única en `src/app/page.tsx`, partida en componentes:

| Componente | Responsabilidad |
| --- | --- |
| `TargetBar` | Cinco botones con los slugs del plan |
| `CoordinateForm` | RA, Dec, radio. Validación visible |
| `ObservationList` | Filas con tiempo, colección, detector, flags |
| `Player` | Imagen, play/pausa, anterior, siguiente, velocidad |
| `Provenance` | `source`, `queried_at`, `warnings`, `comparison_note` |
| `EmptyState` | El estado exacto, no un mensaje genérico |

Hasta que Julio tenga rutas, carga un fixture local en `src/fixtures/wise-0855.json` con dos frames y `source: "fixture"`. El banner fijo dice `Development fixture. Not an observation.` En cuanto `GET /v1/examples/wise-0855` responda, borra el uso del fixture. Puedes dejar el archivo para tests.

Criterio de las 13:00: `npm run dev`, los botones cambian el objetivo seleccionado, play avanza la fecha del fixture, y pausa la deja quieta.

Textos del fixture, ya en inglés, para no reescribirlos luego:

- Play, Pause, Previous frame, Next frame
- Right ascension (degrees), Declination (degrees), Field radius (degrees)
- No observations in this field
- Only one epoch. Temporal playback needs two comparable visits
- Cached example. Not a live archive query
- Apparent change. Not a confirmed discovery
- Incompatible or unknown detector
- Preview not available
- Archive request failed

## Bloque 2 — sábado 13:00 a 16:00. Reproductor de verdad

`Player` guarda el índice del frame. La imagen es el `preview_url` del frame actual. La fecha grande es `iso_time`, y si es `null`, `mjd` con la etiqueta `MJD`. No conviertas MJD a calendario en el cliente: si Mateo no mandó `iso_time`, se muestra el número y la escala.

Controles:

- Play recorre los frames con `role: "epoch"` si ese campo existe; si no existe, todos los que no tengan el flag `display-difference`.
- La diferencia, si viene, tiene su propio botón `Show display difference`, fuera del play.
- Velocidades: 0.5 s, 1 s y 2 s por frame. Default 1 s.
- Pausa al llegar al final, no un bucle infinito. Un control `Loop` apagado por defecto.
- Anterior y siguiente funcionan con el play en pausa.
- Teclado con foco en el player: espacio pausa o sigue, flecha izquierda y derecha cambian de frame. Los botones tienen nombre accesible.
- `prefers-reduced-motion`: el play no arranca solo. La página carga en pausa siempre, también sin esa preferencia. Nadie quiere una animación científica disparada al abrir.

Estados, cada uno con una frase distinta:

| Situación | Qué se ve |
| --- | --- |
| Cargando | `Loading observations` |
| `observations` vacío | `No observations in this field` y el radio usado |
| Un solo frame | La imagen y `Only one epoch...`. Play deshabilitado |
| Error 422 | `Those coordinates are outside the allowed range` |
| Error 502 o 504 | `The archive did not answer` y el botón del ejemplo cacheado del mismo target, si existe |
| `source: "cache"` | Banner `Cached example. Not a live archive query` más `queried_at` |
| `source: "fixture"` | Banner de desarrollo. No puede quedar en el build del domingo |

Zoom visual: botones `Fit` y `100%` sobre el PNG, con CSS. Eso no cambia el radio científico. El radio es el otro control, el del formulario, y solo tiene efecto cuando Julio confirme el POST. Hasta entonces el slider puede verse deshabilitado con `Field radius applies on search`.

`npm run build` tiene que pasar al final del bloque.

## Bloque 3 — sábado 16:00 a 19:00. Datos reales

Base URL `http://localhost:8000`, en `NEXT_PUBLIC_API_BASE_URL`. Solo la base, ningún secreto. TanStack Query para `GET /v1/examples` y `GET /v1/examples/{slug}`.

Al pulsar un objetivo, no llames al POST live. Llama al ejemplo cacheado. El POST live es el formulario `Search this field`, para cuando alguien escribe coordenadas nuevas. Así la demo no depende de IRSA y el reto igual permite buscar un campo arbitrario.

Cuando Mateo entregue el primer JSON real:

1. Quita el fixture del camino de la página.
2. Comprueba que la fecha cambia entre frame 1 y frame 2.
3. Comprueba que un slug sin manifiesto muestra `manifest-not-ready` como estado vacío, no como imagen rota.
4. El panel de procedencia lista `warnings` una por una.

Si el CORS falla, Julio lo corrige. No montes un rewrite de Next para esconder el fallo: en el escenario la web y la API tienen que verse como dos piezas.

## Bloque 4 — sábado 19:00 a 22:00. Cinco objetivos y URL

Los cinco botones leen `GET /v1/examples`. El nombre en pantalla es el `name` del manifiesto, no una traducción tuya.

La URL de la página refleja el estado:

`/?target=wise-0855&ra=133.795129&dec=-7.245147&radius=0.02`

Al cargar, si hay `target`, pides ese ejemplo. Si hay `ra` y `dec` sin target, rellenas el formulario y no disparas el POST hasta que la persona pulse `Search this field`. Copiar el enlace es un botón `Copy link` que copia `window.location.href`.

Fichas de los objetivos no comparables: se pueden abrir, se ve la lista o la advertencia, y el play sigue deshabilitado. No escondas esos botones. El jurado pidió probar los cinco, y una negativa clara cuenta.

Ensayo de un minuto con Julio y el teléfono grabando: clic en WISE 0855, play, pausa, abrir procedencia. Guárdalo fuera del repo si pesa, y anota la ruta en el chat del equipo.

## Domingo 09:00 a 12:00. Lo que se ve en la demo y suma

En este orden. Si a las 11:00 el play de un objetivo real todavía falla, te quedas en el bloque del sábado y no empiezas Aladin.

1. **Campo de visión.** Input numérico de radio entre `0.005` y `0.05` para la demo, aunque la API acepte hasta `0.5`. Al buscar, el POST lleva ese `radius_deg`. La URL se actualiza.
2. **Detector.** Chips construidos con los valores distintos de `frames[].detector`. `All detectors` muestra todo. Elegir uno filtra en pantalla los frames ya descargados y, si Julio añadió el query param, también lo manda. No escribas `D1`…`D6` fijos: hasta que Mateo diga el nombre real, el chip muestra el string del archivo.
3. **Parpadeo.** Con la secuencia en pausa y dos frames epoch, un botón `Blink these two` alterna solo ese par cada 0.4 s, con pausa. No mezcles detectores: si los dos frames tienen detector distinto, el botón explica `These frames use different detectors` y no alterna.
4. **Resta.** Si existe un frame con flag `display-difference`, botón aparte y leyenda `Stretched preview difference. Not a photometric measurement.`
5. **Aladin Lite**, solo con el play ya cerrado. Cárgalo en un client component perezoso, desde la URL vigente del CDS, no desde un paquete npm nuevo si el script oficial basta. Centrado en el RA/Dec actual, campo pequeño, como mapa de situación. Si tarda más de 45 minutos, quítalo. La secuencia SPHEREx es la demo; Aladin es contexto.

Añade una landing de cuatro líneas encima del formulario, en inglés:

- SPHEREx images of one sky position, in time order.
- Enter right ascension and declination, or open a challenge target.
- Dates and detectors come from the archive products.
- Motion on screen is an apparent change and needs review.

## Domingo 12:00 a 15:00. Ensayo

`npm run build` y `npm run start`. Recorre esto sin abrir la consola delante del proyector:

1. Inicio sin query.
2. WISE 0855 desde el botón. Play, pausa, flechas.
3. Procedencia visible, con fecha de consulta.
4. Un objetivo sin dos épocas, y la frase de una sola época.
5. Coordenadas inválidas, por ejemplo Dec `95`, y el 422 en lenguaje claro.
6. Copiar enlace, abrirlo en otra pestaña, ver el mismo target.
7. Modo sin API: si paras el proceso de Julio, el banner de fallo aparece y, si dejaste los PNG en `public/previews/`, un último recurso los muestra solo cuando el manifiesto también está copiado en `src/fixtures/cache/`. Ese último recurso lleva el banner `Offline copy of the cached example`. No es el camino feliz. El camino feliz es la API de Julio.

Pasa a Mateo cada frase nueva para que la lea. Si él tacha una, se cambia el texto, no se discute en el ensayo.

Tú llevas la voz el domingo. Guion en el plan de equipo. Ensáyalo tres veces de pie, con el cronómetro. Si te pasas de tres minutos, se cae Aladin de la charla, no la procedencia.

## Definition of done

- Una sola página, usable con teclado, en inglés, en pausa al cargar.
- Cinco objetivos, coordenadas libres, radio, enlace copiable.
- Play solo con dos o más frames comparables del filtro actual.
- Caché, fixture, vacío, una época, archivo caído y validación se distinguen a simple vista.
- Ninguna imagen científica dibujada a mano.
- `npm run build` pasa.
- El video de respaldo del sábado existe.

## Si te atascas

| Situación | Qué haces |
| --- | --- |
| `create-next-app` no quiere usar el directorio | Crea en `apps/web-tmp` y mueve el contenido a `apps/web`, conservando el README del plan |
| Julio no tiene CORS a las 16:00 | Sigue con el fixture y un banner, y quédate disponible para conectar en cuanto `/v1/examples/wise-0855` responda en el navegador |
| Mateo no tiene dos épocas | Diseña la ficha de una época como pantalla principal de ese objetivo. Es un resultado, no un hueco |
| Quieres un visor 3D o espectros | No entran en la demo hablada. Anótalos debajo del guion como siguiente paso |
| El PNG se ve lavado | No reescales el contraste en el cliente. Pídele a Mateo otro stretch y que lo anote. Un contraste distinto entre frames parece movimiento |
