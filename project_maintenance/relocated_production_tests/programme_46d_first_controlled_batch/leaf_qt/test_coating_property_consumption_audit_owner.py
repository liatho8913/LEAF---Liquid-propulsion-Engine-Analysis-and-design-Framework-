from coating_property_consumption_audit_owner import (
    build_coating_property_consumption_audit,
)


def test_phase_10c1_no_coating_selected_passes_audit_mapping():
    results = {
        "phase_10b8_material_integration_completion_audit_complete": True,
        "phase_9h_material_and_coating_foundation_audit_complete": True,
        "coating_source_validation_mode": "NONE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "NONE",
        "coating_thickness": 0.0,
    }

    audit = build_coating_property_consumption_audit(results)

    assert audit["phase_10c1_coating_property_consumption_audit_owner_complete"] is True
    assert audit["phase_10c1_coating_property_consumption_audit_owner_status"] == (
        "PASS_PHASE_10C1_COATING_PROPERTY_CONSUMPTION_AUDIT_OWNER"
    )


def test_phase_10c1_sourced_coating_maps_missing_solver_paths():
    results = {
        "phase_10b8_material_integration_completion_audit_complete": True,
        "phase_9h_material_and_coating_foundation_audit_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "coating_thickness": 0.0002,
    }

    audit = build_coating_property_consumption_audit(results)

    statuses = [
        row["consumption_status"]
        for row in audit["phase_10c1_coating_property_consumption_audit_owner_findings"]
    ]

    assert audit["phase_10c1_coating_property_consumption_audit_owner_complete"] is True
    assert "MISSING_FROM_SOLVER_OUTPUTS" in statuses


def test_phase_10c1_blocks_placeholder_coating():
    results = {
        "phase_10b8_material_integration_completion_audit_complete": True,
        "phase_9h_material_and_coating_foundation_audit_complete": True,
        "coating_source_validation_mode": "PLACEHOLDER_MODE",
        "coating_source_is_placeholder": True,
        "selected_coating_material": "PLACEHOLDER_COATING",
        "coating_thickness": 0.0002,
    }

    audit = build_coating_property_consumption_audit(results)

    blockers = audit["phase_10c1_coating_property_consumption_audit_owner_blockers"]

    assert audit["phase_10c1_coating_property_consumption_audit_owner_complete"] is True
    assert any("BLOCKED_PLACEHOLDER" in blocker for blocker in blockers)


def test_phase_10c1_blocks_missing_material_integration():
    results = {
        "phase_10b8_material_integration_completion_audit_complete": False,
        "phase_9h_material_and_coating_foundation_audit_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "coating_thickness": 0.0002,
    }

    audit = build_coating_property_consumption_audit(results)

    assert audit["phase_10c1_coating_property_consumption_audit_owner_complete"] is False
    assert any(
        "BLOCKED_PHASE_10B_INCOMPLETE" in blocker
        for blocker in audit["phase_10c1_coating_property_consumption_audit_owner_blockers"]
    )


if __name__ == "__main__":
    test_phase_10c1_no_coating_selected_passes_audit_mapping()
    test_phase_10c1_sourced_coating_maps_missing_solver_paths()
    test_phase_10c1_blocks_placeholder_coating()
    test_phase_10c1_blocks_missing_material_integration()
    print("PASS_PHASE_10C1_COATING_PROPERTY_CONSUMPTION_AUDIT_OWNER_TESTS")