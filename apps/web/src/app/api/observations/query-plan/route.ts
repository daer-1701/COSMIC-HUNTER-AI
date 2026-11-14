import { proxyToApi } from "@/lib/upstream";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.text();
  return proxyToApi("/v1/observations/query-plan", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });
}
