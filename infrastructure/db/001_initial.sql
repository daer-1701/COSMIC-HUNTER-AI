-- Bootstrap for NEW local databases. Adopt Alembic before evolving persistent deployments.
BEGIN;
CREATE TABLE sky_regions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ra_deg double precision NOT NULL CHECK (ra_deg >= 0 AND ra_deg < 360),
  dec_deg double precision NOT NULL CHECK (dec_deg BETWEEN -90 AND 90),
  radius_deg double precision NOT NULL CHECK (radius_deg > 0 AND radius_deg <= 180)
);
CREATE TABLE observations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  archive_id text NOT NULL, collection text NOT NULL, release text NOT NULL,
  pipeline_version text NOT NULL, calibration_version text NOT NULL,
  start_mjd double precision NOT NULL CHECK (start_mjd >= 0),
  end_mjd double precision NOT NULL CHECK (end_mjd >= start_mjd),
  time_scale text NOT NULL, detector text NOT NULL,
  spectral_metadata jsonb NOT NULL, quality_metadata jsonb NOT NULL,
  original_metadata jsonb NOT NULL,
  retrieved_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (archive_id, collection, pipeline_version, calibration_version)
);
CREATE INDEX observations_epoch_idx ON observations(start_mjd, end_mjd);
CREATE TABLE fits_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  observation_id uuid NOT NULL REFERENCES observations(id),
  source_url text NOT NULL, object_key text NOT NULL UNIQUE,
  sha256 text NOT NULL CHECK (sha256 ~ '^[a-f0-9]{64}$'),
  size_bytes bigint NOT NULL CHECK (size_bytes > 0),
  hdu_manifest jsonb NOT NULL, original_header jsonb NOT NULL,
  UNIQUE (observation_id, sha256)
);
CREATE TABLE processing_jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id uuid NOT NULL REFERENCES sky_regions(id),
  idempotency_key text NOT NULL UNIQUE,
  status text NOT NULL CHECK (status IN ('queued','running','succeeded','failed','cancelled')),
  code_commit text NOT NULL, environment_digest text NOT NULL,
  parameters jsonb NOT NULL, error_code text,
  created_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz,
  CHECK (completed_at IS NULL OR completed_at >= created_at)
);
CREATE INDEX processing_jobs_queue_idx ON processing_jobs(status, created_at);
CREATE TABLE job_inputs (
  job_id uuid REFERENCES processing_jobs(id),
  fits_file_id uuid REFERENCES fits_files(id),
  PRIMARY KEY (job_id, fits_file_id)
);
CREATE TABLE detected_sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id uuid NOT NULL REFERENCES processing_jobs(id),
  fits_file_id uuid NOT NULL REFERENCES fits_files(id),
  ra_deg double precision NOT NULL CHECK (ra_deg >= 0 AND ra_deg < 360),
  dec_deg double precision NOT NULL CHECK (dec_deg BETWEEN -90 AND 90),
  epoch_mjd double precision NOT NULL CHECK (epoch_mjd >= 0),
  covariance_arcsec2 jsonb NOT NULL, snr double precision NOT NULL,
  measurement jsonb NOT NULL, flags jsonb NOT NULL,
  UNIQUE (id, job_id)
);
CREATE INDEX detected_sources_position_idx ON detected_sources(ra_deg, dec_deg);
CREATE INDEX detected_sources_input_idx ON detected_sources(fits_file_id);
CREATE TABLE candidate_objects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id uuid NOT NULL REFERENCES processing_jobs(id),
  status text NOT NULL DEFAULT 'unreviewed'
    CHECK (status IN ('unreviewed','under_review','known_object','likely_artifact','needs_followup')),
  priority_score double precision CHECK (priority_score BETWEEN 0 AND 1),
  score_version text, explanation jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (id, job_id)
);
CREATE INDEX candidates_review_idx ON candidate_objects(status, priority_score DESC);
CREATE TABLE candidate_detections (
  candidate_id uuid NOT NULL, source_id uuid NOT NULL, job_id uuid NOT NULL,
  PRIMARY KEY (candidate_id, source_id),
  FOREIGN KEY (candidate_id, job_id) REFERENCES candidate_objects(id, job_id),
  FOREIGN KEY (source_id, job_id) REFERENCES detected_sources(id, job_id)
);
CREATE TABLE motion_estimates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id uuid NOT NULL REFERENCES candidate_objects(id),
  method_version text NOT NULL, reference_epoch_mjd double precision NOT NULL,
  mu_ra_cosdec_arcsec_day double precision NOT NULL,
  mu_dec_arcsec_day double precision NOT NULL,
  covariance jsonb NOT NULL, residuals jsonb NOT NULL, assumptions jsonb NOT NULL
);
CREATE TABLE catalog_matches (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id uuid NOT NULL REFERENCES candidate_objects(id),
  service text NOT NULL, service_version text NOT NULL,
  query_parameters jsonb NOT NULL, queried_at timestamptz NOT NULL DEFAULT now(),
  outcome text NOT NULL CHECK (outcome IN ('matched','no_match','unavailable','error')),
  response_evidence jsonb NOT NULL
);
CREATE TABLE validation_reports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id uuid NOT NULL REFERENCES candidate_objects(id),
  version integer NOT NULL CHECK (version > 0), object_key text NOT NULL,
  evidence_manifest jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (candidate_id, version)
);
CREATE TABLE review_users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_subject text NOT NULL UNIQUE,
  role text NOT NULL CHECK (role IN ('reviewer','moderator','admin'))
);
CREATE TABLE candidate_reviews (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id uuid NOT NULL REFERENCES candidate_objects(id),
  user_id uuid NOT NULL REFERENCES review_users(id),
  verdict text NOT NULL CHECK (verdict IN ('plausible_motion','artifact','uncertain')),
  rationale text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (candidate_id, user_id)
);
CREATE TABLE ai_usage_records (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id uuid REFERENCES candidate_objects(id),
  request_key text NOT NULL UNIQUE, provider_model text NOT NULL,
  pricing_version text NOT NULL,
  input_tokens integer CHECK (input_tokens >= 0),
  output_tokens integer CHECK (output_tokens >= 0),
  reserved_usd numeric(12,8) NOT NULL CHECK (reserved_usd >= 0),
  charged_usd numeric(12,8) CHECK (charged_usd >= 0),
  status text NOT NULL CHECK (status IN ('reserved','settled','failed','unknown')),
  evidence_hash text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
COMMIT;
