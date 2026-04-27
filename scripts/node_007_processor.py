import csv
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT_DIR / "1000_rows_dataset.csv"
NODE_006_BASE = (
    ROOT_DIR
    / "data"
    / "node-006"
    / "validation"
    / "structured"
)
OUTPUT_BASE = (
    ROOT_DIR
    / "data"
    / "node-007"
    / "validation"
    / "structured"
)
KYC_VERIFICATION_DIR = OUTPUT_BASE / "kyc_verification"
INCOME_VALIDATION_DIR = OUTPUT_BASE / "income_validation"
DISCREPANCY_ANALYSIS_DIR = OUTPUT_BASE / "discrepancy_analysis"
UNSTRUCTURED_DIR = ROOT_DIR / "data" / "node-007" / "validation" / "unstructured"
REPORTS_DIR = ROOT_DIR / "data" / "node-007" / "reports"


FLAG_PENALTIES = {
    "DEFAULT_HISTORY": 25,
    "HIGH_DTI": 20,
    "LOW_CREDIT_SCORE": 15,
    "INCOME_MISMATCH": 10,
    "HIGH_ENQUIRIES": 8,
    "BANK_RISK": 8,
    "MEDIUM_DTI": 5,
}


def to_bool(value: str) -> bool:
    if value is None:
        return False
    return str(value).strip().upper() in {"TRUE", "1", "YES", "Y"}


def to_float(value: str, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except ValueError:
        return default


def ensure_dirs():
    paths = [
        KYC_VERIFICATION_DIR / "complete_records",
        KYC_VERIFICATION_DIR / "missing_values",
        KYC_VERIFICATION_DIR / "outliers",
        INCOME_VALIDATION_DIR / "complete_records",
        INCOME_VALIDATION_DIR / "missing_values",
        INCOME_VALIDATION_DIR / "imbalanced_classes",
        DISCREPANCY_ANALYSIS_DIR / "complete_records",
        DISCREPANCY_ANALYSIS_DIR / "missing_values",
        DISCREPANCY_ANALYSIS_DIR / "high_severity",
        UNSTRUCTURED_DIR,
        REPORTS_DIR,
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def load_node_006_flags() -> dict[str, list[str]]:
    app_flags: dict[str, list[str]] = {}
    csv_paths = [
        NODE_006_BASE / "severity_classification" / "critical_severity" / "high_severity.csv",
        NODE_006_BASE / "severity_classification" / "major_severity" / "medium_severity.csv",
        NODE_006_BASE / "severity_classification" / "minor_severity" / "low_severity.csv",
        NODE_006_BASE / "flag_aggregation" / "complete_records" / "no_flags.csv",
    ]

    for csv_path in csv_paths:
        if not csv_path.exists():
            continue

        with csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                app_id = row.get("application_id", "")
                flags_text = row.get("flags", "").strip()
                flags = [flag for flag in flags_text.split("|") if flag] if flags_text else []
                app_flags[app_id] = flags

    return app_flags


def compute_score(row: dict, flags: list[str]) -> tuple[float, str]:
    base_score = 100.0

    flag_penalty = sum(FLAG_PENALTIES.get(flag, 0) for flag in flags)

    ocr_confidence_score = to_float(row.get("ocr_confidence_score"), default=0.0)
    ocr_penalty = (100.0 - ocr_confidence_score) * 0.15

    consistency_penalty = 0.0
    if not to_bool(row.get("data_consistency_flag")):
        consistency_penalty += 10.0
    if not to_bool(row.get("document_consistency_flag")):
        consistency_penalty += 8.0

    total_penalty = flag_penalty + ocr_penalty + consistency_penalty
    total_penalty = min(total_penalty, 70.0)

    confidence_score = base_score - total_penalty
    confidence_score = max(0.0, min(100.0, confidence_score))

    if confidence_score >= 80:
        confidence_level = "HIGH"
    elif confidence_score >= 60:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "LOW"

    return round(confidence_score, 2), confidence_level


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ensure_dirs()
    node_006_flags = load_node_006_flags()

    high_rows: list[dict] = []
    medium_rows: list[dict] = []
    low_rows: list[dict] = []
    all_rows: list[dict] = []

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            app_id = row.get("application_id", "")
            flags = node_006_flags.get(app_id, [])
            confidence_score, confidence_level = compute_score(row, flags)

            out_row = {
                "application_id": app_id,
                "data_consistency_flag": row.get("data_consistency_flag", ""),
                "document_consistency_flag": row.get("document_consistency_flag", ""),
                "ocr_confidence_score": row.get("ocr_confidence_score", ""),
                "flags": "|".join(flags),
                "confidence_score": confidence_score,
                "confidence_level": confidence_level,
            }
            all_rows.append(out_row)

            if confidence_level == "HIGH":
                high_rows.append(out_row)
            elif confidence_level == "MEDIUM":
                medium_rows.append(out_row)
            else:
                low_rows.append(out_row)

    fieldnames = [
        "application_id",
        "data_consistency_flag",
        "document_consistency_flag",
        "ocr_confidence_score",
        "flags",
        "confidence_score",
        "confidence_level",
    ]

    write_csv(KYC_VERIFICATION_DIR / "complete_records" / "confidence_all.csv", all_rows, fieldnames)
    write_csv(INCOME_VALIDATION_DIR / "complete_records" / "high_confidence.csv", high_rows, fieldnames)
    write_csv(INCOME_VALIDATION_DIR / "imbalanced_classes" / "medium_confidence.csv", medium_rows, fieldnames)
    write_csv(DISCREPANCY_ANALYSIS_DIR / "high_severity" / "low_confidence.csv", low_rows, fieldnames)

    total = len(all_rows) if all_rows else 1
    high_pct = round((len(high_rows) / total) * 100, 2)
    medium_pct = round((len(medium_rows) / total) * 100, 2)
    low_pct = round((len(low_rows) / total) * 100, 2)
    high_rate = round(len(high_rows) / total, 4)
    medium_rate = round(len(medium_rows) / total, 4)
    low_rate = round(len(low_rows) / total, 4)

    print("Node-007 confidence scoring complete (data folder only).")
    print(f"Total rows: {len(all_rows)}")
    print(f"HIGH: {len(high_rows)} ({high_pct}%)")
    print(f"MEDIUM: {len(medium_rows)} ({medium_pct}%)")
    print(f"LOW: {len(low_rows)} ({low_pct}%)")

    summary = {
        "total_records": len(all_rows),
        "distribution": {
            "high_confidence": len(high_rows),
            "medium_confidence": len(medium_rows),
            "low_confidence": len(low_rows),
        },
        "key_metrics": {
            "high_confidence_pct": high_rate,
            "medium_confidence_pct": medium_rate,
            "low_confidence_pct": low_rate,
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
