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

const statusDotClass: Record<TimelineEventItem["status"], string> = {
  success: "bg-emerald-500",
  failure: "bg-rose-600",
  pending: "bg-amber-500",
};

export function EventTimeline({ events }: { events: TimelineEventItem[] }) {
  return (
    <section className="h-full overflow-y-auto pr-2">
      <div className="relative space-y-3 pl-5 before:absolute before:left-[7px] before:top-1 before:h-[calc(100%-8px)] before:w-px before:bg-slate-200">
        {events.map((event) => (
          <article key={event.id} className="relative rounded-md border border-slate-200 bg-white p-3 shadow-sm">
            <span
              className={`absolute -left-[19px] top-4 h-3 w-3 rounded-full ring-2 ring-white ${statusDotClass[event.status]}`}
            />
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-slate-500">{event.timestamp}</p>
            <p className="mt-1 text-[11px] font-semibold text-slate-800">{event.code}</p>
            <p className="text-xs font-semibold text-slate-900">{event.name}</p>
            <p className="mt-1 text-xs text-slate-600">{event.description}</p>
            <pre className="mt-2 overflow-x-auto rounded bg-slate-100 p-2 text-[10px] text-slate-700">
              <code>{event.output}</code>
            </pre>
          </article>
        ))}
      </div>
    </section>
  );
}
