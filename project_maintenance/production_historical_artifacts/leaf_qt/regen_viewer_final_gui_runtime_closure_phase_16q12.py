from __future__ import annotations

from typing import Any


def _truthy(value: Any) -> bool:
    return value is True or value == 1 or value == 1.0 or str(value).upper() == "TRUE"


def evaluate_final_gui_runtime_closure(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    blockers = []

    required = {
        "16Q.8 realism pass": "phase_16q8_geometry_realism_pass",
        "16Q.9 runtime report pass": "phase_16q9_realism_runtime_pass",
        "16Q.10 handover lock pass": "phase_16q10_auto_geometry_handover_lock_pass",
        "16Q.11 clean export available": "phase_16q11_clean_handover_export_available",
    }

    for label, key in required.items():
        if not _truthy(results.get(key)):
            blockers.append(f"{label} missing/failing: {key}")

    try:
        n = float(results.get("number_of_coolant_channels"))
        if not (35 <= n <= 60):
            blockers.append(f"Channel count outside closure envelope: {n}")
    except Exception:
        blockers.append("Channel count missing.")

    try:
        w = float(results.get("phase_16p19_runtime_proof_width"))
        if not (0.0010 <= w <= 0.0015):
            blockers.append(f"Width outside closure envelope: {w}")
    except Exception:
        blockers.append("Runtime width missing.")

    try:
        h = float(results.get("phase_16p19_runtime_proof_height"))
        if not (0.0020 <= h <= 0.0032):
            blockers.append(f"Height outside closure envelope: {h}")
    except Exception:
        blockers.append("Runtime height missing.")

    try:
        fit = float(results.get("viewer_channel_fit_ratio"))
        if fit < 1.0:
            blockers.append(f"Fit ratio below 1.0: {fit}")
    except Exception:
        blockers.append("Fit ratio missing.")

    try:
        coverage = float(results.get("viewer_cooling_coverage"))
        if coverage > 0.90:
            blockers.append(f"Cooling coverage above 0.90: {coverage}")
    except Exception:
        blockers.append("Cooling coverage missing.")

    try:
        rib = float(results.get("viewer_effective_rib_width"))
        if rib < 0.00025:
            blockers.append(f"Effective rib width below 0.25 mm: {rib}")
    except Exception:
        blockers.append("Effective rib width missing.")

    try:
        score = float(results.get("phase_16q9_realism_runtime_score"))
        if score < 65.0:
            blockers.append(f"Realism runtime score below 65: {score}")
    except Exception:
        blockers.append("Realism runtime score missing.")

    if results.get("phase_16p19_runtime_proof_stale_old_nudge") is True:
        blockers.append("Stale old automatic geometry still detected.")

    passed = len(blockers) == 0

    return {
        "status": (
            "PASS_REGEN_VIEWER_FINAL_GUI_RUNTIME_CLOSURE_PHASE_16Q12"
            if passed
            else "FAIL_REGEN_VIEWER_FINAL_GUI_RUNTIME_CLOSURE_PHASE_16Q12"
        ),
        "passed": passed,
        "blockers": blockers,
    }


def attach_final_gui_runtime_closure(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    verdict = evaluate_final_gui_runtime_closure(results)

    results["phase_16q12_final_gui_runtime_closure_status"] = verdict["status"]
    results["phase_16q12_final_gui_runtime_closure_pass"] = verdict["passed"]
    results["phase_16q12_final_gui_runtime_closure_blockers"] = verdict["blockers"]

    if verdict["passed"]:
        results["regen_viewer_closed"] = True
        results["regen_viewer_closure_status"] = "PASS"
    else:
        results["regen_viewer_closed"] = False
        results["regen_viewer_closure_status"] = "FAIL"

    return results
