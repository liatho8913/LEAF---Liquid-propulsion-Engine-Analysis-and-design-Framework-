from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.reference_classification_engine_phase_16t2f1 import (
    build_reference_classification_audit,
)


PHASE = "16T.2G"

PASS_STATUS = "PASS_VERIFIED_MOVE_ALLOWLIST_PHASE_16T2G"
WARN_STATUS = "WARN_VERIFIED_MOVE_ALLOWLIST_PHASE_16T2G"
FAIL_STATUS = "FAIL_VERIFIED_MOVE_ALLOWLIST_PHASE_16T2G"

REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"
ALLOWLIST_DIR = ROOT / "_leaf_artifacts" / "allowlists"


def build_verified_move_allowlist() -> dict[str, Any]:
    audit = build_reference_classification_audit()

    blockers = []
    warnings = []

    if audit.get("blockers"):
        blockers.extend(audit["blockers"])

    blocking_candidates = audit.get("blocking_candidates", {})
    nonblocking_only = audit.get("nonblocking_only_candidates", {})
    unreferenced = audit.get("unreferenced_candidates", [])

    allowed = sorted(set(nonblocking_only.keys()) | set(unreferenced))
    blocked = sorted(blocking_candidates.keys())

    if blocked:
        warnings.append(f"{len(blocked)} candidates blocked due to operational references.")

    missing_files = [
        path for path in allowed
        if not (ROOT / path).exists()
    ]

    if missing_files:
        blockers.append(f"{len(missing_files)} allowlisted files are missing from active source.")

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "allowed_count": len(allowed),
        "blocked_count": len(blocked),
        "allowed": allowed,
        "blocked": blocked,
        "missing_files": missing_files,
        "source_reference_status": audit.get("status"),
        "warnings": warnings,
        "blockers": blockers,
        "summary": (
            f"{len(allowed)} files allowlisted for move-only archival; "
            f"{len(blocked)} files blocked."
        ),
    }


def build_verified_move_allowlist_report() -> str:
    allowlist = build_verified_move_allowlist()

    lines = [
        "VERIFIED MOVE ALLOWLIST",
        "=======================",
        f"Phase: {allowlist['phase']}",
        f"Status: {allowlist['status']}",
        f"Passed: {allowlist['passed']}",
        f"Source reference status: {allowlist['source_reference_status']}",
        f"Summary: {allowlist['summary']}",
        "",
        "COUNTS",
        "------",
        f"Allowed: {allowlist['allowed_count']}",
        f"Blocked: {allowlist['blocked_count']}",
        f"Missing files: {len(allowlist['missing_files'])}",
        "",
        "ALLOWLISTED MOVE-ONLY FILES",
        "---------------------------",
    ]

    for path in allowlist["allowed"]:
        lines.append(f"- {path}")

    if allowlist["blocked"]:
        lines.extend(["", "BLOCKED FILES", "-------------"])
        for path in allowlist["blocked"]:
            lines.append(f"- {path}")

    if allowlist["missing_files"]:
        lines.extend(["", "MISSING ALLOWLISTED FILES", "-------------------------"])
        for path in allowlist["missing_files"]:
            lines.append(f"- {path}")

    if allowlist["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in allowlist["warnings"])

    if allowlist["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in allowlist["blockers"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "Only files listed in this allowlist may be moved by the archival cleanup executor. This phase deletes nothing.",
    ])

    return "\n".join(lines)


def write_verified_move_allowlist() -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ALLOWLIST_DIR.mkdir(parents=True, exist_ok=True)

    allowlist = build_verified_move_allowlist()

    allowlist_path = ALLOWLIST_DIR / "VERIFIED_MOVE_ALLOWLIST_PHASE_16T2G.txt"
    report_path = REPORT_DIR / "VERIFIED_MOVE_ALLOWLIST_PHASE_16T2G.txt"

    allowlist_path.write_text("\n".join(allowlist["allowed"]) + "\n", encoding="utf-8")
    report_path.write_text(build_verified_move_allowlist_report(), encoding="utf-8")

    return allowlist_path, report_path


if __name__ == "__main__":
    allowlist_path, report_path = write_verified_move_allowlist()
    allowlist = build_verified_move_allowlist()
    print(allowlist["status"])
    print(allowlist_path)
    print(report_path)
