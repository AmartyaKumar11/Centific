"use client";

import type { ReactNode } from "react";

export type MetricValueKind = "plain" | "percent" | "currency" | "duration";

export type MetricBadgeTone = "positive" | "negative" | "neutral";

export type MetricItemProps = {
  label: string;
  value: string | number;
  valueKind?: MetricValueKind;
  /** Optional secondary text next to value (e.g. CIBIL context) */
  context?: string;
  /** Optional badge below the value row */
  badge?: { text: string; tone: MetricBadgeTone };
};

const badgeToneClass: Record<MetricBadgeTone, string> = {
  positive: "border-emerald-200 bg-emerald-50 text-emerald-800",
  negative: "border-rose-200 bg-rose-50 text-rose-800",
  neutral: "border-slate-200 bg-slate-100 text-slate-700",
};

function formatValue(value: string | number, kind: MetricValueKind): string {
  if (typeof value === "string") return value;
  if (kind === "percent") return `${value}%`;
  if (kind === "currency")
    return `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  if (kind === "duration") return `${value} yrs`;
  return String(value);
}

function valueClassName(kind: MetricValueKind, badge?: MetricItemProps["badge"]): string {
  if (kind === "currency" && !badge) return "font-bold text-emerald-700";
  if (badge?.tone === "negative") return "font-bold text-rose-700";
  return "font-bold text-slate-900";
}

export function MetricItem({ label, value, valueKind = "plain", context, badge }: MetricItemProps) {
  const display = formatValue(value, valueKind);
  const contextNode: ReactNode =
    context !== undefined ? (
      <span className="text-[12px] font-medium text-slate-500"> ({context})</span>
    ) : null;

  return (
    <div className="rounded-md border border-[#e5e7eb] bg-[#f9fafb] p-3 transition-shadow hover:shadow-sm">
      <p className="text-[12px] text-slate-500">{label}</p>
      <p className={`mt-1 text-[16px] leading-tight ${valueClassName(valueKind, badge)}`}>
        {display}
        {contextNode}
      </p>
      {badge ? (
        <span
          className={`mt-2 inline-flex rounded border px-1.5 py-0.5 text-[11px] font-semibold ${badgeToneClass[badge.tone]}`}
        >
          {badge.text}
        </span>
      ) : null}
    </div>
  );
}
