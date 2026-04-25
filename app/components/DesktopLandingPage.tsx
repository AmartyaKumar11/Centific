"use client";

import { DesktopBackground } from "@/app/components/DesktopBackground";

type DesktopLandingPageProps = {
  backgroundImageUrl?: string;
};

export function DesktopLandingPage({ backgroundImageUrl }: DesktopLandingPageProps) {
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

    </main>
  );
}
