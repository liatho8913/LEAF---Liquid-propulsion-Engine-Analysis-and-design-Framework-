"""
LEAF Phase 16Q.1
Regen Viewer GUI Runtime Audit

Purpose:
- Produce a compact GUI/runtime audit from viewer results.
- This is used after launching the actual GUI and clicking automatic/apply/copy.
"""

from __future__ import annotations

from typing import Any


REQUIRED_RESULT_KEYS = [
    "phase_16p19_runtime_proof_banner",
    "phase_16p20_final_runtime_signoff_status",
    "phase_16p21_runtime_signoff_report_available",
    "phase_16p22_gui_runtime_checklist_status",
    "phase_16p23_final_completion_lock_status",
    "regen_viewer_completion_lock",
    "regen_viewer_complete_locked",
]


def build_gui_runtime_audit(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    blockers = []
    checks = {}

    for key in REQUIRED_RESULT_KEYS:
        value = results.get(key)
        present = value is not None
        checks[key] = {"present": present, "value": value}
        if not present:
            blockers.append(f"Missing required runtime key: {key}")

    if results.get("regen_viewer_completion_lock") != "PASS":
        blockers.append("Regen viewer completion lock is not PASS.")

    if results.get("regen_viewer_complete_locked") is not True:
        blockers.append("regen_viewer_complete_locked is not True.")

    if results.get("phase_16p19_runtime_proof_stale_old_nudge") is True:
        blockers.append("Old stale automatic geometry is still detected.")

    if results.get("phase_16p19_runtime_proof_fit_solved") is not True:
        blockers.append("Runtime proof does not confirm fit-solved geometry.")

    passed = len(blockers) == 0

    return {
        "status": (
            "PASS_REGEN_VIEWER_GUI_RUNTIME_AUDIT_PHASE_16Q1"
            if passed
            else "FAIL_REGEN_VIEWER_GUI_RUNTIME_AUDIT_PHASE_16Q1"
        ),
        "passed": passed,
        "checks": checks,
        "blockers": blockers,
    }


def build_gui_runtime_audit_report(results: dict[str, Any]) -> str:
    audit = build_gui_runtime_audit(results)

    lines = [
        "LEAF PHASE 16Q.1 — REGEN VIEWER GUI RUNTIME AUDIT",
        "==================================================",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        "",
        "KEY RUNTIME VALUES",
        "------------------",
        f"Runtime proof banner: {results.get('phase_16p19_runtime_proof_banner')}",
        f"Runtime signoff status: {results.get('phase_16p20_final_runtime_signoff_status')}",
        f"Runtime report available: {results.get('phase_16p21_runtime_signoff_report_available')}",
        f"GUI checklist status: {results.get('phase_16p22_gui_runtime_checklist_status')}",
        f"Completion lock status: {results.get('phase_16p23_final_completion_lock_status')}",
        f"Completion lock: {results.get('regen_viewer_completion_lock')}",
        f"Complete locked: {results.get('regen_viewer_complete_locked')}",
        "",
        "GEOMETRY VALUES",
        "---------------",
        f"Width: {results.get('phase_16p19_runtime_proof_width')}",
        f"Height: {results.get('phase_16p19_runtime_proof_height')}",
        f"Fit ratio: {results.get('viewer_channel_fit_ratio')}",
        f"Cooling coverage: {results.get('viewer_cooling_coverage')}",
        f"Effective rib width: {results.get('viewer_effective_rib_width')}",
        f"Geometry valid: {results.get('viewer_channel_geometry_valid')}",
        "",
        "BLOCKERS",
        "--------",
    ]

    if audit["blockers"]:
        for blocker in audit["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None")

    return "\n".join(lines)


def attach_gui_runtime_audit(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    audit = build_gui_runtime_audit(results)
    report = build_gui_runtime_audit_report(results)

    results["phase_16q1_gui_runtime_audit_status"] = audit["status"]
    results["phase_16q1_gui_runtime_audit_pass"] = audit["passed"]
    results["phase_16q1_gui_runtime_audit_blockers"] = audit["blockers"]
    results["phase_16q1_gui_runtime_audit_report"] = report

    return results
