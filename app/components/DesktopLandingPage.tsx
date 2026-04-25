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
        <div
          className="desktop-title-enter desktop-card-hover w-full max-w-3xl rounded-2xl border border-slate-200 bg-white/85 p-8 text-center shadow-xl backdrop-blur-sm"
          style={{ willChange: "transform, opacity" }}
        >
          <div className="mb-4 flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          </div>
          <p className="desktop-subtitle-enter text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-500">
            Loan Underwriting AI Agent
          </p>
          <h1 className="desktop-text-enter mt-2 text-4xl font-semibold tracking-tight text-slate-900 md:text-5xl">
            AI Loan Agent
          </h1>
          <p className="desktop-subtitle-enter mt-2 text-sm text-slate-600 md:text-base">
            Virtual Credit Underwriter
          </p>
        </div>
      </section>

      <div
        className="desktop-dock-enter absolute bottom-[80px] left-1/2 z-40 flex -translate-x-1/2 items-center gap-6 rounded-2xl border border-slate-200 bg-white/90 px-5 py-3 shadow-lg backdrop-blur sm:gap-6"
        style={{ willChange: "transform, opacity" }}
      >
        {apps.map((app, index) => (
          <AppIcon
            key={app.route}
            label={app.label}
            route={app.route}
            color={app.color}
            glowClass={app.glowClass}
            icon={app.icon}
            delayMs={400 + index * 100}
          />
        ))}
      </div>
    </main>
  );
}
