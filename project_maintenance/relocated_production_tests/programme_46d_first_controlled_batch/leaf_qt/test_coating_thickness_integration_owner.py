from coating_thickness_integration_owner import (
    apply_coating_thickness_integration,
)


def test_phase_10c3_no_coating_selected_does_not_apply():
    results = {
        "phase_10c2_coating_thermal_conductivity_integration_owner_complete": True,
        "coating_source_validation_mode": "NONE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "NONE",
        "coating_thickness": 0.0,
    }

    audit = apply_coating_thickness_integration(results)

    assert audit["phase_10c3_coating_thickness_integration_owner_complete"] is True
    assert audit["phase_10c3_coating_thickness_integration_owner_status"] == (
        "PASS_PHASE_10C3_COATING_THICKNESS_INTEGRATION_OWNER"
    )
    assert audit["phase_10c3_coating_thickness_integration_owner_applied"] is False
    assert audit["phase_10c3_coating_thickness_integration_owner_decision"] == (
        "NO_COATING_SELECTED"
    )


def test_phase_10c3_applies_sourced_coating_thickness():
    results = {
        "phase_10c2_coating_thermal_conductivity_integration_owner_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "coating_thickness": 0.0001,
        "coating_property_interpolation_results": {
            "thickness": {
                "value": 0.0002,
            }
        },
    }

    audit = apply_coating_thickness_integration(results)

    assert audit["phase_10c3_coating_thickness_integration_owner_complete"] is True
    assert audit["phase_10c3_coating_thickness_integration_owner_applied"] is True
    assert results["effective_coating_thickness"] == 0.0002
    assert results["coating_thickness"] == 0.0002
    assert results["coating_thickness_source"] == "SOURCED_OR_SELECTED_COATING_THICKNESS"


def test_phase_10c3_blocks_placeholder_coating_thickness():
    results = {
        "phase_10c2_coating_thermal_conductivity_integration_owner_complete": True,
        "coating_source_validation_mode": "PLACEHOLDER_MODE",
        "coating_source_is_placeholder": True,
        "selected_coating_material": "PLACEHOLDER_COATING",
        "coating_thickness": 0.0001,
        "coating_property_interpolation_results": {
            "thickness": {
                "value": 0.0002,
            }
        },
    }

    audit = apply_coating_thickness_integration(results)

    assert audit["phase_10c3_coating_thickness_integration_owner_complete"] is True
    assert audit["phase_10c3_coating_thickness_integration_owner_applied"] is False
    assert results["coating_thickness"] == 0.0001


def test_phase_10c3_blocks_missing_10c2():
    results = {
        "phase_10c2_coating_thermal_conductivity_integration_owner_complete": False,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "coating_thickness": 0.0001,
        "coating_property_interpolation_results": {
            "thickness": {
                "value": 0.0002,
            }
        },
    }

    audit = apply_coating_thickness_integration(results)

    assert audit["phase_10c3_coating_thickness_integration_owner_complete"] is False
    assert audit["phase_10c3_coating_thickness_integration_owner_applied"] is False


if __name__ == "__main__":
    test_phase_10c3_no_coating_selected_does_not_apply()
    test_phase_10c3_applies_sourced_coating_thickness()
    test_phase_10c3_blocks_placeholder_coating_thickness()
    test_phase_10c3_blocks_missing_10c2()
    print("PASS_PHASE_10C3_COATING_THICKNESS_INTEGRATION_OWNER_TESTS")