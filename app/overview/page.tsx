import { CompactDashboard } from "@/components/Dashboard/CompactDashboard";
import { api } from "@/lib/api";

export default async function OverviewPage() {
  const [applications, chartData] = await Promise.all([api.getApplications(), api.getCharts()]);

  return (
    <main className="mx-auto flex w-full max-w-[1600px] flex-col gap-2 px-3 py-3 pb-24">
      <CompactDashboard applications={applications} chartData={chartData} />
    </main>
  );
}
