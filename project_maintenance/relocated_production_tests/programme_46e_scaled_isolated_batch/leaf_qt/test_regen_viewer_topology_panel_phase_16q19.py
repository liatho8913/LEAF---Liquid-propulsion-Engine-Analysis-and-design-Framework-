from regen_viewer_station_row_fallback_phase_16q17 import attach_station_row_fallback
from regen_viewer_authoritative_station_pipeline_phase_16q16 import attach_authoritative_station_payload
from regen_viewer_station_tab_population_phase_16q18 import attach_station_tab_payload
from regen_viewer_topology_panel_phase_16q19 import (
    build_topology_panel_payload,
    build_topology_panel_text,
    attach_topology_panel_payload,
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
    attach_authoritative_station_payload(results, selected_x=0.5)
    attach_station_tab_payload(results)

    payload = build_topology_panel_payload(results)

    assert payload["passed"] is True
    assert payload["fallback_applied"] is True
    assert payload["row_count"] == 11
    assert payload["status"] == "TOPOLOGY_FALLBACK_PROFILE_AVAILABLE"

    text = build_topology_panel_text(results)

    assert "TOPOLOGY / STATION PROFILE" in text
    assert "Fallback Applied: True" in text
    assert "viewer-only" in text

    attach_topology_panel_payload(results)

    assert results["phase_16q19_topology_panel_pass"] is True
    assert results["phase_16q19_topology_panel_status"] == (
        "PASS_REGEN_VIEWER_TOPOLOGY_PANEL_PHASE_16Q19"
    )
    assert results["channel_topology_status"] == "TOPOLOGY_FALLBACK_PROFILE_AVAILABLE"

    no_profile = {}
    bad = build_topology_panel_payload(no_profile)

    assert bad["passed"] is False
    assert bad["status"] == "TOPOLOGY_UNKNOWN"

    print("PASS_REGEN_VIEWER_TOPOLOGY_PANEL_PHASE_16Q19")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
