"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";

import { ExampleSummary } from "@/components/example-summary";
import { ObservationSequence } from "@/components/observation-sequence";
import {
  ApiError,
  getExample,
  listExamples,
  searchSky,
  type ExampleResponse,
  type ExampleSlug,
  type SearchResponse,
} from "@/lib/api-client";
import {
  COLLECTIONS,
  fromSearchParams,
  toSearchParams,
  validateObservationQuery,
  type Collection,
  type ObservationQueryInput,
} from "@/lib/observation-query";
import { CHALLENGE_TARGETS, WISE_0855_BACKUP } from "@/lib/published-fallback";

const SkyContext = dynamic(
  () => import("@/components/sky-context").then((module) => module.SkyContext),
  {
    ssr: false,
    loading: () => <p className="text-sm text-muted">Loading sky context</p>,
  },
);

const EMPTY: ObservationQueryInput = {
  raDeg: Number.NaN,
  decDeg: Number.NaN,
  radiusDeg: 0.02,
  collection: "spherex_dr1",
  startMjd: null,
  endMjd: null,
};

const SLUGS = new Set<ExampleSlug>([
  "barnards-star",
  "epsilon-indi-b",
  "wise-0855",
  "rw-aurigae",
  "r-draconis",
]);

function isSlug(value: string | null): value is ExampleSlug {
  return value !== null && SLUGS.has(value as ExampleSlug);
}

type FieldDraft = {
  ra: string;
  dec: string;
  radius: string;
  collection: Collection;
};

function draftFrom(input: ObservationQueryInput): FieldDraft {
  return {
    ra: Number.isFinite(input.raDeg) ? String(input.raDeg) : "",
    dec: Number.isFinite(input.decDeg) ? String(input.decDeg) : "",
    radius: Number.isFinite(input.radiusDeg) ? String(input.radiusDeg) : "",
    collection: input.collection,
  };
}

function inputFrom(draft: FieldDraft): ObservationQueryInput {
  const read = (value: string) => (value.trim() === "" ? Number.NaN : Number(value));
  return {
    raDeg: read(draft.ra),
    decDeg: read(draft.dec),
    radiusDeg: read(draft.radius),
    collection: draft.collection,
    startMjd: null,
    endMjd: null,
  };
}

function shareQuery(input: ObservationQueryInput, target: ExampleSlug | null): string {
  const params = new URLSearchParams(toSearchParams(input));
  if (target) {
    params.set("target", target);
  }
  return params.toString();
}

function fromExample(example: ExampleResponse): ObservationQueryInput | null {
  if (!example.query) {
    return null;
  }
  return {
    raDeg: example.query.ra_deg,
    decDeg: example.query.dec_deg,
    radiusDeg: example.query.radius_deg,
    collection: example.query.collection,
    startMjd: null,
    endMjd: null,
  };
}

export function ExploreWorkspace() {
  const params = useSearchParams();
  const router = useRouter();
  const requestedTarget = params.get("target");
  const target = isSlug(requestedTarget) ? requestedTarget : null;
  const initial = useMemo(() => fromSearchParams(params) ?? EMPTY, [params]);
  const [draft, setDraft] = useState<FieldDraft>(() => draftFrom(initial));
  const appliedTarget = useRef<ExampleSlug | null>(null);
  const [clientError, setClientError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [live, setLive] = useState<SearchResponse | null>(null);

  const examples = useQuery({ queryKey: ["examples"], queryFn: listExamples });
  const cached = useQuery({
    queryKey: ["example", target],
    queryFn: () => getExample(target as ExampleSlug),
    enabled: target !== null,
    refetchOnWindowFocus: false,
  });
  const search = useMutation({
    mutationFn: searchSky,
    onSuccess: (result) => setLive(result),
  });

  useEffect(() => {
    if (!target || !cached.data || appliedTarget.current === target) {
      return;
    }
    const parsed = fromExample(cached.data);
    appliedTarget.current = target;
    if (!parsed) {
      return;
    }
    setDraft((current) =>
      current.ra.trim() === "" && current.dec.trim() === "" ? draftFrom(parsed) : current,
    );
  }, [cached.data, target]);

  const form = inputFrom(draft);
  const validNow = validateObservationQuery(form) === null;
  const usingBackup = target === "wise-0855" && cached.isError && !live;
  const shown = live ?? (usingBackup ? WISE_0855_BACKUP : target ? cached.data : undefined);

  function update(partial: Partial<FieldDraft>) {
    setDraft((current) => ({ ...current, ...partial }));
    setClientError(null);
  }

  function openTarget(slug: ExampleSlug) {
    setClientError(null);
    setLive(null);
    if (slug === "wise-0855") {
      const preset: ObservationQueryInput = {
        raDeg: WISE_0855_BACKUP.query?.ra_deg ?? Number.NaN,
        decDeg: WISE_0855_BACKUP.query?.dec_deg ?? Number.NaN,
        radiusDeg: WISE_0855_BACKUP.query?.radius_deg ?? 0.02,
        collection: WISE_0855_BACKUP.query?.collection ?? "spherex_dr1",
        startMjd: null,
        endMjd: null,
      };
      appliedTarget.current = slug;
      setDraft(draftFrom(preset));
      router.replace(`/?${shareQuery(preset, slug)}`);
      return;
    }
    appliedTarget.current = null;
    router.replace(`/?target=${slug}`);
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const problem = validateObservationQuery(form);
    if (problem) {
      setClientError(problem);
      return;
    }
    router.replace(`/?${shareQuery(form, target)}`);
    search.mutate({
      ra_deg: form.raDeg,
      dec_deg: form.decDeg,
      radius_deg: form.radiusDeg,
      collection: form.collection,
    });
  }

  async function copyLink() {
    const problem = validateObservationQuery(form);
    if (problem) {
      setClientError(problem);
      return;
    }
    const url = `${window.location.origin}/?${shareQuery(form, target)}`;
    await navigator.clipboard.writeText(url);
    setCopied(true);
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,340px)_minmax(0,1fr)]">
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        <div>
          <h1 className="font-serif text-4xl tracking-tight">Explore</h1>
          <p className="mt-2 text-sm leading-6 text-muted">
            A challenge target opens the cached example. Search this field asks IRSA and can take
            several seconds. Neither download is a discovery.
          </p>
        </div>
        <fieldset className="space-y-2">
          <legend className="text-sm text-muted">Challenge targets</legend>
          {examples.isPending && <p className="text-sm text-muted">Loading examples</p>}
          {examples.isError && (
            <p className="text-sm text-danger" role="alert">
              The cached examples could not be loaded. WISE 0855 can still play from the published previews.
            </p>
          )}
          <div className="flex flex-wrap gap-2">
            {(examples.data ?? CHALLENGE_TARGETS).map((example) => (
              <button
                key={example.slug}
                type="button"
                className="rounded-full bg-panel-2 px-3 py-1.5 text-sm"
                onClick={() => openTarget(example.slug)}
              >
                {example.name}
              </button>
            ))}
          </div>
        </fieldset>
        <label className="block text-sm">
          Right ascension (degrees)
          <input
            inputMode="decimal"
            className="mt-1 w-full rounded-md border border-line bg-void px-3 py-2 font-mono"
            value={draft.ra}
            autoComplete="off"
            onChange={(event) => update({ ra: event.target.value })}
          />
        </label>
        <label className="block text-sm">
          Declination (degrees)
          <input
            inputMode="decimal"
            className="mt-1 w-full rounded-md border border-line bg-void px-3 py-2 font-mono"
            value={draft.dec}
            autoComplete="off"
            onChange={(event) => update({ dec: event.target.value })}
          />
        </label>
        <label className="block text-sm">
          Field radius (degrees)
          <input
            inputMode="decimal"
            className="mt-1 w-full rounded-md border border-line bg-void px-3 py-2 font-mono"
            value={draft.radius}
            autoComplete="off"
            onChange={(event) => update({ radius: event.target.value })}
          />
        </label>
        <label className="block text-sm">
          Collection
          <select
            className="mt-1 w-full rounded-md border border-line bg-void px-3 py-2"
            value={draft.collection}
            onChange={(event) => update({ collection: event.target.value as Collection })}
          >
            {COLLECTIONS.map((collection) => (
              <option key={collection} value={collection}>
                {collection}
              </option>
            ))}
          </select>
        </label>
        {clientError && (
          <p className="text-sm text-danger" role="alert">
            {clientError}
          </p>
        )}
        {search.isError && (
          <p className="text-sm text-danger" role="alert">
            {search.error instanceof ApiError
              ? `${search.error.message}${search.error.requestId ? ` Request ${search.error.requestId}.` : ""}`
              : "The archive request failed."}
          </p>
        )}
        <div className="flex flex-wrap gap-2">
          <button
            type="submit"
            className="rounded-full bg-ember px-4 py-2 text-sm font-medium text-void disabled:opacity-40"
            disabled={search.isPending}
          >
            {search.isPending ? "Searching the archive" : "Search this field"}
          </button>
          <button type="button" className="rounded-full border border-line px-4 py-2 text-sm" onClick={() => void copyLink()}>
            {copied ? "Link copied" : "Copy link"}
          </button>
        </div>
      </form>
      <div className="space-y-6">
        {validNow ? (
          <SkyContext raDeg={form.raDeg} decDeg={form.decDeg} radiusDeg={form.radiusDeg} />
        ) : (
          <section className="flex h-40 items-center justify-center rounded-lg border border-dashed border-line p-6 text-center">
            <p className="max-w-sm text-sm leading-6 text-muted">
              Enter a valid ICRS position to place the CDS context map. The map is not a SPHEREx exposure.
            </p>
          </section>
        )}
        {cached.isPending && target && <p className="text-sm text-muted">Loading cached example</p>}
        {search.isPending && (
          <p className="text-sm text-muted" role="status">
            Searching the archive. This can take several seconds.
          </p>
        )}
        {usingBackup && (
          <p className="text-sm text-muted" role="status">
            The API did not answer. Playing the two published WISE 0855 previews stored with this app.
          </p>
        )}
        {cached.isError && target && target !== "wise-0855" && (
          <p className="text-sm text-danger" role="alert">
            The cached example could not be loaded.
          </p>
        )}
        {shown && (
          <ObservationSequence key={`${shown.source}-${shown.queried_at ?? "pending"}`} result={shown} />
        )}
        {!shown && !search.isPending && (
          <p className="text-sm text-muted">Open a cached example, or search a field.</p>
        )}
        {target && !live && <ExampleSummary slug={target} />}
      </div>
    </div>
  );
}
