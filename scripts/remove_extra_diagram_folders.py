"""Move validation/backup_unused and node-level migration logs to data/_diagram_archive;
remove empty validation/unstructured. Does not delete file content (archive = move)."""

from __future__ import annotations

import shutil
from pathlib import Path

DATA = Path(r"c:\Users\User\Desktop\Agent Dashboard\data")
ARCH = DATA / "_diagram_archive"


def main() -> None:
    ARCH.mkdir(exist_ok=True)
    for node in sorted(DATA.glob("node-*")):
        bu = node / "validation" / "backup_unused"
        if bu.exists():
            dest = ARCH / node.name / "backup_unused"
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                raise FileExistsError(f"Refusing to overwrite archive: {dest}")
            shutil.move(str(bu), str(dest))
        mig = node / "migration_moved_files.txt"
        if mig.exists():
            dest = ARCH / node.name / "migration_moved_files.txt"
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                raise FileExistsError(f"Refusing to overwrite: {dest}")
            shutil.move(str(mig), str(dest))
        un = node / "validation" / "unstructured"
        if not un.exists():
            continue
        files = [p for p in un.rglob("*") if p.is_file()]
        if not files:
            shutil.rmtree(str(un))
    print("Archive root:", ARCH)


if __name__ == "__main__":
    main()
