"use client";

import { useState } from "react";
import { ApplicationDetailModal } from "@/components/Application/ApplicationDetailModal";
import { Application } from "@/types/application";
import { applications } from "@/lib/mockData";
import { MacWindowCard } from "@/components/ui/MacWindowCard";

const laneStyles = {
  awaiting: "border-amber-300 bg-gradient-to-b from-amber-100/80 to-amber-50/50",
  review: "border-blue-300 bg-gradient-to-b from-blue-100/80 to-blue-50/50",
  approved: "border-emerald-300 bg-gradient-to-b from-emerald-100/80 to-emerald-50/50",
  rejected: "border-rose-300 bg-gradient-to-b from-rose-100/80 to-rose-50/50",
};

function scoreBand(score: number) {
  if (score >= 75) return "Low Risk";
  if (score >= 50) return "Medium Risk";
  if (score >= 30) return "High Risk";
  return "Very High Risk";
}

export function HilReviewClient() {
  const [queueApplications, setQueueApplications] = useState<Application[]>(applications);
  const [selectedApplicationId, setSelectedApplicationId] = useState<string | null>(null);

  const selectedApplication =
    queueApplications.find((application) => application.id === selectedApplicationId) ?? null;

  const awaiting = queueApplications.filter((a) => a.hil_required_flag && a.decision === "HIL Pending");
  const review = queueApplications.filter(
    (a) => a.hil_required_flag && a.decision === "Conditional Approval"
  );
  const approved = queueApplications.filter((a) => a.decision === "STP Approved");
  const rejected = queueApplications.filter((a) => a.decision === "Rejected");

  const openApplicationModal = (application: Application) => {
    setSelectedApplicationId(application.id);
  };

  const handleModalAction = (
    action: "approve" | "reject" | "modify_approve",
    application: Application
  ) => {
    setQueueApplications((prev) =>
      prev.map((item) => {
        if (item.id !== application.id) return item;

        if (action === "approve") {
          return {
            ...item,
            decision: "STP Approved",
            hil_required_flag: false,
            approved_amount: item.approved_amount ?? item.loan_amount,
          };
        }

        if (action === "modify_approve") {
          const adjustedAmount = Math.round(item.loan_amount * 0.85);
          return {
            ...item,
            decision: "Conditional Approval",
            hil_required_flag: true,
            approved_amount: item.approved_amount ?? adjustedAmount,
          };
        }

        return {
          ...item,
          decision: "Rejected",
          hil_required_flag: true,
          approved_amount: null,
        };
      })
    );
    setSelectedApplicationId(null);
  };

  const lanes = [
    { key: "awaiting", title: "Awaiting Review", items: awaiting },
    { key: "review", title: "Under Review", items: review },
    { key: "approved", title: "CO Approved", items: approved },
    { key: "rejected", title: "CO Rejected", items: rejected },
  ] as const;

  return (
    <main className="mx-auto flex w-full max-w-[1500px] flex-col gap-4 px-4 py-4 pb-24">
      <MacWindowCard title="HIL Review - Credit Officer Gate" bodyClassName="p-4">
        <p className="text-sm subtle-text">Mandatory non-bypassable review queue for flagged applications</p>

        <div className="mt-4 grid gap-3 lg:grid-cols-4">
          {lanes.map((lane) => (
            <MacWindowCard
              key={lane.title}
              title={lane.title}
              className={`min-h-[460px] ${laneStyles[lane.key]}`}
              bodyClassName="p-3"
              headerRight={
                <span className="rounded-full bg-white px-2 py-0.5 text-xs text-slate-600">{lane.items.length}</span>
              }
            >
              <div className="space-y-2">
                {lane.items.map((app) => (
                  <div
                    key={app.id}
                    role="button"
                    tabIndex={0}
                    onClick={() => openApplicationModal(app)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        openApplicationModal(app);
                      }
                    }}
                    className="cursor-pointer rounded-lg border border-white bg-white p-3 shadow-md transition hover:-translate-y-0.5 hover:shadow-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-400"
                  >
                    <p className="text-[11px] uppercase tracking-[0.08em] text-slate-500">{app.id}</p>
                    <p className="text-sm font-semibold text-slate-900">{app.applicant_name}</p>
                    <p className="text-xs text-slate-500">
                      INR {app.loan_amount.toLocaleString("en-IN")} - {app.tenure_months}m
                    </p>
                    <p className="mt-2">
                      <span
                        className={
                          app.risk === "Low"
                            ? "chip chip-risk-low"
                            : app.risk === "Medium"
                            ? "chip chip-risk-medium"
                            : app.risk === "High"
                            ? "chip chip-risk-high"
                            : "chip chip-risk-vhigh"
                        }
                      >
                        {scoreBand(app.risk_score)}
                      </span>
                    </p>
                    <div className="mt-2 h-1.5 w-full rounded-full bg-slate-100">
                      <div
                        className={
                          app.risk === "Low"
                            ? "h-1.5 rounded-full bg-emerald-600"
                            : app.risk === "Medium"
                            ? "h-1.5 rounded-full bg-amber-500"
                            : "h-1.5 rounded-full bg-rose-600"
                        }
                        style={{ width: `${app.risk_score}%` }}
                      />
                    </div>
                    <p className="mt-1 text-right text-xs text-slate-500">Score: {app.risk_score}</p>
                  </div>
                ))}
              </div>
            </MacWindowCard>
          ))}
        </div>
      </MacWindowCard>

      <ApplicationDetailModal
        application={selectedApplication}
        onClose={() => setSelectedApplicationId(null)}
        onAction={handleModalAction}
      />
    </main>
  );
}
