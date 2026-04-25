"use client";

import Link from "next/link";
import { MacWindowCard } from "@/components/ui/MacWindowCard";

export function AppTopBar() {
  return (
    <MacWindowCard
      title="Virtual Credit Underwriter"
      bodyClassName="p-0"
      headerRight={
        <div className="flex items-center gap-2">
          <span className="rounded-md border border-violet-200 bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700">
            Credit Officer
          </span>
          <span className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
            Pipeline Active
          </span>
        </div>
      }
    >
      <div className="border-b border-slate-100 px-4 py-2">
        <p className="text-[11px] uppercase tracking-[0.08em] text-slate-500">Loan Underwriting AI Agent</p>
      </div>
      <nav className="flex flex-wrap gap-2 px-4 py-2">
        <Link href="/overview" className="rounded-md bg-blue-50 px-2 py-1 text-xs text-blue-700">
          Overview
        </Link>
        <Link
          href="/hil-review"
          className="rounded-md bg-amber-50 px-2 py-1 text-xs text-amber-700"
        >
          HIL Review
        </Link>
        <Link
          href="/apps"
          className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700"
        >
          Applications
        </Link>
      </nav>
    </MacWindowCard>
  );
}
