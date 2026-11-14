# Mateo — datos y ciencia

Tu resultado del domingo: cinco fichas honestas y, como mínimo, una secuencia real de dos visitas del mismo detector que Eduardo puede reproducir. Otra persona tiene que poder repetir tu consulta con el JSON y el notebook.

No afirmes que un objetivo se mueve hasta haber visto dos imágenes comparables. Si no las hay, la ficha que dice «una sola época» es un entregable válido. Una secuencia inventada descalifica el trabajo.

Lee antes [06-PLAN-EQUIPO.md](06-PLAN-EQUIPO.md). El contrato de campos está ahí. No añadas claves nuevas sin avisar a Julio y a Eduardo en el mismo mensaje.

## Qué es solo tuyo

- `services/astronomy/cosmic_astronomy/`
- `notebooks/01_inventory.ipynb` (créalo)
- `data/manifests/{slug}.json`
- `data/raw/` y `data/processed/` en tu disco, sin Git
- Los PNG que pases a Eduardo para `apps/web/public/previews/`
- `docs/science.md`, solo para añadir qué se comprobó de verdad

No edites `services/api/` ni `apps/web/`. Julio conecta tus funciones. Eduardo no recalcula coordenadas.

## Entorno, una sola vez

Desde la raíz del repo, con Python 3.12 o 3.13 y uv:

```powershell
Copy-Item .env.example .env
uv sync --frozen --extra astronomy
uv run python -c "import astropy, pyvo; print(astropy.__version__, pyvo.__version__)"
```

Anota en el notebook las versiones que imprimió y la fecha. Si `uv sync --frozen` falla por el extra, avisa a Julio: él actualiza `uv.lock`. No instales paquetes con pip global.

Crea las carpetas si no existen: `data/manifests/`, `notebooks/`.

## Bloque 1 — sábado 11:30 a 13:00. Una consulta real

Objetivo: demostrar que IRSA responde para WISE 0855 y guardar la respuesta cruda. Todavía no hagas imágenes bonitas.

Coordenadas del enunciado, ya pasadas a grados para no perder tiempo. Confírmalas con Astropy y no las redondees a menos de seis decimales en el manifiesto:

- RA `08h55m10.831s` → `133.795129` grados
- Dec `-7d14m42.53s` → `-7.245147` grados

En `notebooks/01_inventory.ipynb`, primera sección, con celdas que se puedan volver a ejecutar:

1. Convertir el sexagesimal con `astropy.coordinates.SkyCoord` y comprobar que coincide con esos grados.
2. Listar colecciones SIA que contengan `spherex`. Guardar la lista y la hora.
3. Consultar un radio pequeño, `0.02` grados, colección `spherex_dr1`.
4. Imprimir `colnames`, el número de filas y las primeras filas de tiempo, identificador y URL.
5. Guardar la tabla en `data/raw/wise-0855-sia.vot` o `.ecsv` si el formato real es ese. El archivo grande se queda fuera de Git. En el notebook deja escrito cuántas filas volvieron.

Puedes usar `astroquery.ipac.irsa.Irsa.query_sia` o PyVO contra `https://irsa.ipac.caltech.edu/SIA`. El código del repo, `build_sia_url` en `services/astronomy/cosmic_astronomy/irsa.py`, arma esa URL y no la ejecuta. Úsalo para no divergir del endpoint. La llamada HTTP es nueva y va en este bloque.

Qué mirar en las columnas reales, sin asumir nombres: un identificador de observación, un tiempo, una URL de acceso, algo que distinga detector o banda, y flags. Copia los nombres exactos al final de la celda. Esos nombres son los que Julio va a parsear. Mándaselos en el chat en cuanto los veas, con una fila de ejemplo pegada.

Si la consulta devuelve cero filas: repite con `spherex_qr3`, luego con radio `0.05`. Si sigue en cero, dilo en el chat y pasa al objetivo siguiente. No fabriques filas.

Si IRSA da timeout: un reintento. Si falla otra vez, guarda el error textual y sigue con el bloque de coordenadas de los otros objetivos. Julio puede servir caché, pero alguien tiene que traer al menos una respuesta real antes de las 19:00.

## Bloque 2 — sábado 13:00 a 16:00. Inventario y dos recortes

Una fila no es una época. Arma una tabla, aunque sea en el notebook, con una fila por producto devuelto:

| Qué anotar | Para qué |
| --- | --- |
| `obs_id` tal como venga | No contar dos veces el mismo producto |
| Tiempo y unidad o escala | Ordenar la película |
| Colección y release | No mezclar DR1 con un reprocesado y llamarlo «otro día» |
| Detector o banda | No animar el detector 1 contra el detector 4 |
| URL de acceso | Descargar el recorte, no el cielo entero |
| Flags de calidad o contaminación | Mostrarlos, no esconderlos |
| Si el identificador se repite con otro release | Marcarlo como duplicado, no como visita nueva |

Elige el grupo más largo que comparta detector y colección. Si hay empate, elige el que tenga flags más limpios. Escribe en una celda markdown por qué.

Descarga como mucho cuatro recortes de ese grupo. El servicio de recortes de SPHEREx añade `center` y `size` a la URL de una imagen: lee la página vigente y usa una URL que acabas de obtener, no una URL de un tutorial viejo. Tamaño inicial: 60 segundos de arco. Si el campo queda vacío, sube a 120. Guarda los FITS en `data/raw/` con el `obs_id` en el nombre.

Por cada FITS, imprime y anota:

- Lista de HDUs y cuál tiene la imagen científica. No uses la extensión de previsualización si existe una de ciencia.
- Forma del array, unidad del header (`BUNIT` o la que venga), WCS: ¿`SkyCoord` de la esquina y del centro cae cerca del objetivo?
- Tiempo en el header y si coincide con la fila del inventario.
- Máscara o plano de calidad, si existe. Los pixeles sin cobertura se quedan enmascarados. No los conviertas en cero silencioso.

Genera un PNG por frame para la web:

- Misma escala de estirado en todos los frames de esa secuencia. Anota los parámetros (por ejemplo asíntota hiperbólica, vmin, vmax) en el manifiesto, dentro de `warnings` o en `comparison_note` si aún no hay un campo de stretch. Si necesitas un campo `stretch`, avisa antes de usarlo y Julio lo añade al contrato.
- Norte arriba, misma orientación en todos. Si el WCS no deja hacerlo en este bloque, dilo: Eduardo mostrará la advertencia y no afirmarán movimiento.
- PNG 8 bits, lado corto alrededor de 512 px. Nombre `{slug}-{n}.png`.
- Calcula SHA-256 del FITS y del PNG.

Al terminar este bloque, `data/manifests/wise-0855.json` existe, aunque `comparable` sea `false`. Copia los PNG a una carpeta que Eduardo pueda tomar. El mensaje al equipo lleva: número de filas, número de épocas distintas, detector elegido, si los dos primeros frames se pueden animar, y la ruta de los PNG.

## Bloque 3 — sábado 16:00 a 19:00. El mejor objetivo queda cerrado

Revisa la pareja elegida en cuatro comprobaciones. Si una falla, `comparable` sigue en `false` y la advertencia dice cuál falló.

1. No son el mismo `obs_id` ni el mismo tiempo con otro release.
2. Mismo detector y misma colección.
3. El centro WCS de ambos cae dentro del radio pedido.
4. Una estrella o el propio objetivo, si se ve, cae en el mismo pixel aproximado después de orientar. Si se desplaza todo el campo igual, es un fallo de alineación, no un objeto moviéndose. No entregues esa pareja como comparable.

Cuando la pareja pase, pon `comparable: true` y escribe `comparison_note` en inglés, dos o tres frases: qué se alineó, qué stretch se usó, qué no se midió.

Pasa el JSON final a Julio. Él lo sirve en `GET /v1/examples/wise-0855`. Tú no levantas la API.

## Bloque 4 — sábado 19:00 a 22:00. Los cinco objetivos

Repite el inventario, no hace falta repetir la prosa. Una ficha por objetivo en `data/manifests/`. Plantilla mental de cada una:

| Slug | Qué tienes que resolver |
| --- | --- |
| `wise-0855` | Ya está. Solo actualiza si el bloque 3 cambió el veredicto |
| `barnards-star` | Posición en SIMBAD o SESAME. El movimiento propio es enorme: anota la época de las coordenadas y no uses una posición vieja como si fuera la de la observación |
| `epsilon-indi-b` | Es el par de enanas marrones, no la estrella Epsilon Indi. Confirma el identificador en la fuente y anótalo en `coord_source` |
| `rw-aurigae` | Variable. Una diferencia de brillo no es un desplazamiento. La ficha debe decirlo |
| `r-draconis` | Variable. La misma advertencia |

Para cada uno guarda: fuente de la posición con URL, época, colección consultada, hora de la consulta, cuántas filas, cuántas épocas del mismo detector, y `comparable`. Descarga recortes solo donde haya al menos dos épocas candidatas. Si solo hay una, un PNG basta para mostrar «sabemos qué hay», y la web no debe animar un único frame como película.

Orden si el tiempo aprieta: cierra primero el objetivo que ya tenga dos épocas. Luego WISE 0855 aunque sea ficha corta. Luego los que falten, aunque queden en «consultado, una época» o «consulta fallida». Las cinco fichas existen el sábado por la noche, aunque cuatro digan que no se pueden animar.

Entrega a Eduardo la lista de slugs con `comparable`, las coordenadas y los PNG. Entrega a Julio los nombres reales de columnas y de detectores.

## Domingo 09:00 a 12:00. Una resta, nada más

Solo sobre la pareja con `comparable: true` y alineación revisada.

- Resta los arrays científicos enmascarados, no los PNG.
- El PNG de la resta usa otro stretch y se llama `{slug}-diff.png`.
- En el manifiesto, añade la resta como frame con `id` `{slug}-diff` y `flags` que incluyan `display-difference`.
- `comparison_note` dice que es una diferencia para mirar, que el stretch no es flujo calibrado, y que no se restaron PSF distintas a propósito.
- Si la alineación del sábado era dudosa, no hagas la resta. Escribe por qué.

No implementes extracción de fuentes, trayectorias ni catálogos cruzados en este bloque. Eso no lo pide el reto para el domingo.

## Domingo 12:00 a 15:00. Revisión de lo que se va a decir

Recorre la web con Eduardo. Por cada texto visible, comprueba:

- La fecha en pantalla es la del manifiesto, no la de hoy.
- El detector mostrado existe en el header.
- Ningún objetivo `comparable: false` tiene botón de play que avance entre imágenes de bandas distintas.
- La caché muestra la fecha `queried_at`.
- Barnard's Star, si se usa, menciona que la posición depende de la época.

Actualiza `docs/science.md` con un apartado corto: qué consulta se corrió, qué objetivo es comparable, qué limitaciones quedaron. Sin métricas inventadas.

## Funciones que Julio va a importar

Déjalas en `services/astronomy/cosmic_astronomy/search.py` en cuanto la primera consulta funcione. Así Julio no copia tu notebook dentro de FastAPI.

```python
def search_collection(ra_deg: float, dec_deg: float, radius_deg: float, collection: str) -> dict:
    """Devuelve el dict del contrato de búsqueda, source='live', sin preview_url.

    preview_url lo añade Julio. Si IRSA falla, lanza un error con el mensaje del proveedor.
    No captures el fallo en silencio.
    """

def load_manifest(slug: str) -> dict:
    """Lee data/manifests/{slug}.json. FileNotFoundError si no existe."""
```

Hasta que existan, Julio usa los JSON que le pases. No bloquees su sábado esperando a refactorizar el notebook: el JSON es la entrega; las funciones son la forma de no repetir el parseo el domingo.

## Definition of done

- `data/manifests/` tiene cinco JSON con los slugs del plan.
- Al menos un JSON tiene frames con `obs_id`, tiempo, detector y `sha256` copiados del archivo, más dos PNG que Julio y Eduardo pueden abrir.
- El notebook vuelve a correr las celdas de inventario sin editar a mano la tabla.
- Cada ficha distingue «no hay épocas» de «la consulta falló».
- No hay ningún FITS en `git status`.

## Si te atascas

| Situación | Qué haces |
| --- | --- |
| Cero filas en los cinco | Radio `0.05`, la otra colección, y una ficha por objetivo con el error. Avisa a las 16:00, no a las 21:00 |
| Muchas filas y ningún tiempo | Pega `colnames` a Julio y para de descargar hasta entender qué columna es el tiempo |
| El FITS no abre con Astropy | Guarda el header en texto y usa otro producto de la misma época. No conviertas un HTML de error en FITS |
| Dos imágenes pero el campo salta entero | `comparable: false`, advertencia `alignment-unchecked` |
| Quieres probar un detector automático | No el sábado. Anótalo en `docs/science.md` como trabajo posterior |
