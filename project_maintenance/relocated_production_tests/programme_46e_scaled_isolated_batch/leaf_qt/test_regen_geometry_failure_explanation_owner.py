from regen_geometry_constraint_discovery_audit_owner import (
    attach_regen_geometry_constraint_discovery_audit_owner,
)
from regen_geometry_constraint_validation_owner import (
    attach_regen_geometry_constraint_validation_owner,
)
from regen_geometry_failure_explanation_owner import (
    attach_regen_geometry_failure_explanation_owner,
)


def test_regen_geometry_failure_explanation_owner_explains_warn_and_fail():
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
    solved = attach_regen_geometry_failure_explanation_owner(solved)

    assert solved[
        "phase_11a3_regen_geometry_failure_explanation_owner_complete"
    ] is True

    assert solved[
        "phase_11a3_regen_geometry_failure_explanation_owner_status"
    ] == "PASS_PHASE_11A3_REGEN_GEOMETRY_FAILURE_EXPLANATION_OWNER"

    explanations = solved[
        "phase_11a3_regen_geometry_failure_explanation_owner_explanations"
    ]

    assert isinstance(explanations, list)
    assert len(explanations) > 0

    explanation_ids = {item["constraint_id"] for item in explanations}

    assert "channel_fit_ratio" in explanation_ids
    assert "effective_rib_width" in explanation_ids
    assert "coolant_velocity" in explanation_ids
    assert "reynolds_number" in explanation_ids
    assert "hot_wall_temperature" in explanation_ids

    for explanation in explanations:
        assert explanation["failure_mode"]
        assert explanation["engineering_meaning"]
        assert isinstance(explanation["likely_causes"], list)
        assert isinstance(explanation["engineering_consequences"], list)
        assert isinstance(explanation["future_recommendation_targets"], list)


def test_regen_geometry_failure_explanation_owner_handles_clean_validation():
    results = {
        "coolant_channel_count": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "channel_fit_ratio": 0.75,
        "effective_rib_width": 0.0008,
        "inner_wall_thickness": 0.0012,
        "regen_coolant_velocity": 25.0,
        "regen_reynolds_number": 50000,
        "regen_pressure_drop": 1200000,
        "regen_heat_flux": 18000000,
        "hot_gas_side_wall_temperature": 850,
        "coolant_side_wall_temperature": 450,
    }

    solved = attach_regen_geometry_constraint_discovery_audit_owner(results)
    solved = attach_regen_geometry_constraint_validation_owner(solved)
    solved = attach_regen_geometry_failure_explanation_owner(solved)

    assert solved[
        "phase_11a3_regen_geometry_failure_explanation_owner_complete"
    ] is True

    assert solved[
        "phase_11a3_regen_geometry_failure_explanation_owner_engineering_status"
    ] == "PASS_REGEN_GEOMETRY_FAILURE_EXPLANATION"

    assert solved[
        "phase_11a3_regen_geometry_failure_explanation_owner_explanations"
    ] == []


if __name__ == "__main__":
    test_regen_geometry_failure_explanation_owner_explains_warn_and_fail()
    test_regen_geometry_failure_explanation_owner_handles_clean_validation()
    print("PASS_REGEN_GEOMETRY_FAILURE_EXPLANATION_OWNER")