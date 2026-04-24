import { AppTopBar } from "@/components/Layout/AppTopBar";
import { BottomDock } from "@/components/Layout/BottomDock";
import { applications } from "@/lib/mockData";

const laneStyles = {
  awaiting: "border-amber-200 bg-amber-50/40",
  review: "border-blue-200 bg-blue-50/40",
  approved: "border-emerald-200 bg-emerald-50/40",
  rejected: "border-rose-200 bg-rose-50/40",
};

function scoreBand(score: number) {
  if (score >= 75) return "Low Risk";
  if (score >= 50) return "Medium Risk";
  if (score >= 30) return "High Risk";
  return "Very High Risk";
}

export default function HilReviewPage() {
  const awaiting = applications.filter((a) => a.hil_required_flag && a.decision === "HIL Pending");
  const review = applications.filter(
    (a) => a.hil_required_flag && a.decision === "Conditional Approval"
  );
  const approved = applications.filter((a) => a.decision === "STP Approved");
  const rejected = applications.filter((a) => a.decision === "Rejected");

  const lanes = [
    { key: "awaiting", title: "Awaiting Review", items: awaiting },
    { key: "review", title: "Under Review", items: review },
    { key: "approved", title: "CO Approved", items: approved },
    { key: "rejected", title: "CO Rejected", items: rejected },
  ] as const;

  return (
    <main className="mx-auto flex w-full max-w-[1500px] flex-col gap-4 px-4 py-4">
      <AppTopBar />

      <section className="card-shell p-4">
        <h1 className="text-2xl font-semibold text-slate-900">HIL Review - Credit Officer Gate</h1>
        <p className="text-sm subtle-text">
          Mandatory non-bypassable review queue for flagged applications
        </p>

        <div className="mt-4 grid gap-3 lg:grid-cols-4">
          {lanes.map((lane) => (
            <article
              key={lane.title}
              className={`rounded-xl border p-3 ${laneStyles[lane.key]} min-h-[460px]`}
            >
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-slate-800">{lane.title}</h2>
                <span className="rounded-full bg-white px-2 py-0.5 text-xs text-slate-600">
                  {lane.items.length}
                </span>
              </div>

              <div className="space-y-2">
                {lane.items.map((app) => (
                  <div key={app.id} className="rounded-lg border border-white bg-white p-3 shadow-sm">
                    <p className="text-[11px] uppercase tracking-[0.08em] text-slate-500">{app.id}</p>
                    <p className="text-sm font-semibold text-slate-900">{app.applicant_name}</p>
                    <p className="text-xs text-slate-500">
                      INR {app.loan_amount.toLocaleString("en-IN")} - {app.tenure_months}m
                    </p>
                    <p className="mt-2 text-xs font-medium text-slate-700">{scoreBand(app.risk_score)}</p>
                    <div className="mt-2 h-1.5 w-full rounded-full bg-slate-100">
                      <div className="h-1.5 rounded-full bg-slate-700" style={{ width: `${app.risk_score}%` }} />
                    </div>
                    <p className="mt-1 text-right text-xs text-slate-500">Score: {app.risk_score}</p>
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <BottomDock />
    </main>
  );
}
