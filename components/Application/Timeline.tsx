import { TimelineStep as TimelineStepType } from "@/types/application";
import { TimelineStep } from "./TimelineStep";

export function Timeline({ steps }: { steps: TimelineStepType[] }) {
  return (
    <section className="card-shell p-5">
      <h2 className="text-lg font-semibold text-slate-900">Agent Timeline</h2>
      <p className="mt-1 text-sm subtle-text">
        Step-by-step execution trace showing how the decision was produced.
      </p>
      <div className="relative mt-5 space-y-6 before:absolute before:left-[5px] before:top-2 before:h-[calc(100%-16px)] before:w-px before:bg-slate-200">
        {steps.map((step) => (
          <TimelineStep key={`${step.step_name}-${step.tool_name}`} step={step} />
        ))}
      </div>
    </section>
  );
}
