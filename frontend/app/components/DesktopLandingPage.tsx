"use client";

import { useEffect, useState } from "react";
import { DesktopBackground } from "@/app/components/DesktopBackground";
import { api } from "@/lib/api";

type DesktopLandingPageProps = {
  backgroundImageUrl?: string;
};

export function DesktopLandingPage({ backgroundImageUrl }: DesktopLandingPageProps) {
  const [snapshot, setSnapshot] = useState({
    requiresReview: 0,
    reviewedToday: 0,
    accepted: 0,
    rejected: 0,
    total: 0,
  });

  useEffect(() => {
    let mounted = true;
    api
      .getApplications()
      .then((applications) => {
        if (!mounted) return;
        setSnapshot({
          requiresReview: applications.filter((app) => app.hil_required_flag).length,
          reviewedToday: applications.filter(
            (app) => app.decision === "STP Approved" || app.decision === "Rejected"
          ).length,
          accepted: applications.filter(
            (app) => app.decision === "STP Approved" || app.decision === "Conditional Approval"
          ).length,
          rejected: applications.filter((app) => app.decision === "Rejected").length,
          total: applications.length,
        });
      })
      .catch(() => {
        if (!mounted) return;
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <main className="relative h-screen w-full overflow-hidden">
      <DesktopBackground backgroundImageUrl={backgroundImageUrl} />

      <div className="pointer-events-none absolute inset-x-0 top-5 z-30 hidden items-start justify-between gap-4 px-5 lg:flex">
        <aside className="pointer-events-auto desktop-subtitle-enter w-[290px] rounded-2xl border border-white/50 bg-white/45 p-3 shadow-xl shadow-slate-300/20 backdrop-blur-xl">
          <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-500">
            Today&apos;s Queue Snapshot
          </p>
          <div className="mt-2.5 grid grid-cols-2 gap-2">
            <MetricTile label="Need Review" value={snapshot.requiresReview} tone="amber" />
            <MetricTile label="Reviewed" value={snapshot.reviewedToday} tone="blue" />
            <MetricTile label="Accepted" value={snapshot.accepted} tone="green" />
            <MetricTile label="Rejected" value={snapshot.rejected} tone="red" />
          </div>
        </aside>

        <aside className="pointer-events-auto desktop-subtitle-enter w-[270px] rounded-2xl border border-white/50 bg-white/45 p-3 shadow-xl shadow-slate-300/20 backdrop-blur-xl">
          <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-500">
            Decision Mix
          </p>
          <div className="mt-2.5 space-y-2">
            <MixRow label="Accepted" value={snapshot.accepted} total={snapshot.total} color="bg-emerald-500" />
            <MixRow label="Rejected" value={snapshot.rejected} total={snapshot.total} color="bg-rose-500" />
            <MixRow label="Under Review" value={snapshot.requiresReview} total={snapshot.total} color="bg-amber-500" />
          </div>
        </aside>
      </div>

      <section className="flex h-full w-full items-start justify-center px-6 pb-28 pt-40 md:pt-44 lg:pt-48">
        <div
          className="desktop-title-enter desktop-card-hover w-full max-w-3xl rounded-2xl border border-slate-200 bg-white/85 p-8 text-center shadow-xl backdrop-blur-sm"
          style={{ willChange: "transform, opacity" }}
        >
          <div className="mb-4 flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          </div>
          <p className="desktop-subtitle-enter text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-500">
            Loan Underwriting AI Agent
          </p>
          <h1 className="desktop-text-enter mt-2 text-4xl font-semibold tracking-tight text-slate-900 md:text-5xl">
            AI Loan Agent
          </h1>
          <p className="desktop-subtitle-enter mt-2 text-sm text-slate-600 md:text-base">
            Virtual Credit Underwriter
          </p>
        </div>
      </section>

    </main>
  );
}

function MetricTile({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "blue" | "amber" | "green" | "red";
}) {
  const toneClasses = {
    blue: "border-blue-200 bg-blue-50 text-blue-700",
    amber: "border-amber-200 bg-amber-50 text-amber-700",
    green: "border-emerald-200 bg-emerald-50 text-emerald-700",
    red: "border-rose-200 bg-rose-50 text-rose-700",
  } as const;

  return (
    <div className={`rounded-lg border px-2.5 py-2 ${toneClasses[tone]}`}>
      <p className="text-[10px] font-semibold uppercase tracking-[0.07em]">{label}</p>
      <p className="mt-1 text-xl font-bold leading-none">{value}</p>
    </div>
  );
}

function MixRow({
  label,
  value,
  total,
  color,
}: {
  label: string;
  value: number;
  total: number;
  color: string;
}) {
  const pct = Math.round((value / Math.max(total, 1)) * 100);
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="text-slate-500">
          {value} ({pct}%)
        </span>
      </div>
      <div className="h-2 rounded-full bg-slate-200">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
