"use client";

import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { LucideIcon } from "lucide-react";

type AppIconProps = {
  label: string;
  route: string;
  color: string;
  glowClass?: string;
  icon: LucideIcon;
  delayMs?: number;
};

export function AppIcon({
  label,
  route,
  color,
  glowClass = "hover:shadow-blue-500/40",
  icon: Icon,
  delayMs = 0,
}: AppIconProps) {
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [hovered, setHovered] = useState(false);
  const [pressed, setPressed] = useState(false);

  const transformStyle = useMemo(() => {
    const scale = pressed ? 0.95 : hovered ? 1.2 : 1;
    return `translate3d(${offset.x}px, ${offset.y}px, 0) scale(${scale})`;
  }, [offset.x, offset.y, hovered, pressed]);

  return (
    <Link
      to={route}
      aria-label={label}
      className="group relative focus:outline-none"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => {
        setHovered(false);
        setPressed(false);
        setOffset({ x: 0, y: 0 });
      }}
      onMouseMove={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        const dx = event.clientX - (rect.left + rect.width / 2);
        const dy = event.clientY - (rect.top + rect.height / 2);
        const maxPull = 12;
        setOffset({
          x: Math.max(-maxPull, Math.min(maxPull, dx * 0.25)),
          y: Math.max(-maxPull, Math.min(maxPull, dy * 0.25)),
        });
      }}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
    >
      <span
        className={`desktop-icon-enter flex h-[60px] w-[60px] items-center justify-center rounded-lg bg-gradient-to-br text-white shadow-lg transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl ${glowClass} focus-visible:ring-2 focus-visible:ring-white/50 ${color}`}
        style={{
          transform: transformStyle,
          transitionTimingFunction: "cubic-bezier(0.34, 1.56, 0.64, 1)",
          animationDelay: `${delayMs}ms`,
          willChange: "transform",
        }}
      >
        <Icon size={28} />
      </span>
      <span className="tooltip-fade pointer-events-none absolute bottom-full left-1/2 z-10 mb-3 -translate-x-1/2 rounded bg-white/90 px-3 py-1.5 text-sm font-medium text-slate-900 opacity-0 backdrop-blur transition-all duration-200 group-hover:-translate-y-1 group-hover:opacity-100">
        {label}
      </span>
    </Link>
  );
}
