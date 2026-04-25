"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  ClipboardCheck,
  FileText,
  BarChart4,
  Settings,
  LogOut,
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
  {
    label: "Reports",
    icon: BarChart4,
    color: "from-purple-500 to-purple-600",
    glowClass: "hover:shadow-purple-500/50",
    route: "/reports",
  },
  {
    label: "Settings",
    icon: Settings,
    color: "from-slate-500 to-slate-600",
    glowClass: "hover:shadow-slate-500/50",
    route: "/settings",
  },
  {
    label: "Logout",
    icon: LogOut,
    color: "from-red-500 to-red-600",
    glowClass: "hover:shadow-red-500/50",
    route: "/logout",
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
    <>
      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-black/30 px-3 py-2 backdrop-blur-lg lg:hidden">
        <nav className="flex items-center gap-2 overflow-x-auto pb-1">
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
      </header>

      <footer className="fixed inset-x-0 bottom-0 z-50 hidden h-[70px] border-t border-white/10 bg-black/30 px-6 py-2 backdrop-blur-lg lg:block">
        <div className="mx-auto flex h-full max-w-7xl items-center justify-between">
          <div className="hidden w-[110px] text-xs text-white/70 lg:block">
            {new Date().toLocaleDateString("en-IN")}
          </div>

          <nav className="mx-auto flex items-center justify-center gap-3 md:gap-4">
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

          <div className="w-[110px] text-right text-xs font-medium text-white/80">{time}</div>
        </div>
      </footer>
    </>
  );
}
