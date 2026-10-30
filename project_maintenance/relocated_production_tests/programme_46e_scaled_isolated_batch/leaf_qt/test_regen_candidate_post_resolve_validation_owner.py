from regen_candidate_post_resolve_validation_owner import (
    attach_regen_candidate_post_resolve_validation_owner,
)


def test_post_resolve_validation_detects_improvement():
    results = {
        "hot_gas_side_wall_temperature": 1000.0,
        "regen_pressure_drop": 5000.0,
        "regen_reynolds_number": 2000.0,
        "regen_candidate_resolve_execution_executed": True,
        "regen_candidate_resolve_execution_result": {
            "hot_gas_side_wall_temperature": 900.0,
            "regen_pressure_drop": 4000.0,
            "regen_reynolds_number": 5000.0,
        },
    }

    solved = attach_regen_candidate_post_resolve_validation_owner(results)

    assert solved["phase_11b_1i_regen_candidate_post_validation_complete"] is True
    assert solved["regen_candidate_post_validation_improved"] is True
    assert solved["regen_candidate_post_validation_score"] > 0.0
    assert solved["regen_candidate_post_validation_status"] == (
        "PASS_REGEN_CANDIDATE_POST_RESOLVE_IMPROVED"
    )


def test_post_resolve_validation_detects_worse_candidate():
    results = {
        "hot_gas_side_wall_temperature": 900.0,
        "regen_pressure_drop": 4000.0,
        "regen_reynolds_number": 5000.0,
        "regen_candidate_resolve_execution_executed": True,
        "regen_candidate_resolve_execution_result": {
            "hot_gas_side_wall_temperature": 1000.0,
            "regen_pressure_drop": 5000.0,
            "regen_reynolds_number": 2000.0,
        },
    }

    solved = attach_regen_candidate_post_resolve_validation_owner(results)

    assert solved["regen_candidate_post_validation_improved"] is False
    assert solved["regen_candidate_post_validation_score"] < 0.0
    assert solved["regen_candidate_post_validation_status"] == (
        "FAIL_REGEN_CANDIDATE_POST_RESOLVE_WORSE"
    )


def test_post_resolve_validation_blocks_without_execution():
    solved = attach_regen_candidate_post_resolve_validation_owner({})

    assert solved["regen_candidate_post_validation_status"] == (
        "FAIL_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_BLOCKED"
    )
    assert solved["regen_candidate_post_validation_improved"] is False