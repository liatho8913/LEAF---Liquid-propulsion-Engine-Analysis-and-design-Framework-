from material_thermal_conductivity_integration_owner import (
    apply_material_thermal_conductivity_integration,
)


def test_phase_10b2_applies_sourced_kt():
    results = {
        "phase_10b1_material_property_consumption_audit_owner_complete": True,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "wall_thermal_conductivity": 344.0,
        "material_property_interpolation_query_temperature": 900.0,
        "material_property_interpolation_results": {
            "thermal_conductivity": {
                "value": 250.0,
            }
        },
    }

    audit = apply_material_thermal_conductivity_integration(results)

    assert audit["phase_10b2_material_thermal_conductivity_integration_owner_complete"] is True
    assert audit["phase_10b2_material_thermal_conductivity_integration_owner_status"] == (
        "PASS_PHASE_10B2_MATERIAL_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER"
    )
    assert audit["phase_10b2_material_thermal_conductivity_integration_owner_applied"] is True
    assert results["wall_thermal_conductivity"] == 250.0
    assert results["wall_thermal_conductivity_source"] == "SOURCED_INTERPOLATED_MATERIAL_KT"


def test_phase_10b2_blocks_placeholder_kt():
    results = {
        "phase_10b1_material_property_consumption_audit_owner_complete": True,
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "material_source_is_placeholder": True,
        "wall_thermal_conductivity": 344.0,
        "material_property_interpolation_results": {
            "thermal_conductivity": {
                "value": 250.0,
            }
        },
    }

    audit = apply_material_thermal_conductivity_integration(results)

    assert audit["phase_10b2_material_thermal_conductivity_integration_owner_complete"] is True
    assert audit["phase_10b2_material_thermal_conductivity_integration_owner_applied"] is False
    assert results["wall_thermal_conductivity"] == 344.0
    assert any(
        "BLOCKED_PLACEHOLDER" in blocker
        for blocker in audit["phase_10b2_material_thermal_conductivity_integration_owner_blockers"]
    )


def test_phase_10b2_blocks_partial_source_kt():
    results = {
        "phase_10b1_material_property_consumption_audit_owner_complete": True,
        "material_source_validation_mode": "PARTIAL_SOURCE_MODE",
        "material_source_is_placeholder": False,
        "wall_thermal_conductivity": 344.0,
        "material_property_interpolation_results": {
            "thermal_conductivity": {
                "value": 250.0,
            }
        },
    }

    audit = apply_material_thermal_conductivity_integration(results)

    assert audit["phase_10b2_material_thermal_conductivity_integration_owner_complete"] is True
    assert audit["phase_10b2_material_thermal_conductivity_integration_owner_applied"] is False
    assert results["wall_thermal_conductivity"] == 344.0
    assert any(
        "BLOCKED_PARTIAL_SOURCE" in blocker
        for blocker in audit["phase_10b2_material_thermal_conductivity_integration_owner_blockers"]
    )


def test_phase_10b2_blocks_missing_10b1():
    results = {
        "phase_10b1_material_property_consumption_audit_owner_complete": False,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "wall_thermal_conductivity": 344.0,
        "material_property_interpolation_results": {
            "thermal_conductivity": {
                "value": 250.0,
            }
        },
    }

    audit = apply_material_thermal_conductivity_integration(results)

    assert audit["phase_10b2_material_thermal_conductivity_integration_owner_complete"] is False
    assert audit["phase_10b2_material_thermal_conductivity_integration_owner_applied"] is False
    assert results["wall_thermal_conductivity"] == 344.0
    assert any(
        "BLOCKED_PHASE_10B1_INCOMPLETE" in blocker
        for blocker in audit["phase_10b2_material_thermal_conductivity_integration_owner_blockers"]
    )


if __name__ == "__main__":
    test_phase_10b2_applies_sourced_kt()
    test_phase_10b2_blocks_placeholder_kt()
    test_phase_10b2_blocks_partial_source_kt()
    test_phase_10b2_blocks_missing_10b1()
    print("PASS_PHASE_10B2_MATERIAL_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER_TESTS")