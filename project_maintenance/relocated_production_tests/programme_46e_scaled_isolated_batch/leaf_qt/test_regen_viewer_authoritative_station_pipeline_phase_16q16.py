from regen_viewer_authoritative_station_pipeline_phase_16q16 import (
    extract_station_rows,
    build_station_payload,
    attach_authoritative_station_payload,
)


def main() -> int:
    rows = [
        {
            "station_index": 0,
            "station_x": 0.0,
            "mach": 0.2,
            "static_pressure": 6.0e6,
            "static_temperature": 3000,
            "heat_flux": 4.0e6,
            "coolant_velocity": 12.0,
            "coolant_reynolds_number": 12000,
            "coolant_pressure_drop": 1.0e5,
            "automatic_geometry": {
                "gas_radius": 0.01,
                "coolant_channel_width": 0.0012,
                "coolant_channel_height": 0.0025,
                "rib_width": 0.0005,
                "number_of_coolant_channels": 40,
                "channel_geometry_valid": 1.0,
            },
        },
        {
            "station_index": 1,
            "station_x": 1.0,
            "mach": 3.0,
            "static_pressure": 1.0e5,
            "static_temperature": 1200,
            "heat_flux": 1.0e6,
            "coolant_velocity": 15.0,
            "coolant_reynolds_number": 15000,
            "coolant_pressure_drop": 2.0e5,
            "automatic_geometry": {
                "gas_radius": 0.0225,
                "coolant_channel_width": 0.0012,
                "coolant_channel_height": 0.0025,
                "rib_width": 0.0005,
                "number_of_coolant_channels": 40,
                "channel_geometry_valid": 1.0,
            },
        },
    ]

    results = {"regen_station_rows": rows}

    assert len(extract_station_rows(results)) == 2

    payload = build_station_payload(results, selected_x=0.9)

    assert payload["passed"] is True
    assert payload["station_index"] == 1
    assert payload["nearest_x"] == 1.0
    assert payload["gas_side"]["mach"] == 3.0
    assert payload["coolant"]["reynolds_number"] == 15000

    attach_authoritative_station_payload(results, selected_x=0.9)

    assert results["phase_16q16_station_pipeline_pass"] is True
    assert results["selected_station_index"] == 1
    assert results["viewer_station_mach"] == 3.0
    assert results["viewer_station_coolant_velocity"] == 15.0
    assert results["viewer_station_gas_radius"] == 0.0225
    assert results["channel_topology_status"] == "TOPOLOGY_STATION_DATA_AVAILABLE"

    no_rows = {}
    bad = build_station_payload(no_rows, selected_x=0.5)

    assert bad["passed"] is False
    assert "NO_ROWS" in bad["status"]

    print("PASS_REGEN_VIEWER_AUTHORITATIVE_STATION_PIPELINE_PHASE_16Q16")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
