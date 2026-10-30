from material_property_consumption_audit_owner import (
    build_material_property_consumption_audit,
)


def test_phase_10b1_material_consumption_audit_sourced_mode():
    results = {
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "phase_9e_material_completion_audit_complete": True,
        "phase_10a_solver_integration_planning_owner_complete": True,
    }

    audit = build_material_property_consumption_audit(results)

    assert audit["phase_10b1_material_property_consumption_audit_owner_complete"] is True
    assert audit["phase_10b1_material_property_consumption_audit_owner_status"] == (
        "PASS_PHASE_10B1_MATERIAL_PROPERTY_CONSUMPTION_AUDIT_OWNER"
    )
    assert audit["stage_10b_material_property_integration_status"] == (
        "CONSUMPTION_AUDIT_ONLY_NO_SOLVER_CHANGE"
    )


def test_phase_10b1_blocks_placeholder_material():
    results = {
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "material_source_is_placeholder": True,
        "phase_9e_material_completion_audit_complete": True,
        "phase_10a_solver_integration_planning_owner_complete": True,
    }

    audit = build_material_property_consumption_audit(results)

    blockers = audit["phase_10b1_material_property_consumption_audit_owner_blockers"]

    assert audit["phase_10b1_material_property_consumption_audit_owner_complete"] is True
    assert any("BLOCKED_PLACEHOLDER" in blocker for blocker in blockers)


def test_phase_10b1_blocks_when_10a_missing():
    results = {
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "phase_9e_material_completion_audit_complete": True,
        "phase_10a_solver_integration_planning_owner_complete": False,
    }

    audit = build_material_property_consumption_audit(results)

    assert audit["phase_10b1_material_property_consumption_audit_owner_complete"] is False
    assert any(
        "BLOCKED_PHASE_10A_INCOMPLETE" in blocker
        for blocker in audit["phase_10b1_material_property_consumption_audit_owner_blockers"]
    )


if __name__ == "__main__":
    test_phase_10b1_material_consumption_audit_sourced_mode()
    test_phase_10b1_blocks_placeholder_material()
    test_phase_10b1_blocks_when_10a_missing()
    print("PASS_PHASE_10B1_MATERIAL_PROPERTY_CONSUMPTION_AUDIT_OWNER_TESTS")