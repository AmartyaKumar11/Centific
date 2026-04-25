from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TimelineStep(BaseModel):
    step_name: str
    tool_name: str
    status: Literal["success", "warning", "fail"]
    reasoning: str
    output_data: str
    trigger_reason: str | None = None


class AuditEvent(BaseModel):
    event_time: str
    event_code: str
    title: str
    details: str
    tone: Literal["info", "success", "warning", "danger"]


class Application(BaseModel):
    id: str
    applicant_name: str
    employer: str
    employer_type: Literal["GOVT", "PRIVATE"]
    loan_amount: int
    approved_amount: int | None
    tenure_months: int
    cibil_score: str
    dti_percent: float
    risk_score: int
    risk: Literal["Low", "Medium", "High", "Very High"]
    confidence_score: int
    decision: Literal["STP Approved", "Conditional Approval", "HIL Pending", "Rejected"]
    hil_required_flag: bool
    created_at: str
    reasoning_summary: str
    income_declared: int
    income_verified: int
    income_average: int | None = None
    rate_percent: float
    employment_tenure_years: float | None = None
    bounce_frequency_per_month: float | None = None
    spending_ratio: float | None = None
    post_emi_surplus: int | None = None
    risk_summary: str | None = None
    hil_suggestions: list[str] | None = None
    timeline: list[TimelineStep]
    audit_trail: list[AuditEvent]


class DashboardStats(BaseModel):
    total: int
    approved: int
    rejected: int
    hil_queue: int
    avg_confidence: int
    stp_rate: float
    rejection_rate: float


class HilActionPayload(BaseModel):
    action: Literal["approve", "reject", "modify_approve"]
    officer_id: str
    notes: str = ""


class HilQueueResponse(BaseModel):
    awaiting: list[Application]
    review: list[Application]
    approved: list[Application]
    rejected: list[Application]


class HilActionResponse(BaseModel):
    success: bool
    updated_application: Application


class DailyBatch(BaseModel):
    labels: list[str]
    processed: list[int]
    rejected: list[int]


class DashboardCharts(BaseModel):
    decision_distribution: dict[str, int]
    risk_distribution: dict[str, int]
    employer_split: dict[str, int]
    rejection_reasons: dict[str, int]
    daily_batch: DailyBatch
