import csv
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT_DIR / "1000_rows_dataset.csv"

NODE_007_BASE = ROOT_DIR / "data" / "node-007" / "validation" / "structured"
NODE_008_BASE = ROOT_DIR / "data" / "node-008" / "validation" / "structured"
NODE_009_BASE = ROOT_DIR / "data" / "node-009" / "validation" / "structured"
NODE_010_BASE = ROOT_DIR / "data" / "node-010" / "validation" / "structured"

NODE_012_BASE = ROOT_DIR / "data" / "node-012"
STRUCTURED_BASE = NODE_012_BASE / "validation" / "structured"
REPORTS_DIR = NODE_012_BASE / "reports"

RISK_DIR = STRUCTURED_BASE / "applicant_risk_profile"
LOAN_DIR = STRUCTURED_BASE / "loan_product_eligibility"
EMI_DIR = STRUCTURED_BASE / "emi_estimation"


def ensure_dirs():
    paths = [
        RISK_DIR / "complete_records",
        RISK_DIR / "missing_values",
        RISK_DIR / "outliers",
        LOAN_DIR / "complete_records",
        LOAN_DIR / "imbalanced_classes",
        LOAN_DIR / "outliers",
        EMI_DIR / "complete_records",
        EMI_DIR / "missing_values",
        EMI_DIR / "outliers",
        REPORTS_DIR,
    ]
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def app_index(application_id: str) -> int:
    digits = "".join(ch for ch in str(application_id) if ch.isdigit())
    return int(digits) if digits else 0


def to_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_bool(value, default=False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n", ""}:
        return False
    return default


def to_number(value):
    if value is None:
        return None
    num = to_float(value, default=None)
    if num is None:
        return None
    return int(num) if float(num).is_integer() else round(num, 4)


def load_csv_by_app_id(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    with path.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            app_id = row.get("application_id", "")
            if app_id:
                out[app_id] = row
    return out


def merge_sources(paths: list[Path]) -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for p in paths:
        for app_id, row in load_csv_by_app_id(p).items():
            merged[app_id] = row
    return merged


def risk_category_from_score(risk_score):
    if risk_score is None:
        return "UNKNOWN"
    if risk_score >= 70:
        return "HIGH"
    if risk_score >= 40:
        return "MEDIUM"
    return "LOW"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    ensure_dirs()

    node_007 = merge_sources([
        NODE_007_BASE / "kyc_verification" / "complete_records" / "confidence_all.csv",
        NODE_007_BASE / "income_validation" / "complete_records" / "high_confidence.csv",
        NODE_007_BASE / "income_validation" / "imbalanced_classes" / "medium_confidence.csv",
        NODE_007_BASE / "discrepancy_analysis" / "high_severity" / "low_confidence.csv",
    ])
    node_008 = merge_sources([
        NODE_008_BASE / "credit_bureau_data_processing" / "complete_records" / "complete_records.csv",
        NODE_008_BASE / "credit_bureau_data_processing" / "missing_values" / "missing_values.csv",
        NODE_008_BASE / "credit_bureau_data_processing" / "outliers" / "outliers.csv",
    ])
    node_010 = merge_sources([
        NODE_010_BASE / "credit_data_retrieval" / "complete_records" / "complete_records.csv",
        NODE_010_BASE / "credit_data_retrieval" / "missing_values" / "missing_values.csv",
        NODE_010_BASE / "credit_data_retrieval" / "outliers" / "outliers.csv",
    ])
    node_009 = merge_sources([
        NODE_009_BASE / "routing_decisions" / "critical_priority" / "high_priority.csv",
        NODE_009_BASE / "routing_decisions" / "urgent_priority" / "medium_priority.csv",
        NODE_009_BASE / "routing_decisions" / "standard_priority" / "low_priority.csv",
        NODE_009_BASE / "routing_decisions" / "no_hil_required" / "no_hil_required.csv",
    ])

    risk_complete, risk_missing, risk_outliers = [], [], []
    loan_complete, loan_imbalanced, loan_outliers = [], [], []
    emi_complete, emi_missing, emi_outliers = [], [], []

    all_rows = []

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            application_id = row.get("application_id", "")
            idx = app_index(application_id)
            declared_income = to_number(row.get("declared_income"))

            n007 = node_007.get(application_id, {})
            n008 = node_008.get(application_id, {})
            n009 = node_009.get(application_id, {})
            n010 = node_010.get(application_id, {})

            confidence_score = to_float(n007.get("confidence_score"), default=0.0)
            dti = to_float(n008.get("dti"), default=None)
            risk_band = n008.get("risk_band", "UNKNOWN")
            documented_income = to_float(n008.get("documented_income"), default=None)
            credit_score = to_float(n010.get("credit_score"), default=700.0)
            existing_monthly_obligations = to_float(
                n010.get("existing_monthly_obligations"), default=None
            )
            hil_required_flag = to_bool(n009.get("hil_required_flag"), default=False)

            # STEP 1: Applicant risk profile
            risk_score = 0.0
            credit_component = max(700.0 - credit_score, 0.0)
            risk_score += credit_component * 0.1
            if dti is not None:
                risk_score += dti * 100.0 * 0.5
            risk_score += (100.0 - confidence_score) * 0.3
            if hil_required_flag:
                risk_score += 10.0
            risk_score = max(0.0, min(100.0, risk_score))

            risk_missing_flag = idx % 17 == 0
            risk_outlier_flag = idx % 19 == 0

            if risk_missing_flag:
                risk_score_effective = None
            elif risk_outlier_flag:
                risk_score_effective = 100.0
            else:
                risk_score_effective = round(risk_score, 4)

            risk_category = risk_category_from_score(risk_score_effective)

            if risk_missing_flag:
                risk_bucket = "missing_values"
            elif risk_outlier_flag:
                risk_bucket = "outliers"
            else:
                risk_bucket = "complete_records"

            # STEP 2: Loan product eligibility
            if risk_category == "LOW" and credit_score >= 700:
                product = "PREMIUM_LOAN"
            elif risk_category == "MEDIUM":
                product = "STANDARD_LOAN"
            else:
                product = "BASIC_LOAN"

            eligible = True
            if risk_category == "HIGH" and credit_score < 600:
                eligible = False

            imbalanced_flag = idx % 3 != 0
            if imbalanced_flag:
                product = "STANDARD_LOAN"

            loan_outlier_flag = idx % 23 == 0
            if loan_outlier_flag:
                product = "ULTRA_PREMIUM"

            if loan_outlier_flag:
                loan_bucket = "outliers"
            elif imbalanced_flag:
                loan_bucket = "imbalanced_classes"
            else:
                loan_bucket = "complete_records"

            # STEP 3: EMI estimation
            if documented_income is not None and documented_income > 0:
                emi = documented_income * 0.3
            else:
                emi = None

            if risk_category == "HIGH":
                emi = emi * 0.7 if emi is not None else None
            elif risk_category == "LOW":
                emi = emi * 1.2 if emi is not None else None

            emi_missing_flag = idx % 17 == 0
            if emi_missing_flag:
                emi = None

            emi_outlier_flag = idx % 11 == 0 and emi is not None
            if emi_outlier_flag:
                emi = emi * 3

            if emi_missing_flag or emi is None:
                emi_bucket = "missing_values"
            elif emi_outlier_flag:
                emi_bucket = "outliers"
            else:
                emi_bucket = "complete_records"

            out_row = {
                "application_id": application_id,
                "declared_income": declared_income,
                "documented_income": to_number(documented_income),
                "existing_monthly_obligations": to_number(existing_monthly_obligations),
                "credit_score": to_number(credit_score),
                "confidence_score": round(confidence_score, 4),
                "dti": to_number(dti),
                "risk_band": risk_band,
                "hil_required_flag": hil_required_flag,
                "risk_score": to_number(risk_score_effective),
                "risk_category": risk_category,
                "loan_product": product,
                "eligible": eligible,
                "emi_estimate": to_number(emi),
            }
            all_rows.append(out_row)

            if risk_bucket == "missing_values":
                risk_missing.append(out_row)
            elif risk_bucket == "outliers":
                risk_outliers.append(out_row)
            else:
                risk_complete.append(out_row)

            if loan_bucket == "outliers":
                loan_outliers.append(out_row)
            elif loan_bucket == "imbalanced_classes":
                loan_imbalanced.append(out_row)
            else:
                loan_complete.append(out_row)

            if emi_bucket == "missing_values":
                emi_missing.append(out_row)
            elif emi_bucket == "outliers":
                emi_outliers.append(out_row)
            else:
                emi_complete.append(out_row)

    fieldnames = [
        "application_id",
        "declared_income",
        "documented_income",
        "existing_monthly_obligations",
        "credit_score",
        "confidence_score",
        "dti",
        "risk_band",
        "hil_required_flag",
        "risk_score",
        "risk_category",
        "loan_product",
        "eligible",
        "emi_estimate",
    ]

    write_csv(RISK_DIR / "complete_records" / "complete_records.csv", risk_complete, fieldnames)
    write_csv(RISK_DIR / "missing_values" / "missing_values.csv", risk_missing, fieldnames)
    write_csv(RISK_DIR / "outliers" / "outliers.csv", risk_outliers, fieldnames)

    write_csv(LOAN_DIR / "complete_records" / "complete_records.csv", loan_complete, fieldnames)
    write_csv(
        LOAN_DIR / "imbalanced_classes" / "imbalanced_classes.csv",
        loan_imbalanced,
        fieldnames,
    )
    write_csv(LOAN_DIR / "outliers" / "outliers.csv", loan_outliers, fieldnames)

    write_csv(EMI_DIR / "complete_records" / "complete_records.csv", emi_complete, fieldnames)
    write_csv(EMI_DIR / "missing_values" / "missing_values.csv", emi_missing, fieldnames)
    write_csv(EMI_DIR / "outliers" / "outliers.csv", emi_outliers, fieldnames)

    total = len(all_rows)
    high_risk_rate = round(
        (sum(1 for r in all_rows if r["risk_category"] == "HIGH") / total), 4
    ) if total else 0.0
    eligibility_rate = round(
        (sum(1 for r in all_rows if r["eligible"]) / total), 4
    ) if total else 0.0
    emi_values = [r["emi_estimate"] for r in all_rows if r["emi_estimate"] is not None]
    avg_emi = round((sum(emi_values) / len(emi_values)), 4) if emi_values else 0.0

    summary = {
        "total_records": total,
        "distribution": {
            "risk_profile": {
                "complete_records": len(risk_complete),
                "missing_values": len(risk_missing),
                "outliers": len(risk_outliers),
            },
            "loan_product": {
                "complete_records": len(loan_complete),
                "imbalanced_classes": len(loan_imbalanced),
                "outliers": len(loan_outliers),
            },
            "emi": {
                "complete_records": len(emi_complete),
                "missing_values": len(emi_missing),
                "outliers": len(emi_outliers),
            },
        },
        "key_metrics": {
            "high_risk_rate": high_risk_rate,
            "eligibility_rate": eligibility_rate,
            "avg_emi": avg_emi,
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-012 risk profiling and loan recommendation complete.")
    print(f"Total records: {total}")
    print(
        f"Risk complete/missing/outliers: {len(risk_complete)}/{len(risk_missing)}/{len(risk_outliers)}"
    )
    print(
        "Loan complete/imbalanced/outliers: "
        f"{len(loan_complete)}/{len(loan_imbalanced)}/{len(loan_outliers)}"
    )
    print(
        f"EMI complete/missing/outliers: {len(emi_complete)}/{len(emi_missing)}/{len(emi_outliers)}"
    )


if __name__ == "__main__":
    main()
