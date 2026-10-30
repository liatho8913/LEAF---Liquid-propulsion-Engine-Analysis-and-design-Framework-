from material_integration_validation_owner import (
    build_material_integration_validation,
)


def _base_complete_results():
    return {
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,

        "phase_10b1_material_property_consumption_audit_owner_complete": True,
        "phase_10b1_material_property_consumption_audit_owner_status": "PASS_PHASE_10B1_MATERIAL_PROPERTY_CONSUMPTION_AUDIT_OWNER",

        "phase_10b2_material_thermal_conductivity_integration_owner_complete": True,
        "phase_10b2_material_thermal_conductivity_integration_owner_status": "PASS_PHASE_10B2_MATERIAL_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER",

        "phase_10b3_material_specific_heat_integration_owner_complete": True,
        "phase_10b3_material_specific_heat_integration_owner_status": "PASS_PHASE_10B3_MATERIAL_SPECIFIC_HEAT_INTEGRATION_OWNER",

        "phase_10b4_material_density_integration_owner_complete": True,
        "phase_10b4_material_density_integration_owner_status": "PASS_PHASE_10B4_MATERIAL_DENSITY_INTEGRATION_OWNER",

        "phase_10b5_material_temperature_limit_integration_owner_complete": True,
        "phase_10b5_material_temperature_limit_integration_owner_status": "PASS_PHASE_10B5_MATERIAL_TEMPERATURE_LIMIT_INTEGRATION_OWNER",

        "phase_10b6_material_strength_limit_integration_owner_complete": True,
        "phase_10b6_material_strength_limit_integration_owner_status": "PASS_PHASE_10B6_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER",

        "wall_thermal_conductivity": 250.0,
        "material_specific_heat_cp": 410.0,
        "material_density": 8920.0,
        "effective_material_temperature_limit": 950.0,
        "effective_material_yield_strength": 240_000_000.0,

        "material_temperature_limit_pass": 1.0,
        "material_structural_pass": 1.0,
    }


def test_phase_10b7_passes_complete_sourced_stack():
    results = _base_complete_results()

    audit = build_material_integration_validation(results)

    assert audit["phase_10b7_material_integration_validation_owner_complete"] is True
    assert audit["phase_10b7_material_integration_validation_pass"] is True
    assert audit["phase_10b7_material_integration_validation_owner_status"] == (
        "PASS_PHASE_10B7_MATERIAL_INTEGRATION_VALIDATION_OWNER"
    )


def test_phase_10b7_fails_placeholder_stack():
    results = _base_complete_results()
    results["material_source_validation_mode"] = "PLACEHOLDER_MODE"
    results["material_source_is_placeholder"] = True

    audit = build_material_integration_validation(results)

    assert audit["phase_10b7_material_integration_validation_owner_complete"] is True
    assert audit["phase_10b7_material_integration_validation_pass"] is False
    assert audit["phase_10b7_material_integration_validation_owner_status"] == (
        "FAIL_PHASE_10B7_MATERIAL_INTEGRATION_VALIDATION_OWNER"
    )


def test_phase_10b7_fails_temperature_failure():
    results = _base_complete_results()
    results["material_temperature_limit_pass"] = 0.0

    audit = build_material_integration_validation(results)

    assert audit["phase_10b7_material_integration_validation_pass"] is False
    assert any(
        "temperature" in blocker.lower()
        for blocker in audit["phase_10b7_material_integration_validation_blockers"]
    )


def test_phase_10b7_fails_missing_stage():
    results = _base_complete_results()
    results["phase_10b4_material_density_integration_owner_complete"] = False

    audit = build_material_integration_validation(results)

    assert audit["phase_10b7_material_integration_validation_owner_complete"] is False
    assert audit["phase_10b7_material_integration_validation_pass"] is False


if __name__ == "__main__":
    test_phase_10b7_passes_complete_sourced_stack()
    test_phase_10b7_fails_placeholder_stack()
    test_phase_10b7_fails_temperature_failure()
    test_phase_10b7_fails_missing_stage()
    print("PASS_PHASE_10B7_MATERIAL_INTEGRATION_VALIDATION_OWNER_TESTS")