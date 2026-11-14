"use client";

import { useEffect, useRef, useState } from "react";

type AladinInstance = {
  gotoRaDec: (ra: number, dec: number) => void;
  setFov: (fovDeg: number) => void;
};

type AladinFactory = {
  init: Promise<unknown>;
  aladin: (target: HTMLElement, options: Record<string, unknown>) => AladinInstance;
};

export function SkyContext({
  raDeg,
  decDeg,
  radiusDeg,
}: {
  raDeg: number;
  decDeg: number;
  radiusDeg: number;
}) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<AladinInstance | null>(null);
  const coords = useRef({ raDeg, decDeg, radiusDeg });
  const [error, setError] = useState<string | null>(null);
  coords.current = { raDeg, decDeg, radiusDeg };

  useEffect(() => {
    let cancelled = false;
    const fail = () => {
      if (!cancelled) {
        setError("The CDS sky map could not be loaded. The coordinates you enter stay valid.");
      }
    };
    const onRejection = (event: PromiseRejectionEvent) => {
      const reason = event.reason;
      const message = reason instanceof Error ? `${reason.message}\n${reason.stack ?? ""}` : String(reason ?? "");
      if (!/failed to fetch|hips|dss|aladin/i.test(message)) {
        return;
      }
      event.preventDefault();
      event.stopImmediatePropagation();
      fail();
    };
    window.addEventListener("unhandledrejection", onRejection, true);
    void import("aladin-lite")
      .then(async (module) => {
        const factory = module.default as AladinFactory;
        await factory.init;
        if (cancelled || !host.current) {
          return;
        }
        try {
          const created = factory.aladin(host.current, {
            cooFrame: "ICRS",
            survey: "https://alasky.cds.unistra.fr/DSS/DSSColor",
            fov: Math.max(coords.current.radiusDeg * 2, 0.02),
            target: `${coords.current.raDeg} ${coords.current.decDeg}`,
            showGotoControl: false,
            showFullscreenControl: false,
          });
          view.current = created;
          created.gotoRaDec(coords.current.raDeg, coords.current.decDeg);
          created.setFov(Math.max(coords.current.radiusDeg * 2, 0.02));
        } catch {
          fail();
        }
      })
      .catch(() => fail());
    return () => {
      cancelled = true;
      window.removeEventListener("unhandledrejection", onRejection, true);
    };
  }, []);

  useEffect(() => {
    try {
      view.current?.gotoRaDec(raDeg, decDeg);
      view.current?.setFov(Math.max(radiusDeg * 2, 0.02));
    } catch {
      setError("The CDS sky map could not be loaded. The coordinates you enter stay valid.");
    }
  }, [decDeg, raDeg, radiusDeg]);

  return (
    <section aria-label="Sky context from CDS, not a SPHEREx product" className="space-y-2">
      <div className="flex items-baseline justify-between gap-3">
        <h2 className="font-serif text-2xl">Sky context</h2>
        <p className="text-xs text-muted">CDS DSS2. Not a SPHEREx exposure.</p>
      </div>
      {error && (
        <p className="rounded-lg border border-line bg-panel p-4 text-sm text-muted" role="status">
          {error}
        </p>
      )}
      <div
        ref={host}
        className={error ? "hidden" : "h-[420px] overflow-hidden rounded-lg border border-line"}
      />
    </section>
  );
}
