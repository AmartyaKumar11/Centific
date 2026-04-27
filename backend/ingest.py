"""
=============================================================
Loan Prequalification Agent — Aiven PostgreSQL Ingestion Script
=============================================================
Reads loan_underwriting_perfected.csv and populates all 8 tables:
  1. applications
  2. kyc_api_table
  3. cibil_api_table
  4. bank_api_table
  5. income_api_table
  6. document_analysis_table
  7. decision_engine_output
  8. application_timeline (generated from conditions)

Usage:
    pip install psycopg2-binary pandas
    python ingest.py

Set your Aiven connection string in the DATABASE_URL environment variable
or in a local .env file.
=============================================================
"""

import csv
import json
import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from decimal import Decimal

# ============================================================
# CONNECTION — load from env/.env
# ============================================================
CONNECTION_STRING = None

CSV_PATH = "loan_underwriting_perfected.csv"


# ============================================================
# HELPERS
# ============================================================

def load_local_env(path: str = ".env") -> None:
    """Load KEY=VALUE pairs from a local .env file into os.environ."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"").strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

def to_bool(val: str) -> bool:
    return str(val).strip().upper() == "Y"


def to_float_or_none(val: str):
    v = str(val).strip()
    if v in ("", "nan", "None", "NULL"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def to_int(val) -> int:
    return int(float(str(val).strip()))


def parse_date(val: str):
    """Parse application_date which may include time component."""
    val = str(val).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {val}")


# ============================================================
# TIMELINE GENERATION
# Based on conditions in each row, generates a step-by-step
# agent reasoning trace.
# ============================================================

def generate_timeline(row: dict) -> list:
    """
    Returns a list of timeline step dicts for one application.
    Each step reflects what the agent did and why.
    """
    steps = []
    order = 1

    def add(name, status, triggered_by, output_data):
        nonlocal order
        steps.append({
            "step_order":   order,
            "step_name":    name,
            "step_status":  status,
            "triggered_by": triggered_by,
            "output_data":  json.dumps(output_data),
        })
        order += 1

    # STEP 1: KYC Validation
    add(
        name="KYC_VALIDATION",
        status="PASS",
        triggered_by="application_intake",
        output_data={
            "pan_number":   row["pan_number"],
            "aadhaar_check": "match",
            "dob_verified": row["date_of_birth"],
            "identity_match": True,
            "dedupe_window_30d": "pass",
        }
    )

    # STEP 2: Document Analysis
    ocr = to_int(row["ocr_confidence_score"])
    doc_status = "PASS" if ocr >= 75 else "FLAGGED"
    add(
        name="DOCUMENT_ANALYSIS",
        status=doc_status,
        triggered_by="kyc_validation_complete",
        output_data={
            "ocr_confidence_score":     ocr,
            "document_consistency":     to_bool(row["document_consistency_flag"]),
            "data_consistency":         to_bool(row["data_consistency_flag"]),
            "ocr_result":               "high_confidence" if ocr >= 75 else "low_confidence",
        }
    )

    # STEP 3: Income Verification
    mismatch = to_bool(row["income_mismatch_flag"])
    income_status = "FLAGGED" if mismatch else "PASS"
    add(
        name="INCOME_VERIFICATION",
        status=income_status,
        triggered_by="document_analysis_complete",
        output_data={
            "declared_income":      to_int(row["declared_income"]),
            "verified_income":      to_int(row["verified_income"]),
            "income_mismatch_flag": mismatch,
            "income_stability":     row["income_stability"],
            "mismatch_delta":       to_int(row["declared_income"]) - to_int(row["verified_income"]),
        }
    )

    # STEP 4: Bank API — triggered when income_mismatch_flag = Y
    if mismatch:
        add(
            name="BANK_STATEMENT_ANALYSIS",
            status="PASS",
            triggered_by="income_mismatch_detected",
            output_data={
                "bank_balance":         to_int(row["bank_balance"]),
                "bounce_count":         to_int(row["bounce_count"]),
                "spending_ratio":       float(row["spending_ratio"]),
                "negative_month_count": to_int(row["negative_month_count"]),
                "existing_emi_total":   to_int(row["existing_emi_total"]),
                "trigger_reason":       "income_mismatch_in_prior_step",
                "effective_dti_adjustment": round(
                    float(row["dti_ratio"]) * 100 - (to_int(row["existing_emi_total"]) / to_int(row["declared_income"]) * 100), 2
                ),
            }
        )
    else:
        add(
            name="BANK_STATEMENT_ANALYSIS",
            status="PASS",
            triggered_by="standard_pipeline",
            output_data={
                "bank_balance":         to_int(row["bank_balance"]),
                "bounce_count":         to_int(row["bounce_count"]),
                "spending_ratio":       float(row["spending_ratio"]),
                "negative_month_count": to_int(row["negative_month_count"]),
                "existing_emi_total":   to_int(row["existing_emi_total"]),
            }
        )

    # STEP 5: CIBIL / Credit Bureau Fetch
    cibil = to_int(row["cibil_score"])
    default_f = to_bool(row["default_flag"])
    written_off = to_bool(row["written_off_flag"])
    cibil_status = "FAIL" if (default_f or written_off or cibil < 620) else "PASS"
    add(
        name="CIBIL_FETCH",
        status=cibil_status,
        triggered_by="bank_analysis_complete",
        output_data={
            "cibil_score":          cibil,
            "default_flag":         default_f,
            "written_off_flag":     written_off,
            "credit_enquiries_6m":  to_int(row["credit_enquiries_6m"]),
            "cibil_check":          "below_threshold" if cibil < 620 else "above_threshold",
        }
    )

    # STEP 6: Feature Engineering (DTI, EMI, Risk)
    dti = float(row["dti_ratio"])
    add(
        name="FEATURE_ENGINEERING",
        status="PASS",
        triggered_by="all_api_calls_complete",
        output_data={
            "dti_ratio":        round(dti, 4),
            "proposed_emi":     to_int(row["proposed_emi"]),
            "interest_rate":    float(row["interest_rate"]),
            "risk_score":       row["risk_category"],
            "dti_band":         "HIGH" if dti > 0.5 else "MEDIUM" if dti > 0.35 else "LOW",
        }
    )

    # STEP 7: Decision Engine
    decision_codes = row["decision_reason_codes"]
    add(
        name="DECISION_ENGINE",
        status="PASS",
        triggered_by="feature_engineering_complete",
        output_data={
            "decision":             row["decision"],
            "risk_category":        row["risk_category"],
            "decision_reason_codes":decision_codes,
            "confidence_score":     to_int(row["confidence_score"]),
            "recommendation":       row["decision"].lower(),
            "hard_policy_breach":   any(c in decision_codes for c in ["DEFAULT_FLAG", "HIGH_DTI", "LOW_CIBIL"]),
        }
    )

    # STEP 8: HIL Escalation — triggered when hil_required_flag = Y or low confidence
    hil = to_bool(row["hil_required_flag"])
    confidence = to_int(row["confidence_score"])
    low_confidence = confidence < 80

    if hil or low_confidence:
        add(
            name="HIL_ESCALATION",
            status="ESCALATED",
            triggered_by="hil_required_flag=Y" if hil else "low_confidence_score",
            output_data={
                "hil_required":         True,
                "escalation_reason":    "policy_flags" if hil else "low_confidence",
                "confidence_score":     confidence,
                "assigned_to":          "credit_manager",
                "priority":             "HIGH" if row["risk_category"] == "HIGH" else "MEDIUM",
            }
        )
    else:
        add(
            name="STP_PROCESSING",
            status="PASS",
            triggered_by="high_confidence_no_flags",
            output_data={
                "hil_required":     False,
                "stp_eligible":     True,
                "confidence_score": confidence,
                "auto_processed":   True,
            }
        )

    # STEP 9: Final Status
    final_status = "COMPLETED" if row["decision"] in ("APPROVED", "REJECTED") else "PENDING_HIL"
    add(
        name="TERMINAL_STATE",
        status=final_status,
        triggered_by="decision_engine_output",
        output_data={
            "final_decision":   row["decision"],
            "final_status":     final_status,
            "lms_push_ready":   row["decision"] == "APPROVED" and not hil,
        }
    )

    return steps


# ============================================================
# TABLE INSERTIONS
# ============================================================

def insert_applications(cur, rows):
    sql = """
        INSERT INTO applications (
            application_id, pan_number, applicant_name,
            requested_loan_amount, requested_tenure_months,
            application_date, decision, risk_category,
            confidence_score, hil_required_flag, decision_reason_codes
        ) VALUES %s
        ON CONFLICT (application_id) DO NOTHING;
    """
    data = [(
        r["application_id"],
        r["pan_number"],
        r["applicant_name"],
        to_int(r["requested_loan_amount"]),
        to_int(r["requested_tenure_months"]),
        parse_date(r["application_date"]),
        r["decision"],
        r["risk_category"],
        to_int(r["confidence_score"]),
        to_bool(r["hil_required_flag"]),
        r["decision_reason_codes"],
    ) for r in rows]
    psycopg2.extras.execute_values(cur, sql, data)
    print(f"  [applications] {len(data)} rows inserted.")


def insert_kyc(cur, rows):
    sql = """
        INSERT INTO kyc_api_table (
            application_id, pan_number, applicant_name,
            aadhaar_number, date_of_birth, phone_number, email, address,
            employer_name, employer_type, employment_tenure_years,
            data_consistency_flag
        ) VALUES %s
        ON CONFLICT DO NOTHING;
    """
    data = [(
        r["application_id"],
        r["pan_number"],
        r["applicant_name"],
        int(float(r["aadhaar_number"])),
        datetime.strptime(r["date_of_birth"], "%Y-%m-%d").date(),
        int(float(r["phone_number"])),
        r["email"],
        r["address"],
        r["employer_name"],
        r["employer_type"],
        float(r["employment_tenure_years"]),
        to_bool(r["data_consistency_flag"]),
    ) for r in rows]
    psycopg2.extras.execute_values(cur, sql, data)
    print(f"  [kyc_api_table] {len(data)} rows inserted.")


def insert_cibil(cur, rows):
    sql = """
        INSERT INTO cibil_api_table (
            application_id, pan_number, cibil_score,
            default_flag, written_off_flag, credit_enquiries_6m,
            negative_items_count, oldest_account_years, inquiries_12m,
            accounts_good_standing, derogatory_marks
        ) VALUES %s
        ON CONFLICT DO NOTHING;
    """
    data = [(
        r["application_id"],
        r["pan_number"],
        to_int(r["cibil_score"]),
        to_bool(r["default_flag"]),
        to_bool(r["written_off_flag"]),
        to_int(r["credit_enquiries_6m"]),
        to_float_or_none(r["negative_items_count"]),
        to_float_or_none(r["oldest_account_years"]),
        to_float_or_none(r["inquiries_12m"]),
        to_float_or_none(r["accounts_good_standing"]),
        to_float_or_none(r["derogatory_marks"]),
    ) for r in rows]
    psycopg2.extras.execute_values(cur, sql, data)
    print(f"  [cibil_api_table] {len(data)} rows inserted.")


def insert_bank(cur, rows):
    sql = """
        INSERT INTO bank_api_table (
            application_id, pan_number, bank_balance,
            bounce_count, statement_months, spending_ratio,
            negative_month_count, existing_emi_total
        ) VALUES %s
        ON CONFLICT DO NOTHING;
    """
    data = [(
        r["application_id"],
        r["pan_number"],
        to_int(r["bank_balance"]),
        to_int(r["bounce_count"]),
        to_int(r["statement_months"]),
        float(r["spending_ratio"]),
        to_int(r["negative_month_count"]),
        to_int(r["existing_emi_total"]),
    ) for r in rows]
    psycopg2.extras.execute_values(cur, sql, data)
    print(f"  [bank_api_table] {len(data)} rows inserted.")


def insert_income(cur, rows):
    sql = """
        INSERT INTO income_api_table (
            application_id, pan_number, gross_salary,
            total_deductions, declared_income, verified_income,
            income_mismatch_flag, income_stability
        ) VALUES %s
        ON CONFLICT DO NOTHING;
    """
    data = [(
        r["application_id"],
        r["pan_number"],
        to_int(r["gross_salary"]),
        to_int(r["total_deductions"]),
        to_int(r["declared_income"]),
        to_int(r["verified_income"]),
        to_bool(r["income_mismatch_flag"]),
        r["income_stability"],
    ) for r in rows]
    psycopg2.extras.execute_values(cur, sql, data)
    print(f"  [income_api_table] {len(data)} rows inserted.")


def insert_documents(cur, rows):
    sql = """
        INSERT INTO document_analysis_table (
            application_id, pan_number, ocr_confidence_score,
            document_consistency_flag, data_consistency_flag
        ) VALUES %s
        ON CONFLICT DO NOTHING;
    """
    data = [(
        r["application_id"],
        r["pan_number"],
        to_int(r["ocr_confidence_score"]),
        to_bool(r["document_consistency_flag"]),
        to_bool(r["data_consistency_flag"]),
    ) for r in rows]
    psycopg2.extras.execute_values(cur, sql, data)
    print(f"  [document_analysis_table] {len(data)} rows inserted.")


def insert_decisions(cur, rows):
    sql = """
        INSERT INTO decision_engine_output (
            application_id, pan_number, decision,
            risk_category, decision_reason_codes, confidence_score,
            hil_required_flag, interest_rate, proposed_emi, dti_ratio
        ) VALUES %s
        ON CONFLICT DO NOTHING;
    """
    data = [(
        r["application_id"],
        r["pan_number"],
        r["decision"],
        r["risk_category"],
        r["decision_reason_codes"],
        to_int(r["confidence_score"]),
        to_bool(r["hil_required_flag"]),
        float(r["interest_rate"]),
        to_int(r["proposed_emi"]),
        float(r["dti_ratio"]),
    ) for r in rows]
    psycopg2.extras.execute_values(cur, sql, data)
    print(f"  [decision_engine_output] {len(data)} rows inserted.")


def insert_timeline(cur, rows):
    sql = """
        INSERT INTO application_timeline (
            application_id, step_order, step_name,
            step_status, triggered_by, output_data
        ) VALUES %s
        ON CONFLICT DO NOTHING;
    """
    all_steps = []
    for r in rows:
        steps = generate_timeline(r)
        for s in steps:
            all_steps.append((
                r["application_id"],
                s["step_order"],
                s["step_name"],
                s["step_status"],
                s["triggered_by"],
                s["output_data"],
            ))

    psycopg2.extras.execute_values(cur, sql, all_steps)
    print(f"  [application_timeline] {len(all_steps)} step rows inserted ({len(rows)} applications).")


# ============================================================
# MAIN
# ============================================================

def main():
    global CONNECTION_STRING

    print("=" * 60)
    print("Loan Prequalification Agent — Aiven PostgreSQL Ingestion")
    print("=" * 60)

    load_local_env(".env")
    CONNECTION_STRING = os.getenv("DATABASE_URL")

    # Read CSV
    print(f"\n[1] Reading CSV: {CSV_PATH}")
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"    {len(rows)} rows loaded.")

    # Connect to Aiven Postgres
    print("\n[2] Connecting to Aiven Postgres...")
    if not CONNECTION_STRING:
        raise ValueError(
            "DATABASE_URL is not set. Add it to your environment or .env before running ingest.py."
        )
    conn = psycopg2.connect(CONNECTION_STRING)
    conn.autocommit = False
    cur = conn.cursor()
    print("    Connected.")

    # Insert all tables in dependency order
    print("\n[3] Inserting data...")
    try:
        insert_applications(cur, rows)
        insert_kyc(cur, rows)
        insert_cibil(cur, rows)
        insert_bank(cur, rows)
        insert_income(cur, rows)
        insert_documents(cur, rows)
        insert_decisions(cur, rows)
        insert_timeline(cur, rows)
        conn.commit()
        print("\n[4] All data committed successfully.")
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Rollback triggered: {e}")
        raise
    finally:
        cur.close()
        conn.close()
        print("[5] Connection closed.")

    print("\n" + "=" * 60)
    print("DONE. All 8 tables populated.")
    print("=" * 60)


if __name__ == "__main__":
    main()
