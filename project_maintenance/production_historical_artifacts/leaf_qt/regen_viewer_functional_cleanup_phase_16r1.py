from __future__ import annotations

from typing import Any


USEFUL_GEOMETRY_KEYS = (
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "effective_rib_width",
    "channel_fit_ratio",
    "cooling_coverage",
    "channel_aspect_ratio",
    "gas_radius",
    "hot_gas_wall_thickness",
    "available_pitch",
    "required_pitch",
    "channel_geometry_valid",
)

USEFUL_STATION_KEYS = (
    "selected_station_index",
    "selected_station_x",
    "nearest_station_x",
    "viewer_station_mach",
    "viewer_station_static_pressure",
    "viewer_station_static_temperature",
    "viewer_station_heat_flux",
    "viewer_station_coolant_velocity",
    "viewer_station_reynolds_number",
    "viewer_station_pressure_drop_total",
)


def _valid(value: Any) -> bool:
    return value not in (None, "", "N/A", "None")


def select_geometry_payload(results: dict[str, Any], mode: str) -> dict[str, Any]:
    if not isinstance(results, dict):
        return {}

    mode = str(mode or "").lower()

    if "auto" in mode:
        for key in (
            "regen_ui_applied_geometry",
            "regen_geometry_commit_staged_geometry",
            "phase_16q25_auto_geometry_cache",
            "phase_16p2_automatic_geometry_candidate_geometry",
        ):
            value = results.get(key)
            if key == "phase_16q25_auto_geometry_cache" and isinstance(value, dict):
                value = value.get("geometry")
            if isinstance(value, dict) and value:
                return dict(value)

    for key in (
        "phase_16q24_manual_geometry_snapshot",
        "regen_manual_geometry_snapshot",
        "manual_geometry_snapshot",
        "phase_16p16_manual_geometry_snapshot",
    ):
        value = results.get(key)
        if isinstance(value, dict) and value:
            return dict(value)

    manual = {}
    for key in USEFUL_GEOMETRY_KEYS:
        value = results.get(key)
        if _valid(value):
            manual[key] = value

    return manual


def apply_geometry_mode(results: dict[str, Any], mode: str) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    mode = "automatic" if "auto" in str(mode).lower() else "manual"
    geometry = select_geometry_payload(results, mode)

    results["phase_16r1_selected_geometry_mode"] = mode
    results["regen_viewer_selected_geometry_mode"] = mode
    results["viewer_selected_geometry_mode"] = mode
    results["geometry_display_mode"] = mode

    if geometry:
        results["phase_16r1_active_geometry_payload"] = dict(geometry)
        results["phase_16r1_active_geometry_payload_available"] = True

        for key, value in geometry.items():
            if key not in ("source", "data_origin"):
                results[key] = value

        results["viewer_actual_geometry_source"] = mode
        results["viewer_geometry_source"] = mode
        results["phase_16r1_geometry_switch_status"] = (
            "PASS_REGEN_VIEWER_FUNCTIONAL_GEOMETRY_SWITCH_PHASE_16R1"
        )
    else:
        results["phase_16r1_active_geometry_payload_available"] = False
        results["phase_16r1_geometry_switch_status"] = (
            "WARN_REGEN_VIEWER_FUNCTIONAL_GEOMETRY_SWITCH_NO_PAYLOAD_PHASE_16R1"
        )

    return results


def build_clean_channel_summary(results: dict[str, Any]) -> str:
    lines = [
        "CHANNEL SUMMARY",
        "===============",
    ]

    labels = {
        "number_of_coolant_channels": "Channels",
        "coolant_channel_width": "Width",
        "coolant_channel_height": "Height",
        "rib_width": "Requested Rib",
        "effective_rib_width": "Effective Rib",
        "channel_fit_ratio": "Fit Ratio",
        "cooling_coverage": "Cooling Coverage",
        "channel_aspect_ratio": "Aspect Ratio",
        "available_pitch": "Available Pitch",
        "required_pitch": "Required Pitch",
        "channel_geometry_valid": "Geometry Valid",
    }

    for key in USEFUL_GEOMETRY_KEYS:
        value = results.get(key)
        if _valid(value):
            lines.append(f"{labels.get(key, key)}: {value}")

    return "\n".join(lines)


def build_clean_side_table(results: dict[str, Any]) -> str:
    lines = [
        "REGEN VIEWER DATA",
        "=================",
        "",
        build_clean_channel_summary(results),
        "",
        "STATION SUMMARY",
        "===============",
    ]

    labels = {
        "selected_station_index": "Station Index",
        "selected_station_x": "Selected x",
        "nearest_station_x": "Nearest x",
        "viewer_station_mach": "Mach",
        "viewer_station_static_pressure": "Pressure",
        "viewer_station_static_temperature": "Temperature",
        "viewer_station_heat_flux": "Heat Flux",
        "viewer_station_coolant_velocity": "Coolant Velocity",
        "viewer_station_reynolds_number": "Reynolds Number",
        "viewer_station_pressure_drop_total": "Pressure Drop",
    }

    for key in USEFUL_STATION_KEYS:
        value = results.get(key)
        if _valid(value):
            lines.append(f"{labels.get(key, key)}: {value}")

    return "\n".join(lines)


def should_hide_profile_dropdown(profile_items: list[str] | None) -> bool:
    if not profile_items:
        return True

    useful = [str(x).strip() for x in profile_items if str(x).strip()]
    return len(useful) <= 1


def build_side_profile_payload(results: dict[str, Any]) -> dict[str, Any]:
    rows = (
        results.get("regen_station_rows")
        or results.get("regen_axial_station_rows")
        or results.get("axial_station_rows")
        or []
    )

    profile = []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            geom = row.get("geometry") or row.get("automatic_geometry") or row
            x = None
            for x_key in ("station_x", "x", "selected_length"):
                if row.get(x_key) not in (None, "", "N/A"):
                    x = row.get(x_key)
                    break

            r = None
            if isinstance(geom, dict):
                for r_key in ("gas_radius", "radius"):
                    if geom.get(r_key) not in (None, "", "N/A"):
                        r = geom.get(r_key)
                        break
            if _valid(x) and _valid(r):
                profile.append({"x": float(x), "gas_radius": float(r)})

    selected_x = results.get("selected_station_x") or results.get("viewer_selected_station_x") or 0.0

    return {
        "status": (
            "PASS_REGEN_VIEWER_SIDE_PROFILE_PAYLOAD_PHASE_16R1"
            if profile
            else "WARN_REGEN_VIEWER_SIDE_PROFILE_PAYLOAD_EMPTY_PHASE_16R1"
        ),
        "profile": profile,
        "selected_x": float(selected_x),
        "available": bool(profile),
    }


def attach_functional_cleanup(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    mode = results.get("geometry_display_mode") or results.get("viewer_selected_geometry_mode") or "manual"
    apply_geometry_mode(results, mode)

    results["phase_16r1_clean_channel_summary"] = build_clean_channel_summary(results)
    results["phase_16r1_clean_side_table"] = build_clean_side_table(results)
    results["phase_16r1_side_profile_payload"] = build_side_profile_payload(results)
    results["phase_16r1_functional_cleanup_status"] = (
        "PASS_REGEN_VIEWER_FUNCTIONAL_CLEANUP_PHASE_16R1"
    )
    results["phase_16r1_functional_cleanup_pass"] = True

    return results
