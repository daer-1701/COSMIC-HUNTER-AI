"use client";

import { useMutation } from "@tanstack/react-query";

import { ApiError, summarizeExample, type ExampleSlug, type SummaryResponse } from "@/lib/api-client";

export function ExampleSummary({ slug }: { slug: ExampleSlug }) {
  const summary = useMutation({ mutationFn: () => summarizeExample(slug) });
  const unavailable = summary.error instanceof ApiError && summary.error.status === 503;

  return (
    <section className="space-y-3 rounded-lg border border-line bg-panel p-5" aria-label="Cached example summary">
      <h2 className="font-serif text-2xl">Summary</h2>
      <p className="text-sm text-muted">
        A summary explains the cached manifest. It does not confirm an object or a motion.
      </p>
      <button
        type="button"
        className="rounded-full bg-ember px-4 py-2 text-sm font-medium text-void disabled:opacity-40"
        disabled={summary.isPending}
        onClick={() => summary.mutate()}
      >
        {summary.isPending ? "Requesting summary" : "Summarize cached example"}
      </button>
      {unavailable && (
        <p role="status" className="text-sm text-muted">
          AI summary unavailable
        </p>
      )}
      {summary.error && !unavailable && (
        <p role="alert" className="text-sm text-danger">
          {summary.error instanceof ApiError ? summary.error.message : "The summary request failed."}
        </p>
      )}
      {summary.data && <SummaryBody summary={summary.data} />}
    </section>
  );
}

function SummaryBody({ summary }: { summary: SummaryResponse }) {
  return (
    <div className="space-y-3 text-sm">
      <p>{summary.disclaimer}</p>
      <p className="whitespace-pre-wrap leading-6">{summary.text}</p>
      <p className="font-mono text-xs text-muted">
        {summary.model}
        {summary.cached ? " · cached" : ""} · {summary.generated_at}
      </p>
      <ul className="space-y-2">
        {summary.evidence.map((line) => (
          <li key={line.id} className="rounded-md border border-line px-3 py-2">
            <p className="font-mono text-ember">[{line.id}]</p>
            <p>{line.text}</p>
            {summary.cited.includes(line.id) && <p className="text-xs text-muted">Cited in the summary</p>}
          </li>
        ))}
      </ul>
    </div>
  );
}
