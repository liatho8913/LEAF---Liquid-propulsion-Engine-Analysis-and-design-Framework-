from material_coating_solver_integration_planning_owner import (
    build_material_coating_solver_integration_plan,
)


def test_phase_10a_planning_owner_sourced_material_no_coating():
    results = {
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "coating_source_validation_mode": "NONE",
        "coating_source_is_placeholder": False,
        "phase_9e_material_completion_audit_complete": True,
        "phase_9h_material_and_coating_foundation_audit_complete": True,
    }

    audit = build_material_coating_solver_integration_plan(results)

    assert audit["phase_10a_solver_integration_planning_owner_complete"] is True
    assert audit["phase_10a_solver_integration_planning_owner_status"] == (
        "PASS_PHASE_10A_SOLVER_INTEGRATION_PLANNING_OWNER"
    )
    assert audit["stage_10_solver_integration_status"] == (
        "PLANNING_ONLY_NO_SOLVER_CHANGE"
    )


def test_phase_10a_planning_owner_blocks_placeholder_material():
    results = {
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "material_source_is_placeholder": True,
        "coating_source_validation_mode": "NONE",
        "coating_source_is_placeholder": False,
        "phase_9e_material_completion_audit_complete": True,
        "phase_9h_material_and_coating_foundation_audit_complete": True,
    }

    audit = build_material_coating_solver_integration_plan(results)

    blockers = audit["phase_10a_solver_integration_planning_owner_blockers"]

    assert audit["phase_10a_solver_integration_planning_owner_complete"] is True
    assert any("BLOCKED_PLACEHOLDER" in blocker for blocker in blockers)


def test_phase_10a_planning_owner_blocks_partial_source_material():
    results = {
        "material_source_validation_mode": "PARTIAL_SOURCE_MODE",
        "material_source_is_placeholder": False,
        "coating_source_validation_mode": "NONE",
        "coating_source_is_placeholder": False,
        "phase_9e_material_completion_audit_complete": True,
        "phase_9h_material_and_coating_foundation_audit_complete": True,
    }

    audit = build_material_coating_solver_integration_plan(results)

    blockers = audit["phase_10a_solver_integration_planning_owner_blockers"]

    assert audit["phase_10a_solver_integration_planning_owner_complete"] is True
    assert any("BLOCKED_PARTIAL_SOURCE" in blocker for blocker in blockers)


if __name__ == "__main__":
    test_phase_10a_planning_owner_sourced_material_no_coating()
    test_phase_10a_planning_owner_blocks_placeholder_material()
    test_phase_10a_planning_owner_blocks_partial_source_material()
    print("PASS_PHASE_10A_SOLVER_INTEGRATION_PLANNING_OWNER_TESTS")