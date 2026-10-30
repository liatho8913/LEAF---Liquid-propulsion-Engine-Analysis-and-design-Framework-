from temperature_dependent_solver_completion_audit_owner import (
    attach_temperature_dependent_solver_completion_audit_owner,
)


def test_temperature_dependent_solver_completion_audit_owner_passes_when_all_10d_pass():
    results = {
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "phase_10d1_temperature_dependency_discovery_audit_owner_status": (
            "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER"
        ),
        "phase_10d2_material_conductivity_consumption_audit_owner_complete": True,
        "phase_10d2_material_conductivity_consumption_audit_owner_status": (
            "PASS_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER"
        ),
        "phase_10d3_specific_heat_consumption_audit_owner_complete": True,
        "phase_10d3_specific_heat_consumption_audit_owner_status": (
            "PASS_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER"
        ),
        "phase_10d4_density_coolant_property_consumption_audit_owner_complete": True,
        "phase_10d4_density_coolant_property_consumption_audit_owner_status": (
            "PASS_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER"
        ),
        "phase_10d5_coating_thermal_consumption_audit_owner_complete": True,
        "phase_10d5_coating_thermal_consumption_audit_owner_status": (
            "PASS_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
        ),
        "phase_10d6_bond_coat_consumption_audit_owner_complete": True,
        "phase_10d6_bond_coat_consumption_audit_owner_status": (
            "PASS_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
        ),
        "foundation_result_key_audit_status": "PASS",
    }

    solved = attach_temperature_dependent_solver_completion_audit_owner(results)

    assert solved[
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_complete"
    ] is True

    assert solved[
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_status"
    ] == "PASS_PHASE_10D7_TEMPERATURE_DEPENDENT_SOLVER_COMPLETION_AUDIT_OWNER"

    assert solved[
        "stage_10d_temperature_dependent_solver_framework_complete"
    ] is True


def test_temperature_dependent_solver_completion_audit_owner_fails_when_one_phase_fails():
    results = {
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "phase_10d1_temperature_dependency_discovery_audit_owner_status": (
            "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER"
        ),
        "phase_10d2_material_conductivity_consumption_audit_owner_complete": True,
        "phase_10d2_material_conductivity_consumption_audit_owner_status": (
            "FAIL_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER"
        ),
        "phase_10d3_specific_heat_consumption_audit_owner_complete": True,
        "phase_10d3_specific_heat_consumption_audit_owner_status": (
            "PASS_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER"
        ),
        "phase_10d4_density_coolant_property_consumption_audit_owner_complete": True,
        "phase_10d4_density_coolant_property_consumption_audit_owner_status": (
            "PASS_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER"
        ),
        "phase_10d5_coating_thermal_consumption_audit_owner_complete": True,
        "phase_10d5_coating_thermal_consumption_audit_owner_status": (
            "PASS_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
        ),
        "phase_10d6_bond_coat_consumption_audit_owner_complete": True,
        "phase_10d6_bond_coat_consumption_audit_owner_status": (
            "PASS_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
        ),
        "foundation_result_key_audit_status": "PASS",
    }

    solved = attach_temperature_dependent_solver_completion_audit_owner(results)

    assert solved[
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_status"
    ] == "FAIL_PHASE_10D7_TEMPERATURE_DEPENDENT_SOLVER_COMPLETION_AUDIT_OWNER"

    assert solved[
        "stage_10d_temperature_dependent_solver_framework_complete"
    ] is False


if __name__ == "__main__":
    test_temperature_dependent_solver_completion_audit_owner_passes_when_all_10d_pass()
    test_temperature_dependent_solver_completion_audit_owner_fails_when_one_phase_fails()
    print("PASS_TEMPERATURE_DEPENDENT_SOLVER_COMPLETION_AUDIT_OWNER")