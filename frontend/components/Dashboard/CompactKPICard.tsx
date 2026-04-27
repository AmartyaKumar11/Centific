"use client";

type CompactKPICardProps = {
  title: string;
  value: string | number;
  subtitle: string;
  tone?: "blue" | "green" | "amber" | "red" | "purple";
};

const toneClassMap: Record<NonNullable<CompactKPICardProps["tone"]>, string> = {
  blue: "border-l-blue-500 bg-blue-50/60",
  green: "border-l-emerald-500 bg-emerald-50/60",
  amber: "border-l-amber-500 bg-amber-50/60",
  red: "border-l-rose-500 bg-rose-50/60",
  purple: "border-l-violet-500 bg-violet-50/60",
};

export function CompactKPICard({ title, value, subtitle, tone = "blue" }: CompactKPICardProps) {
  return (
    <article
      className={`h-[68px] rounded-lg border border-slate-200 border-l-4 px-3 py-2 shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md ${toneClassMap[tone]}`}
    >
      <p className="truncate text-[10px] font-semibold uppercase tracking-[0.08em] text-slate-500">{title}</p>
      <div className="mt-0.5 flex items-end justify-between gap-2">
        <p className="text-xl font-semibold leading-none text-slate-900">{value}</p>
        <p className="truncate text-[11px] text-slate-500">{subtitle}</p>
      </div>
    </article>
  );
}
