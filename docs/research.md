# Sources, scope, and assumptions

Research performed on 2026-11-14. No scientific observations were downloaded.

## Requirements and pending verification

The [Cochabamba event site](https://spaceappschallenge-cbba.com/#retos) describes a
public SPHEREx visualization tool for comparing positions across dates. It links to
the [official Planet X and SPHEREx challenge](https://www.spaceappschallenge.org/2026/challenges/planet-x-and-spherex/).
The official page returned HTTP 502 on two attempts. The full statement, mandatory
resources, deliverables, and judging rubric therefore remain unverified. Recheck them
before finalizing competition scope. The local event site does not replace the official
rubric. Do not attribute the team's 20 deliverables or seven engines to the official challenge.

Team extensions: Autonomous Moving Object Investigator, detection, classification,
evidence dossiers, catalog validation, Gemini, collaboration, and metrics. The
architecture incorporates these proposals through incremental implementation.

## Data selection

[IRSA releases](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-releases/)
recommends DR1 and QR3 for new work; they supersede QR2. Always record release and
calibration, and do not mix versions without a compatibility study.

[IRSA access documentation](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access/)
describes SIA2 at `https://irsa.ipac.caltech.edu/SIA`, including `spherex_dr1` and
`spherex_qr3`; the initial query builder supports only these collections. Downloading
and parsing VOTable responses remain phase 2 work.

Team decision: start with individual exposures to preserve epochs. Use aggregated
cubes only for context until their suitability for temporal analysis is demonstrated.
Verify compatible repeat visits per region. A detector label is not assumed to mean
a uniform spectral band at every pixel.

## Primary technical sources

- [IRSA mission portal](https://irsa.ipac.caltech.edu/Missions/spherex.html).
- [SPHEREx products](https://github.com/Caltech-IPAC/spherex-archive-documentation/blob/main/documentation/spherex_data_products.md): inspect HDUs and calibrations before implementing readers.
- [Next.js installation](https://nextjs.org/docs/app/getting-started/installation): reference for frontend setup.
- [Celery Redis documentation](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html): repeated delivery and timeouts.

Unverified assumptions: motion sensitivity over a given interval, candidate count,
useful temporal coverage, astrometric quality, and false-positive reduction. Do not
publish figures before running experiments.
