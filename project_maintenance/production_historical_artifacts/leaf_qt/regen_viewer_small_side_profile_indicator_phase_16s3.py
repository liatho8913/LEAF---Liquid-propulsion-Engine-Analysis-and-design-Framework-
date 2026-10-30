from __future__ import annotations

from typing import Any


def build_small_side_profile_indicator_state(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    payload = results.get("phase_16r2_side_profile_canvas_payload") or results.get("phase_16r1_side_profile_payload") or {}
    profile = payload.get("profile") if isinstance(payload, dict) else []

    available = isinstance(profile, list) and len(profile) >= 2

    return {
        "status": (
            "PASS_REGEN_VIEWER_SMALL_SIDE_PROFILE_INDICATOR_PHASE_16S3"
            if available
            else "WARN_REGEN_VIEWER_SMALL_SIDE_PROFILE_INDICATOR_NO_PROFILE_PHASE_16S3"
        ),
        "passed": available,
        "available": available,
        "profile_point_count": len(profile) if isinstance(profile, list) else 0,
        "selected_x": (
            results.get("selected_station_x")
            or results.get("viewer_selected_station_x")
            or 0.0
        ),
        "purpose": "Small side-profile station-position indicator only; not the main regen cross-section view.",
    }


def attach_small_side_profile_indicator_state(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    state = build_small_side_profile_indicator_state(results)

    results["phase_16s3_small_side_profile_status"] = state["status"]
    results["phase_16s3_small_side_profile_pass"] = state["passed"]
    results["phase_16s3_small_side_profile_available"] = state["available"]
    results["phase_16s3_small_side_profile_state"] = state

    return results
