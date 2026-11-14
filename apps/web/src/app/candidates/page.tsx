import Link from "next/link";

import { PendingContract } from "@/components/pending-contract";
import { PENDING_ROUTES } from "@/lib/pending-routes";

export default function CandidatesPage() {
  return (
    <div className="space-y-6">
      <header className="max-w-3xl">
        <h1 className="font-serif text-4xl tracking-tight">Candidates</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          A candidate is a review target, not a confirmed discovery. Filters stay idle until the
          list endpoint exists.
        </p>
      </header>
      <div className="flex flex-wrap gap-3">
        <label className="text-sm text-muted">
          Sort
          <select disabled className="mt-1 block rounded-md border border-line bg-void px-3 py-2">
            <option>Unavailable</option>
          </select>
        </label>
        <label className="text-sm text-muted">
          Validation state
          <select disabled className="mt-1 block rounded-md border border-line bg-void px-3 py-2">
            <option>Unavailable</option>
          </select>
        </label>
      </div>
      <p className="text-sm text-muted" role="status">
        No candidates. {PENDING_ROUTES.candidates} has not been implemented.
      </p>
      <PendingContract
        route={PENDING_ROUTES.candidates}
        consequence="The dossier, uncertainties, and export stay closed until a real candidate id is returned."
      />
      <p className="text-sm text-muted">
        Detail pages accept an id in the URL, for example{" "}
        <Link className="text-ember underline" href="/candidates/example">
          /candidates/example
        </Link>
        , and still refuse to invent measurements.
      </p>
    </div>
  );
}
