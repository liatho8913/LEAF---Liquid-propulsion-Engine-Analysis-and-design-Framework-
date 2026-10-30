from __future__ import annotations

from pathlib import Path
from typing import Any

from codebase_project_intelligence_audit_phase_16t2c import (
    build_project_intelligence_audit,
)


PHASE = "16T.2D"

PASS_STATUS = "PASS_CODEBASE_SAFE_CLEANUP_PLAN_PHASE_16T2D"
WARN_STATUS = "WARN_CODEBASE_SAFE_CLEANUP_PLAN_PHASE_16T2D"
FAIL_STATUS = "FAIL_CODEBASE_SAFE_CLEANUP_PLAN_PHASE_16T2D"

KEEP = "KEEP"
KEEP_BUT_REVIEW = "KEEP_BUT_REVIEW"
ARCHIVE = "ARCHIVE"
SAFE_TO_REMOVE_AFTER_TESTS = "SAFE_TO_REMOVE_AFTER_TESTS"
DO_NOT_TOUCH = "DO_NOT_TOUCH"

DO_NOT_TOUCH_NAMES = {
    "main.py",
    "main_window.py",
    "engine_solver.py",
    "material_database.py",
    "coolant_database.py",
    "fluid_property_database.py",
    "variable_registry.py",
    "foundation_verification_harness.py",
    "run_foundation_verification.py",
}

KEEP_PREFIXES = (
    "regen_",
    "material_",
    "coating_",
    "foundation_",
    "real_engine_",
    "benchmark_",
    "graph_",
    "output_",
    "input_",
    "diagnostics_",
    "failure_",
    "recommendation_",
    "optimisation_",
)

ARCHIVE_PREFIXES = (
    "phase_",
    "register_phase_",
    "register_post",
    "patch_",
    "recover_",
)

SCRIPT_PREFIXES = (
    "package_",
    "dump_",
    "find_",
    "inspect_",
    "fix_",
    "integrate_",
)


def classify_cleanup_action(path: str) -> tuple[str, str]:
    name = Path(path).name
    stem = Path(path).stem
    lower = path.lower()

    if name in DO_NOT_TOUCH_NAMES:
        return DO_NOT_TOUCH, "Core runtime/foundation file."

    if "/leaf_qt/" in f"/{path}" and stem.startswith(KEEP_PREFIXES):
        return KEEP, "Active LEAF subsystem module or owner."

    if stem.startswith(KEEP_PREFIXES):
        return KEEP, "Active subsystem module or owner."

    if stem.startswith(ARCHIVE_PREFIXES):
        return ARCHIVE, "Historical phase/register/patch helper; archive rather than delete."

    if stem.startswith(SCRIPT_PREFIXES):
        return ARCHIVE, "One-off helper/integration script; archive after tests."

    if stem in {"promethean_forge"}:
        return ARCHIVE, "Legacy Tkinter-era application entry; archive unless still intentionally used."

    if "preview" in lower or "viewer" in lower:
        return KEEP_BUT_REVIEW, "Viewer-related file; may be manually launched or UI-connected."

    if "cea" in lower:
        return KEEP_BUT_REVIEW, "CEA-related file; verify before moving."

    return KEEP_BUT_REVIEW, "Unreferenced by static audit, but requires manual review before cleanup."


def build_safe_cleanup_plan(root: str | Path = ".") -> dict[str, Any]:
    audit = build_project_intelligence_audit(root)
    likely_unused = audit.get("likely_unused_active_modules", [])

    actions = []

    counts = {
        KEEP: 0,
        KEEP_BUT_REVIEW: 0,
        ARCHIVE: 0,
        SAFE_TO_REMOVE_AFTER_TESTS: 0,
        DO_NOT_TOUCH: 0,
    }

    for path in likely_unused:
        action, reason = classify_cleanup_action(path)
        counts[action] += 1
        actions.append(
            {
                "path": path,
                "action": action,
                "reason": reason,
            }
        )

    blockers = []
    warnings = []

    if audit.get("parse_error_count", 0):
        blockers.append("Project intelligence audit has parse errors; cleanup planning blocked.")

    if actions:
        warnings.append(f"{len(actions)} likely unused active modules require cleanup classification.")

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "source_audit_status": audit.get("status"),
        "classified_file_count": len(actions),
        "counts": counts,
        "actions": actions,
        "blockers": blockers,
        "warnings": warnings,
        "summary": (
            f"{len(actions)} likely unused active modules classified; "
            f"{counts[ARCHIVE]} archive candidates; "
            f"{counts[KEEP_BUT_REVIEW]} review candidates; "
            f"{counts[DO_NOT_TOUCH]} do-not-touch files."
        ),
    }


def build_safe_cleanup_plan_report(root: str | Path = ".") -> str:
    plan = build_safe_cleanup_plan(root)

    lines = [
        "SAFE CODEBASE CLEANUP PLAN",
        "==========================",
        f"Phase: {plan['phase']}",
        f"Status: {plan['status']}",
        f"Passed: {plan['passed']}",
        f"Source audit status: {plan['source_audit_status']}",
        f"Summary: {plan['summary']}",
        "",
        "ACTION COUNTS",
        "-------------",
    ]

    for key, value in plan["counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "CLASSIFIED ACTIONS", "------------------"])

    for item in plan["actions"]:
        lines.append(f"- {item['action']}: {item['path']} :: {item['reason']}")

    if plan["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in plan["warnings"])

    if plan["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in plan["blockers"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "This phase does not delete files. Files may only be moved/deleted after backup, tests, and explicit verification.",
    ])

    return "\n".join(lines)


def write_safe_cleanup_plan_report(
    root: str | Path = ".",
    output_path: str | Path = "SAFE_CODEBASE_CLEANUP_PLAN_PHASE_16T2D.txt",
) -> Path:
    output = Path(output_path)
    output.write_text(build_safe_cleanup_plan_report(root), encoding="utf-8")
    return output


if __name__ == "__main__":
    output = write_safe_cleanup_plan_report(".")
    plan = build_safe_cleanup_plan(".")
    print(plan["status"])
    print(output)
