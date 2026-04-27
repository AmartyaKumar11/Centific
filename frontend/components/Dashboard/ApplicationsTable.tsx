"use client";

import { useState } from "react";
import { Link } from "react-router-dom";
import { ApplicationReviewModal } from "@/components/Application/ApplicationReviewModal";
import { Application } from "@/types/application";
import { MacWindowCard } from "@/components/ui/MacWindowCard";

const riskClass: Record<Application["risk"], string> = {
  Low: "chip chip-risk-low",
  Medium: "chip chip-risk-medium",
  High: "chip chip-risk-high",
  "Very High": "chip chip-risk-vhigh",
};

const decisionClass: Record<Application["decision"], string> = {
  "STP Approved": "chip border-emerald-300 bg-emerald-100 text-emerald-800",
  "Conditional Approval": "chip border-amber-300 bg-amber-100 text-amber-800",
  "HIL Pending": "chip border-blue-300 bg-blue-100 text-blue-800",
  Rejected: "chip border-rose-300 bg-rose-100 text-rose-800",
};

export function ApplicationsTable({ applications }: { applications: Application[] }) {
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);

  return (
    <>
      <MacWindowCard
        title="Application Register"
        bodyClassName="p-0"
        headerRight={
          <span className="rounded-full bg-slate-200 px-3 py-1 text-xs text-slate-700">
            {applications.length} applications
          </span>
        }
      >
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
                  className="cursor-pointer border-t border-slate-100 transition hover:bg-blue-50/40"
                >
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-900">{app.applicant_name}</p>
                    <p className="text-xs text-slate-500">{app.id}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    INR {app.loan_amount.toLocaleString("en-IN")}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    <span className={decisionClass[app.decision]}>{app.decision}</span>
                  </td>
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
                      to={`/applications/${app.id}`}
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
      </MacWindowCard>

      <ApplicationReviewModal
        application={selectedApplication}
        onClose={() => setSelectedApplication(null)}
      />
    </>
  );
}
