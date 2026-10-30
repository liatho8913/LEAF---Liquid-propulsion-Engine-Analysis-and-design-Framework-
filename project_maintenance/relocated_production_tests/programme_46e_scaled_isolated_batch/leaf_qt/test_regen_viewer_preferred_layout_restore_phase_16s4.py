from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_preferred_layout_restore_phase_16s4 import (
    attach_preferred_layout_restore_status,
    build_station_indicator_state,
)


def main() -> int:
    results = {"selected_station_x": 0.45}

    state = build_station_indicator_state(results)

    assert state["passed"] is True
    assert state["selected_x"] == 0.45

    results["selected_station_x"] = 2.0
    state = build_station_indicator_state(results)
    assert state["selected_x"] == 1.0

    results["selected_station_x"] = -1.0
    state = build_station_indicator_state(results)
    assert state["selected_x"] == 0.0

    attach_preferred_layout_restore_status(results)

    assert results["phase_16s4_preferred_layout_restore_pass"] is True
    assert results["phase_16s4_preferred_layout_restore_status"] == (
        "PASS_REGEN_VIEWER_PREFERRED_LAYOUT_RESTORE_PHASE_16S4"
    )

    print("PASS_REGEN_VIEWER_PREFERRED_LAYOUT_RESTORE_PHASE_16S4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
