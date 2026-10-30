"""
PHASE 12B.4
Candidate Blueprint Validation Builder

Builds validation packages for blueprints that already contain geometry and
thermal packages.

Does NOT:
- run Bartz
- run coolant solver
- run axial marching
- run optimisation
- mutate candidates
- accept candidates
- commit geometry
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_VALIDATION_BUILDER"
PHASE = "12B.4"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_VALIDATION_BUILDER_PHASE_12B4"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_VALIDATION_BUILDER_PHASE_12B4"


def attach_regen_candidate_blueprint_validation_builder(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_validation_builder(results))
    return results


def build_regen_candidate_blueprint_validation_builder(results):
    blockers = []

    allowed = (
        results.get("phase_12b_4_candidate_blueprint_validation_builder_allowed") is True
        and results.get("regen_candidate_blueprint_validation_builder_allowed") is True
    )

    if not allowed:
        blockers.append("12B.3 thermal builder has not allowed validation package building.")

    blueprints = results.get("regen_candidate_blueprints", [])
    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("No candidate blueprints are available.")

    if isinstance(blueprints, list):
        for blueprint in blueprints:
            geometry_package = blueprint.get("geometry_package", {})
            thermal_package = blueprint.get("thermal_package", {})

            geometry_readiness = (
                geometry_package.get("geometry_readiness", {})
                if isinstance(geometry_package, dict)
                else {}
            )
            thermal_readiness = (
                thermal_package.get("thermal_readiness", {})
                if isinstance(thermal_package, dict)
                else {}
            )

            if geometry_readiness.get("geometry_ready_for_thermal_builder") is not True:
                blockers.append(
                    f"Blueprint {blueprint.get('blueprint_id')} geometry package is not ready."
                )

            if thermal_readiness.get("thermal_ready_for_validation_builder") is not True:
                blockers.append(
                    f"Blueprint {blueprint.get('blueprint_id')} thermal package is not ready."
                )

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    validated_blueprints = []
    if ready:
        for blueprint in blueprints:
            validated_blueprints.append(_attach_validation_package(blueprint, results))

    report = build_report(status, ready, validated_blueprints, blockers)

    return {
        "regen_candidate_blueprint_validation_builder_complete": True,
        "phase_12b_4_regen_candidate_blueprint_validation_builder_complete": True,
        "regen_candidate_blueprint_validation_builder_ready": ready,
        "regen_candidate_blueprint_validation_builder_status": status,
        "regen_candidate_blueprint_validation_builder_blockers": blockers,

        "regen_candidate_blueprints": validated_blueprints,
        "regen_candidate_blueprint_validation_package_count": len(validated_blueprints),
        "regen_candidate_blueprint_validation_ready_ids": [
            blueprint.get("blueprint_id") for blueprint in validated_blueprints
        ],
        "regen_candidate_blueprint_validation_builder_report": report,

        "phase_12b_5_candidate_blueprint_completion_audit_allowed": ready,
        "regen_candidate_blueprint_completion_builder_audit_allowed": ready,

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


def _attach_validation_package(blueprint, results):
    updated = dict(blueprint)

    geometry_package = updated.get("geometry_package", {})
    thermal_package = updated.get("thermal_package", {})

    validation_package = _build_validation_package(
        geometry_package=geometry_package,
        thermal_package=thermal_package,
        results=results,
    )

    passed = validation_package["validation_readiness"]["blueprint_ready_for_completion_audit"]

    updated["validation_package"] = validation_package
    updated["validation_record"] = {
        "status": "VALIDATION_PACKAGE_CREATED",
        "validated": True,
        "validation_passed": passed,
        "solver_executed": False,
        "real_regen_validation_executed": False,
    }

    updated["blueprint_validation_status"] = (
        "BLUEPRINT_VALIDATION_PACKAGE_PASS"
        if passed
        else "BLUEPRINT_VALIDATION_PACKAGE_FAIL"
    )

    updated["blueprint_engineering_status"] = (
        "ENGINEERING_BLUEPRINT_READY_FOR_COMPLETION_AUDIT"
        if passed
        else "ENGINEERING_BLUEPRINT_BLOCKED_BY_VALIDATION_PACKAGE"
    )

    updated["blueprint_lifecycle_state"] = (
        "BLUEPRINT_VALIDATION_READY_COMPLETION_AUDIT_LOCKED"
        if passed
        else "BLUEPRINT_VALIDATION_BLOCKED"
    )

    metadata = dict(updated.get("metadata_record", {}))
    metadata.update({
        "validation_builder": OWNER_NAME,
        "validation_package_created": True,
        "completion_audit_allowed": passed,
        "solver_execution_allowed": False,
        "live_geometry_commit_allowed": False,
    })
    updated["metadata_record"] = metadata

    return updated


def _build_validation_package(geometry_package, thermal_package, results):
    geometry_constraints = (
        geometry_package.get("geometry_constraints", {})
        if isinstance(geometry_package, dict)
        else {}
    )
    thermal_constraints = (
        thermal_package.get("thermal_constraints", {})
        if isinstance(thermal_package, dict)
        else {}
    )

    geometry_readiness = (
        geometry_package.get("geometry_readiness", {})
        if isinstance(geometry_package, dict)
        else {}
    )
    thermal_readiness = (
        thermal_package.get("thermal_readiness", {})
        if isinstance(thermal_package, dict)
        else {}
    )

    checks = [
        _check(
            "geometry_package_exists",
            isinstance(geometry_package, dict) and bool(geometry_package),
            "Geometry package exists.",
        ),
        _check(
            "thermal_package_exists",
            isinstance(thermal_package, dict) and bool(thermal_package),
            "Thermal package exists.",
        ),
        _check(
            "geometry_constraints_pass",
            geometry_constraints.get("status") == "PASS_GEOMETRY_CONSTRAINT_PACKAGE",
            "Geometry constraints pass.",
        ),
        _check(
            "thermal_constraints_pass",
            thermal_constraints.get("status") == "PASS_THERMAL_PACKAGE_CONSTRAINTS",
            "Thermal constraints pass.",
        ),
        _check(
            "geometry_ready_for_thermal_builder",
            geometry_readiness.get("geometry_ready_for_thermal_builder") is True,
            "Geometry readiness is confirmed.",
        ),
        _check(
            "thermal_ready_for_validation_builder",
            thermal_readiness.get("thermal_ready_for_validation_builder") is True,
            "Thermal readiness is confirmed.",
        ),
        _check(
            "real_solver_not_executed",
            _solver_execution_locked(results),
            "Solver and optimisation execution remain locked.",
        ),
    ]

    failed = [check for check in checks if not check["passed"]]
    passed = len(failed) == 0

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": "PASS_BLUEPRINT_VALIDATION_PACKAGE" if passed else "FAIL_BLUEPRINT_VALIDATION_PACKAGE",
        "validation_constraints": {
            "checks": checks,
            "failed_checks": failed,
        },
        "validation_provenance": {
            "source": "12B.2_geometry_package_and_12B.3_thermal_package",
            "derived_by": OWNER_NAME,
            "derived_phase": PHASE,
            "real_solver_executed": False,
            "real_regen_validation_executed": False,
            "mutation_executed": False,
            "candidate_acceptance_executed": False,
            "live_geometry_modified": False,
        },
        "validation_readiness": {
            "blueprint_ready_for_completion_audit": passed,
            "blueprint_ready_for_population_builder": False,
            "blueprint_ready_for_mutation": False,
            "blueprint_ready_for_solver_execution": False,
            "blueprint_ready_for_candidate_acceptance": False,
            "blueprint_ready_for_live_commit": False,
            "next_phase": "12B.5_CANDIDATE_BLUEPRINT_COMPLETION_AUDIT" if passed else None,
        },
    }


def build_report(status, ready, blueprints, blockers):
    lines = [
        "PHASE 12B.4 REGEN CANDIDATE BLUEPRINT VALIDATION BUILDER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12B.5 Candidate Blueprint Completion Audit: {ready}",
        f"Validation Package Count: {len(blueprints)}",
        "",
    ]

    if ready:
        lines.append("BLUEPRINT VALIDATION PACKAGES")
        for blueprint in blueprints:
            package = blueprint.get("validation_package", {})
            readiness = package.get("validation_readiness", {})
            lines.append(
                "- {bid}: validation_status={status}, engineering_status={eng}, completion_ready={ready}".format(
                    bid=blueprint.get("blueprint_id"),
                    status=package.get("status"),
                    eng=blueprint.get("blueprint_engineering_status"),
                    ready=readiness.get("blueprint_ready_for_completion_audit"),
                )
            )

        lines.extend([
            "",
            "SAFETY STATE",
            "- Real solver execution: locked",
            "- Real regen validation: locked",
            "- Mutation: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12B.4 candidate blueprint validation builder is complete.",
            "Validation packages have been attached to all blueprint objects.",
            "12B.5 candidate blueprint completion audit may begin.",
        ])
    else:
        lines.append("BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")

    return "\n".join(lines)


def _solver_execution_locked(results):
    required_false = [
        "regen_candidate_blueprint_generation_execution_allowed",
        "regen_candidate_blueprint_create_blueprints_allowed",
        "regen_candidate_creation_create_candidates_allowed",
        "regen_candidate_generation_create_candidates_allowed",
        "regen_optimisation_runtime_execution_allowed",
        "regen_optimisation_generation_advance_allowed",
        "regen_optimisation_mutation_execution_allowed",
        "regen_optimisation_candidate_acceptance_allowed",
        "regen_optimisation_live_geometry_commit_allowed",
    ]
    return all(results.get(key) is False for key in required_false)


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


def _check(name, passed, message):
    return {
        "name": name,
        "passed": bool(passed),
        "message": message,
    }
