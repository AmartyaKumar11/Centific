import { MacWindowCard } from "@/components/ui/MacWindowCard";

type KPIItem = {
  label: string;
  value: string | number;
  subLabel: string;
  tone: "blue" | "green" | "amber" | "red" | "purple";
};

const toneMap: Record<KPIItem["tone"], string> = {
  blue: "accent-blue border-blue-200 bg-gradient-to-br from-blue-50 to-white",
  green: "accent-green border-emerald-200 bg-gradient-to-br from-emerald-50 to-white",
  amber: "accent-amber border-amber-200 bg-gradient-to-br from-amber-50 to-white",
  red: "accent-red border-rose-200 bg-gradient-to-br from-rose-50 to-white",
  purple: "accent-purple border-violet-200 bg-gradient-to-br from-violet-50 to-white",
};

export function KPICards({ items }: { items: KPIItem[] }) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
      {items.map((item, index) => (
        <MacWindowCard
          key={item.label}
          title={item.label}
          className={`hover:-translate-y-0.5 ${toneMap[item.tone]} animate-fade-up`}
          style={{ animationDelay: `${index * 70}ms` }}
        >
          <p className="text-2xl font-semibold text-slate-900">{item.value}</p>
          <p className="mt-1 text-xs subtle-text">{item.subLabel}</p>
        </MacWindowCard>
      ))}
    </section>
  );
}
