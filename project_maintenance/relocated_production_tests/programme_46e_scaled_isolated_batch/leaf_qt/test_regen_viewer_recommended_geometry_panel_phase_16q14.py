from regen_viewer_recommended_geometry_panel_phase_16q14 import (
    build_recommended_geometry_payload,
    attach_recommended_geometry_payload,
    build_recommended_geometry_panel_text,
)


def main() -> int:
    results = {
        "phase_16q3_manufacturability_status": "PASS_REGEN_MANUFACTURABILITY_GEOMETRY_GATE_PHASE_16Q3",
        "phase_16q8_geometry_realism_score": 87.76,
    }

    geometry = {
        "number_of_coolant_channels": 40,
        "coolant_channel_width": 0.0012,
        "coolant_channel_height": 0.0025,
        "rib_width": 0.0005,
        "effective_rib_width": 0.00074056,
        "required_pitch": 0.0017,
        "available_pitch": 0.00194056,
        "channel_fit_ratio": 1.1415,
        "cooling_coverage": 0.876,
        "channel_geometry_valid": 1.0,
    }

    payload = build_recommended_geometry_payload(results, geometry)

    assert payload["channels"] == 40
    assert payload["width"] == 0.0012
    assert payload["height"] == 0.0025
    assert payload["fit_ratio"] == 1.1415
    assert payload["complete"] is True

    attach_recommended_geometry_payload(results, geometry)

    assert results["phase_16q14_recommended_geometry_payload_available"] is True
    assert results["recommended_geometry_status"] == "APPLIED_AUTOMATIC_GEOMETRY"
    assert results["recommended_geometry_channels"] == 40
    assert results["recommended_geometry_realism_score"] == 87.76

    text = build_recommended_geometry_panel_text(results)

    assert "RECOMMENDED GEOMETRY" in text
    assert "Channels: 40" in text
    assert "Realism Score: 87.76" in text

    print("PASS_REGEN_VIEWER_RECOMMENDED_GEOMETRY_PANEL_PHASE_16Q14")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
