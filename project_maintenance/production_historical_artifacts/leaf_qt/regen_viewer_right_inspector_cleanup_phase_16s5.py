from __future__ import annotations

from typing import Any


def _valid(value: Any) -> bool:
    return value not in (None, "", "N/A", "None")


def _fmt(value: Any) -> str:
    if not _valid(value):
        return "N/A"
    try:
        f = float(value)
        if abs(f) >= 1000 or (0 < abs(f) < 0.001):
            return f"{f:.6e}"
        return f"{f:.6f}".rstrip("0").rstrip(".")
    except Exception:
        return str(value)


INSPECTOR_SECTIONS = {
    "Overview": (
        ("Overall", "regen_overall_status"),
        ("Geometry", "regen_geometry_status"),
        ("Thermal", "thermal_status"),
        ("Coolant", "coolant_status"),
        ("Material", "material_status"),
        ("Final Verdict", "final_regen_design_verdict"),
        ("Geometry Source", "viewer_actual_geometry_source"),
        ("Display Mode", "geometry_display_mode"),
    ),
    "Geometry": (
        ("Channels", "number_of_coolant_channels"),
        ("Gas Radius", "gas_radius"),
        ("Wall Thickness", "hot_gas_wall_thickness"),
        ("Channel Width", "coolant_channel_width"),
        ("Channel Height", "coolant_channel_height"),
        ("Requested Rib", "rib_width"),
        ("Effective Rib", "effective_rib_width"),
        ("Required Pitch", "required_pitch"),
        ("Available Pitch", "available_pitch"),
        ("Fit Ratio", "channel_fit_ratio"),
        ("Cooling Coverage", "cooling_coverage"),
        ("Aspect Ratio", "channel_aspect_ratio"),
        ("Geometry Valid", "channel_geometry_valid"),
    ),
    "Station": (
        ("Station Index", "selected_station_index"),
        ("Selected x", "selected_station_x"),
        ("Nearest x", "nearest_station_x"),
        ("Mach", "viewer_station_mach"),
        ("Pressure", "viewer_station_static_pressure"),
        ("Temperature", "viewer_station_static_temperature"),
        ("Heat Flux", "viewer_station_heat_flux"),
        ("Coolant Velocity", "viewer_station_coolant_velocity"),
        ("Reynolds Number", "viewer_station_reynolds_number"),
        ("Pressure Drop", "viewer_station_pressure_drop_total"),
    ),
    "Validation": (
        ("Runtime Consistency", "phase_16q20_final_runtime_consistency_status"),
        ("GUI Acceptance", "phase_16q28_gui_runtime_acceptance_status"),
        ("Geometry Switch", "phase_16r1_geometry_switch_status"),
        ("Preferred Layout", "phase_16s4_preferred_layout_restore_status"),
        ("Topology", "channel_topology_status"),
        ("Topology Reason", "channel_topology_reason"),
    ),
    "Sources": (
        ("Source Mode", "source_mode"),
        ("Source Gate", "source_gate"),
        ("Material Source", "material_source"),
        ("Reference Verdict", "reference_verdict"),
        ("Source Maturity", "source_maturity_status"),
    ),
    "Reference": (
        ("Reference Engine", "reference_engine"),
        ("Reference Status", "reference_status"),
        ("Comparison Status", "comparison_status"),
    ),
    "Export": (
        ("Station Dump", "phase_16p18_geometry_debug_export_status"),
        ("GUI Acceptance Report", "phase_16q29_copy_gui_acceptance_report_status"),
        ("Closure Handover", "phase_16q30_final_closure_handover_status"),
    ),
}


def build_clean_inspector_section(results: dict[str, Any], section: str) -> list[tuple[str, str]]:
    if not isinstance(results, dict):
        results = {}

    rows = []
    for label, key in INSPECTOR_SECTIONS.get(section, ()):
        value = results.get(key)
        if _valid(value):
            rows.append((label, _fmt(value)))

    return rows


def build_clean_inspector_payload(results: dict[str, Any]) -> dict[str, Any]:
    sections = {}
    total_rows = 0

    for section in INSPECTOR_SECTIONS:
        rows = build_clean_inspector_section(results, section)
        if rows:
            sections[section] = rows
            total_rows += len(rows)

    return {
        "status": "PASS_REGEN_VIEWER_RIGHT_INSPECTOR_CLEANUP_PHASE_16S5",
        "passed": True,
        "sections": sections,
        "section_count": len(sections),
        "row_count": total_rows,
    }


def build_clean_inspector_text(results: dict[str, Any], section: str = "Overview") -> str:
    rows = build_clean_inspector_section(results, section)

    lines = [
        section.upper(),
        "=" * len(section),
    ]

    if not rows:
        lines.append("No populated values for this section.")
    else:
        for label, value in rows:
            lines.append(f"{label}: {value}")

    return "\n".join(lines)


def attach_right_inspector_cleanup(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    payload = build_clean_inspector_payload(results)

    results["phase_16s5_right_inspector_cleanup_status"] = payload["status"]
    results["phase_16s5_right_inspector_cleanup_pass"] = payload["passed"]
    results["phase_16s5_right_inspector_payload"] = payload
    results["phase_16s5_right_inspector_section_count"] = payload["section_count"]
    results["phase_16s5_right_inspector_row_count"] = payload["row_count"]

    return results
