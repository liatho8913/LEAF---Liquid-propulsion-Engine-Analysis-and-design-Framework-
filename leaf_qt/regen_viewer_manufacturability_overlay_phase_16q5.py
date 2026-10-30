from __future__ import annotations

from typing import Any

try:
    from regen_manufacturability_geometry_gate_phase_16q3 import (
        evaluate_manufacturability_geometry,
    )
except Exception:
    evaluate_manufacturability_geometry = None


def build_manufacturability_overlay(results: dict[str, Any], geometry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}
    if not isinstance(geometry, dict):
        geometry = {}

    merged = dict(results)
    merged.update(geometry)

    if evaluate_manufacturability_geometry is None:
        return {
            "status": "ERROR_REGEN_VIEWER_MANUFACTURABILITY_OVERLAY_PHASE_16Q5",
            "passed": False,
            "label": "MANUFACTURABILITY: ERROR",
            "details": ["Manufacturability gate import failed."],
        }

    verdict = evaluate_manufacturability_geometry(merged)

    details = []
    details.append(f"aspect_ratio={verdict.get('aspect_ratio')}")
    details.append(f"width={verdict.get('channel_width')}")
    details.append(f"height={verdict.get('channel_height')}")
    details.append(f"effective_rib_width={verdict.get('effective_rib_width')}")
    details.append(f"cooling_coverage={verdict.get('cooling_coverage')}")

    for blocker in verdict.get("blockers", []):
        details.append(f"BLOCKER: {blocker}")

    for warning in verdict.get("warnings", []):
        details.append(f"WARNING: {warning}")

    if verdict["passed"]:
        label = "MANUFACTURABILITY: PASS"
    else:
        label = "MANUFACTURABILITY: FAIL"

    return {
        "status": (
            "PASS_REGEN_VIEWER_MANUFACTURABILITY_OVERLAY_PHASE_16Q5"
            if verdict["passed"]
            else "FAIL_REGEN_VIEWER_MANUFACTURABILITY_OVERLAY_PHASE_16Q5"
        ),
        "passed": verdict["passed"],
        "label": label,
        "details": details,
        "verdict": verdict,
    }


def attach_manufacturability_overlay(results: dict[str, Any], geometry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    overlay = build_manufacturability_overlay(results, geometry)

    results["phase_16q5_manufacturability_overlay_status"] = overlay["status"]
    results["phase_16q5_manufacturability_overlay_pass"] = overlay["passed"]
    results["phase_16q5_manufacturability_overlay_label"] = overlay["label"]
    results["phase_16q5_manufacturability_overlay_details"] = overlay["details"]

    if not overlay["passed"]:
        results["regen_geometry_status"] = "FAIL"
        results["geometry_status"] = "FAIL"
        results["final_regen_design_verdict"] = "FAIL_REGEN_VIEWER_MANUFACTURABILITY_OVERLAY"

    return results
