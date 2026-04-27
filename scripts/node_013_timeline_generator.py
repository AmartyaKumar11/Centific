import ast
import csv
import hashlib
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
NODE_009_BASE = (
    ROOT_DIR
    / "data"
    / "node-009"
    / "validation"
    / "structured"
)
OUTPUT_BASE = (
    ROOT_DIR
    / "data"
    / "node-013"
    / "validation"
    / "structured"
)
APPLICATION_DATA_DIR = OUTPUT_BASE / "application_data"
ASSESSMENT_OUTCOMES_DIR = OUTPUT_BASE / "assessment_outcomes"
EXPLAINABILITY_SECTIONS_DIR = OUTPUT_BASE / "explainability_sections"
DETAILED_ACTION_LOG_DIR = EXPLAINABILITY_SECTIONS_DIR / "detailed_action_log"
UNSTRUCTURED_DIR = ROOT_DIR / "data" / "node-013" / "validation" / "unstructured"
REPORTS_DIR = ROOT_DIR / "data" / "node-013" / "reports"


def to_float(value: str, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


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


def ensure_dirs():
    paths = [
        APPLICATION_DATA_DIR / "complete_records",
        APPLICATION_DATA_DIR / "missing_values",
        APPLICATION_DATA_DIR / "outliers",
        ASSESSMENT_OUTCOMES_DIR / "high_confidence",
        ASSESSMENT_OUTCOMES_DIR / "low_confidence",
        ASSESSMENT_OUTCOMES_DIR / "discrepancies_present",
        EXPLAINABILITY_SECTIONS_DIR / "complete_explainability",
        EXPLAINABILITY_SECTIONS_DIR / "incomplete_explainability",
        DETAILED_ACTION_LOG_DIR / "high_risk_cases",
        DETAILED_ACTION_LOG_DIR / "medium_risk_cases",
        DETAILED_ACTION_LOG_DIR / "low_risk_cases",
        UNSTRUCTURED_DIR,
        REPORTS_DIR,
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def load_csv_by_app_id(path: Path) -> dict[str, dict]:
    output: dict[str, dict] = {}
    if not path.exists():
        return output
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            app_id = row.get("application_id", "")
            if app_id:
                output[app_id] = row
    return output


def parse_flags(raw_flags: str) -> list[str]:
    if raw_flags is None:
        return []
    text = str(raw_flags).strip()
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (ValueError, SyntaxError):
        pass
    return [flag.strip() for flag in text.split("|") if flag.strip()]


def load_node_006_data() -> dict[str, dict]:
    combined: dict[str, dict] = {}
    files = [
        NODE_006_BASE / "severity_classification" / "critical_severity" / "high_severity.csv",
        NODE_006_BASE / "severity_classification" / "major_severity" / "medium_severity.csv",
        NODE_006_BASE / "severity_classification" / "minor_severity" / "low_severity.csv",
        NODE_006_BASE / "flag_aggregation" / "complete_records" / "no_flags.csv",
    ]
    for path in files:
        for app_id, row in load_csv_by_app_id(path).items():
            combined[app_id] = {
                "severity": row.get("severity", "NONE"),
                "flags": parse_flags(row.get("flags", "")),
            }
    return combined


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
            confidence_map[app_id] = to_float(row.get("confidence_score"), default=100.0)
    return confidence_map


def load_node_009_hil() -> dict[str, dict]:
    hil_map: dict[str, dict] = {}
    files = [
        NODE_009_BASE / "routing_decisions" / "critical_priority" / "high_priority.csv",
        NODE_009_BASE / "routing_decisions" / "urgent_priority" / "medium_priority.csv",
        NODE_009_BASE / "routing_decisions" / "standard_priority" / "low_priority.csv",
        NODE_009_BASE / "routing_decisions" / "no_hil_required" / "no_hil_required.csv",
    ]
    for path in files:
        for app_id, row in load_csv_by_app_id(path).items():
            priority_raw = row.get("hil_priority")
            hil_map[app_id] = {
                "hil_required_flag": to_bool(row.get("hil_required_flag"), default=False),
                "hil_priority": priority_raw if priority_raw not in {"", "NONE", None} else None,
            }
    return hil_map


def step_status_kyc(data_consistency_flag: str) -> str:
    return "VERIFIED" if to_bool(data_consistency_flag, default=False) else "WARNING"


def step_status_credit(cibil_score: float) -> str:
    if cibil_score >= 700:
        return "CLEAN"
    return "WARNING"


def step_status_income(income_mismatch_flag: str) -> str:
    return "MISMATCH" if to_bool(income_mismatch_flag, default=False) else "MATCH"


def step_status_discrepancy(severity: str) -> str:
    if severity == "HIGH":
        return "HIGH"
    if severity == "MEDIUM":
        return "MEDIUM"
    if severity == "LOW":
        return "LOW"
    return "NONE"


def step_status_confidence(confidence_score: float) -> str:
    if confidence_score < 60:
        return "LOW"
    if confidence_score < 75:
        return "MEDIUM"
    return "HIGH"


def step_status_hil(hil_required: bool) -> str:
    return "REQUIRED" if hil_required else "NOT_REQUIRED"


def deterministic_latency_ms(application_id: str, step_name: str) -> int:
    seed = f"{application_id}:{step_name}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()
    value = int(digest[:8], 16)
    return 50 + (value % 151)


def categorize_by_severity(severity: str) -> str:
    if severity == "HIGH":
        return "high_risk_cases"
    if severity == "MEDIUM":
        return "medium_risk_cases"
    return "low_risk_cases"


def build_timeline_record(
    application_id: str,
    cibil_score: float,
    data_consistency_flag: str,
    income_mismatch_flag: str,
    flags: list[str],
    severity: str,
    confidence_score: float,
    hil_required: bool,
    hil_priority,
) -> dict:
    kyc_status = step_status_kyc(data_consistency_flag)
    credit_status = step_status_credit(cibil_score)
    income_status = step_status_income(income_mismatch_flag)
    discrepancy_status = step_status_discrepancy(severity)
    confidence_status = step_status_confidence(confidence_score)
    hil_status = step_status_hil(hil_required)

    key_reasons: list[str] = []
    for flag in flags:
        if flag and flag not in key_reasons:
            key_reasons.append(flag)

    if confidence_score < 60:
        conf_reason = "LOW_CONFIDENCE"
    elif confidence_score < 75:
        conf_reason = "MEDIUM_CONFIDENCE"
    else:
        conf_reason = "HIGH_CONFIDENCE"
    if conf_reason not in key_reasons:
        key_reasons.append(conf_reason)
    key_reasons = key_reasons[:4]

    timeline = [
        {
            "step": "INGESTION",
            "status": "VERIFIED",
            "tool": "dataset_loader",
            "api_simulated": True,
            "latency_ms": deterministic_latency_ms(application_id, "INGESTION"),
            "status_code": 200,
            "triggered_by": None,
            "impact": "Provides normalized inputs for KYC verification and downstream checks.",
            "reasoning": {
                "inputs": {
                    "application_id": application_id,
                },
                "thresholds": {
                    "record_presence": "required",
                },
                "computed_output": {
                    "ingestion_complete": True,
                },
                "decision": "Ingestion successful; continue to KYC verification.",
            },
        },
        {
            "step": "KYC_VERIFICATION",
            "status": kyc_status,
            "tool": "kyc_validator",
            "api_simulated": True,
            "latency_ms": deterministic_latency_ms(application_id, "KYC_VERIFICATION"),
            "status_code": 200,
            "triggered_by": "INGESTION",
            "impact": "Determines reliability of applicant identity data for credit and income checks.",
            "reasoning": {
                "inputs": {
                    "data_consistency_flag": data_consistency_flag,
                },
                "thresholds": {
                    "expected_consistency": True,
                },
                "computed_output": {
                    "is_consistent": to_bool(data_consistency_flag, default=False),
                    "status": kyc_status,
                },
                "decision": (
                    "KYC consistency verified."
                    if kyc_status == "VERIFIED"
                    else "KYC inconsistency detected; mark for caution."
                ),
            },
        },
        {
            "step": "CREDIT_BUREAU",
            "status": credit_status,
            "tool": "credit_bureau_lookup",
            "api_simulated": True,
            "latency_ms": deterministic_latency_ms(application_id, "CREDIT_BUREAU"),
            "status_code": 200,
            "triggered_by": "KYC_VERIFICATION",
            "impact": "Feeds credit risk signal into discrepancy and confidence evaluations.",
            "reasoning": {
                "inputs": {
                    "cibil_score": round(cibil_score, 2),
                },
                "thresholds": {
                    "clear": ">=700",
                    "warning": "650-699.99",
                    "flagged": "<650",
                },
                "computed_output": {
                    "status": credit_status,
                },
                "decision": f"Credit bureau evaluation classified as {credit_status}.",
            },
        },
        {
            "step": "INCOME_VALIDATION",
            "status": income_status,
            "tool": "income_validator",
            "api_simulated": True,
            "latency_ms": deterministic_latency_ms(application_id, "INCOME_VALIDATION"),
            "status_code": 200,
            "triggered_by": "CREDIT_BUREAU",
            "impact": "Contributes mismatch signal to discrepancy analysis and final confidence profile.",
            "reasoning": {
                "inputs": {
                    "income_mismatch_flag": income_mismatch_flag,
                },
                "thresholds": {
                    "match_expected": False,
                },
                "computed_output": {
                    "income_mismatch": to_bool(income_mismatch_flag, default=False),
                    "status": income_status,
                },
                "decision": (
                    "Income consistency confirmed."
                    if income_status == "MATCH"
                    else "Income mismatch identified; escalate discrepancy attention."
                ),
            },
        },
        {
            "step": "DISCREPANCY_ANALYSIS",
            "status": discrepancy_status,
            "tool": "flag_engine_node_006",
            "api_simulated": True,
            "latency_ms": deterministic_latency_ms(application_id, "DISCREPANCY_ANALYSIS"),
            "status_code": 200,
            "triggered_by": "INCOME_VALIDATION",
            "impact": "Determines risk tier and drives confidence scoring penalties downstream.",
            "reasoning": {
                "inputs": {
                    "flags": flags,
                    "severity": severity,
                },
                "thresholds": {
                    "severity_levels": ["HIGH", "MEDIUM", "LOW", "NONE"],
                },
                "computed_output": {
                    "flag_count": len(flags),
                    "status": discrepancy_status,
                },
                "decision": f"Discrepancy severity assessed as {severity}.",
            },
        },
        {
            "step": "CONFIDENCE_SCORING",
            "status": confidence_status,
            "tool": "confidence_engine_node_007",
            "api_simulated": True,
            "latency_ms": deterministic_latency_ms(application_id, "CONFIDENCE_SCORING"),
            "status_code": 200,
            "triggered_by": "DISCREPANCY_ANALYSIS",
            "impact": "Sets confidence band used in HIL decision prioritization.",
            "reasoning": {
                "inputs": {
                    "confidence_score": round(confidence_score, 2),
                },
                "thresholds": {
                    "high": ">=75",
                    "medium": "60-74.99",
                    "low": "<60",
                },
                "computed_output": {
                    "status": confidence_status,
                },
                "decision": f"Confidence evaluation assigned {confidence_status} band.",
            },
        },
        {
            "step": "HIL_DECISION",
            "status": hil_status,
            "tool": "hil_engine_node_009",
            "api_simulated": True,
            "latency_ms": deterministic_latency_ms(application_id, "HIL_DECISION"),
            "status_code": 200,
            "triggered_by": "CONFIDENCE_SCORING",
            "impact": "Determines whether manual intervention enters the underwriting workflow.",
            "reasoning": {
                "inputs": {
                    "hil_required_flag": hil_required,
                    "hil_priority": hil_priority,
                },
                "thresholds": {
                    "manual_intervention": "required when hil_required_flag is true",
                },
                "computed_output": {
                    "status": hil_status,
                    "manual_review_route": "HIL_QUEUE" if hil_required else "AUTO_FLOW",
                },
                "decision": (
                    f"HIL required with priority {hil_priority}."
                    if hil_required
                    else "No HIL required; continue routine automated flow."
                ),
            },
        },
    ]

    return {
        "application_id": application_id,
        "severity": severity,
        "confidence_score": round(confidence_score, 2),
        "hil_required_flag": hil_required,
        "hil_priority": hil_priority,
        "final_summary": {
            "decision": "REVIEW",
            "risk": severity,
            "confidence": round(confidence_score, 2),
            "key_reasons": key_reasons,
            "hil_required": hil_required,
        },
        "agent_metadata": {
            "total_steps": len(timeline),
            "risk_level": severity,
            "processing_mode": "HUMAN_IN_LOOP" if hil_required else "STRAIGHT_THROUGH",
        },
        "timeline": timeline,
    }


def write_json(path: Path, rows: list[dict]):
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def main():
    ensure_dirs()

    node_006_data = load_node_006_data()
    node_007_confidence = load_node_007_confidence()
    node_009_hil = load_node_009_hil()

    grouped = {
        "high_risk_cases": [],
        "medium_risk_cases": [],
        "low_risk_cases": [],
    }
    total_rows = 0

    with DATASET_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            app_id = row.get("application_id", "")
            cibil_score = to_float(row.get("cibil_score"), default=0.0)
            data_consistency_flag = row.get("data_consistency_flag", "")
            income_mismatch_flag = row.get("income_mismatch_flag", "")

            n006 = node_006_data.get(app_id, {"severity": "NONE", "flags": []})
            severity = n006.get("severity", "NONE")
            flags = n006.get("flags", [])

            confidence_score = node_007_confidence.get(app_id, 100.0)

            n009 = node_009_hil.get(
                app_id, {"hil_required_flag": False, "hil_priority": None}
            )
            hil_required = to_bool(n009.get("hil_required_flag"), default=False)
            hil_priority = n009.get("hil_priority")

            timeline_row = build_timeline_record(
                application_id=app_id,
                cibil_score=cibil_score,
                data_consistency_flag=data_consistency_flag,
                income_mismatch_flag=income_mismatch_flag,
                flags=flags,
                severity=severity,
                confidence_score=confidence_score,
                hil_required=hil_required,
                hil_priority=hil_priority,
            )

            risk_bucket = categorize_by_severity(severity)
            grouped[risk_bucket].append(timeline_row)

    write_json(
        DETAILED_ACTION_LOG_DIR / "high_risk_cases" / "high_risk_cases_timeline.json",
        grouped["high_risk_cases"],
    )
    write_json(
        DETAILED_ACTION_LOG_DIR / "medium_risk_cases" / "medium_risk_cases_timeline.json",
        grouped["medium_risk_cases"],
    )
    write_json(
        DETAILED_ACTION_LOG_DIR / "low_risk_cases" / "low_risk_cases_timeline.json",
        grouped["low_risk_cases"],
    )
    all_rows = grouped["high_risk_cases"] + grouped["medium_risk_cases"] + grouped["low_risk_cases"]
    write_json(DETAILED_ACTION_LOG_DIR / "all_timelines.json", all_rows)
    write_json(APPLICATION_DATA_DIR / "complete_records" / "application_data.json", all_rows)
    write_json(ASSESSMENT_OUTCOMES_DIR / "discrepancies_present" / "discrepancies_present.json", grouped["high_risk_cases"] + grouped["medium_risk_cases"])
    write_json(ASSESSMENT_OUTCOMES_DIR / "high_confidence" / "high_confidence.json", [row for row in all_rows if row.get("confidence_score", 0) >= 75])
    write_json(ASSESSMENT_OUTCOMES_DIR / "low_confidence" / "low_confidence.json", [row for row in all_rows if row.get("confidence_score", 0) < 75])

    summary = {
        "total_records": total_rows,
        "distribution": {
            "high_risk_cases": len(grouped["high_risk_cases"]),
            "medium_risk_cases": len(grouped["medium_risk_cases"]),
            "low_risk_cases": len(grouped["low_risk_cases"]),
        },
        "key_metrics": {
            "hil_required_count": sum(1 for row in all_rows if row.get("hil_required_flag")),
            "average_confidence": round(sum(row.get("confidence_score", 0.0) for row in all_rows) / total_rows, 2) if total_rows else 0.0,
        },
    }
    with (REPORTS_DIR / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Node-013 timeline generation complete (data folder only).")
    print(f"Total rows: {total_rows}")
    print(f"High risk cases: {len(grouped['high_risk_cases'])}")
    print(f"Medium risk cases: {len(grouped['medium_risk_cases'])}")
    print(f"Low risk cases: {len(grouped['low_risk_cases'])}")


if __name__ == "__main__":
    main()
