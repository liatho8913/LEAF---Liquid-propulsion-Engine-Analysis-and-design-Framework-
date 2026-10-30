from regen_candidate_resolve_execution_owner import (
    attach_regen_candidate_resolve_execution_owner,
)


def test_resolve_execution_owner_ready_without_solver_callable():
    results = {
        "regen_candidate_resolve_ready": True,
        "regen_candidate_resolve_cloned_state": {
            "candidate_id": "RCG-0001",
            "patched_clone": {
                "number_of_coolant_channels": 96,
                "coolant_channel_width": 0.0012,
                "coolant_channel_height": 0.0025,
                "rib_width": 0.0008,
                "hot_gas_wall_thickness": 0.00125,
            },
        },
    }

    solved = attach_regen_candidate_resolve_execution_owner(results)

    assert solved["phase_11b_1h_regen_candidate_resolve_execution_owner_complete"] is True
    assert solved["regen_candidate_resolve_execution_executed"] is False
    assert solved["regen_candidate_resolve_live_geometry_modified"] is False
    assert solved["regen_candidate_resolve_original_state_mutated"] is False
    assert solved["regen_candidate_resolve_candidate_committed"] is False
    assert solved["regen_candidate_resolve_execution_owner_status"] == (
        "WARN_REGEN_CANDIDATE_RESOLVE_EXECUTION_READY_NO_SOLVER_CALLABLE"
    )


def test_resolve_execution_owner_executes_with_solver_callable():
    results = {
        "regen_candidate_resolve_ready": True,
        "regen_candidate_resolve_cloned_state": {
            "candidate_id": "RCG-0001",
            "patched_clone": {
                "number_of_coolant_channels": 96,
            },
        },
    }

    def fake_solver(inputs):
        return {
            "solver_ran": True,
            "number_of_coolant_channels": inputs["number_of_coolant_channels"],
        }

    solved = attach_regen_candidate_resolve_execution_owner(
        results,
        solver_callable=fake_solver,
    )

    assert solved["regen_candidate_resolve_execution_executed"] is True
    assert solved["regen_candidate_resolve_execution_owner_status"] == (
        "PASS_REGEN_CANDIDATE_RESOLVE_EXECUTED"
    )
    assert solved["regen_candidate_resolve_execution_result"]["solver_ran"] is True


def test_resolve_execution_owner_blocks_without_resolve_state():
    solved = attach_regen_candidate_resolve_execution_owner({})

    assert solved["regen_candidate_resolve_execution_owner_status"] == (
        "FAIL_REGEN_CANDIDATE_RESOLVE_EXECUTION_BLOCKED"
    )
    assert solved["regen_candidate_resolve_execution_executed"] is False