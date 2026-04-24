import Link from "next/link";
import { Application } from "@/types/application";

export function ApplicationHeader({ application }: { application: Application }) {
  return (
    <header className="card-shell p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.08em] text-slate-500">{application.id}</p>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">
            {application.applicant_name}
          </h1>
          <p className="mt-1 text-sm text-slate-600">{application.reasoning_summary}</p>
        </div>
        <Link
          href="/"
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
        >
          Back to Dashboard
        </Link>
      </div>
    </header>
  );
}
