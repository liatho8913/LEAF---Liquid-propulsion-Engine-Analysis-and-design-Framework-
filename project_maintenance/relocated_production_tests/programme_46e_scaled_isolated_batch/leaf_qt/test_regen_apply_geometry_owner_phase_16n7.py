from project_maintenance.production_historical_artifacts.leaf_qt.regen_apply_geometry_owner_phase_16n7 import (
    RegenApplyGeometryOwnerPhase16N7,
    attach_apply_geometry_result_phase_16n7,
)


def main() -> int:
    owner = RegenApplyGeometryOwnerPhase16N7()

    blocked = owner.apply({})
    assert blocked.applied is False
    assert blocked.status == "FAIL_APPLY_GEOMETRY_BLOCKED_PHASE_16N7"
    assert blocked.reasons

    results = {
        "phase_16n6_recommendation_accepted": True,
        "phase_16n6_accepted_staged_geometry": {
            "number_of_coolant_channels": 96,
            "coolant_channel_width": 0.0012,
            "coolant_channel_height": 0.002,
            "rib_width": 0.0008,
        },
    }

    applied = owner.apply(results)
    assert applied.applied is True
    assert applied.status == "PASS_APPLY_GEOMETRY_RECORDED_PHASE_16N7"
    assert applied.applied_geometry["number_of_coolant_channels"] == 96

    updated = attach_apply_geometry_result_phase_16n7(dict(results))
    assert updated["phase_16n7_geometry_applied"] is True
    assert updated["regen_ui_applied_geometry"]["number_of_coolant_channels"] == 96
    assert updated["regen_current_geometry"]["coolant_channel_width"] == 0.0012
    assert updated["phase_16n7_solver_regenerated"] is False
    assert updated["phase_16n7_cea_rerun"] is False

    print("PASS_REGEN_APPLY_GEOMETRY_OWNER_PHASE_16N7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
