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

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function countBy<T extends string>(items: T[]) {
  return items.reduce<Record<string, number>>((acc, key) => {
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {});
}

function WindowCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <article className="card-shell overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-3 py-2">
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-rose-400" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-400" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
        </div>
        <h3 className="text-xs font-semibold text-slate-700">{title}</h3>
      </div>
      <div className="p-3">{children}</div>
    </article>
  );
}

function Gauge({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <WindowCard title={label}>
      <div className="h-36">
        <Doughnut
          data={{
            labels: ["value", "remaining"],
            datasets: [
              {
                data: [value, 100 - value],
                backgroundColor: [color, "#f1f5f9"],
                borderWidth: 0,
              },
            ],
          }}
          options={{
            maintainAspectRatio: false,
            rotation: -90,
            circumference: 180,
            cutout: "72%",
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
          }}
        />
      </div>
      <p className="-mt-2 text-center text-xs font-semibold text-slate-700">{value}%</p>
    </WindowCard>
  );
}

export function OverviewPanels({ applications }: { applications: Application[] }) {
  const decisionCounts = countBy(applications.map((a) => a.decision));
  const riskCounts = countBy(applications.map((a) => a.risk));
  const employerCounts = countBy(applications.map((a) => a.employer_type));
  const rejectionReasons = {
    HIGH_DTI: applications.filter((a) => a.dti_percent > 40).length,
    LOW_CIBIL: applications.filter((a) => Number.parseInt(a.cibil_score, 10) < 620).length,
    HIGH_RISK: applications.filter((a) => a.risk === "High" || a.risk === "Very High").length,
    PROXY_SCORE: applications.filter((a) => a.cibil_score.includes("Proxy")).length,
  };

  return (
    <section className="space-y-4">
      <div className="grid gap-3 lg:grid-cols-3">
        <WindowCard title="Decision Distribution">
          <div className="h-52">
            <Doughnut
              data={{
                labels: Object.keys(decisionCounts),
                datasets: [
                  {
                    data: Object.values(decisionCounts),
                    backgroundColor: ["#15803d", "#d97706", "#1d4ed8", "#b91c1c"],
                    borderWidth: 1,
                    borderColor: "#fff",
                  },
                ],
              }}
              options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }}
            />
          </div>
        </WindowCard>
        <WindowCard title="Risk Tier Distribution">
          <div className="h-52">
            <Doughnut
              data={{
                labels: Object.keys(riskCounts),
                datasets: [
                  {
                    data: Object.values(riskCounts),
                    backgroundColor: ["#15803d", "#d97706", "#b91c1c", "#475569"],
                    borderWidth: 1,
                    borderColor: "#fff",
                  },
                ],
              }}
              options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }}
            />
          </div>
        </WindowCard>
        <WindowCard title="Employer Type Split">
          <div className="h-52">
            <Doughnut
              data={{
                labels: Object.keys(employerCounts),
                datasets: [
                  {
                    data: Object.values(employerCounts),
                    backgroundColor: ["#1d4ed8", "#7c3aed"],
                    borderWidth: 1,
                    borderColor: "#fff",
                  },
                ],
              }}
              options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }}
            />
          </div>
        </WindowCard>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <WindowCard title="Daily Batch Volume">
          <div className="h-52">
            <Bar
              data={{
                labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"],
                datasets: [
                  {
                    label: "Processed",
                    data: [42, 76, 50, 61, 47, 20, 39],
                    backgroundColor: "rgba(59,130,246,0.8)",
                    borderRadius: 5,
                  },
                  {
                    label: "Rejected",
                    data: [9, 14, 7, 11, 8, 3, 12],
                    backgroundColor: "rgba(239,68,68,0.7)",
                    borderRadius: 5,
                  },
                ],
              }}
              options={{ maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }}
            />
          </div>
        </WindowCard>
        <WindowCard title="Top Rejection Reasons">
          <div className="h-52">
            <Bar
              data={{
                labels: Object.keys(rejectionReasons),
                datasets: [
                  {
                    data: Object.values(rejectionReasons),
                    backgroundColor: ["#ef4444", "#f87171", "#f59e0b", "#60a5fa"],
                    borderRadius: 6,
                  },
                ],
              }}
              options={{
                indexAxis: "y",
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true } },
              }}
            />
          </div>
        </WindowCard>
      </div>

      <article className="card-shell p-3">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-800">Live Pipeline - BTC-0426-014</p>
          <span className="rounded-full bg-emerald-100 px-2 py-1 text-[11px] font-semibold text-emerald-700">
            PROCESSING
          </span>
        </div>
        <div className="mt-3 grid grid-cols-7 gap-2 text-center">
          {["Data Intake", "Feature Eng", "Rule Engine", "LLM Reasoning", "HIL Review", "Audit Trail", "LMS Push"].map(
            (step, idx) => (
              <div key={step} className="rounded-md border border-slate-200 bg-slate-50 px-2 py-2">
                <p className="text-[10px] text-slate-500">{String(idx + 1).padStart(2, "0")}</p>
                <p className="text-[11px] font-medium text-slate-700">{step}</p>
              </div>
            )
          )}
        </div>
      </article>

      <div className="grid gap-3 lg:grid-cols-4">
        <Gauge label="STP Rate" value={68} color="#15803d" />
        <Gauge label="Decision Accuracy" value={93} color="#2563eb" />
        <Gauge label="False Reject Rate" value={18} color="#16a34a" />
        <Gauge label="LMS Push Success" value={100} color="#15803d" />
      </div>
    </section>
  );
}
