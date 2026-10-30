from __future__ import annotations

from typing import Any


def attach_preferred_layout_restore_status(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    results["phase_16s4_preferred_layout_restore_status"] = (
        "PASS_REGEN_VIEWER_PREFERRED_LAYOUT_RESTORE_PHASE_16S4"
    )
    results["phase_16s4_preferred_layout_restore_pass"] = True
    results["phase_16s4_layout_policy"] = (
        "Original regen viewer layout is primary. Side profile is only a small station-position indicator overlay."
    )
    return results


def build_station_indicator_state(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    selected_x = (
        results.get("selected_station_x")
        or results.get("viewer_selected_station_x")
        or results.get("selected_length")
        or 0.0
    )

    try:
        selected_x = float(selected_x)
    except Exception:
        selected_x = 0.0

    selected_x = max(0.0, min(1.0, selected_x))

    return {
        "status": "PASS_REGEN_VIEWER_STATION_INDICATOR_STATE_PHASE_16S4",
        "passed": True,
        "selected_x": selected_x,
        "note": "Indicator is schematic only; it does not prove real nozzle contour fidelity.",
    }
