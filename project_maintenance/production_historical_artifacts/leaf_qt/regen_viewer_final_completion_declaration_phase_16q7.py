from __future__ import annotations

from typing import Any


REQUIRED_KEYS = {
    "16P.23 viewer completion lock": "phase_16p23_final_completion_lock_pass",
    "16Q.3 manufacturability gate": "phase_16q3_manufacturability_pass",
    "16Q.5 manufacturability overlay": "phase_16q5_manufacturability_overlay_pass",
    "16Q.6 manufacturability retest": "phase_16q6_manufacturability_retest_pass",
}


def _truthy(value: Any) -> bool:
    return value is True or value == 1 or value == 1.0 or str(value).upper() == "TRUE"


def evaluate_final_viewer_completion_declaration(results: dict[str, Any]) -> dict[str, Any]:
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

    if results.get("regen_viewer_completion_lock") != "PASS":
        blockers.append("regen_viewer_completion_lock is not PASS.")

    if results.get("regen_viewer_complete_locked") is not True:
        blockers.append("regen_viewer_complete_locked is not True.")

    if results.get("phase_16p19_runtime_proof_stale_old_nudge") is True:
        blockers.append("Stale old automatic geometry is detected.")

    try:
        if float(results.get("viewer_channel_fit_ratio")) < 1.0:
            blockers.append("Viewer fit ratio is below 1.0.")
    except Exception:
        blockers.append("Viewer fit ratio is missing.")

    try:
        if float(results.get("viewer_cooling_coverage")) > 0.90:
            blockers.append("Viewer cooling coverage exceeds manufacturability limit 0.90.")
    except Exception:
        blockers.append("Viewer cooling coverage is missing.")

    try:
        if float(results.get("viewer_effective_rib_width")) < 0.00025:
            blockers.append("Viewer effective rib width is below 0.25 mm.")
    except Exception:
        blockers.append("Viewer effective rib width is missing.")

    try:
        if float(results.get("phase_16q3_channel_aspect_ratio")) > 4.0:
            blockers.append("Channel aspect ratio exceeds 4.0.")
    except Exception:
        blockers.append("Channel aspect ratio is missing.")

    passed = len(blockers) == 0

    return {
        "status": (
            "PASS_REGEN_VIEWER_FINAL_COMPLETION_DECLARATION_PHASE_16Q7"
            if passed
            else "FAIL_REGEN_VIEWER_FINAL_COMPLETION_DECLARATION_PHASE_16Q7"
        ),
        "passed": passed,
        "checks": checks,
        "blockers": blockers,
        "summary": (
            "Regen viewer is complete with manufacturability lock."
            if passed
            else "Regen viewer final completion declaration is blocked."
        ),
    }


def build_final_completion_declaration_report(results: dict[str, Any]) -> str:
    verdict = evaluate_final_viewer_completion_declaration(results)

    lines = [
        "LEAF PHASE 16Q.7 — FINAL REGEN VIEWER COMPLETION DECLARATION",
        "=============================================================",
        f"Status: {verdict['status']}",
        f"Passed: {verdict['passed']}",
        f"Summary: {verdict['summary']}",
        "",
        "GEOMETRY SUMMARY",
        "----------------",
        f"Width: {results.get('phase_16p19_runtime_proof_width')}",
        f"Height: {results.get('phase_16p19_runtime_proof_height')}",
        f"Aspect ratio: {results.get('phase_16q3_channel_aspect_ratio')}",
        f"Fit ratio: {results.get('viewer_channel_fit_ratio')}",
        f"Cooling coverage: {results.get('viewer_cooling_coverage')}",
        f"Effective rib width: {results.get('viewer_effective_rib_width')}",
        f"Geometry valid: {results.get('viewer_channel_geometry_valid')}",
        "",
        "LOCK CHECKS",
        "-----------",
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


def attach_final_completion_declaration(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    verdict = evaluate_final_viewer_completion_declaration(results)
    report = build_final_completion_declaration_report(results)

    results["phase_16q7_final_completion_declaration_status"] = verdict["status"]
    results["phase_16q7_final_completion_declaration_pass"] = verdict["passed"]
    results["phase_16q7_final_completion_declaration_blockers"] = verdict["blockers"]
    results["phase_16q7_final_completion_declaration_report"] = report

    if verdict["passed"]:
        results["regen_viewer_final_complete"] = True
        results["regen_viewer_final_completion_status"] = "PASS"
    else:
        results["regen_viewer_final_complete"] = False
        results["regen_viewer_final_completion_status"] = "FAIL"

    return results
