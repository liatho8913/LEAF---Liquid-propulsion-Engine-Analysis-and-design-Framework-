from coating_thermal_conductivity_integration_owner import (
    apply_coating_thermal_conductivity_integration,
)


def test_phase_10c2_no_coating_selected_does_not_apply():
    results = {
        "phase_10c1_coating_property_consumption_audit_owner_complete": True,
        "coating_source_validation_mode": "NONE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "NONE",
        "coating_thickness": 0.0,
    }

    audit = apply_coating_thermal_conductivity_integration(results)

    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_complete"] is True
    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_status"] == (
        "PASS_PHASE_10C2_COATING_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER"
    )
    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_applied"] is False
    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_decision"] == (
        "NO_COATING_SELECTED"
    )


def test_phase_10c2_applies_sourced_coating_conductivity():
    results = {
        "phase_10c1_coating_property_consumption_audit_owner_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "coating_thickness": 0.0002,
        "coating_thermal_conductivity": 1.0,
        "coating_property_interpolation_results": {
            "thermal_conductivity": {
                "value": 2.5,
            }
        },
    }

    audit = apply_coating_thermal_conductivity_integration(results)

    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_complete"] is True
    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_applied"] is True
    assert results["coating_thermal_conductivity"] == 2.5
    assert results["coating_thermal_conductivity_source"] == (
        "SOURCED_INTERPOLATED_COATING_KT"
    )


def test_phase_10c2_blocks_placeholder_coating_conductivity():
    results = {
        "phase_10c1_coating_property_consumption_audit_owner_complete": True,
        "coating_source_validation_mode": "PLACEHOLDER_MODE",
        "coating_source_is_placeholder": True,
        "selected_coating_material": "PLACEHOLDER_COATING",
        "coating_thickness": 0.0002,
        "coating_thermal_conductivity": 1.0,
        "coating_property_interpolation_results": {
            "thermal_conductivity": {
                "value": 2.5,
            }
        },
    }

    audit = apply_coating_thermal_conductivity_integration(results)

    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_complete"] is True
    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_applied"] is False
    assert results["coating_thermal_conductivity"] == 1.0


def test_phase_10c2_blocks_missing_10c1():
    results = {
        "phase_10c1_coating_property_consumption_audit_owner_complete": False,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "coating_thickness": 0.0002,
        "coating_property_interpolation_results": {
            "thermal_conductivity": {
                "value": 2.5,
            }
        },
    }

    audit = apply_coating_thermal_conductivity_integration(results)

    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_complete"] is False
    assert audit["phase_10c2_coating_thermal_conductivity_integration_owner_applied"] is False


if __name__ == "__main__":
    test_phase_10c2_no_coating_selected_does_not_apply()
    test_phase_10c2_applies_sourced_coating_conductivity()
    test_phase_10c2_blocks_placeholder_coating_conductivity()
    test_phase_10c2_blocks_missing_10c1()
    print("PASS_PHASE_10C2_COATING_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER_TESTS")