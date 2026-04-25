"use client";

import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import { Bar, Doughnut } from "react-chartjs-2";
import { Application } from "@/types/application";
import { CompactKPICard } from "@/components/Dashboard/CompactKPICard";
import {
  COMPACT_CHART_HEIGHT_CLASS,
  COMPACT_METRIC_HEIGHT_CLASS,
  COMPACT_PIPELINE_HEIGHT_CLASS,
  DASHBOARD_GAP,
  DASHBOARD_PADDING,
} from "@/components/Dashboard/compact/constants";

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function countBy<T extends string>(items: T[]) {
  return items.reduce<Record<string, number>>((acc, key) => {
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {});
}

function cardShell(heightClass: string) {
  return `rounded-lg border border-slate-200 bg-white shadow-sm ${heightClass}`;
}

const chartOptions = {
  maintainAspectRatio: false,
  layout: { padding: 12 },
  plugins: {
    legend: {
      position: "bottom" as const,
      labels: {
        boxWidth: 10,
        boxHeight: 10,
        font: { size: 11 },
        padding: 8,
      },
    },
  },
};

export function CompactDashboard({ applications }: { applications: Application[] }) {
  const total = applications.length;
  const approved = applications.filter(
    (item) => item.decision === "STP Approved" || item.decision === "Conditional Approval"
  ).length;
  const hilQueue = applications.filter((item) => item.hil_required_flag).length;
  const rejected = applications.filter((item) => item.decision === "Rejected").length;
  const avgTatMinutes = 8.2;
  const avgConfidence = Math.round(
    applications.reduce((sum, item) => sum + item.confidence_score, 0) / Math.max(total, 1)
  );
  const falseRejectRate = 18;

  const decisionCounts = countBy(applications.map((item) => item.decision));
  const riskCounts = countBy(applications.map((item) => item.risk));
  const employerCounts = countBy(applications.map((item) => item.employer_type));
  const rejectionReasons = {
    HIGH_DTI: applications.filter((item) => item.dti_percent > 40).length,
    LOW_CIBIL: applications.filter((item) => Number.parseInt(item.cibil_score, 10) < 620).length,
    HIGH_RISK: applications.filter((item) => item.risk === "High" || item.risk === "Very High").length,
    PROXY_SCORE: applications.filter((item) => item.cibil_score.includes("Proxy")).length,
  };

  return (
    <section className="grid grid-cols-1 gap-2 lg:grid-cols-12" style={{ gap: DASHBOARD_GAP }}>
      <div className="lg:col-span-12">
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-5" style={{ gap: DASHBOARD_GAP }}>
          <CompactKPICard title="Applications Today" value={total} subtitle="Current batch" tone="blue" />
          <CompactKPICard
            title="STP Approved (%)"
            value={`${Math.round((approved / Math.max(total, 1)) * 100)}%`}
            subtitle={`${approved} approvals`}
            tone="green"
          />
          <CompactKPICard title="HIL Queue" value={hilQueue} subtitle="Pending review" tone="amber" />
          <CompactKPICard
            title="Rejected"
            value={rejected}
            subtitle={`${Math.round((rejected / Math.max(total, 1)) * 100)}% rate`}
            tone="red"
          />
          <CompactKPICard title="Avg TAT" value={`${avgTatMinutes}m`} subtitle="Target < 15m" tone="purple" />
        </div>
      </div>

      <div className="lg:col-span-4">
        <article className={cardShell(COMPACT_CHART_HEIGHT_CLASS)} style={{ padding: DASHBOARD_PADDING }}>
          <h3 className="text-xs font-semibold text-slate-700">Decision Distribution</h3>
          <div className="mt-1 h-[180px]">
            <Doughnut
              data={{
                labels: Object.keys(decisionCounts),
                datasets: [
                  {
                    data: Object.values(decisionCounts),
                    backgroundColor: ["#16a34a", "#f59e0b", "#2563eb", "#dc2626"],
                    borderWidth: 0,
                  },
                ],
              }}
              options={{ ...chartOptions, cutout: "72%" }}
            />
          </div>
        </article>
      </div>
      <div className="lg:col-span-4">
        <article className={cardShell(COMPACT_CHART_HEIGHT_CLASS)} style={{ padding: DASHBOARD_PADDING }}>
          <h3 className="text-xs font-semibold text-slate-700">Risk Distribution</h3>
          <div className="mt-1 h-[180px]">
            <Doughnut
              data={{
                labels: Object.keys(riskCounts),
                datasets: [
                  {
                    data: Object.values(riskCounts),
                    backgroundColor: ["#16a34a", "#f59e0b", "#dc2626", "#475569"],
                    borderWidth: 0,
                  },
                ],
              }}
              options={{ ...chartOptions, cutout: "72%" }}
            />
          </div>
        </article>
      </div>
      <div className="lg:col-span-4">
        <article className={cardShell(COMPACT_CHART_HEIGHT_CLASS)} style={{ padding: DASHBOARD_PADDING }}>
          <h3 className="text-xs font-semibold text-slate-700">Employer Split</h3>
          <div className="mt-1 h-[180px]">
            <Doughnut
              data={{
                labels: Object.keys(employerCounts),
                datasets: [
                  {
                    data: Object.values(employerCounts),
                    backgroundColor: ["#2563eb", "#7c3aed"],
                    borderWidth: 0,
                  },
                ],
              }}
              options={{ ...chartOptions, cutout: "72%" }}
            />
          </div>
        </article>
      </div>

      <div className="lg:col-span-6">
        <article className={cardShell(COMPACT_CHART_HEIGHT_CLASS)} style={{ padding: DASHBOARD_PADDING }}>
          <h3 className="text-xs font-semibold text-slate-700">Daily Batch Volume</h3>
          <div className="mt-1 h-[180px]">
            <Bar
              data={{
                labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"],
                datasets: [
                  {
                    label: "Processed",
                    data: [42, 76, 50, 61, 47, 20, 39],
                    backgroundColor: "rgba(59,130,246,0.85)",
                    borderRadius: 4,
                  },
                  {
                    label: "Rejected",
                    data: [9, 14, 7, 11, 8, 3, 12],
                    backgroundColor: "rgba(239,68,68,0.78)",
                    borderRadius: 4,
                  },
                ],
              }}
              options={{
                maintainAspectRatio: false,
                layout: { padding: 12 },
                plugins: { legend: { position: "bottom", labels: { font: { size: 11 }, padding: 8 } } },
                scales: { y: { beginAtZero: true, ticks: { font: { size: 11 } } }, x: { ticks: { font: { size: 11 } } } },
              }}
            />
          </div>
        </article>
      </div>
      <div className="lg:col-span-6">
        <article className={cardShell(COMPACT_CHART_HEIGHT_CLASS)} style={{ padding: DASHBOARD_PADDING }}>
          <h3 className="text-xs font-semibold text-slate-700">Top Rejection Reasons</h3>
          <div className="mt-1 h-[180px]">
            <Bar
              data={{
                labels: Object.keys(rejectionReasons),
                datasets: [
                  {
                    data: Object.values(rejectionReasons),
                    backgroundColor: ["#ef4444", "#f87171", "#f59e0b", "#60a5fa"],
                    borderRadius: 4,
                  },
                ],
              }}
              options={{
                indexAxis: "y",
                maintainAspectRatio: false,
                layout: { padding: 12 },
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, ticks: { font: { size: 11 } } }, y: { ticks: { font: { size: 11 } } } },
              }}
            />
          </div>
        </article>
      </div>

      <div className="lg:col-span-12">
        <article
          className={`${cardShell(COMPACT_PIPELINE_HEIGHT_CLASS)} flex items-center overflow-x-auto`}
          style={{ padding: DASHBOARD_PADDING }}
        >
          <div className="grid min-w-[820px] flex-1 grid-cols-7 gap-2">
            {["Data Intake", "Feature Eng", "Rule Engine", "LLM Reasoning", "HIL Review", "Audit Trail", "LMS Push"].map(
              (step, index) => (
                <div key={step} className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1.5">
                  <p className="text-[10px] text-slate-500">{String(index + 1).padStart(2, "0")}</p>
                  <p className="truncate text-[11px] font-medium text-slate-700">{step}</p>
                </div>
              )
            )}
          </div>
        </article>
      </div>

      <div className="lg:col-span-3">
        <article className={cardShell(COMPACT_METRIC_HEIGHT_CLASS)} style={{ padding: DASHBOARD_PADDING }}>
          <h3 className="text-xs font-semibold text-slate-700">STP Rate</h3>
          <p className="mt-2 text-3xl font-bold text-emerald-700">{Math.round((approved / Math.max(total, 1)) * 100)}%</p>
          <p className="mt-1 text-[11px] text-slate-500">Trend: +4.2% vs yesterday</p>
        </article>
      </div>
      <div className="lg:col-span-3">
        <article className={cardShell(COMPACT_METRIC_HEIGHT_CLASS)} style={{ padding: DASHBOARD_PADDING }}>
          <h3 className="text-xs font-semibold text-slate-700">Decision Accuracy</h3>
          <p className="mt-2 text-3xl font-bold text-blue-700">{avgConfidence}%</p>
          <p className="mt-1 text-[11px] text-slate-500">Model confidence average</p>
        </article>
      </div>
      <div className="lg:col-span-3">
        <article className={cardShell(COMPACT_METRIC_HEIGHT_CLASS)} style={{ padding: DASHBOARD_PADDING }}>
          <h3 className="text-xs font-semibold text-slate-700">False Reject Rate</h3>
          <p className="mt-2 text-3xl font-bold text-rose-700">{falseRejectRate}%</p>
          <p className="mt-1 text-[11px] text-slate-500">Requires policy calibration</p>
        </article>
      </div>
      <div className="lg:col-span-3">
        <article className={cardShell(COMPACT_METRIC_HEIGHT_CLASS)} style={{ padding: DASHBOARD_PADDING }}>
          <h3 className="text-xs font-semibold text-slate-700">LMS Push Success</h3>
          <p className="mt-2 text-3xl font-bold text-emerald-700">100%</p>
          <p className="mt-1 text-[11px] text-slate-500">Zero downstream delivery failures</p>
        </article>
      </div>
    </section>
  );
}
