from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_small_side_profile_indicator_phase_16s3 import (
    build_small_side_profile_indicator_state,
    attach_small_side_profile_indicator_state,
)


def main() -> int:
    results = {
        "phase_16r2_side_profile_canvas_payload": {
            "profile": [
                {"x": 0.0, "gas_radius": 0.01},
                {"x": 1.0, "gas_radius": 0.0225},
            ],
            "selected_x": 0.5,
        },
        "selected_station_x": 0.5,
    }

    state = build_small_side_profile_indicator_state(results)

    assert state["passed"] is True
    assert state["available"] is True
    assert state["profile_point_count"] == 2

    attach_small_side_profile_indicator_state(results)

    assert results["phase_16s3_small_side_profile_pass"] is True
    assert results["phase_16s3_small_side_profile_available"] is True

    empty = {}
    bad = build_small_side_profile_indicator_state(empty)

    assert bad["passed"] is False
    assert bad["available"] is False

    print("PASS_REGEN_VIEWER_SMALL_SIDE_PROFILE_INDICATOR_PHASE_16S3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
