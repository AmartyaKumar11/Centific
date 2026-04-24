import Link from "next/link";
import { Application } from "@/types/application";
import { MacWindowCard } from "@/components/ui/MacWindowCard";

export function ApplicationHeader({ application }: { application: Application }) {
  return (
    <MacWindowCard
      title={application.applicant_name}
      bodyClassName="p-5"
      headerRight={
        <Link
          href="/"
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
        >
          Back to Dashboard
        </Link>
      }
    >
      <p className="text-xs uppercase tracking-[0.08em] text-slate-500">{application.id}</p>
      <p className="mt-2 text-sm text-slate-600">{application.reasoning_summary}</p>
    </MacWindowCard>
  );
}
