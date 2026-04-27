"""Move node-005 extra directories to validation/backup_unused; no CSV/data edits."""

from __future__ import annotations

import shutil
from pathlib import Path

BASE = Path(r"c:\Users\User\Desktop\Agent Dashboard\data\node-005")
VAL = BASE / "validation"
BACKUP = VAL / "backup_unused"
STRUCT = VAL / "structured"


def safe_move(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise FileExistsError(f"Destination already exists: {dest}")
    shutil.move(str(src), str(dest))


def assert_no_files(path: Path) -> None:
    if not path.exists():
        return
    files = [p for p in path.rglob("*") if p.is_file()]
    if files:
        raise RuntimeError(f"Refusing to move non-empty folder (has files): {path}")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    safe_move(VAL / "unstructured", BACKUP / "unstructured")

    legacy = STRUCT / "income_validation" / "mismatch_detection_legacy"
    assert_no_files(legacy)  # only refuse if CSV etc. appear; empty subdirs OK
    if legacy.exists():
        for p in legacy.rglob("*"):
            if p.is_file():
                raise RuntimeError(f"Unexpected file under legacy: {p}")
    safe_move(legacy, BACKUP / "income_validation_mismatch_detection_legacy")

    md_removed = BACKUP / "mismatch_detection_extra_directories"
    for name in ("complete_records", "missing_values", "outliers"):
        src = STRUCT / "mismatch_detection" / name
        if src.exists():
            assert_no_files(src)
            safe_move(src, md_removed / name)

    print("Done. Backup root:", BACKUP)


if __name__ == "__main__":
    main()
