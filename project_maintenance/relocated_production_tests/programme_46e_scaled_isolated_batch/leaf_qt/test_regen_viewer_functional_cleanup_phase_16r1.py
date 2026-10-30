from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_functional_cleanup_phase_16r1 import (
    apply_geometry_mode,
    build_clean_channel_summary,
    build_clean_side_table,
    should_hide_profile_dropdown,
    build_side_profile_payload,
    attach_functional_cleanup,
)


def main() -> int:
    results = {
        "manual_geometry_snapshot": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
        },
        "regen_ui_applied_geometry": {
            "number_of_coolant_channels": 40,
            "coolant_channel_width": 0.0012,
            "coolant_channel_height": 0.0025,
            "rib_width": 0.0005,
            "channel_fit_ratio": 1.14,
            "channel_geometry_valid": 1.0,
        },
        "regen_station_rows": [
            {"station_x": 0.0, "geometry": {"gas_radius": 0.01}},
            {"station_x": 1.0, "geometry": {"gas_radius": 0.0225}},
        ],
        "viewer_station_mach": 2.5,
    }

    apply_geometry_mode(results, "automatic")
    assert results["number_of_coolant_channels"] == 40
    assert results["coolant_channel_width"] == 0.0012

    apply_geometry_mode(results, "manual")
    assert results["number_of_coolant_channels"] == 80
    assert results["coolant_channel_width"] == 0.0015

    summary = build_clean_channel_summary(results)
    assert "CHANNEL SUMMARY" in summary
    assert "Channels: 80" in summary
    assert "N/A" not in summary

    table = build_clean_side_table(results)
    assert "REGEN VIEWER DATA" in table
    assert "Mach: 2.5" in table

    assert should_hide_profile_dropdown(["Base"]) is True
    assert should_hide_profile_dropdown(["Base", "Solver Axial Profile"]) is False

    side = build_side_profile_payload(results)
    assert side["available"] is True
    assert len(side["profile"]) == 2

    attach_functional_cleanup(results)
    assert results["phase_16r1_functional_cleanup_pass"] is True

    print("PASS_REGEN_VIEWER_FUNCTIONAL_CLEANUP_PHASE_16R1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
