"use client";

import { Application } from "@/types/application";

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

export function ApplicationReviewModal({
  application,
  onClose,
}: ApplicationReviewModalProps) {
  if (!application) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm">
      <div className="max-h-[90vh] w-full max-w-6xl overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3">
          <h2 className="text-lg font-semibold text-slate-900">
            Application Review and Status - {application.id}
          </h2>
          <button
            onClick={onClose}
            className="rounded-full border border-slate-200 px-3 py-1 text-sm text-slate-600 hover:bg-slate-50"
          >
            Close
          </button>
        </div>

        <div className="grid max-h-[calc(90vh-64px)] gap-0 overflow-hidden lg:grid-cols-2">
          <section className="overflow-y-auto border-r border-slate-200 p-5">
            <h3 className="text-xl font-semibold text-slate-900">Application Event Log</h3>
            <div className="relative mt-5 space-y-5 pl-6 before:absolute before:left-[8px] before:top-1 before:h-[calc(100%-8px)] before:w-px before:bg-slate-200">
              {application.audit_trail.map((event) => (
                <article key={`${event.event_time}-${event.event_code}`} className="relative">
                  <span
                    className={`absolute -left-6 top-1.5 h-3 w-3 rounded-full ring-4 ring-white ${toneDotClass[event.tone]}`}
                  />
                  <p className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
                    {event.event_time} - {event.event_code}
                  </p>
                  <h4 className="text-base font-semibold text-slate-900">{event.title}</h4>
                  <p className="text-sm text-slate-600">{event.details}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="overflow-y-auto p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.08em] text-slate-500">{application.id}</p>
                <h3 className="text-2xl font-semibold text-slate-900">{application.applicant_name}</h3>
              </div>
              <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                Live
              </span>
            </div>

            <div className="mt-4 grid gap-4 rounded-2xl border border-slate-200 p-4 md:grid-cols-2">
              <div className="space-y-2">
                <p className="text-sm font-semibold text-slate-900">Borrower Profile</p>
                <p className="text-sm text-slate-600">Employer: {application.employer}</p>
                <p className="text-sm text-slate-600">Employment Type: {application.employer_type}</p>
                <p className="text-sm text-slate-600">
                  Gross Monthly Salary: INR {application.income_declared.toLocaleString("en-IN")}
                </p>
                <p className="text-sm text-slate-600">
                  Net Salary: INR {application.income_verified.toLocaleString("en-IN")}
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-semibold text-slate-900">Risk Assessment</p>
                <p className="text-5xl font-bold text-rose-700">{application.risk_score}</p>
                <p className="text-sm text-slate-600">
                  {application.risk} risk / 100
                </p>
                <div className="h-2 w-full rounded-full bg-slate-100">
                  <div
                    className="h-2 rounded-full bg-rose-600"
                    style={{ width: `${application.risk_score}%` }}
                  />
                </div>
                <p className="text-sm text-slate-600">CIBIL: {application.cibil_score}</p>
                <p className="text-sm text-slate-600">DTI Ratio: {application.dti_percent}%</p>
              </div>
            </div>

            <div className="mt-4 rounded-2xl border border-slate-200 p-4">
              <p className="text-sm font-semibold text-slate-900">Decision Explanation</p>
              <p className="mt-2 text-sm text-slate-600">{application.reasoning_summary}</p>
            </div>

            <div className="mt-4 rounded-2xl border border-slate-200 p-4">
              <p className="text-sm font-semibold text-slate-900">Credit Officer Rationale</p>
              <textarea
                placeholder="Enter rationale for your decision."
                className="mt-2 h-24 w-full rounded-lg border border-slate-200 p-3 text-sm outline-none ring-blue-100 transition focus:ring"
              />
            </div>

            <div className="mt-5 flex flex-wrap justify-end gap-2">
              <button
                onClick={onClose}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600">
                Modify and Approve
              </button>
              <button className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium text-white hover:bg-rose-700">
                Reject
              </button>
              <button className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700">
                Approve
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
