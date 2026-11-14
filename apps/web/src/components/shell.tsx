"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { getLiveness } from "@/lib/api-client";

const NAV = [
  { href: "/", label: "Explore" },
  { href: "/compare", label: "Compare" },
  { href: "/candidates", label: "Candidates" },
  { href: "/investigations", label: "Investigations" },
  { href: "/review", label: "Review" },
  { href: "/copilot", label: "Copilot" },
] as const;

export function Shell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const health = useQuery({ queryKey: ["liveness"], queryFn: getLiveness });

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-5 sm:px-6">
      <a
        href="#content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-20 focus:bg-panel focus:px-3 focus:py-2"
      >
        Skip to content
      </a>
      <header className="border-b border-line pb-4">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <Link href="/" className="font-serif text-3xl tracking-tight text-ink">
              Cosmic Hunter
            </Link>
            <p className="mt-1 max-w-xl text-sm text-muted">
              SPHEREx images of one sky position, in time order. A candidate is not a confirmed
              discovery.
            </p>
          </div>
          <p
            className="rounded-full border border-line px-3 py-1 font-mono text-xs text-muted"
            role="status"
          >
            {health.isPending && "Checking API"}
            {health.isError && "API unreachable"}
            {health.isSuccess && `API ${health.data.status} · ${health.data.stage}`}
          </p>
        </div>
        <nav aria-label="Primary" className="mt-4 flex flex-wrap gap-2">
          {NAV.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/" || pathname === "/explore"
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`rounded-full px-3 py-1.5 text-sm ${
                  active ? "bg-ember text-void" : "bg-panel text-ink hover:bg-panel-2"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </header>
      <main id="content" className="flex-1 py-6">
        {children}
      </main>
    </div>
  );
}
