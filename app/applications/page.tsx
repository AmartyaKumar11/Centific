import { ApplicationsTable } from "@/components/Dashboard/ApplicationsTable";
import { Charts } from "@/components/Dashboard/Charts";
import { MacWindowCard } from "@/components/ui/MacWindowCard";
import { api } from "@/lib/api";

export default async function ApplicationsPage() {
  const applications = await api.getApplications();

  return (
    <main className="mx-auto flex w-full max-w-[1500px] flex-col gap-4 px-4 py-4 pb-24">
      <MacWindowCard title="All Applications" bodyClassName="p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm subtle-text">Full application register and underwriting decisions</p>
          <div className="flex flex-wrap gap-2">
            <input
              placeholder="Search applicant or app id"
              className="rounded-md border border-slate-200 px-3 py-2 text-sm outline-none ring-blue-100 focus:ring"
            />
            <select className="rounded-md border border-slate-200 px-3 py-2 text-sm">
              <option>All Status</option>
            </select>
            <select className="rounded-md border border-slate-200 px-3 py-2 text-sm">
              <option>All Risk Tiers</option>
            </select>
            <button className="rounded-md border border-slate-200 px-3 py-2 text-sm text-slate-700">
              Export CSV
            </button>
          </div>
        </div>
      </MacWindowCard>

      <Charts applications={applications} />
      <ApplicationsTable applications={applications} />
    </main>
  );
}
