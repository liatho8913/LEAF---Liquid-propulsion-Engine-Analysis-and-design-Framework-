from regen_viewer_station_row_fallback_phase_16q17 import attach_station_row_fallback
from regen_viewer_authoritative_station_pipeline_phase_16q16 import attach_authoritative_station_payload
from regen_viewer_station_tab_population_phase_16q18 import (
    build_station_tab_payload,
    build_station_tab_text,
    attach_station_tab_payload,
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

    attach_station_row_fallback(results, station_count=11)
    attach_authoritative_station_payload(results, selected_x=1.0)

    payload = build_station_tab_payload(results)

    assert payload["passed"] is True
    assert payload["station_index"] == 10
    assert payload["mach"] is not None
    assert payload["coolant_velocity"] is not None
    assert payload["gas_radius"] == 0.0225

    text = build_station_tab_text(results)

    assert "STATION DATA" in text
    assert "GAS SIDE" in text
    assert "COOLANT SIDE" in text
    assert "STATION GEOMETRY" in text
    assert "Mach:" in text
    assert "Reynolds Number:" in text

    attach_station_tab_payload(results)

    assert results["phase_16q18_station_tab_pass"] is True
    assert results["phase_16q18_station_tab_status"] == (
        "PASS_REGEN_VIEWER_STATION_TAB_POPULATION_PHASE_16Q18"
    )

    print("PASS_REGEN_VIEWER_STATION_TAB_POPULATION_PHASE_16Q18")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
