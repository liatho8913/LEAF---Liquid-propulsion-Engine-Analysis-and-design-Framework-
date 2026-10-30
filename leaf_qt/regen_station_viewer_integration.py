"""
PHASE 16K.6 — Station Viewer Integration

Purpose:
- Link station/axial regen data into the completed viewer system.
- Produce a station viewer payload for inspection of geometry, thermal, and coolant fields.
- Does not alter geometry.
- Does not rerun solver.
- Does not alter Qt layout yet.
"""

PASS_STATUS = "PASS_REGEN_STATION_VIEWER_INTEGRATION_PHASE_16K6"
FAIL_STATUS = "FAIL_REGEN_STATION_VIEWER_INTEGRATION_PHASE_16K6"


STATION_KEYS = (
    "x",
    "station_index",
    "radius",
    "mach",
    "hot_gas_wall_temperature",
    "coolant_wall_temperature",
    "coolant_bulk_temperature",
    "heat_flux",
    "coolant_pressure",
    "coolant_pressure_drop",
    "coolant_reynolds",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
)


def attach_regen_station_viewer_integration(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k5_complete") is not True:
        blockers.append("Phase 16K.5 cross section viewer integration has not passed.")

    stations = _find_station_data(results)

    if not isinstance(stations, list) or not stations:
        stations = _build_fallback_station_data(results)

    if not isinstance(stations, list) or not stations:
        blockers.append("No station or fallback geometry station data could be produced.")

    station_rows = []
    if isinstance(stations, list):
        for idx, station in enumerate(stations):
            if isinstance(station, dict):
                station_rows.append(_normalise_station(idx, station))

    if not station_rows:
        blockers.append("Station rows are empty after normalisation.")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "source_phase": "16K.6",
            "visibility": "UI_REPORT_VIEW",
            "candidate_id": _candidate_id(results),
            "viewer_mode": "STATION_REGEN_INSPECTION",
            "station_count": len(station_rows),
            "columns": list(STATION_KEYS),
            "station_rows": station_rows,
            "presets": {
                "thermal": [
                    "x",
                    "hot_gas_wall_temperature",
                    "coolant_wall_temperature",
                    "coolant_bulk_temperature",
                    "heat_flux",
                ],
                "coolant": [
                    "x",
                    "coolant_pressure",
                    "coolant_pressure_drop",
                    "coolant_reynolds",
                ],
                "geometry": [
                    "x",
                    "radius",
                    "coolant_channel_width",
                    "coolant_channel_height",
                    "rib_width",
                    "hot_gas_wall_thickness",
                ],
                "flow": [
                    "x",
                    "mach",
                    "radius",
                ],
            },
            "read_only": True,
        }

    report = _build_report(status, blockers, payload)

    results["regen_station_viewer_integration_complete"] = True
    results["phase_16k6_complete"] = status == PASS_STATUS
    results["regen_station_viewer_integration_status"] = status
    results["phase_16k6_status"] = status
    results["regen_station_viewer_integration_blockers"] = blockers
    results["regen_station_viewer_payload"] = payload
    results["regen_station_viewer_integration_report"] = report
    results["regen_station_viewer_visibility"] = "UI_REPORT_VIEW"

    results["phase_16k7_viewer_completion_gate_allowed"] = status == PASS_STATUS

    return results


def _find_station_data(results):
    for key in (
        "regen_station_rows",
        "regen_axial_station_rows",
        "regen_station_table",
        "station_rows",
        "axial_station_rows",
        "regen_axial_results",
    ):
        value = results.get(key)
        if isinstance(value, list) and value:
            return value
    return []


def _build_fallback_station_data(results):
    geometry = {}
    for key in (
        "number_of_coolant_channels",
        "coolant_channel_width",
        "coolant_channel_height",
        "rib_width",
        "hot_gas_wall_thickness",
    ):
        if key in results:
            geometry[key] = results[key]

    if not geometry:
        return []

    return [
        {
            "station_index": 0,
            "x": 0.0,
            **geometry,
        }
    ]


def _normalise_station(index, station):
    row = {}

    for key in STATION_KEYS:
        row[key] = station.get(key)

    if row.get("station_index") is None:
        row["station_index"] = index

    if row.get("x") is None:
        row["x"] = station.get("axial_position") or station.get("x_m") or index

    return row


def _candidate_id(results):
    for key in (
        "regen_geometry_active_candidate_id",
        "regen_candidate_pending_application_candidate_id",
    ):
        value = results.get(key)
        if value:
            return value

    payload = results.get("regen_viewer_payload")
    if isinstance(payload, dict):
        return payload.get("candidate_id")

    return None


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16K.6 STATION VIEWER INTEGRATION",
        "=============================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Links station/axial regen data into the viewer system.",
        "- Produces thermal, coolant, geometry, and flow presets.",
        "- Produces read-only station inspection payload.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "- Does not alter Qt layout yet.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Station Viewer Payload:",
        f"- Created: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        f"- Station count: {(payload or {}).get('station_count')}",
        f"- Viewer mode: {(payload or {}).get('viewer_mode')}",
        "- Visibility: UI_REPORT_VIEW",
        "",
        "Next Required Phase:",
        "- 16K.7 Viewer Completion Gate.",
    ])

    return "\n".join(lines)
