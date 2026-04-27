import csv
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT_DIR / "1000_rows_dataset.csv"
OUTPUT_BASE = (
    ROOT_DIR
    / "data"
    / "node-005"
    / "validation"
    / "structured"
)
INCOME_VALIDATION_DIR = OUTPUT_BASE / "income_validation"
MISMATCH_DETECTION_DIR = OUTPUT_BASE / "mismatch_detection"
UNSTRUCTURED_DIR = ROOT_DIR / "data" / "node-005" / "validation" / "unstructured"
REPORTS_DIR = ROOT_DIR / "data" / "node-005" / "reports"


def parse_float(value: str):
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def ensure_dirs():
    paths = [
        INCOME_VALIDATION_DIR / "complete_records",
        INCOME_VALIDATION_DIR / "missing_values",
        INCOME_VALIDATION_DIR / "outliers",
        MISMATCH_DETECTION_DIR / "within_tolerance",
        MISMATCH_DETECTION_DIR / "low_mismatch",
        MISMATCH_DETECTION_DIR / "high_mismatch",
        MISMATCH_DETECTION_DIR / "complete_records",
        MISMATCH_DETECTION_DIR / "missing_values",
        MISMATCH_DETECTION_DIR / "outliers",
        UNSTRUCTURED_DIR,
        REPORTS_DIR,
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def transform_row(row: dict):
    declared_income = parse_float(row.get("declared_income"))
    documented_income = parse_float(row.get("verified_income"))

    mismatch_percentage = None
    validation_status = None
    if (
        declared_income is not None
        and documented_income is not None
        and declared_income != 0
    ):
        mismatch_percentage = abs(declared_income - documented_income) / declared_income
        validation_status = "PASS" if mismatch_percentage <= 0.10 else "FAIL"

    return {
        "application_id": row.get("application_id", ""),
        "declared_income": (
            int(declared_income) if declared_income is not None and declared_income.is_integer() else declared_income
        ),
        "documented_income": (
            int(documented_income)
            if documented_income is not None and documented_income.is_integer()
            else documented_income
        ),
        "mismatch_percentage": mismatch_percentage,
        "validation_status": validation_status,
    }


def write_csv(path: Path, rows: list, fieldnames: list):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ensure_dirs()

    all_transformed = []
    complete_records = []
    missing_values = []
    outliers = []
    within_tolerance = []
    low_mismatch = []
    high_mismatch = []

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transformed = transform_row(row)
            all_transformed.append(transformed)

            declared = transformed["declared_income"]
            documented = transformed["documented_income"]
            mismatch = transformed["mismatch_percentage"]

            if declared is not None and documented is not None:
                complete_records.append(transformed)
            else:
                missing_values.append(transformed)

            if declared is not None and documented is not None and declared != 0:
                ratio = documented / declared
                if ratio > 3 or ratio < 0.3:
                    outliers.append(transformed)

            if mismatch is not None:
                if mismatch <= 0.10:
                    within_tolerance.append(transformed)
                elif mismatch <= 0.25:
                    low_mismatch.append(transformed)
                else:
                    high_mismatch.append(transformed)

    fieldnames = [
        "application_id",
        "declared_income",
        "documented_income",
        "mismatch_percentage",
        "validation_status",
    ]

    write_csv(INCOME_VALIDATION_DIR / "complete_records" / "complete_records.csv", complete_records, fieldnames)
    write_csv(INCOME_VALIDATION_DIR / "missing_values" / "missing_values.csv", missing_values, fieldnames)
    write_csv(INCOME_VALIDATION_DIR / "outliers" / "outliers.csv", outliers, fieldnames)
    write_csv(
        MISMATCH_DETECTION_DIR / "within_tolerance" / "within_tolerance.csv",
        within_tolerance,
        fieldnames,
    )
    write_csv(
        MISMATCH_DETECTION_DIR / "low_mismatch" / "low_mismatch.csv",
        low_mismatch,
        fieldnames,
    )
    write_csv(
        MISMATCH_DETECTION_DIR / "high_mismatch" / "high_mismatch.csv",
        high_mismatch,
        fieldnames,
    )

    summary = {
        "total_records": len(all_transformed),
        "distribution": {
            "complete_records": len(complete_records),
            "missing_values": len(missing_values),
            "outliers": len(outliers),
        },
        "key_metrics": {
            "within_tolerance": len(within_tolerance),
            "low_mismatch": len(low_mismatch),
            "high_mismatch": len(high_mismatch),
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-005 income validation processing complete.")
    print(f"Total rows: {len(all_transformed)}")
    print(f"Complete records: {len(complete_records)}")
    print(f"Missing values: {len(missing_values)}")
    print(f"Outliers: {len(outliers)}")
    print(f"Within tolerance (<=10%): {len(within_tolerance)}")
    print(f"Low mismatch (>10% and <=25%): {len(low_mismatch)}")
    print(f"High mismatch (>25%): {len(high_mismatch)}")


if __name__ == "__main__":
    main()
