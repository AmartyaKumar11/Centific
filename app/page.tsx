import { ApplicationsTable } from "@/components/Dashboard/ApplicationsTable";
import { KPICards } from "@/components/Dashboard/KPICards";
import { OverviewPanels } from "@/components/Dashboard/OverviewPanels";
import { BottomDock } from "@/components/Layout/BottomDock";
import { AppTopBar } from "@/components/Layout/AppTopBar";
import { applications } from "@/lib/mockData";

export default function DashboardPage() {
  return (
    <main className="mx-auto flex w-full max-w-[1500px] flex-col gap-4 px-4 py-4">
      <AppTopBar />

      <KPICards
        items={[
          {
            label: "Applications Today",
            value: 74,
            subLabel: "47 rows validated",
            tone: "blue",
          },
          {
            label: "STP Approved",
            value: 38,
            subLabel: "68.3% STP rate",
            tone: "green",
          },
          {
            label: "HIL Queue",
            value: 12,
            subLabel: "Pending CO review",
            tone: "amber",
          },
          {
            label: "Rejected",
            value: 18,
            subLabel: "24.3% rejection rate",
            tone: "red",
          },
          {
            label: "Avg TAT",
            value: "8.2m",
            subLabel: "Target < 15 min",
            tone: "purple",
          },
        ]}
      />

      <OverviewPanels applications={applications} />
      <ApplicationsTable applications={applications.slice(0, 4)} />
      <BottomDock />
    </main>
  );
}
