# Protocolo científico previsto

No hay detector ni métricas obtenidas en esta fase.

Baseline: extracción de fuentes con fondo/ruido/máscaras, transformación WCS,
asociación con límites de velocidad explícitos y ajuste de movimiento en plano
tangente/esfera. Conservar covarianzas, residuos, épocas y calibración. Comparar
fotometría solo con respuesta espectral compatible; reproyectar no iguala PSFs.
Exigir una tercera época o evidencia adicional para robustecer asociaciones; tratar
paralaje, observador, confusión de fuentes y variabilidad como explicaciones alternativas.

Validación: separar regiones, épocas y objetos de entrenamiento, ajuste y evaluación;
evitar versiones reprocesadas de una misma exposición entre particiones. Fijar
semillas, checksum de datasets, commit, entorno, umbrales y configuración del experimento.

Conjunto A: objetos conocidos con efemérides y posición del observador. Conjunto B:
inyecciones etiquetadas **synthetic** sobre imágenes reales, con PSF/ruido apropiados.
Conjunto C: controles estáticos y artefactos. Nunca presentar inyecciones como hallazgos.

Métricas previstas: precision=TP/(TP+FP), recall=TP/(TP+FN), falsos positivos por
área/época, error astrométrico angular, error/tasa de asociación, residuos de ajuste,
rendimiento por SNR y magnitud calibrada, tiempo y memoria por etapa. Definir
tolerancias y correspondencias uno a uno antes de evaluar; incluir intervalos de
confianza, cobertura y casos excluidos. Denominadores cero se reportan como indefinidos.

Puntuación heurística explicable no es probabilidad calibrada. Comparar IA contra
baseline en test separado antes de afirmar mejoras. Catálogo sin coincidencia,
servicio caído y consulta fallida son resultados distintos; ninguno confirma un planeta.
Cada expediente incluye fuentes originales, versiones, parámetros, incertidumbres,
resultados externos, limitaciones y estado humano. Gemini solo explica ese expediente.
