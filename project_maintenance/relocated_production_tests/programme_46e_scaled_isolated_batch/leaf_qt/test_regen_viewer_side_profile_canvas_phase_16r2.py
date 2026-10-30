from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_functional_cleanup_phase_16r1 import attach_functional_cleanup
from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_side_profile_canvas_phase_16r2 import (
    build_side_profile_canvas_payload,
    attach_side_profile_canvas_payload,
)


def main() -> int:
    results = {
        "manual_geometry_snapshot": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
        },
        "regen_station_rows": [
            {"station_x": 0.0, "geometry": {"gas_radius": 0.01}},
            {"station_x": 0.5, "geometry": {"gas_radius": 0.014}},
            {"station_x": 1.0, "geometry": {"gas_radius": 0.0225}},
        ],
        "selected_station_x": 0.5,
    }

    attach_functional_cleanup(results)

    payload = build_side_profile_canvas_payload(results)

    assert payload["passed"] is True
    assert payload["available"] is True
    assert payload["point_count"] == 3
    assert payload["selected_x"] == 0.5
    assert payload["x_min"] == 0.0
    assert payload["x_max"] == 1.0
    assert payload["r_max"] == 0.0225

    attach_side_profile_canvas_payload(results)

    assert results["phase_16r2_side_profile_canvas_pass"] is True
    assert results["phase_16r2_side_profile_canvas_available"] is True

    print("PASS_REGEN_VIEWER_SIDE_PROFILE_CANVAS_PHASE_16R2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
