from __future__ import annotations

from typing import Any


STATION_ROW_KEYS = (
    "regen_station_rows",
    "regen_axial_station_rows",
    "axial_station_rows",
    "full_engine_regen_station_rows",
    "station_rows",
    "stations",
)


def _num(value: Any, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def extract_station_rows(results: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(results, dict):
        return []

    for key in STATION_ROW_KEYS:
        rows = results.get(key)
        if isinstance(rows, list) and rows:
            return [r for r in rows if isinstance(r, dict)]

    return []


def get_station_x(row: dict[str, Any]) -> float | None:
    return _num(
        row.get("station_x")
        or row.get("x")
        or row.get("axial_position")
        or row.get("selected_length")
        or row.get("length")
    )


def nearest_station_row(rows: list[dict[str, Any]], selected_x: float) -> tuple[int | None, dict[str, Any] | None]:
    if not rows:
        return None, None

    indexed = []
    for i, row in enumerate(rows):
        x = get_station_x(row)
        if x is not None:
            indexed.append((i, x, row))

    if not indexed:
        return 0, rows[0]

    best = min(indexed, key=lambda item: abs(item[1] - selected_x))
    return best[0], best[2]


def build_station_payload(results: dict[str, Any], selected_x: float | None = None) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    rows = extract_station_rows(results)

    if selected_x is None:
        selected_x = _num(
            results.get("viewer_selected_station_x")
            or results.get("selected_station_x")
            or results.get("selected_length")
            or 0.0,
            0.0,
        )

    index, row = nearest_station_row(rows, float(selected_x))

    if row is None:
        return {
            "status": "FAIL_REGEN_VIEWER_AUTHORITATIVE_STATION_PIPELINE_NO_ROWS_PHASE_16Q16",
            "passed": False,
            "row_count": 0,
            "selected_x": selected_x,
            "nearest_x": None,
            "station_index": None,
            "station_row": {},
            "blockers": ["No usable station rows were found in results."],
        }

    nearest_x = get_station_x(row)

    gas_side = {
        "mach": row.get("mach") or row.get("Mach") or row.get("M"),
        "static_pressure": row.get("static_pressure") or row.get("pressure") or row.get("p"),
        "static_temperature": row.get("static_temperature") or row.get("temperature") or row.get("T"),
        "adiabatic_wall_temperature": row.get("adiabatic_wall_temperature") or row.get("Taw"),
        "heat_flux": row.get("heat_flux") or row.get("q_dot") or row.get("q_flux"),
        "hot_wall_temperature": row.get("hot_gas_side_wall_temperature") or row.get("Twg"),
    }

    coolant = {
        "coolant_in": row.get("coolant_inlet_temperature") or row.get("coolant_in"),
        "coolant_out": row.get("coolant_outlet_temperature") or row.get("coolant_out"),
        "coolant_velocity": row.get("coolant_velocity"),
        "reynolds_number": row.get("reynolds_number") or row.get("coolant_reynolds_number"),
        "pressure_drop_total": row.get("pressure_drop_total") or row.get("coolant_pressure_drop"),
        "coolant_wall_temperature": row.get("coolant_side_wall_temperature") or row.get("Twc"),
    }

    geometry = (
        row.get("automatic_geometry")
        or row.get("geometry")
        or row.get("station_geometry")
        or row
    )

    return {
        "status": "PASS_REGEN_VIEWER_AUTHORITATIVE_STATION_PIPELINE_PHASE_16Q16",
        "passed": True,
        "row_count": len(rows),
        "selected_x": selected_x,
        "nearest_x": nearest_x,
        "station_index": index,
        "station_row": row,
        "gas_side": gas_side,
        "coolant": coolant,
        "geometry": geometry if isinstance(geometry, dict) else {},
        "blockers": [],
    }


def attach_authoritative_station_payload(
    results: dict[str, Any],
    selected_x: float | None = None,
) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    payload = build_station_payload(results, selected_x)

    results["phase_16q16_station_pipeline_status"] = payload["status"]
    results["phase_16q16_station_pipeline_pass"] = payload["passed"]
    results["phase_16q16_station_pipeline_row_count"] = payload["row_count"]
    results["phase_16q16_station_pipeline_selected_x"] = payload["selected_x"]
    results["phase_16q16_station_pipeline_nearest_x"] = payload["nearest_x"]
    results["phase_16q16_station_pipeline_station_index"] = payload["station_index"]
    results["phase_16q16_station_pipeline_blockers"] = payload["blockers"]
    results["phase_16q16_station_payload"] = payload

    if payload["passed"]:
        results["selected_station_x"] = payload["selected_x"]
        results["nearest_station_x"] = payload["nearest_x"]
        results["selected_station_index"] = payload["station_index"]
        results["station_profile"] = "regen_axial_profile"

        for key, value in payload["gas_side"].items():
            results[f"viewer_station_{key}"] = value

        for key, value in payload["coolant"].items():
            results[f"viewer_station_{key}"] = value

        geom = payload["geometry"]
        if isinstance(geom, dict):
            for key in (
                "gas_radius",
                "channel_width",
                "coolant_channel_width",
                "channel_height",
                "coolant_channel_height",
                "rib_width",
                "requested_rib_width",
                "effective_rib_width",
                "channel_fit_ratio",
                "cooling_coverage",
                "available_pitch",
                "requested_pitch",
                "channel_geometry_valid",
                "channel_count",
                "number_of_coolant_channels",
            ):
                if key in geom:
                    results[f"viewer_station_{key}"] = geom[key]

        results["channel_topology_status"] = "TOPOLOGY_STATION_DATA_AVAILABLE"
        results["channel_topology_severity"] = "INFO"
        results["channel_topology_reason"] = (
            f"{payload['row_count']} station rows available; selected nearest station x={payload['nearest_x']}."
        )
        results["channel_topology_transition_count"] = max(0, payload["row_count"] - 1)

    return results
