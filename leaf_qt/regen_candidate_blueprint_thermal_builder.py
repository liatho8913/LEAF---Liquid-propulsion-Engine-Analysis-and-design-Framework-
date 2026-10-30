"""
PHASE 12B.3
Candidate Blueprint Thermal Builder

Attaches thermal packages to geometry-ready candidate blueprints.

Does NOT:
- run Bartz
- run coolant-side thermal solving
- run axial marching
- run the engine solver
- mutate candidates
- accept candidates
- commit geometry
"""
import math

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_THERMAL_BUILDER"
PHASE = "12B.3"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_THERMAL_BUILDER_PHASE_12B3"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_THERMAL_BUILDER_PHASE_12B3"


def attach_regen_candidate_blueprint_thermal_builder(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_thermal_builder(results))
    return results


def build_regen_candidate_blueprint_thermal_builder(results):
    blockers = []

    allowed = (
        results.get("phase_12b_3_candidate_blueprint_thermal_builder_allowed") is True
        and results.get("regen_candidate_blueprint_thermal_builder_allowed") is True
    )

    if not allowed:
        blockers.append("12B.2 geometry builder has not allowed thermal package building.")

    blueprints = results.get("regen_candidate_blueprints", [])
    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("No candidate blueprints are available.")

    if isinstance(blueprints, list):
        for blueprint in blueprints:
            package = blueprint.get("geometry_package", {})
            readiness = package.get("geometry_readiness", {}) if isinstance(package, dict) else {}
            if readiness.get("geometry_ready_for_thermal_builder") is not True:
                blockers.append(
                    f"Blueprint {blueprint.get('blueprint_id')} is not geometry-ready for thermal builder."
                )

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    enriched_blueprints = []
    if ready:
        for blueprint in blueprints:
            enriched_blueprints.append(_attach_thermal_package(blueprint, results))

        for blueprint in enriched_blueprints:
            thermal_package = blueprint.get("thermal_package", {})
            thermal_constraints = (
                thermal_package.get("thermal_constraints", {})
                if isinstance(thermal_package, dict)
                else {}
            )

            if (
                thermal_constraints.get("status")
                !=
                "PASS_THERMAL_PACKAGE_CONSTRAINTS"
            ):
                blockers.append(
                    f"Blueprint {blueprint.get('blueprint_id')} thermal constraints did not pass."
                )

        ready = len(blockers) == 0
        status = PASS_STATUS if ready else FAIL_STATUS

    report = build_report(status, ready, enriched_blueprints, blockers)

    return {
        "regen_candidate_blueprint_thermal_builder_complete": True,
        "phase_12b_3_regen_candidate_blueprint_thermal_builder_complete": True,
        "regen_candidate_blueprint_thermal_builder_ready": ready,
        "regen_candidate_blueprint_thermal_builder_status": status,
        "regen_candidate_blueprint_thermal_builder_blockers": blockers,

        "regen_candidate_blueprints": enriched_blueprints,
        "regen_candidate_blueprint_thermal_package_count": len(enriched_blueprints),
        "regen_candidate_blueprint_thermal_ready_ids": [
            blueprint.get("blueprint_id") for blueprint in enriched_blueprints
        ],
        "regen_candidate_blueprint_thermal_builder_report": report,

        "phase_12b_4_candidate_blueprint_validation_builder_allowed": ready,
        "regen_candidate_blueprint_validation_builder_allowed": ready,

        "regen_candidate_blueprint_generation_execution_allowed": False,
        "regen_candidate_blueprint_create_blueprints_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _attach_thermal_package(blueprint, results):
    updated = dict(blueprint)

    geometry_package = updated.get("geometry_package", {})
    dimensions = geometry_package if isinstance(geometry_package, dict) else {}

    thermal_package = _build_thermal_package(dimensions, results)

    updated["thermal_package"] = thermal_package
    updated["thermal_record"] = {
        "status": "THERMAL_PACKAGE_CREATED_SOLVER_NOT_EXECUTED",
        "solver_executed": False,
        "bartz_executed": False,
        "coolant_solver_executed": False,
        "axial_marching_executed": False,
        "thermal_package_ready_for_validation": thermal_package["thermal_readiness"][
            "thermal_ready_for_validation_builder"
        ],
    }

    updated["blueprint_thermal_status"] = "THERMAL_PACKAGE_CREATED_NOT_SOLVED"
    updated["blueprint_lifecycle_state"] = "BLUEPRINT_THERMAL_READY_VALIDATION_LOCKED"

    metadata = dict(updated.get("metadata_record", {}))
    metadata.update({
        "thermal_builder": OWNER_NAME,
        "thermal_package_created": True,
        "validation_builder_allowed": False,
        "solver_execution_allowed": False,
        "live_geometry_commit_allowed": False,
    })
    updated["metadata_record"] = metadata

    return updated


def _build_thermal_package(dimensions, results):
    heat_flux = _float(results.get("regen_heat_flux"), None)
    pressure_drop = _float(results.get("regen_pressure_drop"), None)
    validation_status = results.get("regen_validation_status")

    wall = _float(dimensions.get("hot_gas_wall_thickness_m"), 0.0)
    dh = _float(dimensions.get("hydraulic_diameter_m"), 0.0)
    area = _float(dimensions.get("total_coolant_flow_area_m2"), 0.0)
    flow_fraction = _float(dimensions.get("coolant_flow_fraction"), 1.0)

    thermal_constraints = _build_thermal_constraint_package(
        heat_flux=heat_flux,
        pressure_drop=pressure_drop,
        wall=wall,
        dh=dh,
        area=area,
        flow_fraction=flow_fraction,
    )

    readiness = _build_thermal_readiness_package(thermal_constraints)

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": "THERMAL_PACKAGE_CREATED_SOLVER_NOT_EXECUTED",
        "thermal_state": {
            "regen_heat_flux_reference": heat_flux,
            "regen_pressure_drop_reference": pressure_drop,
            "regen_validation_status_reference": validation_status,
            "hot_gas_wall_thickness_m": wall,
            "hydraulic_diameter_m": dh,
            "total_coolant_flow_area_m2": area,
            "coolant_flow_fraction": flow_fraction,
        },
        "thermal_constraints": thermal_constraints,
        "thermal_provenance": {
            "source": "12B.2_geometry_package_plus_existing_regen_signals",
            "derived_by": OWNER_NAME,
            "derived_phase": PHASE,
            "bartz_executed": False,
            "coolant_solver_executed": False,
            "axial_marching_executed": False,
            "solver_executed": False,
            "live_geometry_modified": False,
        },
        "heat_transfer_readiness": {
            "has_geometry_package": True,
            "has_hydraulic_diameter": dh > 0.0,
            "has_flow_area": area > 0.0,
            "has_wall_thickness": wall > 0.0,
            "has_reference_heat_flux": heat_flux is not None,
            "ready_for_real_solver": False,
        },
        "thermal_readiness": readiness,
    }


def _build_thermal_constraint_package(
        heat_flux,
        pressure_drop,
        wall,
        dh,
        area,
        flow_fraction,
):
    checks = [
        _check("wall_thickness_available", wall > 0.0, "Wall thickness is available."),
        _check("hydraulic_diameter_available", dh > 0.0, "Hydraulic diameter is available."),
        _check("coolant_area_available", area > 0.0, "Coolant flow area is available."),
        _check("coolant_flow_fraction_positive", flow_fraction > 0.0, "Coolant flow fraction is positive."),
        _check("reference_heat_flux_available", heat_flux is not None and math.isfinite(heat_flux), "Reference heat flux signal exists and is finite."),
        _check("reference_pressure_drop_available", pressure_drop is not None and math.isfinite(pressure_drop), "Reference pressure drop signal exists and is finite."),
    ]

    failed = [check for check in checks if not check["passed"]]

    return {
        "status": "PASS_THERMAL_PACKAGE_CONSTRAINTS" if not failed else "FAIL_THERMAL_PACKAGE_CONSTRAINTS",
        "checks": checks,
        "failed_checks": failed,
    }


def _build_thermal_readiness_package(constraints):
    ready = constraints.get("status") == "PASS_THERMAL_PACKAGE_CONSTRAINTS"

    return {
        "thermal_ready_for_validation_builder": ready,
        "thermal_ready_for_real_solver": False,
        "thermal_ready_for_mutation": False,
        "thermal_ready_for_candidate_acceptance": False,
        "thermal_ready_for_live_commit": False,
        "next_phase": "12B.4_CANDIDATE_BLUEPRINT_VALIDATION_BUILDER" if ready else None,
    }


def build_report(status, ready, blueprints, blockers):
    lines = [
        "PHASE 12B.3 REGEN CANDIDATE BLUEPRINT THERMAL BUILDER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12B.4 Candidate Blueprint Validation Builder: {ready}",
        f"Thermal Package Count: {len(blueprints)}",
        "",
    ]

    if ready:
        lines.append("BLUEPRINT THERMAL PACKAGES")
        for blueprint in blueprints:
            package = blueprint.get("thermal_package", {})
            state = package.get("thermal_state", {})
            lines.append(
                "- {bid}: q_ref={q}, dp_ref={dp}, Dh={dh}, area={area}, state={state}".format(
                    bid=blueprint.get("blueprint_id"),
                    q=state.get("regen_heat_flux_reference"),
                    dp=state.get("regen_pressure_drop_reference"),
                    dh=state.get("hydraulic_diameter_m"),
                    area=state.get("total_coolant_flow_area_m2"),
                    state=blueprint.get("blueprint_lifecycle_state"),
                )
            )

        lines.extend([
            "",
            "SAFETY STATE",
            "- Bartz execution: locked",
            "- Coolant solver execution: locked",
            "- Axial marching: locked",
            "- Solver execution: locked",
            "- Mutation: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12B.3 candidate blueprint thermal builder is complete.",
            "Thermal packages have been attached to all blueprint objects.",
            "12B.4 candidate blueprint validation builder may begin.",
        ])
    else:
        lines.append("BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")

    return "\n".join(lines)


def _require_locked(results, blockers):
    required_false = {
        "regen_candidate_blueprint_generation_execution_allowed":
            "Blueprint generation execution is not safely locked.",
        "regen_candidate_blueprint_create_blueprints_allowed":
            "Blueprint creation is not safely locked.",
        "regen_candidate_creation_create_candidates_allowed":
            "Candidate creation is not safely locked.",
        "regen_candidate_generation_create_candidates_allowed":
            "Candidate generation is not safely locked.",
        "regen_optimisation_runtime_execution_allowed":
            "Runtime optimisation execution is not safely locked.",
        "regen_optimisation_generation_advance_allowed":
            "Population generation advance is not safely locked.",
        "regen_optimisation_mutation_execution_allowed":
            "Mutation execution is not safely locked.",
        "regen_optimisation_candidate_acceptance_allowed":
            "Candidate acceptance is not safely locked.",
        "regen_optimisation_live_geometry_commit_allowed":
            "Live geometry commit is not safely locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)


def _float(value, default):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _check(name, passed, message):
    return {
        "name": name,
        "passed": bool(passed),
        "message": message,
    }
