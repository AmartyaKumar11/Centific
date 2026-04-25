"use client";

import { useEffect, useMemo, useState } from "react";
import { Application } from "@/types/application";
import { BorrowerProfile } from "@/components/Application/BorrowerProfile";
import { EventTimeline, TimelineEventItem } from "@/components/Application/EventTimeline";

type ApplicationDetailModalProps = {
  application: Application | null;
  onClose: () => void;
};

function toEventStatus(
  status?: Application["timeline"][number]["status"]
): TimelineEventItem["status"] {
  if (status === "success") return "success";
  if (status === "fail") return "failure";
  return "pending";
}

export function ApplicationDetailModal({ application, onClose }: ApplicationDetailModalProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!application) return;
    const t = setTimeout(() => setVisible(true), 16);
    return () => clearTimeout(t);
  }, [application]);

  const closeWithAnimation = () => {
    setVisible(false);
    setTimeout(onClose, 170);
  };

  const events = useMemo(() => {
    if (!application) return [];
    return application.audit_trail.map((audit, index) => {
      const timeline = application.timeline[index];
      return {
        id: `${audit.event_code}-${index}`,
        code: audit.event_code,
        timestamp: audit.event_time,
        name: audit.title,
        description: audit.details,
        output: timeline?.output_data ?? "output_data=not_available",
        status: toEventStatus(timeline?.status),
      } satisfies TimelineEventItem;
    });
  }, [application]);

  if (!application) return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-slate-900/45 p-3 transition-opacity duration-150 ${
        visible ? "opacity-100" : "opacity-0"
      }`}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) closeWithAnimation();
      }}
    >
      <div
        className={`w-full max-w-[1200px] rounded-xl border border-slate-200 bg-white shadow-2xl transition-all duration-150 ${
          visible ? "translate-y-0 scale-100" : "translate-y-2 scale-[0.985]"
        }`}
      >
        <header className="flex items-center justify-between border-b border-slate-200 px-4 py-2.5">
          <div>
            <p className="text-sm font-semibold text-slate-900">Application Review & Status</p>
            <p className="text-xs text-slate-500">{application.id}</p>
          </div>
          <button
            type="button"
            onClick={closeWithAnimation}
            className="rounded-md border border-slate-200 px-2.5 py-1 text-xs text-slate-600 hover:bg-slate-50"
          >
            Close
          </button>
        </header>

        <div className="grid max-h-[74vh] grid-cols-1 md:grid-cols-5">
          <div className="border-b border-slate-200 p-3 md:col-span-2 md:max-h-[74vh] md:border-b-0 md:border-r">
            <EventTimeline events={events} />
          </div>
          <div className="p-3 md:col-span-3 md:max-h-[74vh]">
            <BorrowerProfile application={application} />
          </div>
        </div>

        <footer className="flex flex-wrap items-center justify-end gap-2 border-t border-slate-200 bg-slate-50 px-4 py-2.5">
          <button
            type="button"
            onClick={closeWithAnimation}
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
          >
            Cancel
          </button>
          <button
            type="button"
            className="rounded-md bg-amber-500 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-600"
          >
            [~] Modify & Approve
          </button>
          <button
            type="button"
            className="rounded-md bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-rose-700"
          >
            [x] Reject
          </button>
          <button
            type="button"
            className="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700"
          >
            [+] Approve
          </button>
        </footer>
      </div>
    </div>
  );
}
