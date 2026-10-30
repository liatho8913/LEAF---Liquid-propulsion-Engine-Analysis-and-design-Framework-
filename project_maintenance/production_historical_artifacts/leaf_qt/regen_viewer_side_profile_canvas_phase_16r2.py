from __future__ import annotations

from typing import Any


def _num(value: Any, default=None):
    try:
        if value is None or value == "" or value == "N/A":
            return default
        return float(value)
    except Exception:
        return default


def build_side_profile_canvas_payload(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    payload = results.get("phase_16r1_side_profile_payload")
    if not isinstance(payload, dict):
        payload = {}

    profile = payload.get("profile") or []

    clean_profile = []
    for point in profile:
        if not isinstance(point, dict):
            continue
        x = _num(point.get("x"))
        r = _num(point.get("gas_radius"))
        if x is not None and r is not None:
            clean_profile.append({"x": x, "gas_radius": r})

    selected_x = _num(
        payload.get("selected_x")
        or results.get("selected_station_x")
        or results.get("viewer_selected_station_x"),
        0.0,
    )

    if not clean_profile:
        return {
            "status": "WARN_REGEN_VIEWER_SIDE_PROFILE_CANVAS_NO_PROFILE_PHASE_16R2",
            "passed": False,
            "available": False,
            "profile": [],
            "selected_x": selected_x,
            "x_min": 0.0,
            "x_max": 1.0,
            "r_max": 1.0,
        }

    x_values = [p["x"] for p in clean_profile]
    r_values = [p["gas_radius"] for p in clean_profile]

    return {
        "status": "PASS_REGEN_VIEWER_SIDE_PROFILE_CANVAS_PHASE_16R2",
        "passed": True,
        "available": True,
        "profile": clean_profile,
        "selected_x": selected_x,
        "x_min": min(x_values),
        "x_max": max(x_values),
        "r_max": max(r_values),
        "point_count": len(clean_profile),
    }


def attach_side_profile_canvas_payload(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    payload = build_side_profile_canvas_payload(results)

    results["phase_16r2_side_profile_canvas_payload"] = payload
    results["phase_16r2_side_profile_canvas_status"] = payload["status"]
    results["phase_16r2_side_profile_canvas_pass"] = payload["passed"]
    results["phase_16r2_side_profile_canvas_available"] = payload["available"]

    return results
