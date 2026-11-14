# Three-person project plan

This plan covers the full project brief, not just the MVP. Replace numbered roles
with team members' names once assigned. It does not assume equal experience or
availability: adjust workload after the first functional vertical slice. No dates
are assigned without knowing available time. Actual implementation status remains
in README.md and docs/roadmap.md.

## Primary owners

| Person | Role | Accountable outcome |
| --- | --- | --- |
| 1 | Data science and astronomy | Reproducible measurements, detection, and validation |
| 2 | Backend, integration, and infrastructure | Reliable services, persistence, execution, and copilot |
| 3 | Frontend, experience, and communication | Understandable public exploration and a verifiable demonstration |

Each person implements and tests their area using Codex or Cursor. Editors are shared
tools, not additional owners. Person 2 coordinates integration; Person 1 reviews
scientific claims; Person 3 coordinates competition delivery. Write all project
documentation, interface text, reports, and presentation materials in English.

## Person 1 — Science, data, and detection

1. **P1-01: scientific requirements and data selection.** Review pending official
   requirements/resources, distinguish mandatory requirements from extensions, choose
   a region, and verify temporally/spectrally compatible visits. Record versions.
2. **P1-02: IRSA connector.** SIA2 queries, VOTable parsing, errors/overflow, product
   discovery and bounded downloads, checksums, and provenance manifests.
3. **P1-03: FITS processor.** Inspect HDUs, WCS, epochs, units, masks, noise, sources,
   PSF, spectral compatibility, alignment, and reprojection. Distinguish scientific
   data products from visualization previews.
4. **P1-04: baseline detector.** Extract sources, associate across epochs, fit apparent
   motion with uncertainties, retain residuals, and reject inconsistencies. Evaluate
   image differencing/shift-and-stack only when supported by the products.
5. **P1-05: astronomical validation.** Appropriate catalogs and ephemerides with correct
   epoch and observer; distinguish match, non-match, error, and unavailability. Define
   scientific dossier content and interpretation states.
6. **P1-06: evaluation and ranking.** Known objects, controls, synthetic injections,
   leakage-free splits, precision/recall/false positives, astrometric/temporal errors,
   performance by SNR/magnitude, and processing cost. Start with explainable ranking;
   train models only with appropriate labels and compare against a held-out baseline.
   Document negative results too.

**Owned paths:** `services/astronomy/`, `services/detection/`, `notebooks/`,
`docs/research.md`, `docs/science.md`, and small `data/` manifests.
Scientific validation can initially be a module within detection; a new microservice
is unnecessary. Keep scientific classification within `services/ai/` in files separate
from the copilot, agreed with Person 2.

**Owned tests:** spherical geometry, units/time, masks and incompatible products,
ambiguous associations, known-object recovery, and reproducible evaluation.

**Exit criterion:** another team member reproduces a run with identified real inputs,
obtains the measurements, and understands their limitations. Do not require invented
accuracy targets or confuse the absence of candidates with implementation failure.

**Skills:** cosmic-spherex-pipeline and cosmic-reproducible-experiments.

## Person 2 — Backend, infrastructure, and copilot

1. **P2-01: contracts and integration.** Maintain architecture, FastAPI/Pydantic contracts,
   OpenAPI export, and documented errors. Agree on Python pipeline interfaces with
   Person 1 and consumption contracts with Person 3 before integration.
2. **P2-02: persistence.** SQLAlchemy, PostgreSQL, migrations, constraints, and indexes;
   integrate all 13 entities and provenance. Store originals, derivatives, and dossiers
   in S3 with authorized downloads and persisted references.
3. **P2-03: asynchronous execution.** Redis/Celery, persisted jobs, reliable enqueue,
   idempotency, bounded retries, cancellation, progress, and failure recovery. Wrap
   Person 1's functions without duplicating scientific algorithms inside endpoints.
4. **P2-04: product API and collaboration.** Search, observations, previews, comparison,
   candidates, trajectories, dossiers, and reviews. Authentication, per-resource
   authorization, roles, quotas, and moderation; votes do not confirm discoveries.
5. **P2-05: backend Gemini.** Verify model/prices at implementation, atomically reserve
   the configurable maximum budget, control tokens/cache/rate limits, and log usage.
   Summaries must reference evidence, protect keys, and reject unsupported claims.
   Do not make paid calls without usage authorization.
6. **P2-06: operations and technical publication.** Docker/Compose, CI, environment
   configuration, logs, metrics, secrets, backups/restoration, and deployment preparation.
   Configure remotes/protections and deploy when authorization and a target are available.

**Owned paths:** `services/api/`, `services/workers/`, copilot files in `services/ai/`,
`infrastructure/`, `.github/`, `compose.yaml`, `.env.example`, `pyproject.toml`,
`uv.lock`, `scripts/export_openapi.py`, `packages/shared/openapi.json`, and
architecture/API/data/Git documentation. OpenAPI is generated, never manually edited.

**Owned tests:** contracts, authorization, PostgreSQL transactions, storage, duplicated/
failed jobs, provider outages, and budget ceilings without real calls. Integration
tests across pipeline, workers, and API.

**Exit criterion:** a clean installation runs the workflow and persists evidence;
failures/restarts do not silently duplicate results or cause unreserved spending.
Distinguish CI and real integration from unit tests or configurations not yet started.

**Skill:** cosmic-api-contracts.

## Person 3 — Frontend, UX, user QA, and delivery

1. **P3-01: web application.** Next.js App Router, TypeScript, Tailwind, and shadcn/ui;
   navigation, accessible dark design, and an OpenAPI-generated client. Use TanStack
   Query for remote data; Zustand only when shared local state is necessary.
2. **P3-02: explorer.** Aladin Lite, RA/Dec, region, dates, and spectral selection;
   observation lists, metadata, provenance, and API-mediated downloads.
3. **P3-03: comparison and trajectories.** Blink/before-after with pause, dates, scale,
   orientation, and compatibility warnings. Use Plotly for backend-provided trajectories,
   residuals, and uncertainties; do not recalculate scientific measurements in the UI.
4. **P3-04: candidates and dossier.** Dashboard, filters, explained priorities, detail,
   original observations, and exportable reports. Explicitly show empty states, errors,
   and synthetic data; never populate views with invented detections.
5. **P3-05: copilot and review.** Questions/summaries with references, quota status,
   and evidence; user evaluations and moderation flow. Consume API authorization and
   states without exposing provider keys in the browser.
6. **P3-06: testing and communication.** End-to-end workflows, accessibility, keyboard,
   and preview performance tests; landing page, usage documentation, demo script,
   originality report, and English presentation. Person 1 reviews scientific claims/
   results; Person 2 reviews technical instructions and deployment.

**Owned paths:** `apps/web/`, frontend dependencies/lockfile, generated TypeScript
client in a path separate from OpenAPI, web tests, and demo/presentation documents.
Coordinate README changes with Person 2 to avoid simultaneous edits.

**Owned tests:** search → comparison → candidate → evidence → review; visible
authorization, real API failures, keyboard, reduced motion, and lazy Aladin/Plotly
loading. Use labeled fixtures during integration. Final validation needs the real
API and data; do not confuse test mode with mission results.

**Exit criterion:** someone outside the development team can follow the demonstration,
identify sources/dates/uncertainties, and understand that a candidate is not a confirmed discovery.

**Skills:** vercel-react-best-practices and web-design-guidelines.

## Integration order and dependencies

| Milestone | Person 1 | Person 2 | Person 3 | Exit condition |
| --- | --- | --- | --- | --- |
| A: agreements | Region/products and provenance | Schemas, IDs, units, and errors | Wireframes and states | Python/HTTP contracts agreed; official requirements reviewed or uncertainty recorded |
| B: real data | Queries and compatible FITS | Persistence, search, and previews | Explorer and metadata | View traceable real products from one region in the web app |
| C: comparison | WCS, PSF/masks, and alignment | Processing job and results | Temporal comparator | Two comparable visits, or an explained exclusion without forcing comparison |
| D: investigation | Baseline, validation, and metrics | Jobs/candidates/dossiers | Detections, detail, and trajectories | Reproducible run with evidence, including known-object controls |
| E: extensions | Ranking; AI if viable | Gemini, identity, and reviews | Copilot and collaboration | Quotas, references, and permissions checked; no automatic discovery claims |
| F: delivery | Scientific report review | Installation, CI, and operations | Demo, originality, and presentation | Complete verified workflow with visible limitations and reviewed deliverables |

Milestone D defines the scientific MVP. E and F complete the project extensions.
Do not silently drop them when time is limited; record and agree on remaining scope.
While awaiting data, Person 2 can build persistence and Person 3 can build navigation/
accessibility. A simulated workflow cannot substitute for validation with real data.

## Contracts all three must agree on

- Person 1 → 2: Python structures for observations, artifacts, detections, motion,
  and validation, with explicit units/epochs, errors, and provenance.
- Person 2 → 3: versioned OpenAPI, pagination, IDs, job states, preview URLs,
  coordinates, uncertainties, and error codes; generate the client from that contract.
- Person 3 → 1/2: concrete comparator/chart requirements. Request missing measurements
  rather than silently inferring them in the browser.

Notify consumers before incompatible changes and update contracts, tests, and
documentation in the same handoff. All three review scientific semantics; Person 2
owns the generated OpenAPI file and coordinates its integration.

## Coverage of the brief's 20 deliverables

The owner ensures delivery; support means scoped collaboration or review, not
simultaneous ownership of the same files.

| # | Deliverable | Owner | Support |
| --- | --- | --- | --- |
| 1 | Technical architecture | 2 | 1 and 3 |
| 2 | Complete repository structure | 2 | 1 and 3 within their modules |
| 3 | Database model | 2 | 1: scientific semantics |
| 4 | Documented backend | 2 | 3: consumption |
| 5 | IRSA connector | 1 | 2: integration/storage |
| 6 | FITS processor | 1 | 3: preview requirements |
| 7 | Detection engine | 1 | 2: execution |
| 8 | Candidate validation | 1 | 2: persistence |
| 9 | Next.js platform | 3 | 2: contract |
| 10 | Temporal comparator | 3 | 1: compatibility, 2: results |
| 11 | Astronomical viewer | 3 | 1: coordinates and units |
| 12 | Gemini integration | 2 | 1: scientific limits, 3: UI |
| 13 | Review module | 2 | 3: UI, 1: criteria |
| 14 | Automated tests | 2: CI and integration | 1: science, 3: frontend/E2E |
| 15 | Docker Compose | 2 | 3: web service |
| 16 | Technical README | 2 | 3: usage, 1: reproduction |
| 17 | Scientific documentation | 1 | 2 and 3: review |
| 18 | Originality report | 3 | 1: scientific comparison, 2: technical comparison |
| 19 | Demo script | 3 | 1 and 2: real workflow |
| 20 | English presentation | 3 | 1 and 2: review |

## Collaboration and workload rules

1. Use task branches and separate clones/worktrees for simultaneous work. Follow
   AGENTS.md: do not overwrite others' changes or force repository history.
2. Person 2 coordinates Python dependencies and shared contracts; Person 3 owns the
   web lockfile. Each person proposes only dependencies needed for the task.
3. Each PR states its P1/P2/P3 task, inputs/outputs, tests, and limitations. Another
   member reviews before integration. Shared documentation has one writer at a time.
4. Close each milestone with an integrated workflow, not three disconnected demos.
   Briefly review data/contract blockers each workday.
5. P1-04 through P1-06 carry concentrated scientific risk. At those milestones,
   Person 2 helps with runners, cache, and automated reports; Person 3 helps with
   diagnostic visualization and artifact inspection under Person 1's criteria.
   Do not postpone all evaluation to the end.
6. For final delivery, Person 2 resolves integration/deployment; Person 1 verifies
   results; Person 3 prepares demonstration materials. Publication and paid calls
   still require user authorization; this allocation alone does not grant it.
