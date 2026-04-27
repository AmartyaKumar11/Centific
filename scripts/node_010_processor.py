import csv
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT_DIR / "1000_rows_dataset.csv"
NODE_BASE = ROOT_DIR / "data" / "node-010"

STRUCTURED_BASE = NODE_BASE / "validation" / "structured"
UNSTRUCTURED_BASE = NODE_BASE / "validation" / "unstructured"
REPORTS_DIR = NODE_BASE / "reports"

CREDIT_DATA_DIR = STRUCTURED_BASE / "credit_data_retrieval"
IDENTITY_DIR = STRUCTURED_BASE / "identity_verification"
RAW_RESPONSE_DIR = UNSTRUCTURED_BASE / "raw_response_handling"


def ensure_dirs():
    paths = [
        CREDIT_DATA_DIR / "complete_records",
        CREDIT_DATA_DIR / "missing_values",
        CREDIT_DATA_DIR / "outliers",
        IDENTITY_DIR / "accurate_identity",
        IDENTITY_DIR / "inaccurate_identity",
        IDENTITY_DIR / "partial_identity",
        RAW_RESPONSE_DIR / "well_formed_json",
        RAW_RESPONSE_DIR / "malformed_json",
        RAW_RESPONSE_DIR / "unexpected_fields",
        REPORTS_DIR,
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def app_index(application_id: str) -> int:
    digits = "".join(ch for ch in str(application_id) if ch.isdigit())
    return int(digits) if digits else 0


def to_number_if_possible(value):
    try:
        num = float(value)
    except (TypeError, ValueError):
        return value
    return int(num) if num.is_integer() else round(num, 2)


def vary_inaccurate_name(name: str, idx: int) -> str:
    mode = idx % 3
    parts = [p for p in name.split() if p]
    if not parts:
        return name

    if mode == 0 and len(parts) >= 2:
        swapped = [parts[-1]] + parts[1:-1] + [parts[0]]
        return " ".join(swapped)
    if mode == 1:
        first = parts[0]
        if len(first) >= 2:
            first = first[:-1] + "Z"
        else:
            first = first + "Z"
        return " ".join([first] + parts[1:])
    return name[: max(3, len(name) // 2)].strip()


def get_base_fields(row: dict):
    name = (row.get("name") or row.get("applicant_name") or "").strip()
    dob = (row.get("dob") or row.get("date_of_birth") or "").strip()
    id_number = (row.get("id_number") or row.get("pan_number") or "").strip()
    return name, dob, id_number


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ensure_dirs()

    # Structured buckets
    complete_records = []
    missing_values = []
    outliers = []

    accurate_identity = []
    inaccurate_identity = []
    partial_identity = []

    # Unstructured buckets
    well_formed_json = []
    malformed_json = []
    unexpected_fields = []

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            application_id = row.get("application_id", "")
            idx = app_index(application_id)

            base_name, base_dob, base_id_number = get_base_fields(row)

            id_type = "PAN" if len(base_id_number) == 10 else "UNKNOWN"

            # Identity verification bucketing (exclusive).
            name = base_name
            dob = base_dob
            id_number = base_id_number
            if idx % 11 == 0:
                identity_status = "inaccurate_identity"
                name = vary_inaccurate_name(base_name, idx)
            elif idx % 7 == 0:
                identity_status = "partial_identity"
                if idx % 2 == 0:
                    dob = ""
                else:
                    id_number = ""
            else:
                identity_status = "accurate_identity"

            # Credit data generation.
            credit_score = 300 + (idx % 550)
            existing_monthly_obligations = (idx % 15 + 1) * 4000
            credit_history_months = (idx % 120) + 1
            active_loans_count = idx % 6

            # Cross-field realism without changing deterministic distribution buckets.
            if identity_status == "inaccurate_identity":
                credit_score = max(300, credit_score - 50)
            if identity_status == "partial_identity":
                active_loans_count = None

            # Missing + outlier injections.
            missing_credit_score = idx % 17 == 0
            missing_obligations = idx % 19 == 0
            outlier_obligations = idx % 13 == 0
            outlier_credit_score = idx % 23 == 0

            if missing_credit_score:
                credit_score = None
            if missing_obligations:
                existing_monthly_obligations = None
            if outlier_obligations and existing_monthly_obligations is not None:
                existing_monthly_obligations *= 5
            if outlier_credit_score:
                credit_score = 900

            any_missing = credit_score is None or existing_monthly_obligations is None
            outlier_triggered = outlier_obligations or outlier_credit_score

            # Credit data retrieval bucket (exclusive strict priority).
            if any_missing:
                credit_bucket = "missing_values"
            elif outlier_triggered:
                credit_bucket = "outliers"
            else:
                credit_bucket = "complete_records"

            base_output = {
                "application_id": application_id,
                "name": name,
                "dob": dob,
                "id_number": id_number,
                "id_type": id_type,
                "credit_score": credit_score,
                "existing_monthly_obligations": existing_monthly_obligations,
                "credit_history_months": credit_history_months,
                "active_loans_count": active_loans_count,
            }

            if credit_bucket == "missing_values":
                missing_values.append(base_output)
            elif credit_bucket == "outliers":
                outliers.append(base_output)
            else:
                complete_records.append(base_output)

            if identity_status == "inaccurate_identity":
                inaccurate_identity.append(base_output)
            elif identity_status == "partial_identity":
                partial_identity.append(base_output)
            else:
                accurate_identity.append(base_output)

            raw_response_dict = {
                "score": credit_score,
                "obligations": existing_monthly_obligations,
                "history_months": credit_history_months,
                "active_loans": active_loans_count,
            }

            if idx % 10 == 0:
                raw_bucket = "malformed_json"
                mode = idx % 3
                canonical = json.dumps(raw_response_dict)
                if mode == 0:
                    raw_response = canonical[:-1]  # remove closing brace
                elif mode == 1:
                    raw_response = canonical.replace('"score"', "score", 1)  # break quotes
                else:
                    raw_response = canonical[: max(8, len(canonical) // 2)]  # truncate
            elif idx % 9 == 0:
                raw_bucket = "unexpected_fields"
                enriched = dict(raw_response_dict)
                enriched["extra_flag"] = "UNKNOWN"
                raw_response = json.dumps(enriched)
            else:
                raw_bucket = "well_formed_json"
                raw_response = json.dumps(raw_response_dict)

            raw_output = dict(base_output)
            raw_output["credit_bureau_raw_response"] = raw_response

            if raw_bucket == "malformed_json":
                malformed_json.append(raw_output)
            elif raw_bucket == "unexpected_fields":
                unexpected_fields.append(raw_output)
            else:
                well_formed_json.append(raw_output)

    base_fields = [
        "application_id",
        "name",
        "dob",
        "id_number",
        "id_type",
        "credit_score",
        "existing_monthly_obligations",
        "credit_history_months",
        "active_loans_count",
    ]
    raw_fields = base_fields + ["credit_bureau_raw_response"]

    write_csv(
        CREDIT_DATA_DIR / "complete_records" / "complete_records.csv",
        complete_records,
        base_fields,
    )
    write_csv(
        CREDIT_DATA_DIR / "missing_values" / "missing_values.csv",
        missing_values,
        base_fields,
    )
    write_csv(CREDIT_DATA_DIR / "outliers" / "outliers.csv", outliers, base_fields)

    write_csv(
        IDENTITY_DIR / "accurate_identity" / "accurate_identity.csv",
        accurate_identity,
        base_fields,
    )
    write_csv(
        IDENTITY_DIR / "inaccurate_identity" / "inaccurate_identity.csv",
        inaccurate_identity,
        base_fields,
    )
    write_csv(
        IDENTITY_DIR / "partial_identity" / "partial_identity.csv",
        partial_identity,
        base_fields,
    )

    write_csv(
        RAW_RESPONSE_DIR / "well_formed_json" / "well_formed_json.csv",
        well_formed_json,
        raw_fields,
    )
    write_csv(
        RAW_RESPONSE_DIR / "malformed_json" / "malformed_json.csv",
        malformed_json,
        raw_fields,
    )
    write_csv(
        RAW_RESPONSE_DIR / "unexpected_fields" / "unexpected_fields.csv",
        unexpected_fields,
        raw_fields,
    )

    total_records = len(complete_records) + len(missing_values) + len(outliers)
    # Decimal rates (0-1), not percentages.
    missing_rate = round((len(missing_values) / total_records), 4) if total_records else 0.0
    outlier_rate = round((len(outliers) / total_records), 4) if total_records else 0.0
    malformed_rate = round((len(malformed_json) / total_records), 4) if total_records else 0.0

    # Internal assertions to enforce exclusivity and total reconciliation.
    credit_complete_ids = {r["application_id"] for r in complete_records}
    credit_missing_ids = {r["application_id"] for r in missing_values}
    credit_outlier_ids = {r["application_id"] for r in outliers}
    identity_accurate_ids = {r["application_id"] for r in accurate_identity}
    identity_inaccurate_ids = {r["application_id"] for r in inaccurate_identity}
    identity_partial_ids = {r["application_id"] for r in partial_identity}
    raw_well_ids = {r["application_id"] for r in well_formed_json}
    raw_malformed_ids = {r["application_id"] for r in malformed_json}
    raw_unexpected_ids = {r["application_id"] for r in unexpected_fields}

    assert total_records == len(complete_records) + len(missing_values) + len(outliers)
    assert len(credit_complete_ids & credit_missing_ids) == 0
    assert len(credit_complete_ids & credit_outlier_ids) == 0
    assert len(credit_missing_ids & credit_outlier_ids) == 0
    assert len(credit_complete_ids | credit_missing_ids | credit_outlier_ids) == total_records

    assert len(identity_accurate_ids & identity_inaccurate_ids) == 0
    assert len(identity_accurate_ids & identity_partial_ids) == 0
    assert len(identity_inaccurate_ids & identity_partial_ids) == 0
    assert len(identity_accurate_ids | identity_inaccurate_ids | identity_partial_ids) == total_records

    assert len(raw_well_ids & raw_malformed_ids) == 0
    assert len(raw_well_ids & raw_unexpected_ids) == 0
    assert len(raw_malformed_ids & raw_unexpected_ids) == 0
    assert len(raw_well_ids | raw_malformed_ids | raw_unexpected_ids) == total_records

    summary = {
        "total_records": total_records,
        "distribution": {
            "identity": {
                "accurate_identity": len(accurate_identity),
                "inaccurate_identity": len(inaccurate_identity),
                "partial_identity": len(partial_identity),
            },
            "credit_data": {
                "complete_records": len(complete_records),
                "missing_values": len(missing_values),
                "outliers": len(outliers),
            },
            "raw_response": {
                "well_formed_json": len(well_formed_json),
                "malformed_json": len(malformed_json),
                "unexpected_fields": len(unexpected_fields),
            },
        },
        "key_metrics": {
            "missing_rate": missing_rate,
            "outlier_rate": outlier_rate,
            "malformed_rate": malformed_rate,
        },
    }

    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-010 data generation complete.")
    print(f"Total records: {total_records}")
    print(
        "Credit data -> complete/missing/outliers: "
        f"{len(complete_records)}/{len(missing_values)}/{len(outliers)}"
    )
    print(
        "Identity -> accurate/inaccurate/partial: "
        f"{len(accurate_identity)}/{len(inaccurate_identity)}/{len(partial_identity)}"
    )
    print(
        "Raw response -> well_formed/malformed/unexpected: "
        f"{len(well_formed_json)}/{len(malformed_json)}/{len(unexpected_fields)}"
    )


if __name__ == "__main__":
    main()
