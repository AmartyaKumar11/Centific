"use client";

import { useState } from "react";
import Link from "next/link";
import { ApplicationReviewModal } from "@/components/Application/ApplicationReviewModal";
import { Application } from "@/types/application";

const riskClass: Record<Application["risk"], string> = {
  Low: "bg-emerald-100 text-emerald-700",
  Medium: "bg-amber-100 text-amber-700",
  High: "bg-rose-100 text-rose-700",
  "Very High": "bg-slate-200 text-slate-700",
};

export function ApplicationsTable({ applications }: { applications: Application[] }) {
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);

  return (
    <>
      <section className="card-shell overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3">
          <h3 className="text-sm font-semibold text-slate-800">Application Register</h3>
          <span className="rounded-full bg-slate-200 px-3 py-1 text-xs text-slate-700">
            {applications.length} applications
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-[11px] uppercase tracking-[0.08em] text-slate-500">
              <tr>
                <th className="px-4 py-3">Applicant</th>
                <th className="px-4 py-3">Loan Amount</th>
                <th className="px-4 py-3">Decision</th>
                <th className="px-4 py-3">Risk</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">HIL</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3">Route</th>
              </tr>
            </thead>
            <tbody>
              {applications.map((app) => (
                <tr
                  key={app.id}
                  onClick={() => setSelectedApplication(app)}
                  className="cursor-pointer border-t border-slate-100 transition hover:bg-slate-50"
                >
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-900">{app.applicant_name}</p>
                    <p className="text-xs text-slate-500">{app.id}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    INR {app.loan_amount.toLocaleString("en-IN")}
                  </td>
                  <td className="px-4 py-3 text-slate-700">{app.decision}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-1 text-xs ${riskClass[app.risk]}`}>
                      {app.risk}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{app.confidence_score}%</td>
                  <td className="px-4 py-3 text-slate-700">
                    {app.hil_required_flag ? "Required" : "Not required"}
                  </td>
                  <td className="px-4 py-3 text-slate-500">
                    {new Date(app.created_at).toLocaleString("en-IN")}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/applications/${app.id}`}
                      onClick={(event) => event.stopPropagation()}
                      className="rounded-md border border-slate-200 px-2 py-1 text-xs text-slate-700 hover:bg-slate-100"
                    >
                      Open page
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <ApplicationReviewModal
        application={selectedApplication}
        onClose={() => setSelectedApplication(null)}
      />
    </>
  );
}
