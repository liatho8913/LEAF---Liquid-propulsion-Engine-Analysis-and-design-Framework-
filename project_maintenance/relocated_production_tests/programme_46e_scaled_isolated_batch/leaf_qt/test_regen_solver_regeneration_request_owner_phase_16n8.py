from project_maintenance.production_historical_artifacts.leaf_qt.regen_solver_regeneration_request_owner_phase_16n8 import (
    RegenSolverRegenerationRequestOwnerPhase16N8,
    attach_solver_regeneration_request_phase_16n8,
)


def main() -> int:
    owner = RegenSolverRegenerationRequestOwnerPhase16N8()

    blocked = owner.request({})
    assert blocked.requested is False
    assert blocked.status == "FAIL_SOLVER_REGENERATION_REQUEST_BLOCKED_PHASE_16N8"
    assert blocked.reasons

    results = {
        "phase_16n7_geometry_applied": True,
        "regen_ui_applied_geometry": {
            "number_of_coolant_channels": 96,
            "coolant_channel_width": 0.0012,
            "coolant_channel_height": 0.002,
            "rib_width": 0.0008,
        },
    }

    requested = owner.request(results)
    assert requested.requested is True
    assert requested.status == "PASS_SOLVER_REGENERATION_REQUEST_RECORDED_PHASE_16N8"
    assert requested.regeneration_geometry["number_of_coolant_channels"] == 96

    updated = attach_solver_regeneration_request_phase_16n8(dict(results))
    assert updated["phase_16n8_solver_regeneration_requested"] is True
    assert updated["phase_16n8_solver_regeneration_geometry"]["coolant_channel_width"] == 0.0012
    assert updated["phase_16n8_solver_regenerated"] is False
    assert updated["phase_16n8_cea_rerun"] is False

    print("PASS_REGEN_SOLVER_REGENERATION_REQUEST_OWNER_PHASE_16N8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
