from regen_geometry_constraint_discovery_audit_owner import (
    attach_regen_geometry_constraint_discovery_audit_owner,
)
from regen_geometry_constraint_validation_owner import (
    attach_regen_geometry_constraint_validation_owner,
)


def test_regen_geometry_constraint_validation_owner_validates_pass_warn_fail():
    results = {
        "coolant_channel_count": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "channel_fit_ratio": 1.2,
        "effective_rib_width": 0.0002,
        "inner_wall_thickness": 0.0012,
        "regen_coolant_velocity": 0.5,
        "regen_reynolds_number": 1785,
        "regen_pressure_drop": 1200000,
        "regen_heat_flux": 18000000,
        "hot_gas_side_wall_temperature": 1848,
        "coolant_side_wall_temperature": 450,
    }

    solved = attach_regen_geometry_constraint_discovery_audit_owner(results)
    solved = attach_regen_geometry_constraint_validation_owner(solved)

    assert solved[
        "phase_11a2_regen_geometry_constraint_validation_owner_complete"
    ] is True

    assert solved[
        "phase_11a2_regen_geometry_constraint_validation_owner_status"
    ] == "PASS_PHASE_11A2_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"

    validation_results = solved[
        "phase_11a2_regen_geometry_constraint_validation_owner_results"
    ]

    assert isinstance(validation_results, list)
    assert len(validation_results) > 0

    states = {item["validation_state"] for item in validation_results}

    assert "PASS" in states
    assert "WARN" in states
    assert "FAIL" in states

    assert solved[
        "phase_11a2_regen_geometry_constraint_validation_owner_engineering_status"
    ] == "FAIL_REGEN_GEOMETRY_CONSTRAINT_VALIDATION"


def test_regen_geometry_constraint_validation_owner_handles_missing_constraints():
    solved = attach_regen_geometry_constraint_discovery_audit_owner({})
    solved = attach_regen_geometry_constraint_validation_owner(solved)

    assert solved[
        "phase_11a2_regen_geometry_constraint_validation_owner_complete"
    ] is True

    assert solved[
        "phase_11a2_regen_geometry_constraint_validation_owner_status"
    ] == "PASS_PHASE_11A2_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"

    assert solved[
        "phase_11a2_regen_geometry_constraint_validation_owner_unavailable_count"
    ] > 0


if __name__ == "__main__":
    test_regen_geometry_constraint_validation_owner_validates_pass_warn_fail()
    test_regen_geometry_constraint_validation_owner_handles_missing_constraints()
    print("PASS_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER")