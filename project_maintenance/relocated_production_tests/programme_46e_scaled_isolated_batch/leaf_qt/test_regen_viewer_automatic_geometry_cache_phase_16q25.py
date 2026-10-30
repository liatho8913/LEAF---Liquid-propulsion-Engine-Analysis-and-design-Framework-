from regen_viewer_automatic_geometry_cache_phase_16q25 import (
    build_geometry_input_signature,
    store_automatic_geometry_cache,
    automatic_geometry_cache_valid,
    apply_cached_automatic_geometry,
)


def main() -> int:
    results = {
        "number_of_coolant_channels": 40,
        "coolant_channel_width": 0.0012,
        "coolant_channel_height": 0.0025,
        "rib_width": 0.0005,
        "hot_gas_wall_thickness": 0.001104,
        "phase_16p2_automatic_geometry_candidate_geometry": {
            "number_of_coolant_channels": 40,
            "coolant_channel_width": 0.0012,
            "coolant_channel_height": 0.0025,
            "rib_width": 0.0005,
            "channel_fit_ratio": 1.14,
            "channel_geometry_valid": 1.0,
        },
    }

    sig1 = build_geometry_input_signature(results)
    store_automatic_geometry_cache(results)

    assert results["phase_16q25_auto_geometry_cache_available"] is True
    assert automatic_geometry_cache_valid(results) is True

    apply_cached_automatic_geometry(results)

    assert results["phase_16q25_auto_geometry_cache_used"] is True
    assert results["regen_ui_applied_geometry"]["coolant_channel_width"] == 0.0012
    assert results["viewer_actual_geometry_source"] == "automatic"

    results["coolant_channel_width"] = 0.002

    assert build_geometry_input_signature(results) != sig1
    assert automatic_geometry_cache_valid(results) is False

    apply_cached_automatic_geometry(results)

    assert results["phase_16q25_auto_geometry_cache_used"] is False

    print("PASS_REGEN_VIEWER_AUTOMATIC_GEOMETRY_CACHE_PHASE_16Q25")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
