import csv
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT_DIR / "1000_rows_dataset.csv"
STRUCTURED_BASE = ROOT_DIR / "data" / "node-008" / "validation" / "structured"
REPORTS_DIR = ROOT_DIR / "data" / "node-008" / "reports"

CREDIT_BUREAU_DIR = STRUCTURED_BASE / "credit_bureau_data_processing"
INCOME_VALIDATION_DIR = STRUCTURED_BASE / "income_data_validation"


def ensure_dirs():
    paths = [
        CREDIT_BUREAU_DIR / "complete_records",
        CREDIT_BUREAU_DIR / "missing_values",
        CREDIT_BUREAU_DIR / "outliers",
        INCOME_VALIDATION_DIR / "consistent_income",
        INCOME_VALIDATION_DIR / "inconsistent_income",
        INCOME_VALIDATION_DIR / "missing_documentation",
        REPORTS_DIR,
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def app_index(application_id: str) -> int:
    digits = "".join(ch for ch in str(application_id) if ch.isdigit())
    return int(digits) if digits else 0


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_number_if_possible(value):
    numeric = to_float(value)
    if numeric is None:
        return None
    return int(numeric) if numeric.is_integer() else round(numeric, 2)


def compute_risk_band(dti):
    if dti is None:
        return "UNKNOWN"
    if dti < 0.3:
        return "LOW"
    if dti <= 0.5:
        return "MEDIUM"
    return "HIGH"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ensure_dirs()

    complete_records = []
    missing_values = []
    outliers = []

    consistent_income = []
    inconsistent_income = []
    missing_documentation = []

    all_rows = []

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            application_id = row.get("application_id", "")
            idx = app_index(application_id)

            declared_income_raw = row.get("declared_income", "")
            declared_income = to_float(declared_income_raw)
            declared_income_num = to_number_if_possible(declared_income_raw)

            if declared_income is not None:
                if idx % 5 == 0:
                    documented_income = declared_income * 0.8
                elif idx % 7 == 0:
                    documented_income = None
                else:
                    documented_income = declared_income
            else:
                documented_income = None

            emi = ((idx % 10) ** 2 + 1) * 3000
            is_outlier = idx % 13 == 0
            if is_outlier:
                emi = emi * (5 + (idx % 3))

            active_loans = idx % 5
            total_emi = emi

            if documented_income is not None and documented_income != 0:
                dti = total_emi / documented_income
                dti = round(dti, 4)
            else:
                dti = None

            risk_band = compute_risk_band(dti)

            output_row = {
                "application_id": application_id,
                "declared_income": declared_income_num,
                "documented_income": to_number_if_possible(documented_income),
                "active_loans": active_loans,
                "total_emi": total_emi,
                "dti": dti,
                "risk_band": risk_band,
            }
            all_rows.append(output_row)

            # Credit bureau processing classification (exclusive priority).
            is_missing_doc = documented_income is None
            if is_missing_doc:
                missing_values.append(output_row)
            elif is_outlier:
                outliers.append(output_row)
            else:
                complete_records.append(output_row)

            # Income validation classification (exclusive).
            if is_missing_doc:
                missing_documentation.append(output_row)
            elif abs(declared_income - documented_income) < 1e-9:
                consistent_income.append(output_row)
            else:
                inconsistent_income.append(output_row)

    fieldnames = [
        "application_id",
        "declared_income",
        "documented_income",
        "active_loans",
        "total_emi",
        "dti",
        "risk_band",
    ]

    write_csv(
        CREDIT_BUREAU_DIR / "complete_records" / "complete_records.csv",
        complete_records,
        fieldnames,
    )
    write_csv(
        CREDIT_BUREAU_DIR / "missing_values" / "missing_values.csv",
        missing_values,
        fieldnames,
    )
    write_csv(CREDIT_BUREAU_DIR / "outliers" / "outliers.csv", outliers, fieldnames)

    write_csv(
        INCOME_VALIDATION_DIR / "consistent_income" / "consistent_income.csv",
        consistent_income,
        fieldnames,
    )
    write_csv(
        INCOME_VALIDATION_DIR / "inconsistent_income" / "inconsistent_income.csv",
        inconsistent_income,
        fieldnames,
    )
    write_csv(
        INCOME_VALIDATION_DIR / "missing_documentation" / "missing_documentation.csv",
        missing_documentation,
        fieldnames,
    )

    dti_values = [r["dti"] for r in all_rows if r["dti"] is not None]
    avg_dti = round(sum(dti_values) / len(dti_values), 4) if dti_values else 0.0
    high_risk_count = sum(1 for r in all_rows if r["risk_band"] == "HIGH")
    high_risk_rate = round((high_risk_count / len(all_rows)), 4) if all_rows else 0.0

    summary = {
        "total_records": len(all_rows),
        "distribution": {
            "complete_records": len(complete_records),
            "missing_values": len(missing_values),
            "outliers": len(outliers),
            "consistent_income": len(consistent_income),
            "inconsistent_income": len(inconsistent_income),
            "missing_documentation": len(missing_documentation),
        },
        "key_metrics": {
            "avg_dti": avg_dti,
            "high_risk_rate": high_risk_rate,
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-008 credit bureau and DTI processing complete.")
    print(f"Total records: {len(all_rows)}")
    print(f"Complete records: {len(complete_records)}")
    print(f"Missing values: {len(missing_values)}")
    print(f"Outliers: {len(outliers)}")
    print(f"Consistent income: {len(consistent_income)}")
    print(f"Inconsistent income: {len(inconsistent_income)}")
    print(f"Missing documentation: {len(missing_documentation)}")
    print(f"Average DTI: {avg_dti}")
    print(f"High risk rate: {high_risk_rate}%")


if __name__ == "__main__":
    main()
