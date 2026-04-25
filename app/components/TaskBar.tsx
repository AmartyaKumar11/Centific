"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  ClipboardCheck,
  FileText,
  type LucideIcon,
} from "lucide-react";
import { AppIcon } from "@/app/components/AppIcon";

type DesktopApp = {
  label: string;
  icon: LucideIcon;
  color: string;
  glowClass: string;
  route: string;
};

export const DESKTOP_APPS: DesktopApp[] = [
  {
    label: "Overview",
    icon: BarChart3,
    color: "from-blue-500 to-blue-600",
    glowClass: "hover:shadow-blue-500/50",
    route: "/overview",
  },
  {
    label: "HIL Review",
    icon: ClipboardCheck,
    color: "from-orange-500 to-orange-600",
    glowClass: "hover:shadow-orange-500/50",
    route: "/hil-review",
  },
  {
    label: "Applications",
    icon: FileText,
    color: "from-green-500 to-green-600",
    glowClass: "hover:shadow-green-500/50",
    route: "/apps",
  },
];

export function TaskBar() {
  const pathname = usePathname();
  const [time, setTime] = useState("");

  useEffect(() => {
    const update = () =>
      setTime(
        new Date().toLocaleTimeString("en-IN", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      );
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, []);

  const activePath = useMemo(() => {
    if (pathname === "/") return "";
    return pathname;
  }, [pathname]);

  return (
    <footer className="fixed bottom-5 left-1/2 z-50 -translate-x-1/2">
      <div className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white/90 px-4 py-2.5 shadow-lg backdrop-blur-md">
        <nav className="flex items-center gap-4">
          {DESKTOP_APPS.map((app) => (
            <AppIcon
              key={app.route}
              label={app.label}
              route={app.route}
              color={app.color}
              glowClass={app.glowClass}
              icon={app.icon}
            />
          ))}
        </nav>
        <span className="ml-1 hidden text-xs font-medium text-slate-500 sm:inline">{time}</span>
      </div>
    </footer>
  );
}
