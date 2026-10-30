from __future__ import annotations

from typing import Any


REQUIRED_PASS_KEYS = {
    "16Q.3 manufacturability gate": "phase_16q3_manufacturability_pass",
    "16Q.5 manufacturability overlay": "phase_16q5_manufacturability_overlay_pass",
}


def _truthy(value: Any) -> bool:
    return value is True or value == 1 or value == 1.0 or str(value).upper() == "TRUE"


def evaluate_manufacturability_retest(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    blockers = []

    for label, key in REQUIRED_PASS_KEYS.items():
        if not _truthy(results.get(key)):
            blockers.append(f"{label} has not passed: {key}")

    try:
        if float(results.get("phase_16q3_channel_aspect_ratio")) > 4.0:
            blockers.append("Aspect ratio exceeds 4.0.")
    except Exception:
        blockers.append("Aspect ratio is missing.")

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

    passed = len(blockers) == 0

    return {
        "status": (
            "PASS_REGEN_VIEWER_MANUFACTURABILITY_RETEST_PHASE_16Q6"
            if passed
            else "FAIL_REGEN_VIEWER_MANUFACTURABILITY_RETEST_PHASE_16Q6"
        ),
        "passed": passed,
        "blockers": blockers,
    }


def attach_manufacturability_retest(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    verdict = evaluate_manufacturability_retest(results)

    results["phase_16q6_manufacturability_retest_status"] = verdict["status"]
    results["phase_16q6_manufacturability_retest_pass"] = verdict["passed"]
    results["phase_16q6_manufacturability_retest_blockers"] = verdict["blockers"]

    return results
