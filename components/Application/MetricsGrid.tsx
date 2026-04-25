"use client";

import { MetricItem, type MetricItemProps } from "@/components/Application/MetricItem";

export function MetricsGrid({ items }: { items: MetricItemProps[] }) {
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2" style={{ gap: "12px" }}>
      {items.map((item) => (
        <MetricItem key={item.label} {...item} />
      ))}
    </div>
  );
}
