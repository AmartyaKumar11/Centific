import { CompactDashboard } from "@/components/Dashboard/CompactDashboard";
import { AppTopBar } from "@/components/Layout/AppTopBar";
import { BottomDock } from "@/components/Layout/BottomDock";
import { applications } from "@/lib/mockData";

export default function DashboardPage() {
  return (
    <main className="mx-auto flex w-full max-w-[1600px] flex-col gap-2 px-3 py-3">
      <div className="animate-fade-up">
        <AppTopBar />
      </div>

      <CompactDashboard applications={applications} />
      <BottomDock />
    </main>
  );
}
