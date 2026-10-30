from regen_geometry_failure_owner import (
    evaluate_regen_geometry_failure,
    flatten_regen_geometry_failure_result,
)
from regen_geometry_solver import solve_regen_geometry


def run_test():
    passing_solver_result = solve_regen_geometry(
        channel_mid_radius=0.012,
        coolant_mass_flow_rate=0.25,
        coolant_density=420.0,
        coolant_dynamic_viscosity=0.00018,
        target_reynolds_number=10000.0,
        minimum_rib_width=0.0005,
        minimum_channel_width=0.0005,
        maximum_channel_height=0.003,
        channel_aspect_ratio=3.0,
        minimum_channel_count=8,
        maximum_channel_count=220,
        maximum_coolant_velocity=80.0,
        minimum_hydraulic_diameter=0.00035,
        pressure_drop_limit=2.0e6,
        nozzle_length=0.15,
        minimum_cooling_coverage=0.25,
    )

    passing_failure = evaluate_regen_geometry_failure(passing_solver_result)
    passing_flat = flatten_regen_geometry_failure_result(passing_failure)

    assert passing_failure["regen_geometry_failure_owner_status"] == "PASS_REGEN_GEOMETRY_FAILURE_OWNER"
    assert "recommended_regen_geometry_failure_owner_status" in passing_flat

    failing_solver_result = {
        "solver_pass": False,
        "candidate_report": {
            "status": "NO_VALID_GEOMETRY_FOUND",
            "candidates_checked": 100,
            "valid_fit_candidates": 0,
            "iteration_history": {
                "most_common_failures": {
                    "EFFECTIVE_RIB_WIDTH_BELOW_MINIMUM": 80,
                    "COOLANT_VELOCITY_ABOVE_LIMIT": 20,
                }
            },
        },
    }

    failing_failure = evaluate_regen_geometry_failure(failing_solver_result)

    assert failing_failure["regen_geometry_failure_detected"] is True
    assert failing_failure["regen_geometry_primary_failure_reason"] == "EFFECTIVE_RIB_WIDTH_BELOW_MINIMUM"
    assert failing_failure["regen_geometry_secondary_failure_reason"] == "COOLANT_VELOCITY_ABOVE_LIMIT"
    assert failing_failure["regen_geometry_failure_severity"] == "HIGH"
    assert failing_failure["regen_geometry_dominant_failure_percentage"] == 80.0

    mapped = passing_solver_result["mapped_results"]
    assert "recommended_regen_geometry_failure_owner_status" in mapped
    assert "recommended_regen_geometry_primary_failure_reason" in mapped
    assert "recommended_regen_geometry_recommended_next_action" in mapped

    print("PASS_REGEN_GEOMETRY_FAILURE_OWNER")


if __name__ == "__main__":
    run_test()