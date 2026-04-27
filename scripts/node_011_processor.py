import csv
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT_DIR / "1000_rows_dataset.csv"
NODE_006_BASE = ROOT_DIR / "data" / "node-006" / "validation" / "structured"
NODE_007_BASE = ROOT_DIR / "data" / "node-007" / "validation" / "structured"
NODE_009_BASE = ROOT_DIR / "data" / "node-009" / "validation" / "structured"

NODE_011_BASE = ROOT_DIR / "data" / "node-011"
STRUCTURED_BASE = NODE_011_BASE / "validation" / "structured"
UNSTRUCTURED_BASE = NODE_011_BASE / "validation" / "unstructured"
REPORTS_DIR = NODE_011_BASE / "reports"

INPUT_DIR = STRUCTURED_BASE / "notification_input"
OUTPUT_DIR = STRUCTURED_BASE / "notification_output"
TEXT_DIR = UNSTRUCTURED_BASE / "notification_text_generation"


def ensure_dirs():
    paths = [
        INPUT_DIR / "complete_records",
        INPUT_DIR / "missing_values",
        INPUT_DIR / "invalid_format",
        OUTPUT_DIR / "valid_notification",
        OUTPUT_DIR / "missing_disclaimer",
        OUTPUT_DIR / "incorrect_type",
        TEXT_DIR / "clear_text",
        TEXT_DIR / "noisy_text",
        TEXT_DIR / "incomplete_text",
        REPORTS_DIR,
    ]
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def app_index(application_id: str) -> int:
    digits = "".join(ch for ch in str(application_id) if ch.isdigit())
    return int(digits) if digits else 0


def load_csv_by_app_id(path: Path) -> dict[str, dict]:
    data = {}
    if not path.exists():
        return data
    with path.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            app_id = row.get("application_id", "")
            if app_id:
                data[app_id] = row
    return data


def to_bool(value, default: bool = False) -> bool:
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


def to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_flags(value: str) -> list[str]:
    text = (value or "").strip()
    return [x for x in text.split("|") if x] if text else []


def load_node_006() -> dict[str, dict]:
    combined = {}
    files = [
        NODE_006_BASE / "severity_classification" / "critical_severity" / "high_severity.csv",
        NODE_006_BASE / "severity_classification" / "major_severity" / "medium_severity.csv",
        NODE_006_BASE / "severity_classification" / "minor_severity" / "low_severity.csv",
        NODE_006_BASE / "flag_aggregation" / "complete_records" / "no_flags.csv",
    ]
    for p in files:
        for app_id, row in load_csv_by_app_id(p).items():
            combined[app_id] = {
                "severity": row.get("severity", "NONE"),
                "flags": parse_flags(row.get("flags", "")),
            }
    return combined


def load_node_007() -> dict[str, float]:
    confidence = {}
    files = [
        NODE_007_BASE / "kyc_verification" / "complete_records" / "confidence_all.csv",
        NODE_007_BASE / "income_validation" / "complete_records" / "high_confidence.csv",
        NODE_007_BASE / "income_validation" / "imbalanced_classes" / "medium_confidence.csv",
        NODE_007_BASE / "discrepancy_analysis" / "high_severity" / "low_confidence.csv",
    ]
    for p in files:
        for app_id, row in load_csv_by_app_id(p).items():
            confidence[app_id] = to_float(row.get("confidence_score"), default=0.0)
    return confidence


def load_node_009() -> dict[str, dict]:
    hil = {}
    files = [
        NODE_009_BASE / "routing_decisions" / "critical_priority" / "high_priority.csv",
        NODE_009_BASE / "routing_decisions" / "urgent_priority" / "medium_priority.csv",
        NODE_009_BASE / "routing_decisions" / "standard_priority" / "low_priority.csv",
        NODE_009_BASE / "routing_decisions" / "no_hil_required" / "no_hil_required.csv",
    ]
    for p in files:
        for app_id, row in load_csv_by_app_id(p).items():
            priority = row.get("hil_priority")
            hil[app_id] = {
                "hil_required_flag": to_bool(row.get("hil_required_flag"), default=False),
                "hil_priority": priority if priority not in {"", "NONE", None} else None,
            }
    return hil


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def build_notification_text(notification_type: str, application_id: str, rejection_reason, hil_priority, missing_fields):
    if missing_fields:
        return (
            "Dear Customer,\n\n"
            f"Your application (ID: {application_id}) is incomplete.\n\n"
            "Please provide the following:\n"
            f"{', '.join(missing_fields)}\n\n"
            "This is a system-generated communication."
        )

    if notification_type == "REJECTION":
        reason_text = rejection_reason if rejection_reason else "Eligibility criteria not met"
        return (
            "Dear Customer,\n\n"
            f"Your loan application (ID: {application_id}) has been reviewed.\n\n"
            "We regret to inform you that your application has been declined due to:\n"
            f"{reason_text}\n\n"
            "You may reapply after addressing the above concerns.\n\n"
            "This is a system-generated communication."
        )
    if notification_type == "HIL_ESCALATION":
        return (
            "Dear Customer,\n\n"
            f"Your application (ID: {application_id}) is under review by our credit officer.\n\n"
            f"Priority level: {hil_priority}\n\n"
            "You will be notified once the review is completed.\n\n"
            "This is a system-generated communication."
        )
    return (
        "Dear Customer,\n\n"
        f"Your application (ID: {application_id}) is currently being processed.\n\n"
        "We will update you shortly.\n\n"
        "This is a system-generated communication."
    )


def main():
    ensure_dirs()

    node_006 = load_node_006()
    node_007 = load_node_007()
    node_009 = load_node_009()

    input_complete = []
    input_missing = []
    input_invalid = []

    output_valid = []
    output_missing_disclaimer = []
    output_incorrect_type = []

    text_clear = []
    text_noisy = []
    text_incomplete = []

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            application_id = row.get("application_id", "")
            idx = app_index(application_id)
            name = (row.get("name") or row.get("applicant_name") or "").strip()

            n006 = node_006.get(application_id, {"severity": "NONE", "flags": []})
            severity = n006.get("severity", "NONE")
            flags = n006.get("flags", [])
            confidence_score = node_007.get(application_id, 0.0)
            n009 = node_009.get(application_id, {"hil_required_flag": False, "hil_priority": None})
            hil_required_flag = n009.get("hil_required_flag", False)
            hil_priority = n009.get("hil_priority")

            bucket = idx % 10
            if bucket < 3:
                notification_type = "REJECTION"
            elif bucket < 6:
                notification_type = "MISSING_FIELDS"
            elif bucket < 8:
                notification_type = "HIL_ESCALATION"
            else:
                notification_type = "STATUS_UPDATE"

            if idx % 8 == 0:
                missing_fields = ["Income Proof"]
            elif idx % 6 == 0:
                missing_fields = ["PAN"]
            else:
                missing_fields = []

            rejection_reason = None
            if notification_type == "REJECTION":
                rejection_reason = ", ".join(flags) if flags else "Policy rules"
            if notification_type == "REJECTION" and not rejection_reason:
                rejection_reason = "Policy rules violation"

            if notification_type == "MISSING_FIELDS" and not missing_fields:
                missing_fields = ["Income Proof"]

            if notification_type == "HIL_ESCALATION":
                hil_required_flag = True

            # Structured input validation injections (type-aware)
            if notification_type == "REJECTION" and idx % 6 == 0:
                rejection_reason = None
            if notification_type == "MISSING_FIELDS" and idx % 4 == 0:
                missing_fields = []
            if notification_type == "HIL_ESCALATION" and idx % 7 == 0:
                hil_priority = None
            if idx % 3 == 0:
                if notification_type == "REJECTION":
                    rejection_reason = None
                elif notification_type == "MISSING_FIELDS":
                    missing_fields = []
                elif notification_type == "HIL_ESCALATION":
                    hil_priority = None
            if notification_type == "HIL_ESCALATION" and idx % 25 == 0:
                hil_priority = "CRITICAL_HIGH"

            # Normalize before classification.
            if hil_priority is None:
                pass
            elif hil_priority not in {"HIGH", "MEDIUM", "LOW", "CRITICAL_HIGH"}:
                hil_priority = "HIGH"

            if notification_type == "REJECTION" and not rejection_reason:
                rejection_reason = "Policy rules violation"

            if notification_type == "REJECTION":
                if rejection_reason is None:
                    input_bucket = "missing_values"
                elif hil_priority not in {"HIGH", "MEDIUM", "LOW", "CRITICAL_HIGH"} and hil_priority is not None:
                    input_bucket = "invalid_format"
                else:
                    input_bucket = "complete_records"
            elif notification_type == "MISSING_FIELDS":
                if not missing_fields:
                    input_bucket = "missing_values"
                elif hil_priority not in {"HIGH", "MEDIUM", "LOW", "CRITICAL_HIGH"} and hil_priority is not None:
                    input_bucket = "invalid_format"
                else:
                    input_bucket = "complete_records"
            elif notification_type == "HIL_ESCALATION":
                if hil_priority not in {"HIGH", "MEDIUM", "LOW", "CRITICAL_HIGH"}:
                    input_bucket = "invalid_format"
                else:
                    input_bucket = "complete_records"
            elif hil_priority not in {"HIGH", "MEDIUM", "LOW", "CRITICAL_HIGH"} and hil_priority is not None:
                input_bucket = "invalid_format"
            else:
                input_bucket = "complete_records"

            base_record = {
                "application_id": application_id,
                "name": name,
                "severity": severity,
                "flags": "|".join(flags),
                "confidence_score": round(confidence_score, 2),
                "hil_required_flag": hil_required_flag,
                "hil_priority": hil_priority,
                "notification_type": notification_type,
                "rejection_reason": rejection_reason,
                "missing_fields": json.dumps(missing_fields) if isinstance(missing_fields, list) else missing_fields,
            }

            if input_bucket == "missing_values":
                input_missing.append(base_record)
            elif input_bucket == "invalid_format":
                input_invalid.append(base_record)
            else:
                input_complete.append(base_record)

            text = build_notification_text(
                notification_type=notification_type,
                application_id=application_id,
                rejection_reason=rejection_reason,
                hil_priority=hil_priority,
                missing_fields=missing_fields if isinstance(missing_fields, list) else [],
            )

            incorrect_type = False
            notification_type_output = notification_type
            if idx % 11 == 0:
                incorrect_type = True
                if notification_type == "REJECTION":
                    notification_type_output = "STATUS_UPDATE"
                elif notification_type == "HIL_ESCALATION":
                    notification_type_output = "REJECTION"

            disclaimer_missing = False
            if idx % 10 == 0:
                disclaimer_missing = True
                text = text.replace("This is a system-generated communication.", "").strip()

            output_record = dict(base_record)
            output_record["notification_type_output"] = notification_type_output
            output_record["notification_text"] = text

            if disclaimer_missing:
                output_missing_disclaimer.append(output_record)
            elif incorrect_type:
                output_incorrect_type.append(output_record)
            else:
                output_valid.append(output_record)

            noisy = False
            incomplete = False
            text_quality_text = text

            if idx % 7 == 0:
                noisy = True
                text_quality_text += "\n\nPlease note that this is an important notification."
            elif idx % 9 == 0:
                incomplete = True
                text_quality_text = text_quality_text.replace("Please provide the following:\n", "")
                text_quality_text = text_quality_text.replace(
                    "We regret to inform you that your application has been declined due to:\n", ""
                )

            text_record = dict(output_record)
            text_record["notification_text"] = text_quality_text

            if noisy:
                text_noisy.append(text_record)
            elif incomplete:
                text_incomplete.append(text_record)
            else:
                text_clear.append(text_record)

    input_fields = [
        "application_id",
        "name",
        "severity",
        "flags",
        "confidence_score",
        "hil_required_flag",
        "hil_priority",
        "notification_type",
        "rejection_reason",
        "missing_fields",
    ]
    output_fields = input_fields + ["notification_type_output", "notification_text"]

    write_csv(INPUT_DIR / "complete_records" / "complete_records.csv", input_complete, input_fields)
    write_csv(INPUT_DIR / "missing_values" / "missing_values.csv", input_missing, input_fields)
    write_csv(INPUT_DIR / "invalid_format" / "invalid_format.csv", input_invalid, input_fields)

    write_csv(OUTPUT_DIR / "valid_notification" / "valid_notification.csv", output_valid, output_fields)
    write_csv(
        OUTPUT_DIR / "missing_disclaimer" / "missing_disclaimer.csv",
        output_missing_disclaimer,
        output_fields,
    )
    write_csv(OUTPUT_DIR / "incorrect_type" / "incorrect_type.csv", output_incorrect_type, output_fields)

    write_csv(TEXT_DIR / "clear_text" / "clear_text.csv", text_clear, output_fields)
    write_csv(TEXT_DIR / "noisy_text" / "noisy_text.csv", text_noisy, output_fields)
    write_csv(TEXT_DIR / "incomplete_text" / "incomplete_text.csv", text_incomplete, output_fields)

    total_records = len(input_complete) + len(input_missing) + len(input_invalid)
    error_rate = round(
        (
            len(input_missing)
            + len(input_invalid)
            + len(output_missing_disclaimer)
            + len(output_incorrect_type)
        )
        / (total_records * 2),
        4,
    ) if total_records else 0.0
    clarity_rate = round((len(text_clear) / total_records), 4) if total_records else 0.0

    # Internal exclusivity checks
    assert total_records == len(output_valid) + len(output_missing_disclaimer) + len(output_incorrect_type)
    assert total_records == len(text_clear) + len(text_noisy) + len(text_incomplete)

    summary = {
        "total_records": total_records,
        "distribution": {
            "input": {
                "complete_records": len(input_complete),
                "missing_values": len(input_missing),
                "invalid_format": len(input_invalid),
            },
            "output": {
                "valid_notification": len(output_valid),
                "missing_disclaimer": len(output_missing_disclaimer),
                "incorrect_type": len(output_incorrect_type),
            },
            "text_quality": {
                "clear_text": len(text_clear),
                "noisy_text": len(text_noisy),
                "incomplete_text": len(text_incomplete),
            },
        },
        "key_metrics": {
            "error_rate": error_rate,
            "clarity_rate": clarity_rate,
        },
    }

    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-011 notification engine processing complete.")
    print(f"Total records: {total_records}")
    print(
        f"Input complete/missing/invalid: {len(input_complete)}/{len(input_missing)}/{len(input_invalid)}"
    )
    print(
        f"Output valid/missing_disclaimer/incorrect_type: "
        f"{len(output_valid)}/{len(output_missing_disclaimer)}/{len(output_incorrect_type)}"
    )
    print(
        f"Text clear/noisy/incomplete: {len(text_clear)}/{len(text_noisy)}/{len(text_incomplete)}"
    )


if __name__ == "__main__":
    main()
