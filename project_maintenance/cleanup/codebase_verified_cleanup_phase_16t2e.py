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

from project_maintenance.production_historical_artifacts.leaf_qt.root_level_review.codebase_safe_cleanup_plan_phase_16t2d import ARCHIVE, build_safe_cleanup_plan


PHASE = "16T.2E"

PASS_STATUS = "PASS_CODEBASE_VERIFIED_CLEANUP_PLAN_PHASE_16T2E"
WARN_STATUS = "WARN_CODEBASE_VERIFIED_CLEANUP_PLAN_PHASE_16T2E"
FAIL_STATUS = "FAIL_CODEBASE_VERIFIED_CLEANUP_PLAN_PHASE_16T2E"

REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"
ZIP_DIR = ROOT / "_leaf_artifacts" / "zips"
ARCHIVE_DIR = ROOT / "_leaf_archive" / "python_legacy_scripts_phase_16t2e"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _archive_candidates() -> list[dict[str, Any]]:
    plan = build_safe_cleanup_plan(ROOT)
    return [item for item in plan.get("actions", []) if item.get("action") == ARCHIVE]


def _safe_destination(source: Path) -> Path:
    relative = source.relative_to(ROOT)
    return ARCHIVE_DIR / relative


def build_verified_cleanup_plan() -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    candidates = _archive_candidates()

    items = []
    blockers = []
    warnings = []

    for item in candidates:
        source = ROOT / item["path"]
        destination = _safe_destination(source)

        exists = source.exists()
        already_archived = destination.exists()

        if not exists and not already_archived:
            blockers.append(f"Missing source file and no archived copy found: {item['path']}")

        if exists and already_archived:
            warnings.append(f"Source and archive copy both exist: {item['path']}")

        items.append(
            {
                "path": item["path"],
                "source": str(source),
                "destination": str(destination),
                "exists": exists,
                "already_archived": already_archived,
                "reason": item.get("reason", ""),
            }
        )

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "candidate_count": len(candidates),
        "items": items,
        "blockers": blockers,
        "warnings": warnings,
        "report_dir": str(REPORT_DIR),
        "zip_dir": str(ZIP_DIR),
        "archive_dir": str(ARCHIVE_DIR),
        "summary": f"{len(candidates)} archive candidates prepared for backup-first move-only cleanup.",
    }


def build_verified_cleanup_report(plan: dict[str, Any], executed: bool = False, backup_zip: str | None = None) -> str:
    lines = [
        "VERIFIED CODEBASE CLEANUP EXECUTION PLAN",
        "========================================",
        f"Phase: {plan['phase']}",
        f"Status: {plan['status']}",
        f"Passed: {plan['passed']}",
        f"Executed: {executed}",
        f"Summary: {plan['summary']}",
        f"Archive folder: {plan['archive_dir']}",
        f"Zip folder: {plan['zip_dir']}",
        f"Report folder: {plan['report_dir']}",
    ]

    if backup_zip:
        lines.append(f"Backup zip: {backup_zip}")

    lines.extend(["", "MOVE-ONLY ACTIONS", "-----------------"])

    for item in plan["items"]:
        lines.append(
            f"- {item['path']} -> {item['destination']} | "
            f"exists={item['exists']} | already_archived={item['already_archived']} | "
            f"{item['reason']}"
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
        "This tool never deletes files. It only creates a zip backup and moves archive candidates into _leaf_archive.",
    ])

    return "\n".join(lines)


def write_report(text: str, filename: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / filename
    path.write_text(text, encoding="utf-8")
    return path


def create_backup_zip(plan: dict[str, Any]) -> Path:
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = ZIP_DIR / f"LEAF_PHASE_16T2E_ARCHIVE_CANDIDATES_BACKUP_{_timestamp()}.zip"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in plan["items"]:
            source = Path(item["source"])
            if source.exists():
                zf.write(source, source.relative_to(ROOT).as_posix())

    return zip_path


def execute_move_only_cleanup() -> dict[str, Any]:
    plan = build_verified_cleanup_plan()

    if plan["blockers"]:
        report = build_verified_cleanup_report(plan, executed=False)
        report_path = write_report(report, "VERIFIED_CLEANUP_BLOCKED_PHASE_16T2E.txt")
        return {
            "status": FAIL_STATUS,
            "executed": False,
            "report_path": str(report_path),
            "backup_zip": None,
        }

    backup_zip = create_backup_zip(plan)

    moved = []

    for item in plan["items"]:
        source = Path(item["source"])
        destination = Path(item["destination"])

        if not source.exists():
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved.append(item["path"])

    post_plan = build_verified_cleanup_plan()
    report = build_verified_cleanup_report(post_plan, executed=True, backup_zip=str(backup_zip))
    report_path = write_report(report, "VERIFIED_CLEANUP_EXECUTED_PHASE_16T2E.txt")

    return {
        "status": PASS_STATUS,
        "executed": True,
        "moved": moved,
        "moved_count": len(moved),
        "backup_zip": str(backup_zip),
        "report_path": str(report_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Actually move archive candidates after creating backup zip.")
    args = parser.parse_args()

    plan = build_verified_cleanup_plan()

    if not args.execute:
        report = build_verified_cleanup_report(plan, executed=False)
        report_path = write_report(report, "VERIFIED_CLEANUP_DRY_RUN_PHASE_16T2E.txt")
        print(plan["status"])
        print(report_path)
        print("DRY_RUN_ONLY")
        return 0 if plan["passed"] else 1

    result = execute_move_only_cleanup()
    print(result["status"])
    print(result["report_path"])
    if result.get("backup_zip"):
        print(result["backup_zip"])
    return 0 if result["status"] == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
