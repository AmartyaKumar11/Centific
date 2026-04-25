"use client";

import Link from "next/link";
import type { LucideIcon } from "lucide-react";

type AppIconProps = {
  label: string;
  route: string;
  color: string;
  glowClass?: string;
  icon: LucideIcon;
};

export function AppIcon({
  label,
  route,
  color,
  glowClass = "hover:shadow-blue-500/40",
  icon: Icon,
}: AppIconProps) {
  return (
    <Link href={route} aria-label={label} className="group relative focus:outline-none">
      <span
        className={`flex h-[60px] w-[60px] items-center justify-center rounded-lg bg-gradient-to-br text-white shadow-lg transition-all duration-200 hover:scale-110 hover:shadow-xl ${glowClass} focus-visible:ring-2 focus-visible:ring-white/50 ${color}`}
      >
        <Icon size={28} />
      </span>
      <span className="tooltip-fade pointer-events-none absolute bottom-full left-1/2 z-10 mb-3 -translate-x-1/2 rounded bg-white/90 px-3 py-1.5 text-sm font-medium text-slate-900 opacity-0 backdrop-blur transition-opacity duration-200 group-hover:opacity-100">
        {label}
      </span>
    </Link>
  );
}
