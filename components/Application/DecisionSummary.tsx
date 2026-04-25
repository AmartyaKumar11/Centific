"use client";

import { Application } from "@/types/application";

type RecommendationKind = "rejected" | "approved" | "conditional";
type BreachSeverity = "critical" | "warning";

export type PolicyBreach = {
  text: string;
  severity: BreachSeverity;
};

type DecisionSummaryProps = {
  recommendation: Application["decision"];
  reasons: string[];
  policyBreaches?: PolicyBreach[];
  confidence?: number;
};

const recommendationStyle: Record<
  RecommendationKind,
  { border: string; badge: string; progress: string; confidenceText: string; label: string }
> = {
  rejected: {
    border: "border-l-rose-600",
    badge: "border-rose-200 bg-rose-50 text-rose-700",
    progress: "bg-rose-600",
    confidenceText: "text-rose-700",
    label: "Rejected",
  },
  approved: {
    border: "border-l-emerald-600",
    badge: "border-emerald-200 bg-emerald-50 text-emerald-700",
    progress: "bg-emerald-600",
    confidenceText: "text-emerald-700",
    label: "Approved",
  },
  conditional: {
    border: "border-l-amber-500",
    badge: "border-amber-200 bg-amber-50 text-amber-700",
    progress: "bg-amber-500",
    confidenceText: "text-amber-700",
    label: "Conditional Approval",
  },
};

function toRecommendationKind(decision: Application["decision"]): RecommendationKind {
  if (decision === "Rejected") return "rejected";
  if (decision === "Conditional Approval") return "conditional";
  return "approved";
}

function severityClass(severity: BreachSeverity) {
  return severity === "critical"
    ? "border-rose-200 bg-rose-50 text-rose-700"
    : "border-amber-200 bg-amber-50 text-amber-700";
}

function severityLabel(severity: BreachSeverity) {
  return severity === "critical" ? "Critical" : "Warning";
}

export function DecisionSummary({
  recommendation,
  reasons,
  policyBreaches = [],
  confidence,
}: DecisionSummaryProps) {
  const kind = toRecommendationKind(recommendation);
  const style = recommendationStyle[kind];
  const confidenceValue = Math.max(0, Math.min(100, Math.round(confidence ?? 0)));

  return (
    <section className={`rounded-md border border-slate-200 border-l-4 bg-white p-4 ${style.border}`}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h4 className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-600">Decision Summary</h4>
        <span className={`rounded border px-2 py-0.5 text-xs font-semibold ${style.badge}`}>
          {style.label}
        </span>
      </div>

      {reasons.length > 0 ? (
        <div className="mt-3">
          <p className="text-xs font-semibold text-slate-700">Top Reasons</p>
          <ul className="mt-1 list-disc space-y-1 pl-4 text-xs text-slate-700">
            {reasons.slice(0, 3).map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {policyBreaches.length > 0 ? (
        <div className="mt-3">
          <p className="text-xs font-semibold text-slate-700">Policy Breaches</p>
          <ul className="mt-1 space-y-1.5">
            {policyBreaches.map((breach) => (
              <li
                key={`${breach.severity}-${breach.text}`}
                className={`rounded border px-2 py-1 text-xs ${severityClass(breach.severity)}`}
              >
                <span className="font-semibold">{severityLabel(breach.severity)}:</span> {breach.text}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {typeof confidence === "number" ? (
        <div className="mt-3">
          <div className="mb-1 flex items-center justify-between text-xs">
            <p className="font-semibold text-slate-700">Confidence</p>
            <p className={style.confidenceText}>{confidenceValue}%</p>
          </div>
          <div className="h-2 rounded-full bg-slate-200">
            <div
              className={`h-2 rounded-full transition-all ${style.progress}`}
              style={{ width: `${confidenceValue}%` }}
            />
          </div>
          <p className="mt-1 text-[11px] text-slate-500">
            {confidenceValue >= 85 ? "High confidence in this decision" : "Moderate confidence in this decision"}
          </p>
        </div>
      ) : null}
    </section>
  );
}
