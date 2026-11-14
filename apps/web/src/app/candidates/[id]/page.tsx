import { PendingContract } from "@/components/pending-contract";
import { PENDING_ROUTES } from "@/lib/pending-routes";

export default async function CandidateDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="space-y-6">
      <header>
        <p className="font-mono text-xs text-ember uppercase">Not a confirmed discovery</p>
        <h1 className="mt-2 font-serif text-4xl tracking-tight">Candidate</h1>
        <p className="mt-2 font-mono text-sm text-muted">Identifier from the URL: {id}</p>
      </header>
      <dl className="grid gap-3 sm:grid-cols-2">
        {[
          ["Coordinates", "Not returned"],
          ["Observations", "Not returned"],
          ["Measurements", "Not returned"],
          ["Uncertainties", "Not returned"],
          ["Validation", "Unavailable"],
          ["Visual evidence", "Preview not available"],
        ].map(([term, detail]) => (
          <div key={term} className="rounded-lg border border-line bg-panel p-4">
            <dt className="text-xs tracking-wide text-muted uppercase">{term}</dt>
            <dd className="mt-2 text-sm">{detail}</dd>
          </div>
        ))}
      </dl>
      <button
        type="button"
        disabled
        className="rounded-full border border-line px-4 py-2 text-sm opacity-50"
      >
        Export dossier
      </button>
      <PendingContract
        route={PENDING_ROUTES.candidate}
        consequence="Export uses the evidence route and stays disabled. This identifier was not loaded from a catalog."
      />
    </div>
  );
}
