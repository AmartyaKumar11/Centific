import csv
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT_DIR / "1000_rows_dataset.csv"
OUTPUT_BASE = (
    ROOT_DIR
    / "data"
    / "node-006"
    / "validation"
    / "structured"
)
FLAG_AGGREGATION_DIR = OUTPUT_BASE / "flag_aggregation"
SEVERITY_CLASSIFICATION_DIR = OUTPUT_BASE / "severity_classification"
UNSTRUCTURED_DIR = ROOT_DIR / "data" / "node-006" / "validation" / "unstructured"
REPORTS_DIR = ROOT_DIR / "data" / "node-006" / "reports"


FLAG_PRIORITY = [
    "DEFAULT_HISTORY",
    "HIGH_DTI",
    "LOW_CREDIT_SCORE",
    "BANK_RISK",
    "HIGH_ENQUIRIES",
    "INCOME_MISMATCH",
    "MEDIUM_DTI",
]


def to_bool(value: str) -> bool:
    if value is None:
        return False
    return str(value).strip().upper() in {"TRUE", "1", "YES", "Y"}


def to_float(value: str):
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def to_int(value: str):
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def ensure_dirs():
    paths = [
        FLAG_AGGREGATION_DIR / "complete_records",
        FLAG_AGGREGATION_DIR / "missing_values",
        FLAG_AGGREGATION_DIR / "duplicated_flags",
        SEVERITY_CLASSIFICATION_DIR / "critical_severity",
        SEVERITY_CLASSIFICATION_DIR / "major_severity",
        SEVERITY_CLASSIFICATION_DIR / "minor_severity",
        SEVERITY_CLASSIFICATION_DIR / "complete_records",
        SEVERITY_CLASSIFICATION_DIR / "missing_values",
        SEVERITY_CLASSIFICATION_DIR / "outliers",
        UNSTRUCTURED_DIR,
        REPORTS_DIR,
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def derive_flags(row: dict) -> list[str]:
    flags = []

    income_mismatch_flag = to_bool(row.get("income_mismatch_flag"))
    dti_ratio = to_float(row.get("dti_ratio"))
    cibil_score = to_int(row.get("cibil_score"))
    default_flag = to_bool(row.get("default_flag"))
    bounce_count = to_int(row.get("bounce_count"))
    credit_enquiries_6m = to_int(row.get("credit_enquiries_6m"))

    if income_mismatch_flag:
        flags.append("INCOME_MISMATCH")

    if dti_ratio is not None:
        if dti_ratio > 0.5:
            flags.append("HIGH_DTI")
        elif 0.3 <= dti_ratio <= 0.5:
            flags.append("MEDIUM_DTI")

    if cibil_score is not None and cibil_score < 650:
        flags.append("LOW_CREDIT_SCORE")

    if default_flag:
        flags.append("DEFAULT_HISTORY")

    if credit_enquiries_6m is not None and credit_enquiries_6m > 4:
        flags.append("HIGH_ENQUIRIES")

    if bounce_count is not None and bounce_count >= 3:
        flags.append("BANK_RISK")

    unique = set(flags)
    ordered = [flag for flag in FLAG_PRIORITY if flag in unique]
    return ordered[:3]


def derive_severity(flags: list[str]) -> str:
    if not flags:
        return "NONE"
    if "DEFAULT_HISTORY" in flags or "HIGH_DTI" in flags:
        return "HIGH"
    if len(flags) >= 2:
        return "MEDIUM"
    return "LOW"


def transform_row(row: dict) -> dict:
    flags = derive_flags(row)
    severity = derive_severity(flags)

    return {
        "application_id": row.get("application_id", ""),
        "income_mismatch_flag": row.get("income_mismatch_flag", ""),
        "dti_ratio": row.get("dti_ratio", ""),
        "cibil_score": row.get("cibil_score", ""),
        "default_flag": row.get("default_flag", ""),
        "bounce_count": row.get("bounce_count", ""),
        "credit_enquiries_6m": row.get("credit_enquiries_6m", ""),
        "flags": "|".join(flags),
        "severity": severity,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ensure_dirs()

    high_rows, medium_rows, low_rows, none_rows = [], [], [], []

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        transformed_rows = [transform_row(row) for row in reader]

    for row in transformed_rows:
        if row["severity"] == "HIGH":
            high_rows.append(row)
        elif row["severity"] == "MEDIUM":
            medium_rows.append(row)
        elif row["severity"] == "LOW":
            low_rows.append(row)
        else:
            none_rows.append(row)

    fieldnames = [
        "application_id",
        "income_mismatch_flag",
        "dti_ratio",
        "cibil_score",
        "default_flag",
        "bounce_count",
        "credit_enquiries_6m",
        "flags",
        "severity",
    ]

    write_csv(SEVERITY_CLASSIFICATION_DIR / "critical_severity" / "high_severity.csv", high_rows, fieldnames)
    write_csv(SEVERITY_CLASSIFICATION_DIR / "major_severity" / "medium_severity.csv", medium_rows, fieldnames)
    write_csv(SEVERITY_CLASSIFICATION_DIR / "minor_severity" / "low_severity.csv", low_rows, fieldnames)
    write_csv(FLAG_AGGREGATION_DIR / "complete_records" / "no_flags.csv", none_rows, fieldnames)
    write_csv(FLAG_AGGREGATION_DIR / "complete_records" / "all_records.csv", transformed_rows, fieldnames)
    write_csv(FLAG_AGGREGATION_DIR / "duplicated_flags" / "duplicated_flags.csv", [], fieldnames)

    summary = {
        "total_records": len(transformed_rows),
        "distribution": {
            "high_severity": len(high_rows),
            "medium_severity": len(medium_rows),
            "low_severity": len(low_rows),
            "none_severity": len(none_rows),
        },
        "key_metrics": {
            "total_flagged_records": len(high_rows) + len(medium_rows) + len(low_rows),
            "unflagged_records": len(none_rows),
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-006 discrepancy detection complete (root data folder).")
    print(f"Total rows processed: {len(transformed_rows)}")
    print(f"HIGH severity: {len(high_rows)}")
    print(f"MEDIUM severity: {len(medium_rows)}")
    print(f"LOW severity: {len(low_rows)}")
    print(f"NONE severity: {len(none_rows)}")


if __name__ == "__main__":
    main()
