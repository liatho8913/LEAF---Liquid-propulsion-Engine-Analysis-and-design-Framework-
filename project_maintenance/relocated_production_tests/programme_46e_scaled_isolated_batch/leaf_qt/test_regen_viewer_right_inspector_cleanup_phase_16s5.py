from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_right_inspector_cleanup_phase_16s5 import (
    build_clean_inspector_section,
    build_clean_inspector_payload,
    build_clean_inspector_text,
    attach_right_inspector_cleanup,
)


def main() -> int:
    results = {
        "regen_overall_status": "PASS",
        "regen_geometry_status": "PASS",
        "final_regen_design_verdict": "PASS_VIEWER_PHYSICAL_GEOMETRY_VALID",
        "viewer_actual_geometry_source": "automatic",
        "number_of_coolant_channels": 40,
        "coolant_channel_width": 0.0012,
        "coolant_channel_height": 0.0025,
        "rib_width": 0.0005,
        "effective_rib_width": 0.00074056,
        "channel_fit_ratio": 1.1415,
        "cooling_coverage": 0.876,
        "viewer_station_mach": 2.5,
        "viewer_station_static_pressure": 101325,
        "viewer_station_reynolds_number": 12000,
        "source_mode": "N/A",
    }

    overview = build_clean_inspector_section(results, "Overview")
    geometry = build_clean_inspector_section(results, "Geometry")
    station = build_clean_inspector_section(results, "Station")
    sources = build_clean_inspector_section(results, "Sources")

    assert ("Overall", "PASS") in overview
    assert ("Channels", "40") in geometry
    assert ("Mach", "2.5") in station
    assert sources == []

    text = build_clean_inspector_text(results, "Geometry")

    assert "GEOMETRY" in text
    assert "Channels: 40" in text
    assert "N/A" not in text

    payload = build_clean_inspector_payload(results)

    assert payload["passed"] is True
    assert payload["row_count"] > 0
    assert "Sources" not in payload["sections"]

    attach_right_inspector_cleanup(results)

    assert results["phase_16s5_right_inspector_cleanup_pass"] is True

    print("PASS_REGEN_VIEWER_RIGHT_INSPECTOR_CLEANUP_PHASE_16S5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
