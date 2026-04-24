import Link from "next/link";

export function AppTopBar() {
  return (
    <header className="card-shell px-4 py-2">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.08em] text-slate-500">
            Loan Underwriting AI Agent
          </p>
          <p className="text-lg font-semibold text-slate-900">Virtual Credit Underwriter</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-md border border-violet-200 bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700">
            Credit Officer
          </span>
          <span className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
            Pipeline Active
          </span>
        </div>
      </div>
      <nav className="mt-2 flex flex-wrap gap-2 border-t border-slate-100 pt-2">
        <Link href="/" className="rounded-md bg-blue-50 px-2 py-1 text-xs text-blue-700">
          Overview
        </Link>
        <Link
          href="/hil-review"
          className="rounded-md bg-amber-50 px-2 py-1 text-xs text-amber-700"
        >
          HIL Review
        </Link>
        <Link
          href="/applications"
          className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700"
        >
          Applications
        </Link>
      </nav>
    </header>
  );
}
