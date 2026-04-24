type KPIItem = {
  label: string;
  value: string | number;
  subLabel: string;
  tone: "blue" | "green" | "amber" | "red" | "purple";
};

const toneMap: Record<KPIItem["tone"], string> = {
  blue: "bg-blue-50 border-blue-200",
  green: "bg-emerald-50 border-emerald-200",
  amber: "bg-amber-50 border-amber-200",
  red: "bg-rose-50 border-rose-200",
  purple: "bg-violet-50 border-violet-200",
};

export function KPICards({ items }: { items: KPIItem[] }) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
      {items.map((item) => (
        <article
          key={item.label}
          className={`card-shell p-4 transition hover:-translate-y-0.5 hover:shadow-md ${toneMap[item.tone]}`}
        >
          <p className="text-[11px] font-medium uppercase tracking-[0.08em] subtle-text">
            {item.label}
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{item.value}</p>
          <p className="mt-1 text-xs subtle-text">{item.subLabel}</p>
        </article>
      ))}
    </section>
  );
}
