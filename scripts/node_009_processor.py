import csv
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_CSV = ROOT_DIR / "1000_rows_dataset.csv"
NODE_006_BASE = (
    ROOT_DIR
    / "data"
    / "node-006"
    / "validation"
    / "structured"
)
NODE_007_BASE = (
    ROOT_DIR
    / "data"
    / "node-007"
    / "validation"
    / "structured"
)
OUTPUT_BASE = (
    ROOT_DIR
    / "data"
    / "node-009"
    / "validation"
    / "structured"
)
ROUTING_DECISIONS_DIR = OUTPUT_BASE / "routing_decisions"
UNSTRUCTURED_DIR = ROOT_DIR / "data" / "node-009" / "validation" / "unstructured"
REPORTS_DIR = ROOT_DIR / "data" / "node-009" / "reports"


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
        ROUTING_DECISIONS_DIR / "critical_priority",
        ROUTING_DECISIONS_DIR / "urgent_priority",
        ROUTING_DECISIONS_DIR / "standard_priority",
        ROUTING_DECISIONS_DIR / "no_hil_required",
        ROUTING_DECISIONS_DIR / "complete_records",
        ROUTING_DECISIONS_DIR / "missing_values",
        ROUTING_DECISIONS_DIR / "outliers",
        UNSTRUCTURED_DIR,
        REPORTS_DIR,
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def load_csv_by_app_id(path: Path) -> dict[str, dict]:
    records = {}
    if not path.exists():
        return records
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            app_id = row.get("application_id", "")
            if app_id:
                records[app_id] = row
    return records


def load_node_006_severity() -> dict[str, str]:
    severity_map: dict[str, str] = {}
    files = [
        NODE_006_BASE / "severity_classification" / "critical_severity" / "high_severity.csv",
        NODE_006_BASE / "severity_classification" / "major_severity" / "medium_severity.csv",
        NODE_006_BASE / "severity_classification" / "minor_severity" / "low_severity.csv",
        NODE_006_BASE / "flag_aggregation" / "complete_records" / "no_flags.csv",
    ]
    for path in files:
        for app_id, row in load_csv_by_app_id(path).items():
            severity_map[app_id] = row.get("severity", "NONE")
    return severity_map


def load_node_007_confidence() -> dict[str, float]:
    confidence_map: dict[str, float] = {}
    files = [
        NODE_007_BASE / "kyc_verification" / "complete_records" / "confidence_all.csv",
        NODE_007_BASE / "income_validation" / "complete_records" / "high_confidence.csv",
        NODE_007_BASE / "income_validation" / "imbalanced_classes" / "medium_confidence.csv",
        NODE_007_BASE / "discrepancy_analysis" / "high_severity" / "low_confidence.csv",
    ]
    for path in files:
        for app_id, row in load_csv_by_app_id(path).items():
            confidence_map[app_id] = to_float(row.get("confidence_score"), default=0.0)
    return confidence_map


def derive_hil_fields(severity: str, confidence_score: float, decision: str):
    decision_upper = (decision or "").strip().upper()

    if severity == "HIGH":
        hil_required = True
    elif confidence_score < 60.0:
        hil_required = True
    elif decision_upper == "REVIEW" and confidence_score < 75.0:
        hil_required = True
    else:
        hil_required = False

    if not hil_required:
        hil_priority = None
    else:
        if severity == "HIGH" and confidence_score < 65.0:
            hil_priority = "HIGH"
        elif severity == "HIGH" or confidence_score < 60.0:
            hil_priority = "MEDIUM"
        else:
            hil_priority = "LOW"

    if severity == "HIGH" and confidence_score < 60.0:
        hil_reason = "High risk with low confidence"
    elif severity == "HIGH":
        hil_reason = "High risk detected"
    elif confidence_score < 60.0:
        hil_reason = "Low confidence in data"
    elif decision_upper == "REVIEW":
        hil_reason = "Requires manual verification"
    else:
        hil_reason = "Routine validation"

    return hil_required, hil_priority, hil_reason


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ensure_dirs()

    severity_map = load_node_006_severity()
    confidence_map = load_node_007_confidence()

    high_rows: list[dict] = []
    medium_rows: list[dict] = []
    low_rows: list[dict] = []
    no_hil_rows: list[dict] = []
    all_rows: list[dict] = []

    with DATASET_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            app_id = row.get("application_id", "")
            decision = row.get("decision", "")
            severity = severity_map.get(app_id, "NONE")
            confidence_score = confidence_map.get(app_id, 100.0)

            hil_required, hil_priority, hil_reason = derive_hil_fields(
                severity=severity,
                confidence_score=confidence_score,
                decision=decision,
            )

            out_row = {
                "application_id": app_id,
                "severity": severity,
                "confidence_score": round(confidence_score, 2),
                "decision": decision,
                "hil_required_flag": hil_required,
                "hil_completed_flag": True,
                "hil_priority": hil_priority,
                "hil_reason": hil_reason,
            }
            all_rows.append(out_row)

            if not hil_required:
                no_hil_rows.append(out_row)
            elif hil_priority == "HIGH":
                high_rows.append(out_row)
            elif hil_priority == "MEDIUM":
                medium_rows.append(out_row)
            else:
                low_rows.append(out_row)

    fieldnames = [
        "application_id",
        "severity",
        "confidence_score",
        "decision",
        "hil_required_flag",
        "hil_completed_flag",
        "hil_priority",
        "hil_reason",
    ]

    write_csv(ROUTING_DECISIONS_DIR / "critical_priority" / "high_priority.csv", high_rows, fieldnames)
    write_csv(ROUTING_DECISIONS_DIR / "urgent_priority" / "medium_priority.csv", medium_rows, fieldnames)
    write_csv(ROUTING_DECISIONS_DIR / "standard_priority" / "low_priority.csv", low_rows, fieldnames)
    write_csv(ROUTING_DECISIONS_DIR / "no_hil_required" / "no_hil_required.csv", no_hil_rows, fieldnames)

    total = len(all_rows) if all_rows else 1
    hil_required_count = len(high_rows) + len(medium_rows) + len(low_rows)
    hil_required_pct = round((hil_required_count / total) * 100, 2)
    high_pct = round((len(high_rows) / total) * 100, 2)
    medium_pct = round((len(medium_rows) / total) * 100, 2)
    low_pct = round((len(low_rows) / total) * 100, 2)
    hil_required_rate = round(hil_required_count / total, 4)
    high_rate = round(len(high_rows) / total, 4)
    medium_rate = round(len(medium_rows) / total, 4)
    low_rate = round(len(low_rows) / total, 4)

    print("Node-009 HIL decision processing complete (data folder only).")
    print(f"Total rows: {len(all_rows)}")
    print(f"HIL required: {hil_required_count} ({hil_required_pct}%)")
    print(f"High priority: {len(high_rows)} ({high_pct}%)")
    print(f"Medium priority: {len(medium_rows)} ({medium_pct}%)")
    print(f"Low priority: {len(low_rows)} ({low_pct}%)")
    print(f"No HIL required: {len(no_hil_rows)} ({round((len(no_hil_rows)/total)*100, 2)}%)")

    summary = {
        "total_records": len(all_rows),
        "distribution": {
            "hil_required": hil_required_count,
            "no_hil_required": len(no_hil_rows),
            "high_priority": len(high_rows),
            "medium_priority": len(medium_rows),
            "low_priority": len(low_rows),
        },
        "key_metrics": {
            "hil_required_pct": hil_required_rate,
            "high_priority_pct": high_rate,
            "medium_priority_pct": medium_rate,
            "low_priority_pct": low_rate,
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
