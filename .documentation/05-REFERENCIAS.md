# Referencias y ruta de lectura

Revisión documental: 14 de noviembre de 2026. Los enlaces no equivalen a endpoints probados. Se enlazan los originales en lugar de redistribuir documentación completa; revisar atribución y licencia antes de copiar código o recursos.

## Reto y contexto

- [Enunciado oficial](https://www.spaceappschallenge.org/2026/challenges/planet-x-and-spherex/): autoridad sobre el reto. Error 502 durante la revisión.
- [Reproducción del enunciado en HackAthlone](https://hackathlone.com/challenges/planet-x-and-spherex): consultada; objetivos y consideraciones. Fuente secundaria; confirmar cambios con el original.
- [Página oficial de equipo con resumen del reto](https://www.spaceappschallenge.org/2026/find-a-team/lsp26/): consultada previamente; corroboración del objetivo general, no instrucciones del equipo actual.
- [Sede Cochabamba](https://spaceappschallenge-cbba.com/): contexto local; el proyecto tratado aquí es el internacional Planet X and SPHEREx. Visualizador distrital y alertas en cuencas fueron alternativas discutidas, no alcance de este proyecto.

## Recursos técnicos primarios consultados

- [Portal SPHEREx en IRSA](https://irsa.ipac.caltech.edu/Missions/spherex.html): entrada al archivo.
- [Acceso a datos](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access/): APIs, colecciones y métodos de acceso; disponibilidad intermitente al revisar.
- [Espejo de documentación de acceso](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/): misma institución; consultado durante el chat.
- [Introducción a imágenes espectrales](https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/): punto de partida para código y FITS.
- [Servicio de recortes](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/cutout_tool.html): parámetros y métodos de recorte.
- [Source Discovery Tool](https://caltech-ipac.github.io/irsa-tutorials/spherex-source-discovery-tool-demo/): procesamiento y exploración más avanzados.
- [Preguntas frecuentes del explorador](https://irsa.ipac.caltech.edu/onlinehelp/spherex/spherex/faq.html): consultas y alternativas de acceso.

## Recursos adicionales enlazados; revisar antes de usarlos

- [Repositorio de tutoriales IRSA](https://github.com/Caltech-IPAC/irsa-tutorials): código fuente y entornos. Revisar licencia y fecha del commit; el código fuente puede diferir del sitio publicado.
- [Repositorio de pipelines SPHEREx](https://github.com/Caltech-IPAC/spherex-pipelines): contexto del procesamiento del proveedor; no necesario para el primer MVP.
- [Astroquery IRSA](https://astroquery.readthedocs.io/en/latest/ipac/irsa/irsa.html): cliente de consultas.
- [Astropy FITS](https://docs.astropy.org/en/stable/io/fits/): lectura de datos.
- [Astropy WCS](https://docs.astropy.org/en/stable/wcs/): coordenadas de imágenes.
- [PyVO](https://pyvo.readthedocs.io/en/latest/): cliente de protocolos astronómicos.
- [WiseView](https://byw.tools/wiseview): inspiración para experiencia de comparación; usa otra misión.

## Orden recomendado

Enunciado → portal IRSA → acceso → notebook introductorio → recortes → prueba real mínima → procesamiento/visor → Source Discovery Tool solo si aporta al alcance.

No usar como referencia el enlace `https://caltech-ipac.github.io/spherex-quickstart/`: se intentó en la investigación pero no fue accesible. El tutorial válido utilizado es `irsa-tutorials/spherex-intro/`.

## Mantener actualizado

Por cada recurso nuevo, registrar URL, institución, fecha de consulta, uso concreto y si se probó operativamente. Si dos documentos discrepan sobre releases o colecciones, consultar el listado vigente y guardar evidencia de la elección.
