"use client";

import { useEffect, useState } from "react";
import { CompactDashboard } from "@/components/Dashboard/CompactDashboard";
import { api } from "@/lib/api";
import { Application } from "@/types/application";
import { ChartData } from "@/lib/api";

export default function OverviewPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [chartData, setChartData] = useState<ChartData | undefined>(undefined);

  useEffect(() => {
    let mounted = true;
    Promise.all([api.getApplications(), api.getCharts()])
      .then(([apps, charts]) => {
        if (!mounted) return;
        setApplications(apps);
        setChartData(charts);
      })
      .catch(() => {
        if (!mounted) return;
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <main className="mx-auto flex w-full max-w-[1600px] flex-col gap-2 px-3 py-3 pb-24">
      <CompactDashboard applications={applications} chartData={chartData} />
    </main>
  );
}
