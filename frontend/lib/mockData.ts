import { Application } from "@/types/application";

const baseTimeline = (
  incomeMismatch: boolean,
  needsHil: boolean,
  rejected: boolean
) => [
  {
    step_name: "KYC Validation",
    tool_name: "KYC Service",
    status: "success" as const,
    reasoning: "PAN, Aadhaar and DOB matched with onboarding payload.",
    output_data: "identity_match=true, dedupe_window_30d=pass",
  },
  {
    step_name: "CIBIL Fetch",
    tool_name: "CIBIL API",
    status: rejected ? ("fail" as const) : ("success" as const),
    reasoning: rejected
      ? "Score is below policy threshold for automated approval."
      : "Credit profile available and consumable for risk model.",
    output_data: rejected ? "cibil_check=below_threshold" : "cibil_check=pass",
  },
  {
    step_name: "Income Validation",
    tool_name: "Income Verification Tool",
    status: incomeMismatch ? ("warning" as const) : ("success" as const),
    reasoning: incomeMismatch
      ? "Declared income differs from verified salary credits."
      : "Declared income aligns with verified salary pattern.",
    output_data: incomeMismatch
      ? "income_delta_detected=true"
      : "income_delta_detected=false",
  },
  {
    step_name: "Bank Statement Analysis",
    tool_name: "Bank Analyzer",
    status: incomeMismatch ? ("warning" as const) : ("success" as const),
    trigger_reason: incomeMismatch
      ? "Triggered due to income mismatch in prior step."
      : undefined,
    reasoning: incomeMismatch
      ? "Monthly obligations increased effective DTI beyond target band."
      : "Spending stability and repayment behavior are acceptable.",
    output_data: incomeMismatch
      ? "effective_dti_adjustment=+4.2"
      : "bounce_frequency=low",
  },
  {
    step_name: "Decision Engine",
    tool_name: "Policy Rules Engine",
    status: rejected ? ("fail" as const) : ("warning" as const),
    reasoning: rejected
      ? "Hard policy breach identified; case not eligible for STP."
      : "Case eligible with either STP or conditional recommendation.",
    output_data: rejected ? "recommendation=reject" : "recommendation=approve_or_hil",
  },
  {
    step_name: "HIL Escalation",
    tool_name: "HIL Orchestrator",
    status: needsHil ? ("warning" as const) : ("success" as const),
    reasoning: needsHil
      ? "Case routed to Credit Manager due to policy flags."
      : "No mandatory manual review criteria met.",
    output_data: needsHil ? "hil_required=true" : "hil_required=false",
  },
];

const baseAuditTrail = (
  applicationId: string,
  applicantName: string,
  hilRequired: boolean
) => [
  {
    event_time: "09:16:55",
    event_code: "EVT_DEDUP",
    title: `PAN deduplication pass - ${applicationId}`,
    details: `No prior duplicate application found for ${applicantName} in 30-day window.`,
    tone: "info" as const,
  },
  {
    event_time: "09:17:02",
    event_code: "EVT_FEATURES",
    title: `Feature engineering complete - ${applicationId}`,
    details: "Affordability, utilization and stability factors were computed.",
    tone: "success" as const,
  },
  {
    event_time: "09:17:18",
    event_code: "EVT_SCORE",
    title: `Risk score computed - ${applicationId}`,
    details: "Score generated from credit, income, and banking components.",
    tone: "info" as const,
  },
  {
    event_time: "09:17:31",
    event_code: "EVT_FLAGS",
    title: `Policy flags evaluated - ${applicationId}`,
    details: hilRequired
      ? "One or more review conditions matched and HIL routing was enabled."
      : "No critical policy flags found for manual intervention.",
    tone: hilRequired ? ("warning" as const) : ("success" as const),
  },
  {
    event_time: "09:18:07",
    event_code: hilRequired ? "EVT_HIL_QUEUE" : "EVT_STP",
    title: hilRequired
      ? `Queued for HIL review - ${applicationId}`
      : `Straight-through processing complete - ${applicationId}`,
    details: hilRequired
      ? "Case assigned to Credit Officer queue for final decision."
      : "Decision completed without manual review requirement.",
    tone: hilRequired ? ("warning" as const) : ("success" as const),
  },
];

export const applications: Application[] = [
  {
    id: "APP-2026-00412",
    applicant_name: "Priya Sharma",
    employer: "TCS Ltd",
    employer_type: "PRIVATE",
    loan_amount: 800000,
    approved_amount: null,
    tenure_months: 48,
    cibil_score: "598",
    dti_percent: 52.4,
    risk_score: 38,
    risk: "High",
    confidence_score: 93,
    decision: "Rejected",
    hil_required_flag: true,
    created_at: "2026-04-25T09:16:55+05:30",
    reasoning_summary:
      "Application rejected due to two critical policy breaches: DTI of 52.4% exceeds the 40% threshold (HIGH_DTI), and CIBIL score of 598 falls below the minimum requirement of 620 (LOW_CREDIT_SCORE). Post-EMI surplus of INR 9,200 is insufficient to support the requested EMI obligation.",
    income_declared: 72000,
    income_verified: 61200,
    income_average: 60400,
    employment_tenure_years: 2.5,
    bounce_frequency_per_month: 0.8,
    spending_ratio: 0.78,
    post_emi_surplus: 9200,
    rate_percent: 15.5,
    risk_summary:
      "Borrower presents elevated risk across credit history (CIBIL 598) and affordability (DTI 52.4%). Income stability is acceptable, but it does not offset the policy breaches.",
    hil_suggestions: [
      "Verify if applicant has any undeclared income that could lower effective DTI.",
      "Request updated CIBIL report in case the score has improved since last pull.",
      "Assess if a reduced loan amount could satisfy DTI constraints.",
      "Consider requesting a co-applicant or guarantor if policy allows.",
      "If rejecting, confirm rationale is documented for audit compliance.",
    ],
    timeline: baseTimeline(true, true, true),
    audit_trail: baseAuditTrail("APP-2026-00412", "Priya Sharma", true),
  },
  {
    id: "APP-2026-00411",
    applicant_name: "Kavitha Naidu",
    employer: "BSNL",
    employer_type: "GOVT",
    loan_amount: 500000,
    approved_amount: 480000,
    tenure_months: 36,
    cibil_score: "728",
    dti_percent: 34.1,
    risk_score: 76,
    risk: "Low",
    confidence_score: 96,
    decision: "STP Approved",
    hil_required_flag: false,
    created_at: "2026-04-25T09:12:44+05:30",
    reasoning_summary:
      "Strong credit profile and affordability made this application STP eligible.",
    income_declared: 75000,
    income_verified: 72500,
    rate_percent: 10.5,
    timeline: baseTimeline(false, false, false),
    audit_trail: baseAuditTrail("APP-2026-00411", "Kavitha Naidu", false),
  },
  {
    id: "APP-2026-00410",
    applicant_name: "Deepa Menon",
    employer: "Kerala Govt",
    employer_type: "GOVT",
    loan_amount: 400000,
    approved_amount: 350000,
    tenure_months: 36,
    cibil_score: "Proxy: 618",
    dti_percent: 38,
    risk_score: 58,
    risk: "Medium",
    confidence_score: 82,
    decision: "HIL Pending",
    hil_required_flag: true,
    created_at: "2026-04-25T09:10:12+05:30",
    reasoning_summary:
      "Proxy score applied; routed for mandatory manual review despite acceptable DTI.",
    income_declared: 58000,
    income_verified: 55200,
    rate_percent: 12.5,
    timeline: baseTimeline(false, true, false),
    audit_trail: baseAuditTrail("APP-2026-00410", "Deepa Menon", true),
  },
  {
    id: "APP-2026-00409",
    applicant_name: "Suresh Kumar",
    employer: "Infosys",
    employer_type: "PRIVATE",
    loan_amount: 250000,
    approved_amount: 250000,
    tenure_months: 24,
    cibil_score: "782",
    dti_percent: 27.2,
    risk_score: 83,
    risk: "Low",
    confidence_score: 97,
    decision: "STP Approved",
    hil_required_flag: false,
    created_at: "2026-04-25T09:08:36+05:30",
    reasoning_summary:
      "Excellent CIBIL and low DTI led to instant straight-through approval.",
    income_declared: 55000,
    income_verified: 53100,
    rate_percent: 10.5,
    timeline: baseTimeline(false, false, false),
    audit_trail: baseAuditTrail("APP-2026-00409", "Suresh Kumar", false),
  },
  {
    id: "APP-2026-00408",
    applicant_name: "Vikram Nair",
    employer: "Reliance Industries",
    employer_type: "PRIVATE",
    loan_amount: 1500000,
    approved_amount: null,
    tenure_months: 60,
    cibil_score: "541",
    dti_percent: 68,
    risk_score: 22,
    risk: "Very High",
    confidence_score: 91,
    decision: "Rejected",
    hil_required_flag: true,
    created_at: "2026-04-25T09:05:18+05:30",
    reasoning_summary:
      "Multiple hard-policy breaches including high DTI and weak credit profile.",
    income_declared: 120000,
    income_verified: 94000,
    rate_percent: 18.5,
    timeline: baseTimeline(true, true, true),
    audit_trail: baseAuditTrail("APP-2026-00408", "Vikram Nair", true),
  },
  {
    id: "APP-2026-00418",
    applicant_name: "Meena Krishnan",
    employer: "Wipro Ltd",
    employer_type: "PRIVATE",
    loan_amount: 1200000,
    approved_amount: 840000,
    tenure_months: 60,
    cibil_score: "671",
    dti_percent: 44.8,
    risk_score: 41,
    risk: "High",
    confidence_score: 84,
    decision: "Conditional Approval",
    hil_required_flag: true,
    created_at: "2026-04-25T09:02:26+05:30",
    reasoning_summary:
      "Reduced amount approved conditionally to bring DTI into policy-compliant range.",
    income_declared: 110000,
    income_verified: 104000,
    rate_percent: 15.5,
    timeline: baseTimeline(true, true, false),
    audit_trail: baseAuditTrail("APP-2026-00418", "Meena Krishnan", true),
  },
  {
    id: "APP-2026-00415",
    applicant_name: "Rahul Verma",
    employer: "State Bank of India",
    employer_type: "GOVT",
    loan_amount: 350000,
    approved_amount: 350000,
    tenure_months: 24,
    cibil_score: "Proxy: 618",
    dti_percent: 38.2,
    risk_score: 62,
    risk: "Medium",
    confidence_score: 80,
    decision: "HIL Pending",
    hil_required_flag: true,
    created_at: "2026-04-25T08:58:10+05:30",
    reasoning_summary:
      "Proxy credit score requires manual confirmation before final sanction.",
    income_declared: 65000,
    income_verified: 62800,
    rate_percent: 12.5,
    timeline: baseTimeline(false, true, false),
    audit_trail: baseAuditTrail("APP-2026-00415", "Rahul Verma", true),
  },
];

export const dashboardKpis = (data: Application[]) => {
  const total = data.length;
  const approved = data.filter(
    (app) => app.decision === "STP Approved" || app.decision === "Conditional Approval"
  ).length;
  const rejected = data.filter((app) => app.decision === "Rejected").length;
  const review = data.filter((app) => app.hil_required_flag).length;
  const avgConfidence = Math.round(
    data.reduce((acc, app) => acc + app.confidence_score, 0) / total
  );

  return { total, approved, rejected, review, avgConfidence };
};
