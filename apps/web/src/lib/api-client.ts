import type { components } from "@/lib/schema";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type SearchResponse = components["schemas"]["SearchResponse"];
export type ExampleResponse = components["schemas"]["ExampleResponse"];
export type Observation = components["schemas"]["Observation"];
export type SummaryResponse = components["schemas"]["SummaryResponse"];
export type SkySearchQuery = components["schemas"]["SkySearchQuery"];
export type ExampleSlug = ExampleResponse["slug"];

export class ApiError extends Error {
  readonly status: number;
  readonly requestId: string | null;

  constructor(message: string, status: number, requestId: string | null = null) {
    super(message);
    this.status = status;
    this.requestId = requestId;
  }
}

export type Liveness = {
  status: string;
  stage: string;
};

export function absoluteApiUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return null;
  }
}

function requestIdOf(payload: unknown): string | null {
  if (payload && typeof payload === "object" && "request_id" in payload && typeof payload.request_id === "string") {
    return payload.request_id;
  }
  return null;
}

function errorFor(payload: unknown, status: number): ApiError {
  const requestId = requestIdOf(payload);
  if (status === 422) {
    return new ApiError("Those coordinates are outside the allowed range.", status, requestId);
  }
  if (status === 502 || status === 504) {
    return new ApiError("The archive did not answer.", status, requestId);
  }
  if (status === 503) {
    return new ApiError("AI summary unavailable", status, requestId);
  }
  return new ApiError("The request could not be completed.", status, requestId);
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(absoluteApiUrl(path), { cache: "no-store", ...init });
  const payload = await readJson(response);
  if (!response.ok) {
    throw errorFor(payload, response.status);
  }
  return payload as T;
}

export function getLiveness(): Promise<Liveness> {
  return requestJson<Liveness>("/health/live");
}

export function listExamples(): Promise<ExampleResponse[]> {
  return requestJson<ExampleResponse[]>("/v1/examples");
}

export function getExample(slug: string): Promise<ExampleResponse> {
  return requestJson<ExampleResponse>(`/v1/examples/${encodeURIComponent(slug)}`);
}

export function searchSky(query: SkySearchQuery): Promise<SearchResponse> {
  return requestJson<SearchResponse>("/v1/sky/search", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(query),
  });
}

export function summarizeExample(slug: string): Promise<SummaryResponse> {
  return requestJson<SummaryResponse>(`/v1/examples/${encodeURIComponent(slug)}/summary`, {
    method: "POST",
  });
}
