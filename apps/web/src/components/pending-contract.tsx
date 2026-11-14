import { PENDING_ROUTES } from "@/lib/pending-routes";

export function PendingContract({
  route,
  consequence,
}: {
  route: string;
  consequence: string;
}) {
  return (
    <section className="rounded-lg border border-dashed border-line bg-panel/70 p-5">
      <p className="font-mono text-xs tracking-wide text-ember uppercase">Waiting on the API</p>
      <p className="mt-3 font-mono text-sm text-ink">{route}</p>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">{consequence}</p>
      <p className="mt-3 text-sm text-muted">
        This route is described in the project contract and is not in the running OpenAPI document.
        Nothing here is filled with a placeholder detection.
      </p>
    </section>
  );
}

export function contractFor(key: keyof typeof PENDING_ROUTES): string {
  return PENDING_ROUTES[key];
}
