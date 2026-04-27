import csv
import json
from datetime import datetime, timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
NODE_013_TIMELINE = (
    ROOT_DIR
    / "data"
    / "node-013"
    / "validation"
    / "structured"
    / "explainability_sections"
    / "detailed_action_log"
    / "all_timelines.json"
)
NODE_009_BASE = ROOT_DIR / "data" / "node-009" / "validation" / "structured" / "routing_decisions"
NODE_012_BASE = ROOT_DIR / "data" / "node-012" / "validation" / "structured"

NODE_014_BASE = ROOT_DIR / "data" / "node-014"
AUDIT_DIR = NODE_014_BASE / "validation" / "structured" / "audit_log_entries"
REPORTS_DIR = NODE_014_BASE / "reports"


def ensure_dirs():
    paths = [
        AUDIT_DIR / "complete_records",
        AUDIT_DIR / "missing_values",
        AUDIT_DIR / "outliers",
        AUDIT_DIR / "imbalanced_classes",
        AUDIT_DIR / "duplicate_entries",
        REPORTS_DIR,
    ]
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def app_index(application_id: str) -> int:
    digits = "".join(ch for ch in str(application_id) if ch.isdigit())
    return int(digits) if digits else 0


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


def to_bool(value, default=False):
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


def to_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def merge_sources(paths: list[Path]) -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for p in paths:
        merged.update(load_csv_by_app_id(p))
    return merged


def to_number(value):
    if value is None:
        return None
    val = to_float(value, default=None)
    if val is None:
        return None
    return int(val) if val.is_integer() else round(val, 4)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ensure_dirs()

    if not NODE_013_TIMELINE.exists():
        raise FileNotFoundError(f"Missing Node-013 timeline file: {NODE_013_TIMELINE}")

    timeline_data = json.loads(NODE_013_TIMELINE.read_text(encoding="utf-8"))

    node_009 = merge_sources(
        [
            NODE_009_BASE / "critical_priority" / "high_priority.csv",
            NODE_009_BASE / "urgent_priority" / "medium_priority.csv",
            NODE_009_BASE / "standard_priority" / "low_priority.csv",
            NODE_009_BASE / "no_hil_required" / "no_hil_required.csv",
        ]
    )
    node_012 = merge_sources(
        [
            NODE_012_BASE / "loan_product_eligibility" / "complete_records" / "complete_records.csv",
            NODE_012_BASE / "loan_product_eligibility" / "imbalanced_classes" / "imbalanced_classes.csv",
            NODE_012_BASE / "loan_product_eligibility" / "outliers" / "outliers.csv",
        ]
    )
    node_012_emi = merge_sources(
        [
            NODE_012_BASE / "emi_estimation" / "complete_records" / "complete_records.csv",
            NODE_012_BASE / "emi_estimation" / "missing_values" / "missing_values.csv",
            NODE_012_BASE / "emi_estimation" / "outliers" / "outliers.csv",
        ]
    )

    complete_records = []
    missing_values = []
    outliers = []
    imbalanced_classes = []
    duplicate_entries = []
    all_events = []

    base_time = datetime(2026, 1, 1, 0, 0, 0)
    app_timestamps: dict[str, list[datetime]] = {}

    for app_row in timeline_data:
        application_id = app_row.get("application_id", "")
        idx = app_index(application_id)

        timeline = app_row.get("timeline", [])
        severity = app_row.get("severity")
        confidence_score = app_row.get("confidence_score")

        n009 = node_009.get(application_id, {})
        hil_flag = to_bool(n009.get("hil_required_flag"), default=to_bool(app_row.get("hil_required_flag"), False))
        hil_priority = n009.get("hil_priority") if n009.get("hil_priority") not in {"", "NONE"} else app_row.get("hil_priority")

        n012 = node_012.get(application_id, {})
        n012_emi = node_012_emi.get(application_id, {})
        risk_category = n012.get("risk_category")
        product = n012.get("loan_product")
        emi_estimate = to_number(n012_emi.get("emi_estimate"))

        app_base_ts = base_time + timedelta(seconds=idx * 60)
        app_timestamps.setdefault(application_id, [])

        duplicated_for_app = False
        for step_index, step in enumerate(timeline):
            event_type = step.get("step")
            status = step.get("status")
            tool = step.get("tool")
            details = step.get("details")

            actor = "SYSTEM"
            imbalanced_flag = False

            timestamp = app_base_ts + timedelta(seconds=step_index * 5)

            # Injections for validation buckets.
            if idx % 19 == 0:
                timestamp = timestamp + timedelta(seconds=10**6)

            app_num = app_index(application_id)
            if event_type != "HIL_DECISION":
                if (app_num + step_index) % 3 == 0:
                    actor = "SYSTEM"
                    imbalanced_flag = True
                else:
                    imbalanced_flag = False
            if event_type == "HIL_DECISION":
                actor = "HUMAN"

            missing_flag = False
            if idx % 17 == 0:
                details = None
                missing_flag = True

            outlier_flag = idx % 19 == 0
            duplicate_flag = idx % 23 == 0
            # imbalanced_flag determined by event-level skew above.

            metadata = {
                "severity": severity,
                "confidence_score": confidence_score,
                "risk_category": risk_category,
                "hil_flag": hil_flag,
                "hil_priority": hil_priority,
                "loan_product": product,
                "emi_estimate": emi_estimate,
            }

            event_payload = {
                "application_id": application_id,
                "event_id": f"{application_id}_{step_index}",
                "timestamp": timestamp.isoformat(),
                "actor": actor,
                "event_type": event_type,
                "status": status,
                "tool": tool,
                "details": details,
                "metadata": metadata,
            }

            # Priority: missing > outliers > duplicate > imbalanced > complete
            if missing_flag:
                bucket = "missing_values"
            elif outlier_flag:
                bucket = "outliers"
            elif duplicate_flag and duplicated_for_app:
                bucket = "duplicate_entries"
            elif imbalanced_flag:
                bucket = "imbalanced_classes"
            else:
                bucket = "complete_records"

            if bucket == "missing_values":
                missing_values.append(event_payload)
            elif bucket == "outliers":
                outliers.append(event_payload)
            elif bucket == "duplicate_entries":
                duplicate_entries.append(event_payload)
            elif bucket == "imbalanced_classes":
                imbalanced_classes.append(event_payload)
            else:
                complete_records.append(event_payload)

            all_events.append(event_payload)
            app_timestamps[application_id].append(timestamp)

            # Inject exactly one duplicate entry per app (exact copy).
            if duplicate_flag and not duplicated_for_app:
                duplicate_copy = dict(event_payload)
                duplicate_entries.append(duplicate_copy)
                all_events.append(duplicate_copy)
                app_timestamps[application_id].append(timestamp)
                duplicated_for_app = True

    # Validation checks requested.
    for app_id, stamps in app_timestamps.items():
        ordered = all(stamps[i] <= stamps[i + 1] for i in range(len(stamps) - 1))
        if not ordered:
            raise AssertionError(f"Timestamps not ordered for {app_id}")

    for event in all_events:
        if event["event_type"] == "HIL_DECISION" and event["actor"] != "HUMAN":
            raise AssertionError(f"HIL actor mismatch in {event['event_id']}")

    # Duplicate entries should be exact copies by construction.
    # Check at least one duplicate app exists when condition applies.
    if not duplicate_entries:
        raise AssertionError("Expected duplicate entries, found none.")

    fieldnames = [
        "application_id",
        "event_id",
        "timestamp",
        "actor",
        "event_type",
        "status",
        "tool",
        "details",
        "metadata",
    ]

    def serialize(rows: list[dict]) -> list[dict]:
        out = []
        for r in rows:
            x = dict(r)
            x["metadata"] = json.dumps(x["metadata"], ensure_ascii=True)
            out.append(x)
        return out

    write_csv(AUDIT_DIR / "complete_records" / "complete_records.csv", serialize(complete_records), fieldnames)
    write_csv(AUDIT_DIR / "missing_values" / "missing_values.csv", serialize(missing_values), fieldnames)
    write_csv(AUDIT_DIR / "outliers" / "outliers.csv", serialize(outliers), fieldnames)
    write_csv(
        AUDIT_DIR / "imbalanced_classes" / "imbalanced_classes.csv",
        serialize(imbalanced_classes),
        fieldnames,
    )
    write_csv(
        AUDIT_DIR / "duplicate_entries" / "duplicate_entries.csv",
        serialize(duplicate_entries),
        fieldnames,
    )

    total_records = len(all_events)
    human_action_rate = round(
        sum(1 for e in all_events if e["actor"] == "HUMAN") / total_records, 4
    ) if total_records else 0.0
    duplicate_rate = round(len(duplicate_entries) / total_records, 4) if total_records else 0.0
    missing_rate = round(len(missing_values) / total_records, 4) if total_records else 0.0

    summary = {
        "total_records": total_records,
        "distribution": {
            "complete": len(complete_records),
            "missing": len(missing_values),
            "outliers": len(outliers),
            "imbalanced": len(imbalanced_classes),
            "duplicates": len(duplicate_entries),
        },
        "key_metrics": {
            "human_action_rate": human_action_rate,
            "duplicate_rate": duplicate_rate,
            "missing_rate": missing_rate,
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-014 audit log generation complete.")
    print(f"Total audit events: {total_records}")
    print(
        "complete/missing/outliers/imbalanced/duplicates: "
        f"{len(complete_records)}/{len(missing_values)}/{len(outliers)}/"
        f"{len(imbalanced_classes)}/{len(duplicate_entries)}"
    )


if __name__ == "__main__":
    main()
