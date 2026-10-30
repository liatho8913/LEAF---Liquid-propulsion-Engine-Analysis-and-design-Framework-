from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


PHASE = "16T.2H"

PASS_STATUS = "PASS_ALLOWLIST_CONSTRAINED_MOVE_EXECUTION_PHASE_16T2H"
WARN_STATUS = "WARN_ALLOWLIST_CONSTRAINED_MOVE_EXECUTION_PHASE_16T2H"
FAIL_STATUS = "FAIL_ALLOWLIST_CONSTRAINED_MOVE_EXECUTION_PHASE_16T2H"

ALLOWLIST_PATH = ROOT / "_leaf_artifacts" / "allowlists" / "VERIFIED_MOVE_ALLOWLIST_PHASE_16T2G.txt"
REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"
ZIP_DIR = ROOT / "_leaf_artifacts" / "zips"
ARCHIVE_DIR = ROOT / "_leaf_archive" / "python_legacy_scripts_phase_16t2h"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _read_allowlist() -> list[str]:
    if not ALLOWLIST_PATH.exists():
        return []

    return [
        line.strip()
        for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _destination_for(relative_path: str) -> Path:
    return ARCHIVE_DIR / relative_path


def build_allowlist_move_plan() -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    allowlisted = _read_allowlist()

    blockers: list[str] = []
    warnings: list[str] = []
    items: list[dict[str, Any]] = []

    if not ALLOWLIST_PATH.exists():
        blockers.append(f"Allowlist file missing: {ALLOWLIST_PATH}")

    if not allowlisted:
        blockers.append("Allowlist is empty; no files may be moved.")

    for relative_path in allowlisted:
        source = ROOT / relative_path
        destination = _destination_for(relative_path)

        exists = source.exists()
        already_archived = destination.exists()

        if not exists and not already_archived:
            blockers.append(f"Allowlisted file missing and no archived copy found: {relative_path}")

        if exists and already_archived:
            warnings.append(f"Both active and archived copies exist: {relative_path}")

        items.append(
            {
                "path": relative_path,
                "source": str(source),
                "destination": str(destination),
                "exists": exists,
                "already_archived": already_archived,
                "will_move": exists,
            }
        )

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "allowlist_path": str(ALLOWLIST_PATH),
        "allowed_count": len(allowlisted),
        "move_count": sum(1 for item in items if item["will_move"]),
        "already_archived_count": sum(1 for item in items if item["already_archived"]),
        "items": items,
        "blockers": blockers,
        "warnings": warnings,
        "archive_dir": str(ARCHIVE_DIR),
        "zip_dir": str(ZIP_DIR),
        "report_dir": str(REPORT_DIR),
        "summary": f"{len(allowlisted)} allowlisted files checked; {sum(1 for item in items if item['will_move'])} ready to move.",
    }


def build_allowlist_move_report(plan: dict[str, Any], executed: bool = False, backup_zip: str | None = None) -> str:
    lines = [
        "ALLOWLIST-CONSTRAINED MOVE EXECUTION",
        "====================================",
        f"Phase: {plan['phase']}",
        f"Status: {plan['status']}",
        f"Passed: {plan['passed']}",
        f"Executed: {executed}",
        f"Summary: {plan['summary']}",
        f"Allowlist: {plan['allowlist_path']}",
        f"Archive folder: {plan['archive_dir']}",
        f"Zip folder: {plan['zip_dir']}",
        f"Report folder: {plan['report_dir']}",
    ]

    if backup_zip:
        lines.append(f"Backup zip: {backup_zip}")

    lines.extend([
        "",
        "COUNTS",
        "------",
        f"Allowed files: {plan['allowed_count']}",
        f"Files ready to move: {plan['move_count']}",
        f"Already archived: {plan['already_archived_count']}",
        "",
        "MOVE PLAN",
        "---------",
    ])

    for item in plan["items"]:
        lines.append(
            f"- {item['path']} | exists={item['exists']} | "
            f"already_archived={item['already_archived']} | "
            f"will_move={item['will_move']} | destination={item['destination']}"
        )

    if plan["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in plan["warnings"])

    if plan["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in plan["blockers"])

    lines.extend([
        "",
        "SAFETY GUARANTEE",
        "----------------",
        "This executor deletes nothing. It only moves allowlisted files after first creating a zip backup.",
    ])

    return "\n".join(lines)


def _write_report(text: str, filename: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / filename
    path.write_text(text, encoding="utf-8")
    return path


def _create_backup_zip(plan: dict[str, Any]) -> Path:
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = ZIP_DIR / f"LEAF_PHASE_16T2H_ALLOWLIST_MOVE_BACKUP_{_timestamp()}.zip"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in plan["items"]:
            source = Path(item["source"])
            if source.exists():
                zf.write(source, source.relative_to(ROOT).as_posix())

    return zip_path


def execute_allowlist_move() -> dict[str, Any]:
    plan = build_allowlist_move_plan()

    if plan["blockers"]:
        report = build_allowlist_move_report(plan, executed=False)
        report_path = _write_report(report, "ALLOWLIST_MOVE_BLOCKED_PHASE_16T2H.txt")
        return {
            "status": FAIL_STATUS,
            "executed": False,
            "moved_count": 0,
            "moved": [],
            "backup_zip": None,
            "report_path": str(report_path),
        }

    backup_zip = _create_backup_zip(plan)
    moved: list[str] = []

    for item in plan["items"]:
        if not item["will_move"]:
            continue

        source = Path(item["source"])
        destination = Path(item["destination"])
        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(source), str(destination))
        moved.append(item["path"])

    post_plan = build_allowlist_move_plan()
    report = build_allowlist_move_report(post_plan, executed=True, backup_zip=str(backup_zip))
    report_path = _write_report(report, "ALLOWLIST_MOVE_EXECUTED_PHASE_16T2H.txt")

    return {
        "status": PASS_STATUS,
        "executed": True,
        "moved_count": len(moved),
        "moved": moved,
        "backup_zip": str(backup_zip),
        "report_path": str(report_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Move allowlisted files after zip backup.")
    args = parser.parse_args()

    plan = build_allowlist_move_plan()

    if not args.execute:
        report = build_allowlist_move_report(plan, executed=False)
        report_path = _write_report(report, "ALLOWLIST_MOVE_DRY_RUN_PHASE_16T2H.txt")
        print(plan["status"])
        print(report_path)
        print("DRY_RUN_ONLY")
        return 0 if plan["passed"] else 1

    result = execute_allowlist_move()
    print(result["status"])
    print(result["report_path"])
    if result.get("backup_zip"):
        print(result["backup_zip"])
    print(f"moved_count={result['moved_count']}")
    return 0 if result["status"] == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
