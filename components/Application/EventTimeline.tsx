"use client";

export type TimelineEventItem = {
  id: string;
  code: string;
  timestamp: string;
  name: string;
  description: string;
  output: string;
  status: "success" | "failure" | "pending";
};

type EventVisual = {
  dotClass: string;
  badgeClass: string;
  icon: string;
};

const eventVisuals: Record<string, EventVisual> = {
  EVT_DEDUP: {
    dotClass: "bg-blue-500",
    badgeClass: "border-blue-200 bg-blue-50 text-blue-700",
    icon: "\u2713",
  },
  EVT_INTAKE: {
    dotClass: "bg-emerald-500",
    badgeClass: "border-emerald-200 bg-emerald-50 text-emerald-700",
    icon: "\u2713",
  },
  EVT_FEATURES: {
    dotClass: "bg-emerald-500",
    badgeClass: "border-emerald-200 bg-emerald-50 text-emerald-700",
    icon: "\u2713",
  },
  EVT_SCORE: {
    dotClass: "bg-blue-500",
    badgeClass: "border-blue-200 bg-blue-50 text-blue-700",
    icon: "\u2713",
  },
  EVT_FLAGS: {
    dotClass: "bg-amber-500",
    badgeClass: "border-amber-200 bg-amber-50 text-amber-700",
    icon: "!",
  },
  EVT_DECISION: {
    dotClass: "bg-rose-600",
    badgeClass: "border-rose-200 bg-rose-50 text-rose-700",
    icon: "\u2717",
  },
  EVT_HIL: {
    dotClass: "bg-amber-500",
    badgeClass: "border-amber-200 bg-amber-50 text-amber-700",
    icon: "\u26A0",
  },
};

const defaultVisual: EventVisual = {
  dotClass: "bg-slate-400",
  badgeClass: "border-slate-200 bg-slate-50 text-slate-700",
  icon: "\u2022",
};

function EventTimelineItem({ event, isLast }: { event: TimelineEventItem; isLast: boolean }) {
  const visual = eventVisuals[event.code] ?? defaultVisual;
  return (
    <article className="relative pl-6">
      {!isLast ? <span className="absolute left-[9px] top-6 h-[calc(100%+16px)] w-px bg-slate-200" /> : null}
      <span className={`absolute left-0 top-1.5 h-[10px] w-[10px] rounded-full ring-2 ring-white ${visual.dotClass}`} />

      <div className="rounded-md border border-slate-200 bg-white p-3 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-[13px] font-semibold leading-tight text-slate-700">{event.timestamp}</p>
          <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-[11px] font-semibold ${visual.badgeClass}`}>
            {visual.icon} {event.code}
          </span>
        </div>
        <p className="mt-1 text-[13px] font-semibold leading-tight text-slate-900">{event.name}</p>
        <p className="mt-1 text-[11px] leading-relaxed text-slate-600">{event.description}</p>
        <pre className="mt-2 overflow-x-auto rounded bg-slate-100 px-2 py-1.5 text-[11px] text-slate-700">
          <code>{event.output}</code>
        </pre>
      </div>
    </article>
  );
}

export function EventTimeline({ events }: { events: TimelineEventItem[] }) {
  return (
    <section className="max-h-[400px] overflow-y-auto pr-2">
      <div className="space-y-4">
        {events.map((event, index) => (
          <EventTimelineItem key={event.id} event={event} isLast={index === events.length - 1} />
        ))}
      </div>
    </section>
  );
}
