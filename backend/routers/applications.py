import json
from datetime import datetime
from typing import Any

import asyncpg
from fastapi import APIRouter, HTTPException, Query

from database import close_pool, get_pool
from models import Application, DashboardStats, TimelineStep, AuditEvent

router = APIRouter()

DECISION_MAP = {
    "APPROVED": "STP Approved",
    "REVIEW": "HIL Pending",
    "REJECTED": "Rejected",
}

RISK_MAP = {
    "LOW": "Low",
    "MEDIUM": "Medium",
    "HIGH": "High",
    "VERY_HIGH": "Very High",
}

TONE_MAP = {
    "PASS": "success",
    "FAIL": "danger",
    "FLAGGED": "warning",
    "ESCALATED": "warning",
    "COMPLETED": "info",
}

EMPLOYER_TYPE_MAP = {
    "GOVERNMENT": "GOVT",
    "GOVT": "GOVT",
    "PRIVATE": "PRIVATE",
}


def map_decision(db_decision: str, approved_amount: int | None, loan_amount: int) -> str:
    decision = DECISION_MAP.get(db_decision, "HIL Pending")
    if db_decision == "APPROVED" and approved_amount is not None and approved_amount < loan_amount:
        return "Conditional Approval"
    return decision


def map_risk(db_risk: str) -> str:
    return RISK_MAP.get(db_risk, "Medium")


def map_employer_type(db_employer_type: str | None) -> str:
    if not db_employer_type:
        return "PRIVATE"
    return EMPLOYER_TYPE_MAP.get(db_employer_type.upper(), "PRIVATE")


def generate_reasoning_summary(reason_codes: str | None, dti: float, cibil: int) -> str:
    codes = reason_codes.split("|") if reason_codes else []
    parts: list[str] = []
    if "HIGH_DTI" in codes:
        parts.append(f"DTI of {dti:.1f}% exceeds the 40% threshold (HIGH_DTI)")
    if "LOW_CIBIL" in codes:
        parts.append(f"CIBIL score of {cibil} falls below minimum requirement of 620 (LOW_CREDIT_SCORE)")
    if "DEFAULT_FLAG" in codes:
        parts.append("Default flag detected on credit record")
    if not parts:
        parts.append("Application processed through standard underwriting pipeline")
    return ". ".join(parts) + "."


def generate_hil_suggestions(reason_codes: str | None) -> list[str]:
    codes = reason_codes.split("|") if reason_codes else []
    suggestions: list[str] = []
    if "HIGH_DTI" in codes:
        suggestions.append("Verify if applicant has any undeclared income that could lower effective DTI.")
        suggestions.append("Assess if a reduced loan amount could satisfy DTI constraints.")
    if "LOW_CIBIL" in codes:
        suggestions.append("Request updated CIBIL report in case the score has improved since last pull.")
    suggestions.append("If rejecting, confirm rationale is documented for audit compliance.")
    return suggestions


def map_timeline_step(row: dict[str, Any]) -> TimelineStep:
    output = row.get("output_data") or {}
    if isinstance(output, str):
        try:
            output = json.loads(output)
        except json.JSONDecodeError:
            output = {}

    step_map = {
        "KYC_VALIDATION": ("KYC Validation", "KYC Service"),
        "CIBIL_FETCH": ("CIBIL Fetch", "CIBIL API"),
        "INCOME_VERIFICATION": ("Income Validation", "Income Verification Tool"),
        "BANK_STATEMENT_ANALYSIS": ("Bank Statement Analysis", "Bank Analyzer"),
        "DECISION_ENGINE": ("Decision Engine", "Policy Rules Engine"),
        "HIL_ESCALATION": ("HIL Escalation", "HIL Orchestrator"),
        "STP_PROCESSING": ("HIL Escalation", "HIL Orchestrator"),
    }
    step_name, tool_name = step_map.get(row["step_name"], (row["step_name"], "System"))

    status_map = {
        "PASS": "success",
        "FAIL": "fail",
        "FLAGGED": "warning",
        "ESCALATED": "warning",
        "COMPLETED": "success",
    }
    status = status_map.get(row["step_status"], "warning")

    reasoning = output.get("escalation_reason", output.get("final_decision", "Step completed"))
    output_str = " ".join([f"{k}={v}" for k, v in output.items() if k != "triggered_by"])

    return TimelineStep(
        step_name=step_name,
        tool_name=tool_name,
        status=status,  # type: ignore[arg-type]
        reasoning=str(reasoning),
        output_data=output_str[:120],
        trigger_reason=row.get("triggered_by") if row["step_name"] == "BANK_STATEMENT_ANALYSIS" else None,
    )


def map_audit_event(row: dict[str, Any], index: int) -> AuditEvent:
    event_code_map = {
        "KYC_VALIDATION": ("EVT_DEDUP", "info"),
        "INCOME_VERIFICATION": ("EVT_FEATURES", "success"),
        "BANK_STATEMENT_ANALYSIS": ("EVT_SCORE", "info"),
        "CIBIL_FETCH": ("EVT_FLAGS", "warning"),
        "DECISION_ENGINE": ("EVT_DECISION", "danger"),
        "HIL_ESCALATION": ("EVT_HIL_QUEUE", "warning"),
        "STP_PROCESSING": ("EVT_STP", "success"),
    }
    code, default_tone = event_code_map.get(row["step_name"], ("EVT_UNKNOWN", "info"))
    tone = TONE_MAP.get(row.get("step_status", ""), default_tone)
    created_at = row.get("created_at")
    event_time = created_at.strftime("%H:%M:%S") if isinstance(created_at, datetime) else "09:00:00"
    return AuditEvent(
        event_time=event_time,
        event_code=code,
        title=f"{row['step_name'].replace('_', ' ').title()} - {row['application_id']}",
        details=row.get("triggered_by") or "Processing step completed.",
        tone=tone,  # type: ignore[arg-type]
    )


def parse_output_data(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


APPLICATION_SELECT = """
SELECT
  a.application_id,
  a.applicant_name,
  k.employer_name,
  k.employer_type,
  a.requested_loan_amount,
  de.proposed_emi,
  b.existing_emi_total,
  CASE
    WHEN a.decision = 'APPROVED' AND de.proposed_emi IS NOT NULL THEN
      GREATEST(a.requested_loan_amount - (de.proposed_emi * a.requested_tenure_months / 2), 0)::INT
    ELSE NULL
  END AS approved_amount_estimate,
  a.requested_tenure_months,
  c.cibil_score,
  de.dti_ratio,
  a.confidence_score,
  a.risk_category,
  a.decision,
  a.hil_required_flag,
  a.application_date,
  de.decision_reason_codes,
  i.declared_income,
  i.verified_income,
  de.interest_rate,
  k.employment_tenure_years,
  b.bounce_count,
  b.statement_months,
  b.spending_ratio,
  (i.verified_income - COALESCE(de.proposed_emi,0) - COALESCE(b.existing_emi_total,0))::INT AS post_emi_surplus
FROM applications a
JOIN kyc_api_table k ON k.application_id = a.application_id
JOIN income_api_table i ON i.application_id = a.application_id
JOIN bank_api_table b ON b.application_id = a.application_id
JOIN cibil_api_table c ON c.application_id = a.application_id
JOIN decision_engine_output de ON de.application_id = a.application_id
"""


async def fetch_with_retry(query: str, *params: Any):
    last_error: Exception | None = None
    for _ in range(2):
        pool = await get_pool()
        try:
            return await pool.fetch(query, *params)
        except (asyncpg.ConnectionDoesNotExistError, asyncpg.InterfaceError) as exc:
            last_error = exc
            await close_pool()
    if last_error:
        raise last_error
    return []


async def fetchrow_with_retry(query: str, *params: Any):
    last_error: Exception | None = None
    for _ in range(2):
        pool = await get_pool()
        try:
            return await pool.fetchrow(query, *params)
        except (asyncpg.ConnectionDoesNotExistError, asyncpg.InterfaceError) as exc:
            last_error = exc
            await close_pool()
    if last_error:
        raise last_error
    return None


async def fetch_timeline(pool, application_id: str) -> tuple[list[TimelineStep], list[AuditEvent]]:
    timeline_rows = await fetch_with_retry(
        """
        SELECT application_id, step_order, step_name, step_status, triggered_by, output_data, created_at
        FROM application_timeline
        WHERE application_id = $1
        ORDER BY step_order ASC
        """,
        application_id,
    )
    normalized = []
    for row in timeline_rows:
        item = dict(row)
        item["output_data"] = parse_output_data(item.get("output_data"))
        normalized.append(item)
    timeline = [map_timeline_step(row) for row in normalized]
    audit = [map_audit_event(row, idx) for idx, row in enumerate(normalized)]
    return timeline, audit


async def map_application_row(pool, row: dict[str, Any]) -> Application:
    application_id = row["application_id"]
    timeline, audit_trail = await fetch_timeline(pool, application_id)

    cibil_int = int(row["cibil_score"])
    cibil_str = str(cibil_int)
    if row.get("decision_reason_codes") and "PROXY_SCORE" in row["decision_reason_codes"]:
        cibil_str = f"Proxy: {cibil_int}"

    loan_amount = int(row["requested_loan_amount"])
    approved_amount = row.get("approved_amount_estimate")
    approved_amount_int = int(approved_amount) if approved_amount is not None else None
    decision = map_decision(row["decision"], approved_amount_int, loan_amount)
    dti_percent = round(float(row["dti_ratio"]) * 100, 2)
    confidence = int(row["confidence_score"])
    income_declared = int(row["declared_income"])
    income_verified = int(row["verified_income"])
    avg_income = round((income_declared + income_verified) / 2)
    bounce_count = int(row["bounce_count"])
    statement_months = int(row["statement_months"]) or 1
    bounce_freq = round(bounce_count / statement_months, 2)
    post_emi_surplus = int(row["post_emi_surplus"]) if row["post_emi_surplus"] is not None else None

    return Application(
        id=application_id,
        applicant_name=row["applicant_name"],
        employer=row["employer_name"],
        employer_type=map_employer_type(row.get("employer_type")),  # type: ignore[arg-type]
        loan_amount=loan_amount,
        approved_amount=approved_amount_int if decision in ("STP Approved", "Conditional Approval") else None,
        tenure_months=int(row["requested_tenure_months"]),
        cibil_score=cibil_str,
        dti_percent=dti_percent,
        risk_score=confidence,
        risk=map_risk(row["risk_category"]),  # type: ignore[arg-type]
        confidence_score=confidence,
        decision=decision,  # type: ignore[arg-type]
        hil_required_flag=bool(row["hil_required_flag"]),
        created_at=row["application_date"].isoformat() if isinstance(row["application_date"], datetime) else str(row["application_date"]),
        reasoning_summary=generate_reasoning_summary(row.get("decision_reason_codes"), dti_percent, cibil_int),
        income_declared=income_declared,
        income_verified=income_verified,
        income_average=avg_income,
        rate_percent=float(row["interest_rate"]),
        employment_tenure_years=float(row["employment_tenure_years"]) if row["employment_tenure_years"] is not None else None,
        bounce_frequency_per_month=bounce_freq,
        spending_ratio=float(row["spending_ratio"]) if row["spending_ratio"] is not None else None,
        post_emi_surplus=post_emi_surplus,
        risk_summary=None,
        hil_suggestions=generate_hil_suggestions(row.get("decision_reason_codes")),
        timeline=timeline,
        audit_trail=audit_trail,
    )


@router.get("/applications", response_model=list[Application])
async def get_applications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    decision: str | None = None,
    risk_category: str | None = None,
    search: str | None = None,
):
    pool = await get_pool()
    conditions = []
    params: list[Any] = []

    if decision:
        conditions.append(f"a.decision = ${len(params) + 1}")
        params.append(decision)
    if risk_category:
        conditions.append(f"a.risk_category = ${len(params) + 1}")
        params.append(risk_category)
    if search:
        conditions.append(f"(a.application_id ILIKE ${len(params) + 1} OR a.applicant_name ILIKE ${len(params) + 1})")
        params.append(f"%{search}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.extend([limit, skip])
    query = (
        APPLICATION_SELECT
        + f"\n{where_clause}\nORDER BY a.application_date DESC\nLIMIT ${len(params)-1} OFFSET ${len(params)}"
    )
    rows = await fetch_with_retry(query, *params)
    return [await map_application_row(pool, dict(row)) for row in rows]


@router.get("/applications/stats", response_model=DashboardStats)
async def get_application_stats():
    pool = await get_pool()
    row = await fetchrow_with_retry(
        """
        SELECT
          COUNT(*)::INT AS total,
          COUNT(*) FILTER (WHERE decision = 'APPROVED')::INT AS approved_raw,
          COUNT(*) FILTER (WHERE decision = 'REJECTED')::INT AS rejected,
          COUNT(*) FILTER (WHERE hil_required_flag = TRUE)::INT AS hil_queue,
          COALESCE(ROUND(AVG(confidence_score)), 0)::INT AS avg_confidence
        FROM applications
        """
    )
    total = row["total"] or 0
    approved = row["approved_raw"] or 0
    rejected = row["rejected"] or 0
    return DashboardStats(
        total=total,
        approved=approved,
        rejected=rejected,
        hil_queue=row["hil_queue"] or 0,
        avg_confidence=row["avg_confidence"] or 0,
        stp_rate=round((approved / total) * 100, 2) if total else 0.0,
        rejection_rate=round((rejected / total) * 100, 2) if total else 0.0,
    )


@router.get("/applications/{application_id}", response_model=Application)
async def get_application(application_id: str):
    pool = await get_pool()
    row = await fetchrow_with_retry(
        APPLICATION_SELECT + "\nWHERE a.application_id = $1\nLIMIT 1",
        application_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    return await map_application_row(pool, dict(row))
