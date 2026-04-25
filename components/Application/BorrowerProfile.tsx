"use client";

import { Application } from "@/types/application";

type BorrowerMetric = {
  label: string;
  value: string;
};

function fmtInr(value?: number) {
  if (typeof value !== "number") return "N/A";
  return `INR ${value.toLocaleString("en-IN")}`;
}

function parseCibil(value: string) {
  const parsed = Number.parseInt(value.replace(/[^\d]/g, ""), 10);
  return Number.isFinite(parsed) ? parsed : null;
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

function recommendationClass(decision: Application["decision"]) {
  if (decision === "Rejected") return "text-rose-700";
  if (decision === "STP Approved") return "text-emerald-700";
  if (decision === "Conditional Approval") return "text-amber-700";
  return "text-blue-700";
}

export function BorrowerProfile({ application }: { application: Application }) {
  const tags = deriveTags(application);
  const metrics: BorrowerMetric[] = [
    { label: "CIBIL Score", value: application.cibil_score },
    { label: "DTI Ratio", value: `${application.dti_percent}%` },
    {
      label: "Bounce Frequency",
      value:
        typeof application.bounce_frequency_per_month === "number"
          ? `${application.bounce_frequency_per_month}/mo`
          : "N/A",
    },
    { label: "Spending Ratio", value: application.spending_ratio?.toString() ?? "N/A" },
    { label: "Post-EMI Surplus", value: fmtInr(application.post_emi_surplus) },
    {
      label: "Employment Tenure",
      value:
        typeof application.employment_tenure_years === "number"
          ? `${application.employment_tenure_years} yrs`
          : "N/A",
    },
  ];

  const policyBreaches = [
    application.dti_percent > 40 ? "DTI threshold exceeded (>40%)." : null,
    parseCibil(application.cibil_score) !== null && parseCibil(application.cibil_score)! < 620
      ? "Credit score below policy minimum (<620)."
      : null,
    application.cibil_score.toLowerCase().includes("proxy")
      ? "Proxy score used, requires manual confirmation."
      : null,
  ].filter(Boolean) as string[];

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
        <div className="mt-2 grid grid-cols-2 gap-2">
          {metrics.map((metric) => (
            <div key={metric.label} className="rounded border border-slate-200 bg-slate-50 p-2">
              <p className="text-[10px] text-slate-500">{metric.label}</p>
              <p className="text-sm font-semibold text-slate-900">{metric.value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-md border border-slate-200 bg-white p-3">
        <h4 className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-600">Decision Summary</h4>
        <p className={`mt-2 text-sm font-bold ${recommendationClass(application.decision)}`}>
          Recommendation: {application.decision.toUpperCase()}
        </p>

        <ul className="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-700">
          {application.hil_suggestions?.slice(0, 3).map((reason) => <li key={reason}>{reason}</li>)}
        </ul>

        {policyBreaches.length > 0 ? (
          <div className="mt-3 rounded border border-rose-200 bg-rose-50 p-2">
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-rose-700">Policy Breaches</p>
            <ul className="mt-1 list-disc space-y-0.5 pl-4 text-xs text-rose-700">
              {policyBreaches.map((breach) => <li key={breach}>{breach}</li>)}
            </ul>
          </div>
        ) : null}

        <p className="mt-3 text-xs text-slate-600">
          Confidence Score: <span className="font-semibold text-slate-900">{application.confidence_score}%</span>
        </p>
      </div>
    </section>
  );
}
