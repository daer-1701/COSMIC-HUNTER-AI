const API_BASE_URL = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";

export async function proxyToApi(path: string, init?: RequestInit): Promise<Response> {
  try {
    const upstream = await fetch(new URL(path, API_BASE_URL), {
      ...init,
      cache: "no-store",
      redirect: "error",
    });
    const contentType = upstream.headers.get("content-type") ?? "application/json";
    return new Response(upstream.body, {
      status: upstream.status,
      headers: { "content-type": contentType },
    });
  } catch {
    return Response.json(
      {
        detail:
          "The API process is not reachable. Start it with: uv run uvicorn cosmic_api.main:app --reload",
      },
      { status: 503 },
    );
  }
}
