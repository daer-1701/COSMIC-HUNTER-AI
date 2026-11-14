/** Routes documented in docs/api.md that are absent from the running OpenAPI contract. */
export const PENDING_ROUTES = {
  searches: "POST /v1/observation-searches",
  observations: "GET /v1/observations",
  jobs: "GET /v1/jobs/{id}",
  candidates: "GET /v1/candidates",
  candidate: "GET /v1/candidates/{id}",
  evidence: "GET /v1/candidates/{id}/evidence",
  reviews: "POST /v1/candidates/{id}/reviews",
  summary: "POST /v1/candidates/{id}/summary",
} as const;
