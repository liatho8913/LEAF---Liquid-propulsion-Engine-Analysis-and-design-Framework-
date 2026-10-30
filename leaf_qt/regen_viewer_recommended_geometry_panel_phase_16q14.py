from __future__ import annotations

from typing import Any


def _get(results: dict[str, Any], geometry: dict[str, Any], *keys: str, default=None):
    for key in keys:
        if isinstance(geometry, dict) and geometry.get(key) not in (None, ""):
            return geometry.get(key)
        if isinstance(results, dict) and results.get(key) not in (None, ""):
            return results.get(key)
    return default


def build_recommended_geometry_payload(
    results: dict[str, Any],
    geometry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}
    if geometry is None or not isinstance(geometry, dict):
        geometry = {}

    payload = {
        "status": "APPLIED_AUTOMATIC_GEOMETRY",
        "channels": _get(results, geometry, "number_of_coolant_channels", "channel_count", default="N/A"),
        "width": _get(results, geometry, "coolant_channel_width", "channel_width", "phase_16p19_runtime_proof_width", default="N/A"),
        "height": _get(results, geometry, "coolant_channel_height", "channel_height", "phase_16p19_runtime_proof_height", default="N/A"),
        "rib": _get(results, geometry, "rib_width", "requested_rib_width", default="N/A"),
        "effective_rib": _get(results, geometry, "effective_rib_width", "viewer_effective_rib_width", default="N/A"),
        "pitch": _get(results, geometry, "required_pitch", "requested_pitch", default="N/A"),
        "available_pitch": _get(results, geometry, "available_pitch", default="N/A"),
        "fit_ratio": _get(results, geometry, "channel_fit_ratio", "viewer_channel_fit_ratio", default="N/A"),
        "coverage": _get(results, geometry, "cooling_coverage", "viewer_cooling_coverage", default="N/A"),
        "valid": _get(results, geometry, "channel_geometry_valid", "viewer_channel_geometry_valid", default="N/A"),
        "manufacturability": _get(
            results,
            geometry,
            "phase_16q3_manufacturability_status",
            "phase_16q5_manufacturability_overlay_label",
            default="N/A",
        ),
        "realism_score": _get(
            results,
            geometry,
            "phase_16q8_geometry_realism_score",
            "phase_16q9_realism_runtime_score",
            "geometry_realism_score",
            default="N/A",
        ),
    }

    missing = [
        key for key, value in payload.items()
        if key not in ("status",) and value in (None, "", "N/A")
    ]

    payload["complete"] = len(missing) == 0
    payload["missing"] = missing

    return payload


def attach_recommended_geometry_payload(
    results: dict[str, Any],
    geometry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    payload = build_recommended_geometry_payload(results, geometry)

    results["phase_16q14_recommended_geometry_payload"] = payload
    results["phase_16q14_recommended_geometry_payload_available"] = True
    results["phase_16q14_recommended_geometry_panel_status"] = (
        "PASS_REGEN_VIEWER_RECOMMENDED_GEOMETRY_PANEL_PHASE_16Q14"
        if payload["complete"]
        else "WARN_REGEN_VIEWER_RECOMMENDED_GEOMETRY_PANEL_INCOMPLETE_PHASE_16Q14"
    )

    results["recommended_geometry_status"] = payload["status"]
    results["recommended_geometry_channels"] = payload["channels"]
    results["recommended_geometry_width"] = payload["width"]
    results["recommended_geometry_height"] = payload["height"]
    results["recommended_geometry_rib"] = payload["rib"]
    results["recommended_geometry_effective_rib"] = payload["effective_rib"]
    results["recommended_geometry_pitch"] = payload["pitch"]
    results["recommended_geometry_available_pitch"] = payload["available_pitch"]
    results["recommended_geometry_fit_ratio"] = payload["fit_ratio"]
    results["recommended_geometry_coverage"] = payload["coverage"]
    results["recommended_geometry_valid"] = payload["valid"]
    results["recommended_geometry_manufacturability"] = payload["manufacturability"]
    results["recommended_geometry_realism_score"] = payload["realism_score"]

    return results


def build_recommended_geometry_panel_text(results: dict[str, Any]) -> str:
    payload = results.get("phase_16q14_recommended_geometry_payload")
    if not isinstance(payload, dict):
        payload = build_recommended_geometry_payload(results)

    lines = [
        "RECOMMENDED GEOMETRY",
        "====================",
        f"Status: {payload.get('status')}",
        f"Channels: {payload.get('channels')}",
        f"Width: {payload.get('width')}",
        f"Height: {payload.get('height')}",
        f"Rib: {payload.get('rib')}",
        f"Pitch: {payload.get('pitch')}",
        f"Available Pitch: {payload.get('available_pitch')}",
        f"Effective Rib: {payload.get('effective_rib')}",
        f"Fit Ratio: {payload.get('fit_ratio')}",
        f"Coverage: {payload.get('coverage')}",
        f"Valid: {payload.get('valid')}",
        f"Manufacturability: {payload.get('manufacturability')}",
        f"Realism Score: {payload.get('realism_score')}",
    ]

    missing = payload.get("missing") or []
    if missing:
        lines.append("")
        lines.append("Missing:")
        for item in missing:
            lines.append(f"- {item}")

    return "\n".join(lines)
