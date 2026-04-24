"use client";

import { useMemo, useState, type ReactNode } from "react";
import { Application } from "@/types/application";
import { MacWindowCard } from "@/components/ui/MacWindowCard";

type ApplicationReviewModalProps = {
  application: Application | null;
  onClose: () => void;
};

const toneDotClass = {
  info: "bg-blue-500",
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  danger: "bg-rose-500",
};

function formatInr(amount: number) {
  return `INR ${amount.toLocaleString("en-IN")}`;
}

function parseCibilNumeric(value: string) {
  const digits = value.replace(/[^\d]/g, "");
  if (!digits) return null;
  const n = Number.parseInt(digits, 10);
  return Number.isFinite(n) ? n : null;
}

function deriveFlags(application: Application) {
  const flags: string[] = [];
  if (application.dti_percent > 40) flags.push("HIGH_DTI");
  const cibilNum = parseCibilNumeric(application.cibil_score);
  if (cibilNum !== null && cibilNum < 620) flags.push("LOW_CREDIT_SCORE");
  if (application.cibil_score.toLowerCase().includes("proxy")) flags.push("PROXY_SCORE_APPLIED");
  return flags;
}

function riskBarColor(application: Application) {
  if (application.risk === "Low") return "bg-emerald-600";
  if (application.risk === "Medium") return "bg-amber-500";
  if (application.risk === "High") return "bg-rose-600";
  return "bg-slate-800";
}

function riskScoreColor(application: Application) {
  if (application.risk === "Low") return "text-emerald-700";
  if (application.risk === "Medium") return "text-amber-700";
  if (application.risk === "High") return "text-rose-700";
  return "text-slate-900";
}

function decisionPill(application: Application) {
  if (application.decision === "Rejected") return "chip border-rose-300 bg-rose-50 text-rose-800";
  if (application.decision === "STP Approved") return "chip border-emerald-300 bg-emerald-50 text-emerald-800";
  if (application.decision === "Conditional Approval") return "chip border-amber-300 bg-amber-50 text-amber-800";
  return "chip border-blue-300 bg-blue-50 text-blue-800";
}

type AccordionKey = "decision" | "risk" | "hil";

export function ApplicationReviewModal({ application, onClose }: ApplicationReviewModalProps) {
  const [openSections, setOpenSections] = useState<Record<AccordionKey, boolean>>({
    decision: true,
    risk: true,
    hil: true,
  });

  const toggleSection = (key: AccordionKey) => {
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const flags = useMemo(() => (application ? deriveFlags(application) : []), [application]);
  const avgIncome =
    application?.income_average ??
    (application ? Math.round((application.income_declared + application.income_verified) / 2) : 0);

  if (!application) return null;

  const riskSummary =
    application.risk_summary ??
    "Risk summary is not available for this demo record. Populate `risk_summary` in mock data to mirror production outputs.";
  const hilSuggestions =
    application.hil_suggestions ??
    (application.hil_required_flag
      ? [
          "Request clarifications on any unresolved policy flags.",
          "Validate employment and income documentation against bank credits.",
          "Confirm final decision rationale for audit trail completeness.",
        ]
      : ["No HIL assistant suggestions are required for this application."]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/45 p-3 backdrop-blur-sm animate-fade-up"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <MacWindowCard
        title={application.applicant_name.toUpperCase()}
        className="max-h-[92vh] w-full max-w-[min(1400px,96vw)] shadow-2xl animate-fade-up-delay-1"
        bodyClassName="p-0"
        headerRight={
          <div className="flex items-center gap-2">
            <span className="hidden text-[11px] font-medium text-slate-500 sm:inline">{application.id}</span>
            <span className="pulse-live rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
              Live
            </span>
            <button
              onClick={onClose}
              className="rounded-full border border-slate-200 px-3 py-1 text-sm text-slate-600 transition hover:bg-slate-50"
            >
              Close
            </button>
          </div>
        }
      >
        <div className="border-b border-slate-200 bg-slate-50/80 px-4 py-3">
          <div className="flex flex-wrap gap-2">
            {flags.map((flag) => (
              <span key={flag} className="chip border-rose-300 bg-rose-50 text-rose-800">
                {flag}
              </span>
            ))}
            <span className={decisionPill(application)}>{application.decision.toUpperCase()}</span>
          </div>
        </div>

        <div className="grid max-h-[calc(92vh-120px)] grid-cols-1 gap-0 overflow-hidden xl:grid-cols-12">
          <section className="xl:col-span-4 border-b border-slate-200 p-4 xl:border-b-0 xl:border-r">
            <MacWindowCard
              title="Application Event Log"
              bodyClassName="p-0"
              headerRight={
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600">
                  Audit
                </span>
              }
            >
              <div className="relative max-h-[calc(92vh-200px)] space-y-4 overflow-y-auto p-4 pl-6 before:absolute before:left-[8px] before:top-2 before:h-[calc(100%-16px)] before:w-px before:bg-slate-200">
                {application.audit_trail.map((event) => (
                  <article
                    key={`${event.event_time}-${event.event_code}`}
                    className="relative rounded-lg border border-slate-100 bg-slate-50/60 p-3 transition hover:-translate-y-0.5 hover:shadow-sm"
                  >
                    <span
                      className={`absolute -left-6 top-3 h-3 w-3 rounded-full ring-4 ring-white ${toneDotClass[event.tone]}`}
                    />
                    <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-500">
                      {event.event_time} - {event.event_code}
                    </p>
                    <h4 className="text-sm font-semibold text-slate-900">{event.title}</h4>
                    <p className="mt-1 text-xs text-slate-600">{event.details}</p>
                  </article>
                ))}
              </div>
            </MacWindowCard>
          </section>

          <section className="xl:col-span-5 border-b border-slate-200 p-4 xl:border-b-0 xl:border-r">
            <div className="max-h-[calc(92vh-160px)] space-y-4 overflow-y-auto pr-1">
              <div className="grid gap-3 lg:grid-cols-2">
                <MacWindowCard title="Borrower Profile">
                  <div className="space-y-2 text-sm text-slate-700">
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Employer</span>
                      <span className="text-right font-medium text-slate-900">
                        {application.employer} ({application.employer_type})
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Employment Tenure</span>
                      <span className="font-medium text-slate-900">
                        {application.employment_tenure_years
                          ? `${application.employment_tenure_years} yrs`
                          : "Not provided"}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Gross Monthly Salary</span>
                      <span className="font-medium text-slate-900">{formatInr(application.income_declared)}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Net Salary</span>
                      <span className="font-medium text-slate-900">{formatInr(application.income_verified)}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Avg Monthly Income</span>
                      <span className="font-medium text-slate-900">{formatInr(avgIncome)}</span>
                    </div>
                  </div>
                </MacWindowCard>

                <MacWindowCard title="Risk Assessment">
                  <div className="text-center">
                    <p className={`text-5xl font-bold ${riskScoreColor(application)}`}>{application.risk_score}</p>
                    <p className="mt-1 text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">
                      {application.risk} Risk / 100
                    </p>
                    <div className="mx-auto mt-3 h-2 w-full max-w-xs rounded-full bg-slate-100">
                      <div
                        className={`h-2 rounded-full ${riskBarColor(application)}`}
                        style={{ width: `${application.risk_score}%` }}
                      />
                    </div>
                  </div>
                  <div className="mt-4 space-y-2 text-sm text-slate-700">
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">CIBIL Score</span>
                      <span className="font-medium text-slate-900">{application.cibil_score} (Direct)</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">DTI Ratio</span>
                      <span
                        className={`font-semibold ${
                          application.dti_percent > 40 ? "text-rose-700" : "text-slate-900"
                        }`}
                      >
                        {application.dti_percent}%
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Bounce Frequency</span>
                      <span className="font-medium text-slate-900">
                        {typeof application.bounce_frequency_per_month === "number"
                          ? `${application.bounce_frequency_per_month} / mo`
                          : "Not provided"}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Spending Ratio</span>
                      <span className="font-medium text-slate-900">{application.spending_ratio ?? "Not provided"}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Post-EMI Surplus</span>
                      <span className="font-medium text-slate-900">
                        {application.post_emi_surplus ? formatInr(application.post_emi_surplus) : "Not provided"}
                      </span>
                    </div>
                  </div>
                </MacWindowCard>
              </div>

              <MacWindowCard title="Loan Details">
                <div className="space-y-2 text-sm text-slate-700">
                  <div className="flex justify-between gap-3">
                    <span className="text-slate-500">Requested Amount</span>
                    <span className="font-medium text-slate-900">{formatInr(application.loan_amount)}</span>
                  </div>
                  <div className="flex justify-between gap-3">
                    <span className="text-slate-500">Approved Amount</span>
                    <span
                      className={`font-semibold ${
                        application.approved_amount ? "text-emerald-700" : "text-rose-700"
                      }`}
                    >
                      {application.approved_amount ? formatInr(application.approved_amount) : "—"}
                    </span>
                  </div>
                  <div className="flex justify-between gap-3">
                    <span className="text-slate-500">Tenure</span>
                    <span className="font-medium text-slate-900">{application.tenure_months} months</span>
                  </div>
                  <div className="flex justify-between gap-3">
                    <span className="text-slate-500">Rate Band</span>
                    <span className="font-medium text-slate-900">{application.rate_percent}% p.a.</span>
                  </div>
                </div>
              </MacWindowCard>
            </div>
          </section>

          <section className="xl:col-span-3 p-4">
            <div className="max-h-[calc(92vh-160px)] space-y-3 overflow-y-auto pr-1">
              <Accordion
                title="01 Decision Explanation"
                badge="Advisory"
                badgeClass="chip border-blue-300 bg-blue-50 text-blue-800"
                open={openSections.decision}
                onToggle={() => toggleSection("decision")}
              >
                <p className="text-sm text-slate-700">{application.reasoning_summary}</p>
              </Accordion>

              <Accordion
                title="02 Risk Summary"
                badge="Advisory"
                badgeClass="chip border-blue-300 bg-blue-50 text-blue-800"
                open={openSections.risk}
                onToggle={() => toggleSection("risk")}
              >
                <p className="text-sm text-slate-700">{riskSummary}</p>
              </Accordion>

              <Accordion
                title="03 HIL Assistant Suggestions"
                badge="CO Action Required"
                badgeClass="chip border-amber-300 bg-amber-50 text-amber-900"
                open={openSections.hil}
                onToggle={() => toggleSection("hil")}
              >
                <ol className="list-decimal space-y-2 pl-4 text-sm text-slate-700">
                  {hilSuggestions.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              </Accordion>

              <MacWindowCard title="CO Decision Required">
                <textarea
                  placeholder="Enter rationale for your decision (mandatory for audit trail)."
                  className="h-28 w-full rounded-lg border border-slate-200 p-3 text-sm outline-none ring-blue-100 transition focus:ring"
                />
              </MacWindowCard>
            </div>
          </section>
        </div>

        <div className="flex flex-wrap items-center justify-end gap-2 border-t border-slate-200 bg-slate-50 px-4 py-3">
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            Cancel
          </button>
          <button className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-amber-600">
            Modify and Approve
          </button>
          <button className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-700">
            Reject
          </button>
          <button className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700">
            Approve
          </button>
        </div>
      </MacWindowCard>
    </div>
  );
}

function Accordion({
  title,
  badge,
  badgeClass,
  open,
  onToggle,
  children,
}: {
  title: string;
  badge: string;
  badgeClass: string;
  open: boolean;
  onToggle: () => void;
  children: ReactNode;
}) {
  return (
    <MacWindowCard title={title} bodyClassName="p-0" headerRight={<span className={badgeClass}>{badge}</span>}>
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-3 border-b border-slate-100 px-4 py-2 text-left text-xs font-semibold text-slate-500 transition hover:bg-slate-50"
      >
        <span>{open ? "Hide" : "Show"}</span>
      </button>
      {open ? <div className="px-4 py-3">{children}</div> : null}
    </MacWindowCard>
  );
}
