"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { ExampleSummary } from "@/components/example-summary";
import { listExamples, type ExampleSlug } from "@/lib/api-client";

export function CopilotPanel() {
  const examples = useQuery({ queryKey: ["examples"], queryFn: listExamples });
  const [slug, setSlug] = useState<ExampleSlug | null>(null);

  return (
    <div className="space-y-6">
      <header className="max-w-3xl">
        <h1 className="font-serif text-4xl tracking-tight">Copilot</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          A summary explains one cached example and cites its evidence. It does not confirm a
          discovery, and this page never holds a provider key.
        </p>
      </header>
      {examples.isPending && <p className="text-sm text-muted">Loading examples</p>}
      {examples.isError && (
        <p className="text-sm text-danger" role="alert">
          The cached examples could not be loaded.
        </p>
      )}
      <div className="flex flex-wrap gap-2">
        {(examples.data ?? []).map((example) => (
          <button
            key={example.slug}
            type="button"
            aria-pressed={slug === example.slug}
            className={`rounded-full px-3 py-1.5 text-sm ${slug === example.slug ? "bg-ember text-void" : "bg-panel-2"}`}
            onClick={() => setSlug(example.slug)}
          >
            {example.name}
          </button>
        ))}
      </div>
      {slug ? (
        <ExampleSummary slug={slug} />
      ) : (
        <p className="text-sm text-muted" role="status">
          Choose a cached example. No summary has been requested.
        </p>
      )}
    </div>
  );
}
