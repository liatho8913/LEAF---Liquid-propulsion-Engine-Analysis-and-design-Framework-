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
from regen_geometry_apply_recommendation_owner import (
    attach_regen_geometry_apply_recommendation_owner,
)


def test_regen_geometry_apply_recommendation_owner_creates_candidate():
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
    solved = attach_regen_geometry_apply_recommendation_owner(solved)

    assert solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_complete"
    ] is True

    assert solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_status"
    ] == "PASS_PHASE_11A5_REGEN_GEOMETRY_APPLY_RECOMMENDATION_OWNER"

    baseline = solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_baseline_geometry"
    ]

    candidate = solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry"
    ]

    assert isinstance(candidate, dict)
    assert candidate != baseline

    applied = solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_applied_actions"
    ]

    assert len(applied) > 0

    improvement = solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_improvement"
    ]

    assert improvement["changed_count"] > 0


def test_regen_geometry_apply_recommendation_owner_handles_clean_design():
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
    solved = attach_regen_geometry_apply_recommendation_owner(solved)

    assert solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_complete"
    ] is True

    assert solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_applied_count"
    ] == 0

    assert solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry"
    ] == solved[
        "phase_11a5_regen_geometry_apply_recommendation_owner_baseline_geometry"
    ]


if __name__ == "__main__":
    test_regen_geometry_apply_recommendation_owner_creates_candidate()
    test_regen_geometry_apply_recommendation_owner_handles_clean_design()
    print("PASS_REGEN_GEOMETRY_APPLY_RECOMMENDATION_OWNER")