from material_density_integration_owner import (
    apply_material_density_integration,
)


def test_phase_10b4_applies_sourced_density():
    results = {
        "phase_10b3_material_specific_heat_integration_owner_complete": True,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "material_density": 8960.0,
        "material_property_interpolation_results": {
            "density": {
                "value": 8920.0,
            }
        },
    }

    audit = apply_material_density_integration(results)

    assert audit["phase_10b4_material_density_integration_owner_complete"] is True
    assert audit["phase_10b4_material_density_integration_owner_status"] == (
        "PASS_PHASE_10B4_MATERIAL_DENSITY_INTEGRATION_OWNER"
    )
    assert audit["phase_10b4_material_density_integration_owner_applied"] is True
    assert results["material_density"] == 8920.0
    assert results["material_density_source"] == "SOURCED_INTERPOLATED_MATERIAL_RHO_T"


def test_phase_10b4_blocks_placeholder_density():
    results = {
        "phase_10b3_material_specific_heat_integration_owner_complete": True,
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "material_source_is_placeholder": True,
        "material_density": 8960.0,
        "material_property_interpolation_results": {
            "density": {
                "value": 8920.0,
            }
        },
    }

    audit = apply_material_density_integration(results)

    assert audit["phase_10b4_material_density_integration_owner_complete"] is True
    assert audit["phase_10b4_material_density_integration_owner_applied"] is False
    assert results["material_density"] == 8960.0


def test_phase_10b4_blocks_partial_source_density():
    results = {
        "phase_10b3_material_specific_heat_integration_owner_complete": True,
        "material_source_validation_mode": "PARTIAL_SOURCE_MODE",
        "material_source_is_placeholder": False,
        "material_density": 8960.0,
        "material_property_interpolation_results": {
            "density": {
                "value": 8920.0,
            }
        },
    }

    audit = apply_material_density_integration(results)

    assert audit["phase_10b4_material_density_integration_owner_complete"] is True
    assert audit["phase_10b4_material_density_integration_owner_applied"] is False
    assert results["material_density"] == 8960.0


def test_phase_10b4_blocks_missing_10b3():
    results = {
        "phase_10b3_material_specific_heat_integration_owner_complete": False,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "material_density": 8960.0,
        "material_property_interpolation_results": {
            "density": {
                "value": 8920.0,
            }
        },
    }

    audit = apply_material_density_integration(results)

    assert audit["phase_10b4_material_density_integration_owner_complete"] is False
    assert audit["phase_10b4_material_density_integration_owner_applied"] is False
    assert results["material_density"] == 8960.0


if __name__ == "__main__":
    test_phase_10b4_applies_sourced_density()
    test_phase_10b4_blocks_placeholder_density()
    test_phase_10b4_blocks_partial_source_density()
    test_phase_10b4_blocks_missing_10b3()
    print("PASS_PHASE_10B4_MATERIAL_DENSITY_INTEGRATION_OWNER_TESTS")