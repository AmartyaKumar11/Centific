"use client";

import { Application } from "@/types/application";
import { MetricsGrid } from "@/components/Application/MetricsGrid";
import type { MetricItemProps } from "@/components/Application/MetricItem";
import { DecisionSummary } from "@/components/Application/DecisionSummary";
import type { PolicyBreach } from "@/components/Application/DecisionSummary";

function parseCibil(value: string) {
  const parsed = Number.parseInt(value.replace(/[^\d]/g, ""), 10);
  return Number.isFinite(parsed) ? parsed : null;
}

function cibilContextLabel(score: string): string {
  const lower = score.toLowerCase();
  if (lower.includes("proxy")) return "Bureau Pull";
  if (parseCibil(score) !== null) return "Direct";
  return "Cached";
}

function deriveTags(application: Application) {
  const tags: string[] = [];
  if (application.dti_percent > 40) tags.push("HIGH_DTI");
  const cibil = parseCibil(application.cibil_score);
  if (cibil !== null && cibil < 620) tags.push("LOW_CREDIT_SCORE");
  if (application.cibil_score.toLowerCase().includes("proxy")) tags.push("PROXY_SCORE");
  tags.push(application.decision.toUpperCase());
  return tags;
}

function riskBarClass(risk: Application["risk"]) {
  if (risk === "Low") return "bg-emerald-500";
  if (risk === "Medium") return "bg-amber-500";
  if (risk === "High") return "bg-rose-600";
  return "bg-slate-700";
}

export function BorrowerProfile({ application }: { application: Application }) {
  const tags = deriveTags(application);
  const cibilNumeric = parseCibil(application.cibil_score);
  const metricItems: MetricItemProps[] = [
    {
      label: "CIBIL Score",
      value: cibilNumeric ?? application.cibil_score,
      valueKind: "plain",
      context: cibilContextLabel(application.cibil_score),
    },
    {
      label: "DTI Ratio",
      value: application.dti_percent,
      valueKind: "percent",
      badge:
        application.dti_percent > 40
          ? { text: "High Risk", tone: "negative" }
          : { text: "Within policy", tone: "neutral" },
    },
    {
      label: "Bounce Frequency",
      value:
        typeof application.bounce_frequency_per_month === "number"
          ? `${application.bounce_frequency_per_month}/mo`
          : "N/A",
      valueKind: "plain",
    },
    {
      label: "Spending Ratio",
      value: application.spending_ratio ?? "N/A",
      valueKind: "plain",
    },
    {
      label: "Post-EMI Surplus",
      value:
        typeof application.post_emi_surplus === "number" ? application.post_emi_surplus : "N/A",
      valueKind: typeof application.post_emi_surplus === "number" ? "currency" : "plain",
    },
    {
      label: "Employment Tenure",
      value: application.employment_tenure_years ?? "N/A",
      valueKind: typeof application.employment_tenure_years === "number" ? "duration" : "plain",
    },
  ];

  const policyBreaches = [
    application.dti_percent > 40
      ? { text: "DTI > 40% hard policy breach", severity: "critical" as const }
      : null,
    parseCibil(application.cibil_score) !== null && parseCibil(application.cibil_score)! < 620
      ? { text: "CIBIL < 620 soft policy breach", severity: "warning" as const }
      : null,
  ].filter((breach): breach is PolicyBreach => breach !== null);

  return (
    <section className="h-full space-y-3 overflow-y-auto pr-1">
      <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
        <p className="text-lg font-semibold text-slate-900">{application.applicant_name}</p>
        <p className="text-xs text-slate-500">{application.id}</p>

        <div className="mt-2 flex flex-wrap gap-1.5">
          {tags.map((tag) => (
            <span key={tag} className="rounded border border-slate-200 bg-white px-2 py-0.5 text-[10px] font-semibold text-slate-700">
              {tag}
            </span>
          ))}
        </div>

        <div className="mt-3">
          <div className="flex items-end justify-between">
            <p className="text-4xl font-bold text-slate-900">{application.risk_score}</p>
            <p className="text-xs font-semibold text-slate-500">/ 100</p>
          </div>
          <div className="mt-2 h-2 rounded-full bg-slate-200">
            <div className={`h-2 rounded-full ${riskBarClass(application.risk)}`} style={{ width: `${application.risk_score}%` }} />
          </div>
        </div>
      </div>

      <div className="rounded-md border border-slate-200 bg-white p-3">
        <h4 className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-600">Key Metrics</h4>
        <div className="mt-2">
          <MetricsGrid items={metricItems} />
        </div>
      </div>

      <DecisionSummary
        recommendation={application.decision}
        reasons={application.hil_suggestions ?? []}
        policyBreaches={policyBreaches}
        confidence={application.confidence_score}
      />
    </section>
  );
}
