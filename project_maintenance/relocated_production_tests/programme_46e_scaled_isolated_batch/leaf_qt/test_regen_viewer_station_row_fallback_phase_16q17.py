from regen_viewer_station_row_fallback_phase_16q17 import (
    build_fallback_station_rows,
    attach_station_row_fallback,
)
from regen_viewer_authoritative_station_pipeline_phase_16q16 import (
    build_station_payload,
)


def main() -> int:
    results = {
        "number_of_coolant_channels": 40,
        "coolant_channel_width": 0.0012,
        "coolant_channel_height": 0.0025,
        "rib_width": 0.0005,
        "hot_gas_wall_thickness": 0.001104,
        "outer_wall_thickness": 0.002,
        "throat_radius": 0.01,
        "exit_radius": 0.0225,
    }

    rows = build_fallback_station_rows(results, station_count=11)

    assert len(rows) == 11
    assert rows[0]["station_x"] == 0.0
    assert rows[-1]["station_x"] == 1.0
    assert rows[0]["automatic_geometry"]["gas_radius"] < rows[-1]["automatic_geometry"]["gas_radius"]
    assert rows[-1]["automatic_geometry"]["channel_geometry_valid"] == 1.0

    attach_station_row_fallback(results, station_count=11)

    assert results["phase_16q17_station_fallback_applied"] is True
    assert len(results["regen_station_rows"]) == 11
    assert results["channel_topology_status"] == "TOPOLOGY_FALLBACK_PROFILE_AVAILABLE"

    payload = build_station_payload(results, selected_x=1.0)

    assert payload["passed"] is True
    assert payload["station_index"] == 10
    assert payload["geometry"]["gas_radius"] == 0.0225
    assert payload["gas_side"]["mach"] is not None
    assert payload["coolant"]["reynolds_number"] is not None

    print("PASS_REGEN_VIEWER_STATION_ROW_FALLBACK_PHASE_16Q17")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
