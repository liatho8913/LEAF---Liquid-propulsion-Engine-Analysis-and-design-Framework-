from __future__ import annotations

import math
from typing import Any


def _num(value: Any, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _pick(results: dict[str, Any], *keys: str, default=None):
    for key in keys:
        value = results.get(key)
        if value not in (None, "", "N/A"):
            return value
    return default


def build_fallback_station_rows(results: dict[str, Any], station_count: int = 51) -> list[dict[str, Any]]:
    if not isinstance(results, dict):
        results = {}

    station_count = max(3, int(station_count))

    n = int(round(_num(_pick(results, "number_of_coolant_channels", "recommended_geometry_channels"), 40)))
    width = _num(_pick(results, "coolant_channel_width", "recommended_geometry_width", "phase_16p19_runtime_proof_width"), 0.0012)
    height = _num(_pick(results, "coolant_channel_height", "recommended_geometry_height", "phase_16p19_runtime_proof_height"), 0.0025)
    rib = _num(_pick(results, "rib_width", "recommended_geometry_rib"), 0.0005)
    wall = _num(_pick(results, "hot_gas_wall_thickness", "wall"), 0.001104)
    outer = _num(_pick(results, "outer_wall_thickness", "jacket"), 0.002)

    throat_radius = _num(_pick(results, "throat_radius", "minimum_gas_radius"), 0.01)
    exit_radius = _num(_pick(results, "exit_radius"), max(throat_radius * 2.25, 0.0225))

    rows: list[dict[str, Any]] = []

    for i in range(station_count):
        x = i / (station_count - 1)

        # Viewer-only monotonic radius profile:
        # starts at throat_radius and expands smoothly to exit_radius.
        smooth = x * x * (3.0 - 2.0 * x)
        gas_radius = throat_radius + (exit_radius - throat_radius) * smooth

        channel_mid_radius = gas_radius + wall + 0.5 * height
        available_pitch = (2.0 * math.pi * channel_mid_radius) / n
        requested_pitch = width + rib
        effective_rib = available_pitch - width
        fit_ratio = available_pitch / requested_pitch if requested_pitch > 0 else 0.0
        coolant_coverage = width / available_pitch if available_pitch > 0 else 0.0
        pitch_coverage = requested_pitch / available_pitch if available_pitch > 0 else 0.0
        valid = width > 0 and height > 0 and rib > 0 and effective_rib > 0 and fit_ratio >= 1.0

        mach = 0.2 + 2.8 * smooth
        static_pressure = 6.0e6 * (1.0 - smooth) + 1.0e5 * smooth
        static_temperature = 3000.0 * (1.0 - smooth) + 1200.0 * smooth
        heat_flux = 4.0e6 * (1.0 - smooth) + 1.0e6 * smooth

        coolant_velocity = 12.0 + 3.0 * smooth
        reynolds = 12000.0 + 3000.0 * smooth
        pressure_drop = 1.0e5 + 1.0e5 * smooth

        geometry = {
            "source": "viewer_fallback_station_profile",
            "data_origin": "fallback_generated_from_applied_geometry",
            "selected_length": x,
            "gas_radius": gas_radius,
            "wall": wall,
            "hot_gas_wall_thickness": wall,
            "jacket": outer,
            "outer_wall_thickness": outer,
            "channel_count": n,
            "number_of_coolant_channels": n,
            "channel_width": width,
            "coolant_channel_width": width,
            "channel_height": height,
            "coolant_channel_height": height,
            "requested_rib_width": rib,
            "rib_width": rib,
            "requested_pitch": requested_pitch,
            "required_pitch": requested_pitch,
            "available_pitch": available_pitch,
            "effective_rib_width": effective_rib,
            "channel_fit_ratio": fit_ratio,
            "cooling_coverage": coolant_coverage,
            "pitch_coverage": pitch_coverage,
            "channel_geometry_valid": 1.0 if valid else 0.0,
            "channel_aspect_ratio": height / width if width > 0 else None,
        }

        rows.append({
            "station_index": i,
            "station_x": x,
            "generated_by_fallback": True,
            "fallback_profile_warning": "Viewer-only fallback profile. Not a full solver axial solution.",
            "mach": mach,
            "static_pressure": static_pressure,
            "static_temperature": static_temperature,
            "adiabatic_wall_temperature": static_temperature * 1.08,
            "heat_flux": heat_flux,
            "coolant_velocity": coolant_velocity,
            "coolant_reynolds_number": reynolds,
            "coolant_pressure_drop": pressure_drop,
            "coolant_inlet_temperature": 298.0,
            "coolant_outlet_temperature": 298.0 + 80.0 * smooth,
            "coolant_side_wall_temperature": 600.0 + 80.0 * (1.0 - smooth),
            "automatic_geometry": geometry,
            "geometry": geometry,
        })

    return rows


def attach_station_row_fallback(results: dict[str, Any], station_count: int = 51) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    existing = (
        results.get("regen_station_rows")
        or results.get("regen_axial_station_rows")
        or results.get("axial_station_rows")
        or results.get("full_engine_regen_station_rows")
        or []
    )

    if isinstance(existing, list) and existing:
        results["phase_16q17_station_fallback_status"] = (
            "PASS_REGEN_VIEWER_STATION_ROW_FALLBACK_NOT_REQUIRED_PHASE_16Q17"
        )
        results["phase_16q17_station_fallback_applied"] = False
        return results

    rows = build_fallback_station_rows(results, station_count=station_count)

    results["regen_station_rows"] = rows
    results["regen_axial_station_rows"] = rows
    results["phase_16q17_station_fallback_status"] = (
        "PASS_REGEN_VIEWER_STATION_ROW_FALLBACK_PHASE_16Q17"
    )
    results["phase_16q17_station_fallback_applied"] = True
    results["phase_16q17_station_fallback_row_count"] = len(rows)
    results["phase_16q17_station_fallback_warning"] = (
        "Fallback rows are viewer-only geometry/profile rows, not full solver station data."
    )

    results["channel_topology_status"] = "TOPOLOGY_FALLBACK_PROFILE_AVAILABLE"
    results["channel_topology_severity"] = "INFO"
    results["channel_topology_reason"] = (
        f"{len(rows)} viewer fallback station rows generated from applied geometry."
    )
    results["channel_topology_transition_count"] = max(0, len(rows) - 1)

    return results
