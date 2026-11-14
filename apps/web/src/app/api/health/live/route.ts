import { proxyToApi } from "@/lib/upstream";

export const dynamic = "force-dynamic";

export function GET() {
  return proxyToApi("/health/live");
}
