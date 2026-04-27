"""One-off structural fix for data/node-007 validation buckets.
Uses confidence_all.csv as canonical 7-column rows; partitions by rules on master CSV.
"""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE007 = ROOT / "data" / "node-007"
VAL = NODE007 / "validation"
STRUCT = VAL / "structured"
BACKUP = VAL / "backup_unused"
MASTER = ROOT / "1000_rows_dataset.csv"
CANONICAL = STRUCT / "kyc_verification" / "complete_records" / "confidence_all.csv"

COLS = [
    "application_id",
    "data_consistency_flag",
    "document_consistency_flag",
    "ocr_confidence_score",
    "flags",
    "confidence_score",
    "confidence_level",
]


def load_master_by_id() -> dict[str, dict]:
    with MASTER.open(newline="", encoding="utf-8") as f:
        return {r["application_id"]: r for r in csv.DictReader(f)}


def load_canonical_rows_ordered() -> list[dict]:
    with CANONICAL.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: r["application_id"])
    return rows


def identity_missing(m: dict) -> bool:
    for k in ("pan_number", "aadhaar_number", "applicant_name"):
        v = m.get(k)
        if v is None or str(v).strip() == "":
            return True
    return False


def partition_kyc_ids(
    master: dict[str, dict], ids: list[str], ca_by_id: dict[str, dict]
) -> tuple[set[str], set[str], set[str]]:
    missing: set[str] = set()
    outliers: set[str] = set()
    complete: set[str] = set()
    for aid in ids:
        m = master[aid]
        crow = ca_by_id[aid]
        conf = float(crow["confidence_score"])
        if identity_missing(m) or str(m.get("data_consistency_flag", "")).upper() == "FALSE":
            missing.add(aid)
        elif conf < 40 or conf > 95:
            outliers.add(aid)
        else:
            complete.add(aid)
    return missing, outliers, complete


def partition_income_ids(master: dict[str, dict], ids: list[str]) -> tuple[set[str], set[str], set[str]]:
    missing: set[str] = set()
    imbalanced: set[str] = set()
    complete: set[str] = set()

    declared_vals: list[float] = []
    for aid in ids:
        m = master[aid]
        if str(m.get("document_consistency_flag", "")).upper() == "FALSE":
            continue
        di = m.get("declared_income")
        try:
            declared_vals.append(float(di))
        except (TypeError, ValueError):
            pass

    declared_vals.sort()
    n = len(declared_vals)
    if n == 0:
        p5 = p95 = 0.0
    else:
        p5 = declared_vals[int(0.05 * (n - 1))]
        p95 = declared_vals[int(0.95 * (n - 1))]

    for aid in ids:
        m = master[aid]
        if str(m.get("document_consistency_flag", "")).upper() == "FALSE":
            missing.add(aid)
            continue
        di = m.get("declared_income")
        try:
            di_f = float(di)
        except (TypeError, ValueError):
            missing.add(aid)
            continue
        if di_f <= p5 or di_f >= p95:
            imbalanced.add(aid)
        else:
            complete.add(aid)

    return missing, imbalanced, complete


def partition_discrepancy_ids(ids: list[str], ca_by_id: dict[str, dict]) -> tuple[set[str], set[str], set[str]]:
    missing: set[str] = set()
    imbalanced: set[str] = set()
    complete: set[str] = set()
    for aid in ids:
        fl = (ca_by_id[aid].get("flags") or "").strip()
        if fl == "":
            missing.add(aid)
            continue
        parts = [p for p in fl.split("|") if p.strip()]
        if len(parts) >= 2:
            imbalanced.add(aid)
        else:
            complete.add(aid)
    return missing, imbalanced, complete


def write_bucket(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def move_folder(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise FileExistsError(dest)
    shutil.move(str(src), str(dest))


def backup_file(src: Path, dest_name: str) -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)
    dest = BACKUP / dest_name
    if src.exists():
        shutil.copy2(str(src), str(dest))


def main() -> None:
    if not CANONICAL.exists():
        raise FileNotFoundError(CANONICAL)

    BACKUP.mkdir(parents=True, exist_ok=True)

    # --- Task 1: move confidence_scoring_legacy
    legacy = STRUCT / "confidence_scoring_legacy"
    if legacy.exists():
        dest = BACKUP / "confidence_scoring_legacy"
        if not dest.exists():
            move_folder(legacy, dest)

    # --- Task 2: move discrepancy_analysis/high_severity
    hs = STRUCT / "discrepancy_analysis" / "high_severity"
    if hs.exists():
        dest = BACKUP / "discrepancy_analysis_high_severity"
        if not dest.exists():
            move_folder(hs, dest)

    # Backup redundant CSVs (keep copy under backup_unused)
    backup_file(
        STRUCT / "kyc_verification" / "complete_records" / "confidence_all.csv",
        "kyc_complete_records_confidence_all.csv",
    )
    backup_file(
        STRUCT / "income_validation" / "complete_records" / "high_confidence.csv",
        "income_complete_records_high_confidence.csv",
    )
    backup_file(
        STRUCT / "income_validation" / "imbalanced_classes" / "medium_confidence.csv",
        "income_imbalanced_classes_medium_confidence.csv",
    )

    master = load_master_by_id()
    rows = load_canonical_rows_ordered()
    ids = [r["application_id"] for r in rows]
    ca_by_id = {r["application_id"]: r for r in rows}

    if len(ids) != 1000 or len(set(ids)) != 1000:
        raise ValueError(f"Expected 1000 unique application_ids, got {len(ids)} / {len(set(ids))}")

    k_m, k_o, k_c = partition_kyc_ids(master, ids, ca_by_id)
    i_m, i_b, i_c = partition_income_ids(master, ids)
    d_m, d_b, d_c = partition_discrepancy_ids(ids, ca_by_id)

    def rows_for(id_set: set[str]) -> list[dict]:
        out = [ca_by_id[i] for i in ids if i in id_set]
        return out

    # kyc
    write_bucket(STRUCT / "kyc_verification" / "complete_records" / "complete_records_validation.csv", rows_for(k_c))
    write_bucket(STRUCT / "kyc_verification" / "missing_values" / "missing_values_validation.csv", rows_for(k_m))
    write_bucket(STRUCT / "kyc_verification" / "outliers" / "outliers_validation.csv", rows_for(k_o))

    # Remove duplicate canonical from complete folder (backed up above)
    conf_all = STRUCT / "kyc_verification" / "complete_records" / "confidence_all.csv"
    if conf_all.exists():
        conf_all.unlink()

    # income
    write_bucket(STRUCT / "income_validation" / "complete_records" / "complete_records_validation.csv", rows_for(i_c))
    write_bucket(STRUCT / "income_validation" / "missing_values" / "missing_values_validation.csv", rows_for(i_m))
    write_bucket(STRUCT / "income_validation" / "imbalanced_classes" / "imbalanced_classes_validation.csv", rows_for(i_b))

    hfc = STRUCT / "income_validation" / "complete_records" / "high_confidence.csv"
    if hfc.exists():
        hfc.unlink()
    mcf = STRUCT / "income_validation" / "imbalanced_classes" / "medium_confidence.csv"
    if mcf.exists():
        mcf.unlink()

    # discrepancy
    write_bucket(
        STRUCT / "discrepancy_analysis" / "complete_records" / "complete_records_validation.csv",
        rows_for(d_c),
    )
    write_bucket(
        STRUCT / "discrepancy_analysis" / "missing_values" / "missing_values_validation.csv",
        rows_for(d_m),
    )
    write_bucket(
        STRUCT / "discrepancy_analysis" / "imbalanced_classes" / "imbalanced_classes_validation.csv",
        rows_for(d_b),
    )

    # Summary for caller
    def stats(name: str, a: set, b: set, c: set) -> None:
        print(f"{name}: {len(a)} + {len(b)} + {len(c)} = {len(a)+len(b)+len(c)}")

    stats("kyc", k_m, k_o, k_c)
    stats("income", i_m, i_b, i_c)
    stats("disc", d_m, d_b, d_c)


if __name__ == "__main__":
    main()
