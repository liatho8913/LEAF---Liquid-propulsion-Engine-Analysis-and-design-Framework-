from leaf_qt.solver_status_access import solver_pass as status_solver_pass
try:
    from leaf_qt.regen_geometry_candidate_generator import (
        generate_regen_geometry_candidates,
        map_candidate_report_to_engine_results,
    )
    from leaf_qt.regen_geometry_report_owner import (
        build_regen_geometry_report,
        flatten_regen_geometry_report,
    )
    from leaf_qt.regen_geometry_failure_owner import (
        evaluate_regen_geometry_failure,
        flatten_regen_geometry_failure_result,
    )
    from leaf_qt.regen_geometry_master_gate import (
        evaluate_regen_geometry_master_gate,
        flatten_regen_geometry_master_gate_result,
    )
except Exception:
    from regen_geometry_candidate_generator import (
        generate_regen_geometry_candidates,
        map_candidate_report_to_engine_results,
    )
    from regen_geometry_report_owner import (
        build_regen_geometry_report,
        flatten_regen_geometry_report,
    )
    from regen_geometry_failure_owner import (
        evaluate_regen_geometry_failure,
        flatten_regen_geometry_failure_result,
    )
    from regen_geometry_master_gate import (
        evaluate_regen_geometry_master_gate,
        flatten_regen_geometry_master_gate_result,
    )

def solve_regen_geometry(
    channel_mid_radius=None,
    coolant_mass_flow_rate=None,
    coolant_density=None,
    coolant_dynamic_viscosity=None,
    target_reynolds_number=10000.0,
    minimum_rib_width=0.0005,
    minimum_channel_width=0.0005,
    maximum_channel_height=None,
    channel_aspect_ratio=2.0,
    minimum_channel_count=4,
    maximum_channel_count=300,
    maximum_coolant_velocity=None,
    minimum_hydraulic_diameter=None,
    pressure_drop_limit=None,
    nozzle_length=None,
    minimum_cooling_coverage=None,
):
    """
    Regen Geometry Phase 1D solver wrapper.

    This is the stable public interface for automatic regen geometry solving.

    It owns:
    - calling the candidate generator
    - preserving the solver-level status
    - exposing the best candidate
    - exposing iteration history
    - exposing flattened engine-result keys

    It does not own:
    - low-level geometry constraints
    - thermal validation
    - material validation
    - coating validation
    """

    candidate_report = generate_regen_geometry_candidates(
        channel_mid_radius=channel_mid_radius,
        coolant_mass_flow_rate=coolant_mass_flow_rate,
        coolant_density=coolant_density,
        coolant_dynamic_viscosity=coolant_dynamic_viscosity,
        target_reynolds_number=target_reynolds_number,
        minimum_rib_width=minimum_rib_width,
        minimum_channel_width=minimum_channel_width,
        maximum_channel_height=maximum_channel_height,
        channel_aspect_ratio=channel_aspect_ratio,
        minimum_channel_count=minimum_channel_count,
        maximum_channel_count=maximum_channel_count,
        maximum_coolant_velocity=maximum_coolant_velocity,
        minimum_hydraulic_diameter=minimum_hydraulic_diameter,
        pressure_drop_limit=pressure_drop_limit,
        nozzle_length=nozzle_length,
        minimum_cooling_coverage=minimum_cooling_coverage,
    )

    mapped_results = map_candidate_report_to_engine_results(
        candidate_report,
        target_reynolds_number=target_reynolds_number,
    )

    best_candidate = candidate_report.get("best_candidate")
    solver_pass = status_solver_pass(candidate_report.get("status")) and best_candidate is not None

    solver_status = "PASS_REGEN_GEOMETRY_SOLVER" if solver_pass else "FAIL_REGEN_GEOMETRY_SOLVER"

    solver_report = {
        "regen_geometry_solver_status": solver_status,
        "regen_geometry_solver_pass": solver_pass,
        "regen_geometry_candidate_report": candidate_report,
        "regen_geometry_best_candidate": best_candidate,
        "regen_geometry_iteration_history": candidate_report.get("iteration_history", {}),
        "regen_geometry_engine_result_keys": mapped_results,
    }

    temporary_solver_result = {
        "solver_status": solver_status,
        "solver_pass": solver_pass,
        "best_candidate": best_candidate,
        "candidate_report": candidate_report,
        "mapped_results": mapped_results,
        "solver_report": solver_report,
    }

    regen_geometry_report = build_regen_geometry_report(temporary_solver_result)
    report_flat = flatten_regen_geometry_report(regen_geometry_report)
    failure_result = evaluate_regen_geometry_failure(temporary_solver_result)
    failure_flat = flatten_regen_geometry_failure_result(failure_result)

    mapped_results.update(
        {
            "recommended_regen_geometry_solver_status": solver_status,
            "recommended_regen_geometry_solver_pass": 1.0 if solver_pass else 0.0,
        }
    )

    mapped_results.update(report_flat)
    mapped_results.update(failure_flat)

    gate_input = {
        "solver_status": solver_status,
        "solver_pass": solver_pass,
        "best_candidate": best_candidate,
        "candidate_report": candidate_report,
        "mapped_results": mapped_results,
        "solver_report": solver_report,
        "regen_geometry_report": regen_geometry_report,
        "regen_geometry_failure": failure_result,
    }

    master_gate_result = evaluate_regen_geometry_master_gate(gate_input)
    master_gate_flat = flatten_regen_geometry_master_gate_result(master_gate_result)

    mapped_results.update(master_gate_flat)

    return {
        "solver_status": solver_status,
        "solver_pass": solver_pass,
        "best_candidate": best_candidate,
        "candidate_report": candidate_report,
        "mapped_results": mapped_results,
        "solver_report": solver_report,
        "regen_geometry_report": regen_geometry_report,
        "regen_geometry_failure": failure_result,
        "regen_geometry_master_gate": master_gate_result,
    }


def solve_regen_geometry_to_engine_results(**kwargs):
    """
    Convenience function for engine_solver.py.

    Returns only flattened result keys suitable for merging into the main
    results dictionary.
    """

    result = solve_regen_geometry(**kwargs)
    return result.get("mapped_results", {})