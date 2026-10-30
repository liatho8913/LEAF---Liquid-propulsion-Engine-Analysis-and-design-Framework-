from __future__ import annotations

from typing import Any


REQUIRED_KEYS = {
    "16Q.8 geometry realism pass": "phase_16q8_geometry_realism_pass",
    "16Q.9 realism runtime report available": "phase_16q9_realism_runtime_report_available",
    "16Q.9 realism runtime pass": "phase_16q9_realism_runtime_pass",
}


def _truthy(value: Any) -> bool:
    return value is True or value == 1 or value == 1.0 or str(value).upper() == "TRUE"


def evaluate_auto_geometry_handover_lock(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    blockers = []
    checks = {}

    for label, key in REQUIRED_KEYS.items():
        passed = _truthy(results.get(key))
        checks[label] = {
            "key": key,
            "passed": passed,
            "value": results.get(key),
        }
        if not passed:
            blockers.append(f"{label} has not passed: {key}")

    try:
        if float(results.get("phase_16q9_realism_runtime_score")) < 65.0:
            blockers.append("Realism runtime score is below 65.")
    except Exception:
        blockers.append("Realism runtime score is missing.")

    try:
        if float(results.get("viewer_channel_fit_ratio")) < 1.0:
            blockers.append("Viewer fit ratio is below 1.0.")
    except Exception:
        blockers.append("Viewer fit ratio is missing.")

    try:
        if float(results.get("viewer_cooling_coverage")) > 0.90:
            blockers.append("Viewer cooling coverage exceeds 0.90.")
    except Exception:
        blockers.append("Viewer cooling coverage is missing.")

    try:
        if float(results.get("viewer_effective_rib_width")) < 0.00025:
            blockers.append("Viewer effective rib width is below 0.25 mm.")
    except Exception:
        blockers.append("Viewer effective rib width is missing.")

    if results.get("phase_16p19_runtime_proof_stale_old_nudge") is True:
        blockers.append("Stale old automatic geometry is still detected.")

    passed = len(blockers) == 0

    return {
        "status": (
            "PASS_REGEN_VIEWER_AUTO_GEOMETRY_HANDOVER_LOCK_PHASE_16Q10"
            if passed
            else "FAIL_REGEN_VIEWER_AUTO_GEOMETRY_HANDOVER_LOCK_PHASE_16Q10"
        ),
        "passed": passed,
        "checks": checks,
        "blockers": blockers,
    }


def build_auto_geometry_handover_lock_report(results: dict[str, Any]) -> str:
    verdict = evaluate_auto_geometry_handover_lock(results)

    lines = [
        "LEAF PHASE 16Q.10 — REGEN VIEWER / AUTO GEOMETRY HANDOVER LOCK",
        "================================================================",
        f"Status: {verdict['status']}",
        f"Passed: {verdict['passed']}",
        "",
        "HANDOVER GEOMETRY",
        "-----------------",
        f"Width: {results.get('phase_16p19_runtime_proof_width')}",
        f"Height: {results.get('phase_16p19_runtime_proof_height')}",
        f"Channel count: {results.get('number_of_coolant_channels')}",
        f"Fit ratio: {results.get('viewer_channel_fit_ratio')}",
        f"Cooling coverage: {results.get('viewer_cooling_coverage')}",
        f"Effective rib width: {results.get('viewer_effective_rib_width')}",
        f"Realism score: {results.get('phase_16q9_realism_runtime_score')}",
        "",
        "CHECKS",
        "------",
    ]

    for label, item in verdict["checks"].items():
        state = "PASS" if item["passed"] else "FAIL"
        lines.append(f"{state} | {label} | {item['key']} = {item['value']}")

    lines.extend(["", "BLOCKERS", "--------"])

    if verdict["blockers"]:
        for blocker in verdict["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None")

    return "\n".join(lines)


def attach_auto_geometry_handover_lock(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    verdict = evaluate_auto_geometry_handover_lock(results)
    report = build_auto_geometry_handover_lock_report(results)

    results["phase_16q10_auto_geometry_handover_lock_status"] = verdict["status"]
    results["phase_16q10_auto_geometry_handover_lock_pass"] = verdict["passed"]
    results["phase_16q10_auto_geometry_handover_lock_blockers"] = verdict["blockers"]
    results["phase_16q10_auto_geometry_handover_lock_report"] = report

    if verdict["passed"]:
        results["regen_viewer_auto_geometry_handover_ready"] = True
        results["regen_viewer_auto_geometry_handover_status"] = "PASS"
    else:
        results["regen_viewer_auto_geometry_handover_ready"] = False
        results["regen_viewer_auto_geometry_handover_status"] = "FAIL"

    return results
