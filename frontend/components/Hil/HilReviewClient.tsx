"use client";

import { useEffect, useMemo, useState } from "react";
import { ApplicationDetailModal } from "@/components/Application/ApplicationDetailModal";
import { Application } from "@/types/application";
import { api, HilQueue } from "@/lib/api";
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
  const [queueData, setQueueData] = useState<HilQueue>({
    awaiting: [],
    review: [],
    approved: [],
    rejected: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isActing, setIsActing] = useState(false);
  const [selectedApplicationId, setSelectedApplicationId] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    api
      .getHilQueue()
      .then((data) => {
        if (!isMounted) return;
        setQueueData(data);
        setError(null);
      })
      .catch((err: unknown) => {
        if (!isMounted) return;
        setError(err instanceof Error ? err.message : "Failed to load HIL queue");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const queueApplications = useMemo(
    () => [...queueData.awaiting, ...queueData.review, ...queueData.approved, ...queueData.rejected],
    [queueData]
  );
  const selectedApplication =
    queueApplications.find((application) => application.id === selectedApplicationId) ?? null;

  const awaiting = queueData.awaiting;
  const review = queueData.review;
  const approved = queueData.approved;
  const rejected = queueData.rejected;

  const openApplicationModal = (application: Application) => {
    setSelectedApplicationId(application.id);
  };

  const handleModalAction = async (
    action: "approve" | "reject" | "modify_approve",
    application: Application
  ) => {
    if (isActing) return;
    setIsActing(true);
    setError(null);

    const optimistic = { ...queueData };
    const removeFromAll = (id: string) => {
      optimistic.awaiting = optimistic.awaiting.filter((item) => item.id !== id);
      optimistic.review = optimistic.review.filter((item) => item.id !== id);
      optimistic.approved = optimistic.approved.filter((item) => item.id !== id);
      optimistic.rejected = optimistic.rejected.filter((item) => item.id !== id);
    };

    removeFromAll(application.id);
    if (action === "approve") {
      optimistic.approved = [
        {
          ...application,
          decision: "STP Approved",
          hil_required_flag: false,
          approved_amount: application.approved_amount ?? application.loan_amount,
        },
        ...optimistic.approved,
      ];
    } else if (action === "modify_approve") {
      optimistic.review = [
        {
          ...application,
          decision: "Conditional Approval",
          hil_required_flag: true,
          approved_amount: application.approved_amount ?? Math.round(application.loan_amount * 0.85),
        },
        ...optimistic.review,
      ];
    } else {
      optimistic.rejected = [
        { ...application, decision: "Rejected", hil_required_flag: true, approved_amount: null },
        ...optimistic.rejected,
      ];
    }
    setQueueData(optimistic);

    try {
      await api.hilAction(application.id, action);
      const updated = await api.getHilQueue();
      setQueueData(updated);
      setSelectedApplicationId(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to submit HIL action");
      const refreshed = await api.getHilQueue();
      setQueueData(refreshed);
    } finally {
      setIsActing(false);
    }
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
        {loading ? <p className="mt-3 text-sm text-slate-500">Loading queue...</p> : null}
        {error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}

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
