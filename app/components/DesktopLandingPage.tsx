"use client";

import { BarChart3, ClipboardCheck, FileText } from "lucide-react";
import { DesktopBackground } from "@/app/components/DesktopBackground";
import { AppIcon } from "@/app/components/AppIcon";

type DesktopLandingPageProps = {
  backgroundImageUrl?: string;
};

export function DesktopLandingPage({ backgroundImageUrl }: DesktopLandingPageProps) {
  const apps = [
    {
      label: "Overview",
      route: "/overview",
      color: "from-blue-500 to-blue-600",
      glowClass: "hover:shadow-blue-500/50",
      icon: BarChart3,
    },
    {
      label: "HIL Review",
      route: "/hil-review",
      color: "from-orange-500 to-orange-600",
      glowClass: "hover:shadow-orange-500/50",
      icon: ClipboardCheck,
    },
    {
      label: "Applications",
      route: "/apps",
      color: "from-green-500 to-green-600",
      glowClass: "hover:shadow-green-500/50",
      icon: FileText,
    },
  ] as const;

  return (
    <main className="relative h-screen w-full overflow-hidden">
      <DesktopBackground backgroundImageUrl={backgroundImageUrl} />

      <section className="flex h-full w-full items-center justify-center px-6">
        <div className="text-center text-white">
          <h1 className="text-4xl font-semibold tracking-tight md:text-5xl">AI Loan Agent</h1>
          <p className="mt-2 text-sm text-blue-100 md:text-base">Virtual Credit Underwriter</p>
        </div>
      </section>

      <div className="absolute bottom-[80px] left-1/2 z-40 flex -translate-x-1/2 items-center gap-6 rounded-2xl bg-black/20 px-5 py-3 backdrop-blur-md sm:gap-6">
        {apps.map((app) => (
          <AppIcon
            key={app.route}
            label={app.label}
            route={app.route}
            color={app.color}
            glowClass={app.glowClass}
            icon={app.icon}
          />
        ))}
      </div>
    </main>
  );
}
