import { PendingContract } from "@/components/pending-contract";
import { PENDING_ROUTES } from "@/lib/pending-routes";

export default function ReviewPage() {
  return (
    <div className="space-y-6">
      <header className="max-w-3xl">
        <h1 className="font-serif text-4xl tracking-tight">Review</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          A human review records a judgment. It does not confirm a discovery, and neither does a
          vote or a model summary.
        </p>
      </header>
      <form className="max-w-xl space-y-3">
        <label className="block text-sm">
          Note
          <textarea
            disabled
            rows={4}
            className="mt-1 w-full rounded-md border border-line bg-void px-3 py-2"
            placeholder="Reviews open when a candidate id exists."
          />
        </label>
        <button
          type="button"
          disabled
          className="rounded-full bg-ember px-4 py-2 text-sm font-medium text-void opacity-40"
        >
          Submit review
        </button>
      </form>
      <PendingContract
        route={PENDING_ROUTES.reviews}
        consequence="The button stays disabled so a note cannot be mistaken for a stored scientific review."
      />
    </div>
  );
}
