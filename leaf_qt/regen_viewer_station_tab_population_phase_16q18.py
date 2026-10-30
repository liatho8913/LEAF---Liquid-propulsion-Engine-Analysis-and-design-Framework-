from __future__ import annotations

from typing import Any


def _fmt(value: Any, unit: str = "") -> str:
    if value in (None, "", "N/A"):
        return "N/A"
    try:
        f = float(value)
        if abs(f) >= 1000 or (abs(f) < 0.001 and f != 0):
            text = f"{f:.6e}"
        else:
            text = f"{f:.6f}".rstrip("0").rstrip(".")
        return f"{text} {unit}".strip()
    except Exception:
        return str(value)


def build_station_tab_payload(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    station_payload = results.get("phase_16q16_station_payload")
    if not isinstance(station_payload, dict):
        station_payload = {}

    gas = station_payload.get("gas_side") if isinstance(station_payload.get("gas_side"), dict) else {}
    coolant = station_payload.get("coolant") if isinstance(station_payload.get("coolant"), dict) else {}
    geometry = station_payload.get("geometry") if isinstance(station_payload.get("geometry"), dict) else {}

    payload = {
        "status": (
            "PASS_REGEN_VIEWER_STATION_TAB_POPULATION_PHASE_16Q18"
            if station_payload.get("passed")
            else "FAIL_REGEN_VIEWER_STATION_TAB_POPULATION_PHASE_16Q18"
        ),
        "passed": bool(station_payload.get("passed")),
        "station_index": station_payload.get("station_index", results.get("selected_station_index")),
        "selected_x": station_payload.get("selected_x", results.get("selected_station_x")),
        "nearest_x": station_payload.get("nearest_x", results.get("nearest_station_x")),
        "row_count": station_payload.get("row_count", results.get("phase_16q16_station_pipeline_row_count")),
        "source": geometry.get("source", results.get("station_profile", "N/A")),
        "warning": results.get("phase_16q17_station_fallback_warning", ""),
        "mach": gas.get("mach", results.get("viewer_station_mach")),
        "pressure": gas.get("static_pressure", results.get("viewer_station_static_pressure")),
        "temperature": gas.get("static_temperature", results.get("viewer_station_static_temperature")),
        "adiabatic_wall_temperature": gas.get("adiabatic_wall_temperature", results.get("viewer_station_adiabatic_wall_temperature")),
        "heat_flux": gas.get("heat_flux", results.get("viewer_station_heat_flux")),
        "hot_wall_temperature": gas.get("hot_wall_temperature", results.get("viewer_station_hot_wall_temperature")),
        "coolant_in": coolant.get("coolant_in", results.get("viewer_station_coolant_in")),
        "coolant_out": coolant.get("coolant_out", results.get("viewer_station_coolant_out")),
        "coolant_velocity": coolant.get("coolant_velocity", results.get("viewer_station_coolant_velocity")),
        "reynolds_number": coolant.get("reynolds_number", results.get("viewer_station_reynolds_number")),
        "pressure_drop_total": coolant.get("pressure_drop_total", results.get("viewer_station_pressure_drop_total")),
        "coolant_wall_temperature": coolant.get("coolant_wall_temperature", results.get("viewer_station_coolant_wall_temperature")),
        "gas_radius": geometry.get("gas_radius", results.get("viewer_station_gas_radius")),
        "channel_width": geometry.get("coolant_channel_width", geometry.get("channel_width", results.get("viewer_station_coolant_channel_width"))),
        "channel_height": geometry.get("coolant_channel_height", geometry.get("channel_height", results.get("viewer_station_coolant_channel_height"))),
        "effective_rib_width": geometry.get("effective_rib_width", results.get("viewer_station_effective_rib_width")),
        "fit_ratio": geometry.get("channel_fit_ratio", results.get("viewer_station_channel_fit_ratio")),
        "coverage": geometry.get("cooling_coverage", results.get("viewer_station_cooling_coverage")),
        "valid": geometry.get("channel_geometry_valid", results.get("viewer_station_channel_geometry_valid")),
    }

    return payload


def build_station_tab_text(results: dict[str, Any]) -> str:
    payload = build_station_tab_payload(results)

    lines = [
        "STATION DATA",
        "============",
        f"Status: {payload['status']}",
        f"Station Index: {_fmt(payload['station_index'])}",
        f"Selected x: {_fmt(payload['selected_x'], 'm')}",
        f"Nearest x: {_fmt(payload['nearest_x'], 'm')}",
        f"Row Count: {_fmt(payload['row_count'])}",
        f"Source: {payload['source']}",
    ]

    if payload.get("warning"):
        lines.extend(["", "WARNING", "-------", str(payload["warning"])])

    lines.extend([
        "",
        "GAS SIDE",
        "--------",
        f"Mach: {_fmt(payload['mach'])}",
        f"Pressure: {_fmt(payload['pressure'], 'Pa')}",
        f"Temperature: {_fmt(payload['temperature'], 'K')}",
        f"Adiabatic Wall Temperature: {_fmt(payload['adiabatic_wall_temperature'], 'K')}",
        f"Heat Flux: {_fmt(payload['heat_flux'], 'W/m^2')}",
        f"Hot Wall Temperature: {_fmt(payload['hot_wall_temperature'], 'K')}",
        "",
        "COOLANT SIDE",
        "------------",
        f"Coolant In: {_fmt(payload['coolant_in'], 'K')}",
        f"Coolant Out: {_fmt(payload['coolant_out'], 'K')}",
        f"Coolant Velocity: {_fmt(payload['coolant_velocity'], 'm/s')}",
        f"Reynolds Number: {_fmt(payload['reynolds_number'])}",
        f"Pressure Drop Total: {_fmt(payload['pressure_drop_total'], 'Pa')}",
        f"Coolant Wall Temperature: {_fmt(payload['coolant_wall_temperature'], 'K')}",
        "",
        "STATION GEOMETRY",
        "----------------",
        f"Gas Radius: {_fmt(payload['gas_radius'], 'm')}",
        f"Channel Width: {_fmt(payload['channel_width'], 'm')}",
        f"Channel Height: {_fmt(payload['channel_height'], 'm')}",
        f"Effective Rib Width: {_fmt(payload['effective_rib_width'], 'm')}",
        f"Fit Ratio: {_fmt(payload['fit_ratio'])}",
        f"Coverage: {_fmt(payload['coverage'])}",
        f"Valid: {_fmt(payload['valid'])}",
    ])

    return "\n".join(lines)


def attach_station_tab_payload(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    payload = build_station_tab_payload(results)
    text = build_station_tab_text(results)

    results["phase_16q18_station_tab_payload"] = payload
    results["phase_16q18_station_tab_text"] = text
    results["phase_16q18_station_tab_status"] = payload["status"]
    results["phase_16q18_station_tab_pass"] = payload["passed"]

    return results
