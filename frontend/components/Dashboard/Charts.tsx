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
import { MacWindowCard } from "@/components/ui/MacWindowCard";

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function countBy<T extends string>(items: T[]) {
  return items.reduce<Record<string, number>>((acc, key) => {
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {});
}

export function Charts({ applications }: { applications: Application[] }) {
  const decisionCounts = countBy(applications.map((a) => a.decision));
  const riskCounts = countBy(applications.map((a) => a.risk));
  const confidenceBands = {
    "90-100": applications.filter((a) => a.confidence_score >= 90).length,
    "75-89": applications.filter((a) => a.confidence_score >= 75 && a.confidence_score < 90)
      .length,
    "Below 75": applications.filter((a) => a.confidence_score < 75).length,
  };

  return (
    <section className="grid gap-4 lg:grid-cols-3">
      <MacWindowCard title="Decision Distribution" bodyClassName="p-0">
        <div className="h-56 p-4 pt-0">
          <Doughnut
            data={{
              labels: Object.keys(decisionCounts),
              datasets: [
                {
                  data: Object.values(decisionCounts),
                  backgroundColor: ["#15803d", "#d97706", "#1d4ed8", "#b91c1c"],
                  borderWidth: 0,
                },
              ],
            }}
            options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }}
          />
        </div>
      </MacWindowCard>

      <MacWindowCard title="Risk Distribution" bodyClassName="p-0">
        <div className="h-56 p-4 pt-0">
          <Doughnut
            data={{
              labels: Object.keys(riskCounts),
              datasets: [
                {
                  data: Object.values(riskCounts),
                  backgroundColor: ["#15803d", "#d97706", "#b91c1c", "#475569"],
                  borderWidth: 0,
                },
              ],
            }}
            options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }}
          />
        </div>
      </MacWindowCard>

      <MacWindowCard title="Confidence Distribution" bodyClassName="p-0">
        <div className="h-56 p-4 pt-0">
          <Bar
            data={{
              labels: Object.keys(confidenceBands),
              datasets: [
                {
                  label: "Applications",
                  data: Object.values(confidenceBands),
                  backgroundColor: ["#1d4ed8", "#7c3aed", "#b91c1c"],
                  borderRadius: 6,
                },
              ],
            }}
            options={{
              maintainAspectRatio: false,
              scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
              plugins: { legend: { display: false } },
            }}
          />
        </div>
      </MacWindowCard>
    </section>
  );
}
