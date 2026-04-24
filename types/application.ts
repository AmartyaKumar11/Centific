export type TimelineStatus = "success" | "warning" | "fail";

export type TimelineStep = {
  step_name: string;
  tool_name: string;
  status: TimelineStatus;
  reasoning: string;
  output_data: string;
  trigger_reason?: string;
};

export type AuditEvent = {
  event_time: string;
  event_code: string;
  title: string;
  details: string;
  tone: "info" | "success" | "warning" | "danger";
};

export type ApplicationDecision =
  | "STP Approved"
  | "Conditional Approval"
  | "HIL Pending"
  | "Rejected";

export type RiskTier = "Low" | "Medium" | "High" | "Very High";

export type Application = {
  id: string;
  applicant_name: string;
  employer: string;
  employer_type: "GOVT" | "PRIVATE";
  loan_amount: number;
  approved_amount: number | null;
  tenure_months: number;
  cibil_score: string;
  dti_percent: number;
  risk_score: number;
  risk: RiskTier;
  confidence_score: number;
  decision: ApplicationDecision;
  hil_required_flag: boolean;
  created_at: string;
  reasoning_summary: string;
  income_declared: number;
  income_verified: number;
  rate_percent: number;
  timeline: TimelineStep[];
  audit_trail: AuditEvent[];
};
