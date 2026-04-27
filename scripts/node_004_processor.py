import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT_DIR / "1000_rows_dataset.csv"
STRUCTURED_BASE = ROOT_DIR / "data" / "node-004" / "validation" / "structured"
REPORTS_DIR = ROOT_DIR / "data" / "node-004" / "reports"

KYC_DIR = STRUCTURED_BASE / "kyc_identity_verification"
CROSS_DOC_DIR = STRUCTURED_BASE / "cross_document_consistency"


def ensure_dirs():
    paths = [
        KYC_DIR / "complete_records",
        KYC_DIR / "missing_values",
        KYC_DIR / "format_inconsistencies",
        CROSS_DOC_DIR / "consistent_fields",
        CROSS_DOC_DIR / "inconsistent_names",
        CROSS_DOC_DIR / "inconsistent_dates",
        REPORTS_DIR,
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def parse_app_index(application_id: str) -> int:
    digits = "".join(ch for ch in str(application_id) if ch.isdigit())
    return int(digits) if digits else 0


def is_valid_dob(dob: str) -> bool:
    if not dob:
        return False
    try:
        datetime.strptime(dob, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_pan(pan_number: str) -> bool:
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan_number or ""))


def normalize_name(value: str) -> str:
    return " ".join((value or "").strip().upper().split())


def generate_doc_values(base_name: str, base_dob: str, base_pan: str, idx: int):
    name = base_name
    dob = base_dob
    id_number = base_pan

    # Missing values (priority over format issues).
    if idx % 19 == 0:
        name = None
    elif idx % 23 == 0:
        dob = None

    aadhaar_name = name
    pan_name = name
    aadhaar_dob = dob
    pan_dob = dob
    aadhaar_id = f"AADHAAR-{idx:06d}"
    pan_id = id_number

    # Format inconsistencies.
    if aadhaar_dob is not None and pan_dob is not None and idx % 11 == 0 and is_valid_dob(aadhaar_dob):
        parsed = datetime.strptime(aadhaar_dob, "%Y-%m-%d")
        wrong_format = parsed.strftime("%m/%d/%Y")
        aadhaar_dob = wrong_format
        pan_dob = wrong_format
    if idx % 13 == 0:
        pan_id = "INVALID_PAN"

    # Cross-document inconsistencies; force non-overlap by precedence.
    if aadhaar_name is not None and idx % 7 == 0:
        name_parts = aadhaar_name.split()
        if len(name_parts) >= 2:
            pan_name = f"{aadhaar_name[:3]} {name_parts[-1]}"
        else:
            pan_name = f"{aadhaar_name[:3]} X"
    elif aadhaar_dob is not None and idx % 9 == 0 and is_valid_dob(aadhaar_dob):
        shifted = datetime.strptime(aadhaar_dob, "%Y-%m-%d") + timedelta(days=1)
        pan_dob = shifted.strftime("%Y-%m-%d")

    return {
        "name": name,
        "dob": dob,
        "id_number": id_number,
        "aadhaar_name": aadhaar_name,
        "aadhaar_dob": aadhaar_dob,
        "aadhaar_id_number": aadhaar_id,
        "pan_name": pan_name,
        "pan_dob": pan_dob,
        "pan_id_number": pan_id,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ensure_dirs()

    complete_records: list[dict] = []
    missing_values: list[dict] = []
    format_inconsistencies: list[dict] = []

    consistent_fields: list[dict] = []
    inconsistent_names: list[dict] = []
    inconsistent_dates: list[dict] = []

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    output_rows: list[dict] = []
    for row in all_rows:
        app_id = row.get("application_id", "")
        idx = parse_app_index(app_id)

        base_name = row.get("applicant_name", "").strip() or None
        base_dob = row.get("date_of_birth", "").strip() or None
        base_pan = row.get("pan_number", "").strip() or None
        base_aadhaar = row.get("aadhaar_number", "").strip()

        docs = generate_doc_values(base_name, base_dob, base_pan, idx)

        required_values = [
            app_id,
            docs["name"],
            docs["dob"],
            docs["id_number"],
            base_aadhaar,
            docs["aadhaar_name"],
            docs["aadhaar_dob"],
            docs["aadhaar_id_number"],
            docs["pan_name"],
            docs["pan_dob"],
            docs["pan_id_number"],
        ]
        has_missing = any(v is None or str(v).strip() == "" for v in required_values)

        dob_valid = is_valid_dob(docs["dob"]) and is_valid_dob(docs["aadhaar_dob"]) and is_valid_dob(
            docs["pan_dob"]
        )
        id_valid = is_valid_pan(docs["id_number"]) and is_valid_pan(docs["pan_id_number"])
        has_format_issue = not dob_valid or not id_valid

        name_match = normalize_name(docs["aadhaar_name"]) == normalize_name(docs["pan_name"])
        dob_match = docs["aadhaar_dob"] == docs["pan_dob"]

        out_row = {
            "application_id": app_id,
            "name": docs["name"],
            "dob": docs["dob"],
            "id_number": docs["id_number"],
            "aadhaar_name": docs["aadhaar_name"],
            "aadhaar_dob": docs["aadhaar_dob"],
            "aadhaar_id_number": docs["aadhaar_id_number"],
            "pan_name": docs["pan_name"],
            "pan_dob": docs["pan_dob"],
            "pan_id_number": docs["pan_id_number"],
            "is_complete_record": not has_missing,
            "has_format_issue": has_format_issue,
            "name_match": name_match,
            "dob_match": dob_match,
        }
        output_rows.append(out_row)

        if has_missing:
            missing_values.append(out_row)
        elif has_format_issue:
            format_inconsistencies.append(out_row)
        else:
            complete_records.append(out_row)

        if not name_match:
            inconsistent_names.append(out_row)
        elif not dob_match:
            inconsistent_dates.append(out_row)
        else:
            consistent_fields.append(out_row)

    fieldnames = [
        "application_id",
        "name",
        "dob",
        "id_number",
        "aadhaar_name",
        "aadhaar_dob",
        "aadhaar_id_number",
        "pan_name",
        "pan_dob",
        "pan_id_number",
        "is_complete_record",
        "has_format_issue",
        "name_match",
        "dob_match",
    ]

    write_csv(KYC_DIR / "complete_records" / "complete_records.csv", complete_records, fieldnames)
    write_csv(KYC_DIR / "missing_values" / "missing_values.csv", missing_values, fieldnames)
    write_csv(
        KYC_DIR / "format_inconsistencies" / "format_inconsistencies.csv",
        format_inconsistencies,
        fieldnames,
    )

    write_csv(CROSS_DOC_DIR / "consistent_fields" / "consistent_fields.csv", consistent_fields, fieldnames)
    write_csv(CROSS_DOC_DIR / "inconsistent_names" / "inconsistent_names.csv", inconsistent_names, fieldnames)
    write_csv(CROSS_DOC_DIR / "inconsistent_dates" / "inconsistent_dates.csv", inconsistent_dates, fieldnames)

    total = len(output_rows) if output_rows else 1
    summary = {
        "total_records": len(output_rows),
        "distribution": {
            "complete_records": len(complete_records),
            "missing_values": len(missing_values),
            "format_inconsistencies": len(format_inconsistencies),
            "consistent_fields": len(consistent_fields),
            "inconsistent_names": len(inconsistent_names),
            "inconsistent_dates": len(inconsistent_dates),
        },
        "key_metrics": {
            "format_error_rate": round((len(format_inconsistencies) / total), 4),
            "consistency_error_rate": round(
                ((len(inconsistent_names) + len(inconsistent_dates)) / total),
                4,
            ),
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-004 KYC and cross-document consistency processing complete.")
    print(f"Total rows: {len(output_rows)}")
    print(f"Complete records: {len(complete_records)}")
    print(f"Missing values: {len(missing_values)}")
    print(f"Format inconsistencies: {len(format_inconsistencies)}")
    print(f"Consistent fields: {len(consistent_fields)}")
    print(f"Inconsistent names: {len(inconsistent_names)}")
    print(f"Inconsistent dates: {len(inconsistent_dates)}")


if __name__ == "__main__":
    main()
