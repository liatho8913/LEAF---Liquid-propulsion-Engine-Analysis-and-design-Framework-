from coating_integration_validation_owner import (
    build_coating_integration_validation,
)


def _base_stage_complete_results():
    return {
        "phase_10c1_coating_property_consumption_audit_owner_complete": True,
        "phase_10c1_coating_property_consumption_audit_owner_status": "PASS_PHASE_10C1_COATING_PROPERTY_CONSUMPTION_AUDIT_OWNER",

        "phase_10c2_coating_thermal_conductivity_integration_owner_complete": True,
        "phase_10c2_coating_thermal_conductivity_integration_owner_status": "PASS_PHASE_10C2_COATING_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER",

        "phase_10c3_coating_thickness_integration_owner_complete": True,
        "phase_10c3_coating_thickness_integration_owner_status": "PASS_PHASE_10C3_COATING_THICKNESS_INTEGRATION_OWNER",

        "phase_10c4_coating_thermal_resistance_integration_owner_complete": True,
        "phase_10c4_coating_thermal_resistance_integration_owner_status": "PASS_PHASE_10C4_COATING_THERMAL_RESISTANCE_INTEGRATION_OWNER",

        "phase_10c5_coating_temperature_limit_integration_owner_complete": True,
        "phase_10c5_coating_temperature_limit_integration_owner_status": "PASS_PHASE_10C5_COATING_TEMPERATURE_LIMIT_INTEGRATION_OWNER",

        "phase_10c6_bond_coat_integration_owner_complete": True,
        "phase_10c6_bond_coat_integration_owner_status": "PASS_PHASE_10C6_BOND_COAT_INTEGRATION_OWNER",
    }


def test_phase_10c7_passes_no_coating_selected():
    results = _base_stage_complete_results()
    results.update({
        "selected_coating_material": "NONE",
        "effective_coating_thickness": 0.0,
        "bond_coat_enabled": False,
        "coating_source_validation_mode": "NONE",
        "coating_source_is_placeholder": False,
    })

    audit = build_coating_integration_validation(results)

    assert audit["phase_10c7_coating_integration_validation_owner_complete"] is True
    assert audit["phase_10c7_coating_integration_validation_pass"] is True
    assert audit["phase_10c7_coating_integration_validation_owner_status"] == (
        "PASS_PHASE_10C7_COATING_INTEGRATION_VALIDATION_OWNER"
    )


def test_phase_10c7_passes_complete_sourced_coating_stack():
    results = _base_stage_complete_results()
    results.update({
        "selected_coating_material": "YBCO",
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "effective_coating_thickness": 0.0002,
        "coating_thermal_conductivity": 2.5,
        "effective_coating_thermal_resistance": 0.00008,
        "effective_coating_temperature_limit": 1500.0,
        "coating_temperature_limit_pass": 1.0,
        "bond_coat_enabled": False,
    })

    audit = build_coating_integration_validation(results)

    assert audit["phase_10c7_coating_integration_validation_owner_complete"] is True
    assert audit["phase_10c7_coating_integration_validation_pass"] is True
    assert audit["phase_10c7_coating_integration_validation_owner_status"] == (
        "PASS_PHASE_10C7_COATING_INTEGRATION_VALIDATION_OWNER"
    )


def test_phase_10c7_fails_placeholder_coating():
    results = _base_stage_complete_results()
    results.update({
        "selected_coating_material": "PLACEHOLDER_COATING",
        "coating_source_validation_mode": "PLACEHOLDER_MODE",
        "coating_source_is_placeholder": True,
        "effective_coating_thickness": 0.0002,
        "coating_thermal_conductivity": 2.5,
        "effective_coating_thermal_resistance": 0.00008,
        "effective_coating_temperature_limit": 1500.0,
        "coating_temperature_limit_pass": 1.0,
        "bond_coat_enabled": False,
    })

    audit = build_coating_integration_validation(results)

    assert audit["phase_10c7_coating_integration_validation_owner_complete"] is True
    assert audit["phase_10c7_coating_integration_validation_pass"] is False
    assert audit["phase_10c7_coating_integration_validation_owner_status"] == (
        "FAIL_PHASE_10C7_COATING_INTEGRATION_VALIDATION_OWNER"
    )


def test_phase_10c7_fails_hot_coating():
    results = _base_stage_complete_results()
    results.update({
        "selected_coating_material": "YBCO",
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "effective_coating_thickness": 0.0002,
        "coating_thermal_conductivity": 2.5,
        "effective_coating_thermal_resistance": 0.00008,
        "effective_coating_temperature_limit": 1500.0,
        "coating_temperature_limit_pass": 0.0,
        "bond_coat_enabled": False,
    })

    audit = build_coating_integration_validation(results)

    assert audit["phase_10c7_coating_integration_validation_pass"] is False
    assert any(
        "temperature" in blocker.lower()
        for blocker in audit["phase_10c7_coating_integration_validation_blockers"]
    )


def test_phase_10c7_passes_complete_sourced_bond_coat_stack():
    results = _base_stage_complete_results()
    results.update({
        "selected_coating_material": "YBCO",
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "effective_coating_thickness": 0.0002,
        "coating_thermal_conductivity": 2.5,
        "effective_coating_thermal_resistance": 0.00008,
        "effective_coating_temperature_limit": 1500.0,
        "coating_temperature_limit_pass": 1.0,

        "bond_coat_enabled": True,
        "selected_bond_coat_material": "MCrAlY",
        "bond_coat_source_is_placeholder": False,
        "bond_coat_thickness": 0.0001,
        "bond_coat_thermal_conductivity": 12.5,
        "effective_bond_coat_thermal_resistance": 0.000008,
        "bond_coat_temperature_limit_pass": 1.0,
    })

    audit = build_coating_integration_validation(results)

    assert audit["phase_10c7_coating_integration_validation_owner_complete"] is True
    assert audit["phase_10c7_coating_integration_validation_pass"] is True


def test_phase_10c7_fails_missing_stage():
    results = _base_stage_complete_results()
    results["phase_10c4_coating_thermal_resistance_integration_owner_complete"] = False

    audit = build_coating_integration_validation(results)

    assert audit["phase_10c7_coating_integration_validation_owner_complete"] is False
    assert audit["phase_10c7_coating_integration_validation_pass"] is False


if __name__ == "__main__":
    test_phase_10c7_passes_no_coating_selected()
    test_phase_10c7_passes_complete_sourced_coating_stack()
    test_phase_10c7_fails_placeholder_coating()
    test_phase_10c7_fails_hot_coating()
    test_phase_10c7_passes_complete_sourced_bond_coat_stack()
    test_phase_10c7_fails_missing_stage()
    print("PASS_PHASE_10C7_COATING_INTEGRATION_VALIDATION_OWNER_TESTS")