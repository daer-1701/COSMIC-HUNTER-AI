import { PendingContract } from "@/components/pending-contract";
import { PENDING_ROUTES } from "@/lib/pending-routes";

export default function InvestigationsPage() {
  return (
    <div className="space-y-6">
      <header className="max-w-3xl">
        <h1 className="font-serif text-4xl tracking-tight">Investigations</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          Past jobs will appear here after they are persisted. An empty history means no run has
          been stored, not that the sky was searched.
        </p>
      </header>
      <p role="status" className="text-sm text-muted">
        No investigations.
      </p>
      <PendingContract
        route={PENDING_ROUTES.jobs}
        consequence="Job state, progress, and failure recovery are owned by the backend."
      />
    </div>
  );
}
