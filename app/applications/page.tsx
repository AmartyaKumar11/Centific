import { ApplicationsTable } from "@/components/Dashboard/ApplicationsTable";
import { Charts } from "@/components/Dashboard/Charts";
import { AppTopBar } from "@/components/Layout/AppTopBar";
import { BottomDock } from "@/components/Layout/BottomDock";
import { applications } from "@/lib/mockData";

export default function ApplicationsPage() {
  return (
    <main className="mx-auto flex w-full max-w-[1500px] flex-col gap-4 px-4 py-4">
      <AppTopBar />

      <section className="card-shell p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">All Applications</h1>
            <p className="text-sm subtle-text">Full application register and underwriting decisions</p>
          </div>
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
      </section>

      <Charts applications={applications} />
      <ApplicationsTable applications={applications} />
      <BottomDock />
    </main>
  );
}
