import { TimelineStep as TimelineStepType } from "@/types/application";

const statusStyle: Record<TimelineStepType["status"], string> = {
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  fail: "bg-rose-500",
};

export function TimelineStep({ step }: { step: TimelineStepType }) {
  return (
    <article className="relative pl-8">
      <span
        className={`absolute left-0 top-1.5 h-3 w-3 rounded-full ring-4 ring-white ${statusStyle[step.status]}`}
      />
      <p className="text-xs uppercase tracking-[0.08em] text-slate-500">{step.tool_name}</p>
      <h3 className="text-base font-semibold text-slate-900">{step.step_name}</h3>
      {step.trigger_reason ? (
        <p className="mt-1 rounded-md bg-amber-50 px-2 py-1 text-xs text-amber-800">
          Trigger: {step.trigger_reason}
        </p>
      ) : null}
      <p className="mt-2 text-sm text-slate-700">{step.reasoning}</p>
      <p className="mt-2 rounded-md bg-slate-50 px-3 py-2 text-xs text-slate-600">
        Output: {step.output_data}
      </p>
    </article>
  );
}
