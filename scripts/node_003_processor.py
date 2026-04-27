import csv
import json
import re
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT_DIR / "1000_rows_dataset.csv"
STRUCTURED_BASE = (
    ROOT_DIR
    / "data"
    / "node-003"
    / "validation"
    / "structured"
    / "mandatory_field_validation"
)
REPORTS_DIR = ROOT_DIR / "data" / "node-003" / "reports"


def ensure_dirs():
    (STRUCTURED_BASE / "complete_records").mkdir(parents=True, exist_ok=True)
    (STRUCTURED_BASE / "missing_values").mkdir(parents=True, exist_ok=True)
    (STRUCTURED_BASE / "outliers").mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def app_index(application_id: str) -> int:
    digits = "".join(ch for ch in str(application_id) if ch.isdigit())
    return int(digits) if digits else 0


def is_valid_dob(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def is_valid_pan(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value or ""))


def is_valid_aadhaar(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9]{12}", value or ""))


def to_float(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_number_if_valid(value):
    numeric = to_float(value)
    if numeric is None:
        return value
    return int(numeric) if numeric.is_integer() else numeric


def transformed_fields(row: dict, idx: int) -> dict:
    fields = {
        "application_id": row.get("application_id", ""),
        "name": row.get("applicant_name", ""),
        "dob": row.get("date_of_birth", ""),
        "id_number": row.get("pan_number", ""),
        "aadhaar_number": row.get("aadhaar_number", ""),
        "declared_income": to_number_if_valid(row.get("declared_income", "")),
    }

    # Deterministic, non-random variation: 8% missing, 12% outlier.
    bucket = idx % 50
    if bucket < 4:
        if bucket in (0, 2):
            fields["name"] = ""
        else:
            fields["dob"] = ""
    elif bucket < 10:
        if bucket in (4, 7):
            fields["dob"] = "31/02/1990"
        elif bucket in (5, 8):
            fields["id_number"] = "INVALID_PAN"
        else:
            fields["declared_income"] = "INVALID_NUMERIC"

    return fields


def build_extracted_docs(fields: dict) -> list[dict]:
    return [
        {
            "doc_type": "AADHAAR",
            "fields": {
                "name": fields["name"],
                "dob": fields["dob"],
                "aadhaar_number": fields["aadhaar_number"],
            },
        },
        {
            "doc_type": "PAN",
            "fields": {
                "name": fields["name"],
                "dob": fields["dob"],
                "id_number": fields["id_number"],
            },
        },
        {
            "doc_type": "INCOME_DOC",
            "fields": {
                "application_id": fields["application_id"],
                "declared_income": fields["declared_income"],
            },
        },
    ]


def classify(fields: dict) -> str:
    mandatory = [
        fields["application_id"],
        fields["name"],
        fields["dob"],
        fields["id_number"],
        fields["aadhaar_number"],
        fields["declared_income"],
    ]
    has_missing = any(v is None or str(v).strip() == "" for v in mandatory)
    if has_missing:
        return "missing_values"

    has_outlier = (
        not is_valid_dob(fields["dob"])
        or not is_valid_pan(fields["id_number"])
        or to_float(fields["declared_income"]) is None
    )
    if has_outlier:
        return "outliers"

    return "complete_records"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ensure_dirs()

    complete_records: list[dict] = []
    missing_values: list[dict] = []
    outliers: list[dict] = []

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            application_id = row.get("application_id", "")
            idx = app_index(application_id)
            fields = transformed_fields(row, idx)
            category = classify(fields)

            output_row = {
                "application_id": fields["application_id"],
                "name": fields["name"],
                "dob": fields["dob"],
                "id_number": fields["id_number"],
                "aadhaar_number": fields["aadhaar_number"],
                "declared_income": fields["declared_income"],
                "extracted_fields_all_docs": json.dumps(
                    build_extracted_docs(fields), ensure_ascii=True
                ),
                "category": category,
            }

            if category == "missing_values":
                missing_values.append(output_row)
            elif category == "outliers":
                outliers.append(output_row)
            else:
                complete_records.append(output_row)

    fieldnames = [
        "application_id",
        "name",
        "dob",
        "id_number",
        "aadhaar_number",
        "declared_income",
        "extracted_fields_all_docs",
        "category",
    ]

    write_csv(
        STRUCTURED_BASE / "complete_records" / "complete_records.csv",
        complete_records,
        fieldnames,
    )
    write_csv(
        STRUCTURED_BASE / "missing_values" / "missing_values.csv",
        missing_values,
        fieldnames,
    )
    write_csv(STRUCTURED_BASE / "outliers" / "outliers.csv", outliers, fieldnames)

    total_records = len(complete_records) + len(missing_values) + len(outliers)
    missing_rate = round((len(missing_values) / total_records), 4) if total_records else 0.0
    outlier_rate = round((len(outliers) / total_records), 4) if total_records else 0.0

    summary = {
        "total_records": total_records,
        "distribution": {
            "complete_records": len(complete_records),
            "missing_values": len(missing_values),
            "outliers": len(outliers),
        },
        "key_metrics": {
            "missing_rate": missing_rate,
            "outlier_rate": outlier_rate,
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-003 mandatory field validation complete.")
    print(f"Total records: {total_records}")
    print(f"Missing values: {len(missing_values)} ({missing_rate}%)")
    print(f"Outliers: {len(outliers)} ({outlier_rate}%)")
    print(f"Complete records: {len(complete_records)}")


if __name__ == "__main__":
    main()
