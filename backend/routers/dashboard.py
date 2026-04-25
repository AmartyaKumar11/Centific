from collections import Counter

from fastapi import APIRouter

from models import DashboardCharts, DailyBatch
from routers.applications import fetch_with_retry

router = APIRouter()


@router.get("/dashboard/charts", response_model=DashboardCharts)
async def get_dashboard_charts():
    rows = await fetch_with_retry(
        """
        SELECT
          a.decision,
          a.risk_category,
          k.employer_type,
          de.decision_reason_codes,
          de.dti_ratio,
          c.cibil_score
        FROM applications a
        JOIN kyc_api_table k ON k.application_id = a.application_id
        JOIN decision_engine_output de ON de.application_id = a.application_id
        JOIN cibil_api_table c ON c.application_id = a.application_id
        """
    )

    decision_counter = Counter()
    risk_counter = Counter()
    employer_counter = Counter()
    rejection_counter = Counter({"HIGH_DTI": 0, "LOW_CIBIL": 0, "HIGH_RISK": 0, "PROXY_SCORE": 0})

    decision_map = {"APPROVED": "STP Approved", "REVIEW": "HIL Pending", "REJECTED": "Rejected"}
    risk_map = {"LOW": "Low", "MEDIUM": "Medium", "HIGH": "High", "VERY_HIGH": "Very High"}

    for row in rows:
        decision_counter[decision_map.get(row["decision"], row["decision"])] += 1
        risk_counter[risk_map.get(row["risk_category"], row["risk_category"])] += 1
        employer_counter[row["employer_type"]] += 1
        codes = (row["decision_reason_codes"] or "").split("|")
        if float(row["dti_ratio"]) > 0.4:
            rejection_counter["HIGH_DTI"] += 1
        if int(row["cibil_score"]) < 620:
            rejection_counter["LOW_CIBIL"] += 1
        if row["risk_category"] in ("HIGH", "VERY_HIGH"):
            rejection_counter["HIGH_RISK"] += 1
        if "PROXY_SCORE" in codes:
            rejection_counter["PROXY_SCORE"] += 1

    daily = DailyBatch(
        labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"],
        processed=[42, 76, 50, 61, 47, 20, 39],
        rejected=[9, 14, 7, 11, 8, 3, 12],
    )

    return DashboardCharts(
        decision_distribution=dict(decision_counter),
        risk_distribution=dict(risk_counter),
        employer_split=dict(employer_counter),
        rejection_reasons=dict(rejection_counter),
        daily_batch=daily,
    )
