"use client";

import Link from "next/link";

export function BottomDock() {
  return (
    <div className="fixed bottom-4 left-1/2 z-40 -translate-x-1/2 rounded-2xl border border-slate-200 bg-white/95 px-2 py-1 shadow-lg backdrop-blur">
      <div className="flex items-center gap-1">
        <Link href="/" className="rounded-xl px-3 py-2 text-xs text-slate-600 hover:bg-slate-100">
          Overview
        </Link>
        <Link
          href="/hil-review"
          className="rounded-xl px-3 py-2 text-xs text-slate-600 hover:bg-slate-100"
        >
          HIL Review
        </Link>
        <Link
          href="/applications"
          className="rounded-xl px-3 py-2 text-xs text-slate-600 hover:bg-slate-100"
        >
          Apps
        </Link>
      </div>
    </div>
  );
}
