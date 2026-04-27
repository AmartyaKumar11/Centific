import { TimelineStep as TimelineStepType } from "@/types/application";
import { TimelineStep } from "./TimelineStep";
import { MacWindowCard } from "@/components/ui/MacWindowCard";

export function Timeline({ steps }: { steps: TimelineStepType[] }) {
  return (
    <MacWindowCard title="Agent Timeline" bodyClassName="p-5">
      <p className="text-sm subtle-text">
        Step-by-step execution trace showing how the decision was produced.
      </p>
      <div className="relative mt-5 space-y-6 before:absolute before:left-[5px] before:top-2 before:h-[calc(100%-16px)] before:w-px before:bg-slate-200">
        {steps.map((step) => (
          <TimelineStep key={`${step.step_name}-${step.tool_name}`} step={step} />
        ))}
      </div>
    </MacWindowCard>
  );
}
