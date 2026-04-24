import { Application } from "@/types/application";

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 py-2 last:border-none">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-medium text-slate-800">{value}</span>
    </div>
  );
}

export function ApplicationSummary({ application }: { application: Application }) {
  return (
    <section className="card-shell p-5">
      <h2 className="text-lg font-semibold text-slate-900">Application Summary</h2>
      <div className="mt-4 grid gap-5 md:grid-cols-2">
        <div>
          <SummaryRow label="Employer" value={application.employer} />
          <SummaryRow
            label="Income (Declared vs Verified)"
            value={`INR ${application.income_declared.toLocaleString(
              "en-IN"
            )} vs INR ${application.income_verified.toLocaleString("en-IN")}`}
          />
          <SummaryRow label="CIBIL Score" value={application.cibil_score} />
          <SummaryRow label="DTI" value={`${application.dti_percent}%`} />
        </div>
        <div>
          <SummaryRow label="Risk Category" value={application.risk} />
          <SummaryRow label="Decision" value={application.decision} />
          <SummaryRow
            label="Approved Amount"
            value={
              application.approved_amount
                ? `INR ${application.approved_amount.toLocaleString("en-IN")}`
                : "Not approved"
            }
          />
          <SummaryRow label="Confidence Score" value={`${application.confidence_score}%`} />
        </div>
      </div>
    </section>
  );
}
