# Skills y reglas para Codex + Cursor

Selección revisada el 2026-11-14 para el estado real del proyecto. Se priorizó
encaje con el stack, procedencia identificable, portabilidad y alcance pequeño.
No es un ranking universal ni una garantía de calidad científica.

## Skills instaladas en el repositorio

| Skill | Origen | Usarla cuando |
| --- | --- | --- |
| vercel-react-best-practices | Vercel | Implementar/revisar React y Next.js: carga, render y consultas |
| web-design-guidelines | Vercel | Revisar UI, accesibilidad y experiencia de navegación |
| cosmic-spherex-pipeline | Creada para este proyecto | IRSA, FITS, WCS, compatibilidad y movimiento aparente |
| cosmic-api-contracts | Creada para este proyecto | FastAPI, contratos, jobs, persistencia y límites del copiloto |
| cosmic-reproducible-experiments | Creada para este proyecto | Notebooks, evaluación, baseline e inyecciones etiquetadas |

Las tres skills del proyecto proceden de la arquitectura y requisitos del equipo;
no son skills oficiales de NASA ni de Astropy. Una skill guía el trabajo: no instala
la librería científica, implementa un detector ni demuestra precisión por sí misma.

Se consultó el catálogo disponible con skill-installer. El repositorio
[openai/skills](https://github.com/openai/skills) declara estar obsoleto y remite a
[openai/plugins](https://github.com/openai/plugins). Por eso no se instalaron copias
antiguas de skills de notebooks, CI o seguridad desde ese catálogo. Las opciones
actuales revisadas incluyen dependencias de otros plugins; para este alcance se
prefirieron workflows locales sin exigir servicios adicionales.

Las dos skills externas proceden de
[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills), fijadas al
commit `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62`. El manifiesto
`.agents/skills-sources.json` conserva rutas y revisión. Se preservan sus metadatos
de autoría/licencia; no atribuir estas guías al equipo Cosmic Hunter AI.
Para actualizar, revisar primero el diff upstream y después sustituir de forma
deliberada la revisión del manifiesto. No descargar y ejecutar automáticamente código
de terceros cada vez que se abra el proyecto.

`web-design-guidelines` consulta una guía remota vigente al revisar interfaces;
la revisión del paquete está fijada, pero ese contenido remoto puede cambiar.
Registrar URL/revisión consultada si se necesita reproducir una auditoría.

## Activación

El [formato de personalización de Codex](https://learn.chatgpt.com/docs/customization/overview)
admite AGENTS.md y skills del repositorio en `.agents/skills`.
La [documentación de Cursor](https://cursor.com/docs/skills) también reconoce esa
carpeta. Así se mantiene una sola copia por skill. Abrir esta raíz como proyecto en
ambas herramientas; las skills se esperan disponibles en un nuevo turno/sesión tras
redescubrir el repositorio. Comprobar la lista del editor: aún no se ha verificado
la carga en una sesión de Cursor en esta máquina.

Codex: invocar por nombre, por ejemplo `$cosmic-spherex-pipeline`.
Cursor: escribir `/` y buscar el nombre de la skill. Si una versión antigua no la
descubre, se puede pedir que lea directamente el SKILL.md correspondiente sin
duplicar archivos. Actualizar el editor cuando se necesite descubrimiento nativo.

## Reglas

AGENTS.md es la guía central para ambos asistentes: límites de arquitectura,
integridad científica, seguridad, comandos de comprobación y coordinación.
Las [reglas de Cursor](https://cursor.com/docs/rules) se guardan en `.cursor/rules`:

- project.mdc: siempre activa; conduce a la guía central.
- science.mdc: se adjunta al trabajar en astronomy, detection o notebooks.
- backend.mdc: API, workers, AI, SQL y contratos.
- frontend.mdc: interfaz Next.js y visualizaciones científicas.

Las guías Vercel no cambian decisiones del proyecto: usar TanStack Query aunque un
ejemplo recomiende SWR. No aplicar consejos de rendimiento a una versión incompatible
sin comprobarla. Las reglas y skills orientan al modelo; no sustituyen CI,
autorización, restricciones de red o protección de ramas.

## Reparto de trabajo recomendado

Codex puede encargarse de backend, pipeline, contratos y evaluación; Cursor, de
interfaz e integración con ese contrato. Ambos pueden hacer cualquiera de esas tareas.
Importa asignar archivos distintos y un responsable del contrato compartido.

En el estado actual todavía no hay commit base. Trabajar por turnos en esta carpeta
hasta crear el primer commit. Después se pueden usar ramas/worktrees separados para
trabajo simultáneo. Evitar dos agentes escribiendo el mismo archivo o uv.lock.

Cada entrega debe indicar objetivo logrado, archivos modificados, contrato generado,
checks ejecutados y limitaciones. El siguiente editor debe inspeccionar estado/diff
antes de continuar. No confundir cambios presentes con commits o contenido publicado.

## Ejemplos de solicitudes

```text
Codex: usa $cosmic-spherex-pipeline para implementar una consulta IRSA acotada.
Lee AGENTS.md. Conserva procedencia y prueba fallos del archivo. No descargues
regiones grandes ni inventes resultados si no hay acceso al servicio.
```

```text
Cursor: lee AGENTS.md y usa vercel-react-best-practices para implementar el
explorador en apps/web consumiendo el contrato OpenAPI existente. Muestra estados
vacíos y errores reales; no rellenes observaciones con datos ficticios.
```

```text
Codex: usa $cosmic-reproducible-experiments para evaluar el baseline disponible.
Declara datos y particiones, ejecuta desde cero y separa resultados sintéticos
de recuperación con objetos conocidos. No afirmes métricas sin ejecución.
```
