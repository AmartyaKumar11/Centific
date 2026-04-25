import { CompactDashboard } from "@/components/Dashboard/CompactDashboard";
import { applications } from "@/lib/mockData";

export default function OverviewPage() {
  return (
    <main className="mx-auto flex w-full max-w-[1600px] flex-col gap-2 px-3 py-3 pb-24">
      <CompactDashboard applications={applications} />
    </main>
  );
}
