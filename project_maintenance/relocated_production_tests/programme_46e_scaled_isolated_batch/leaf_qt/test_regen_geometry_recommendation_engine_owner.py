from regen_geometry_constraint_discovery_audit_owner import (
    attach_regen_geometry_constraint_discovery_audit_owner,
)
from regen_geometry_constraint_validation_owner import (
    attach_regen_geometry_constraint_validation_owner,
)
from regen_geometry_failure_explanation_owner import (
    attach_regen_geometry_failure_explanation_owner,
)
from regen_geometry_recommendation_engine_owner import (
    attach_regen_geometry_recommendation_engine_owner,
)


def test_regen_geometry_recommendation_engine_generates_actions_for_failures():
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
    solved = attach_regen_geometry_recommendation_engine_owner(solved)

    assert solved[
        "phase_11a4_regen_geometry_recommendation_engine_owner_complete"
    ] is True

    assert solved[
        "phase_11a4_regen_geometry_recommendation_engine_owner_status"
    ] == "PASS_PHASE_11A4_REGEN_GEOMETRY_RECOMMENDATION_ENGINE_OWNER"

    recommendations = solved[
        "phase_11a4_regen_geometry_recommendation_engine_owner_recommendations"
    ]

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    recommendation_ids = {item["recommendation_id"] for item in recommendations}

    assert "reduce_channel_pitch_demand" in recommendation_ids
    assert "restore_effective_rib_width" in recommendation_ids
    assert "correct_coolant_velocity" in recommendation_ids
    assert "increase_reynolds_number_margin" in recommendation_ids
    assert "reduce_hot_wall_temperature" in recommendation_ids

    for recommendation in recommendations:
        assert recommendation["title"]
        assert recommendation["rationale"]
        assert recommendation["target_variables"]
        assert recommendation["proposed_direction"]
        assert recommendation["expected_benefit"]


def test_regen_geometry_recommendation_engine_handles_clean_design():
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
    solved = attach_regen_geometry_recommendation_engine_owner(solved)

    assert solved[
        "phase_11a4_regen_geometry_recommendation_engine_owner_complete"
    ] is True

    assert solved[
        "phase_11a4_regen_geometry_recommendation_engine_owner_recommendations"
    ] == []

    assert solved[
        "phase_11a4_regen_geometry_recommendation_engine_owner_engineering_status"
    ] == "PASS_REGEN_GEOMETRY_RECOMMENDATION_ENGINE"


if __name__ == "__main__":
    test_regen_geometry_recommendation_engine_generates_actions_for_failures()
    test_regen_geometry_recommendation_engine_handles_clean_design()
    print("PASS_REGEN_GEOMETRY_RECOMMENDATION_ENGINE_OWNER")