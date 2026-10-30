"""
PHASE 12B.5
Candidate Blueprint Engineering Completion Audit

Final audit for generated candidate blueprint engineering objects.

Does NOT:
- run solver
- run Bartz
- run coolant solver
- mutate candidates
- accept candidates
- commit geometry
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_ENGINEERING_COMPLETION_AUDIT"
PHASE = "12B.5"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_ENGINEERING_COMPLETION_AUDIT_PHASE_12B5"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_ENGINEERING_COMPLETION_AUDIT_PHASE_12B5"


def attach_regen_candidate_blueprint_engineering_completion_audit(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_engineering_completion_audit(results))
    return results


def build_regen_candidate_blueprint_engineering_completion_audit(results):
    blockers = []

    allowed = (
        results.get("phase_12b_5_candidate_blueprint_completion_audit_allowed") is True
        and results.get("regen_candidate_blueprint_completion_builder_audit_allowed") is True
    )

    if not allowed:
        blockers.append("12B.4 validation builder has not allowed blueprint completion audit.")

    blueprints = results.get("regen_candidate_blueprints", [])
    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("No candidate blueprints are available for completion audit.")

    _require_locked(results, blockers)

    audited_blueprints = []
    if isinstance(blueprints, list) and blueprints:
        for blueprint in blueprints:
            audited_blueprints.append(_audit_blueprint(blueprint))

    failed_blueprints = [
        blueprint for blueprint in audited_blueprints
        if blueprint.get("blueprint_completion_status") != "PASS_BLUEPRINT_ENGINEERING_COMPLETION_AUDIT"
    ]

    ready = len(blockers) == 0 and len(audited_blueprints) > 0 and len(failed_blueprints) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    audit = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "complete": ready,
        "ready": ready,
        "blueprint_count": len(audited_blueprints),
        "failed_blueprint_count": len(failed_blueprints),
        "failed_blueprint_ids": [
            blueprint.get("blueprint_id") for blueprint in failed_blueprints
        ],
        "blueprint_engineering_state": (
            "BLUEPRINT_ENGINEERING_OBJECTS_COMPLETE_POPULATION_LOCKED"
            if ready
            else "BLUEPRINT_ENGINEERING_OBJECTS_INCOMPLETE"
        ),
        "next_phase": "12C.1_CANDIDATE_BLUEPRINT_POPULATION_BUILDER" if ready else None,
    }

    report = build_report(status, ready, audit, audited_blueprints, blockers)

    return {
        "regen_candidate_blueprint_engineering_completion_audit_complete": True,
        "phase_12b_5_regen_candidate_blueprint_engineering_completion_audit_complete": True,
        "regen_candidate_blueprint_engineering_completion_audit_ready": ready,
        "regen_candidate_blueprint_engineering_completion_audit_status": status,
        "regen_candidate_blueprint_engineering_completion_audit_blockers": blockers,
        "regen_candidate_blueprint_engineering_completion_audit": audit,
        "regen_candidate_blueprints": audited_blueprints,
        "regen_candidate_blueprint_engineering_complete_count": len(audited_blueprints) - len(failed_blueprints),
        "regen_candidate_blueprint_engineering_failed_count": len(failed_blueprints),
        "regen_candidate_blueprint_engineering_complete_ids": [
            blueprint.get("blueprint_id")
            for blueprint in audited_blueprints
            if blueprint.get("blueprint_completion_status") == "PASS_BLUEPRINT_ENGINEERING_COMPLETION_AUDIT"
        ],
        "regen_candidate_blueprint_engineering_completion_audit_report": report,

        "phase_12c_1_candidate_blueprint_population_builder_allowed": ready,
        "regen_candidate_blueprint_population_builder_allowed": ready,

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


def _audit_blueprint(blueprint):
    updated = dict(blueprint)

    checks = [
        _check(
            "blueprint_id_exists",
            bool(updated.get("blueprint_id")),
            "Blueprint ID exists.",
        ),
        _check(
            "geometry_package_exists",
            isinstance(updated.get("geometry_package"), dict)
            and bool(updated.get("geometry_package")),
            "Geometry package exists.",
        ),
        _check(
            "thermal_package_exists",
            isinstance(updated.get("thermal_package"), dict)
            and bool(updated.get("thermal_package")),
            "Thermal package exists.",
        ),
        _check(
            "validation_package_exists",
            isinstance(updated.get("validation_package"), dict)
            and bool(updated.get("validation_package")),
            "Validation package exists.",
        ),
        _check(
            "geometry_constraints_pass",
            _safe_get(updated, "geometry_package", "geometry_constraints", "status")
            == "PASS_GEOMETRY_CONSTRAINT_PACKAGE",
            "Geometry constraints pass.",
        ),
        _check(
            "thermal_constraints_pass",
            _safe_get(updated, "thermal_package", "thermal_constraints", "status")
            == "PASS_THERMAL_PACKAGE_CONSTRAINTS",
            "Thermal constraints pass.",
        ),
        _check(
            "validation_package_pass",
            _safe_get(updated, "validation_package", "status")
            == "PASS_BLUEPRINT_VALIDATION_PACKAGE",
            "Validation package passes.",
        ),
        _check(
            "engineering_status_ready",
            updated.get("blueprint_engineering_status")
            == "ENGINEERING_BLUEPRINT_READY_FOR_COMPLETION_AUDIT",
            "Blueprint engineering status is ready.",
        ),
        _check(
            "lifecycle_state_ready",
            updated.get("blueprint_lifecycle_state")
            == "BLUEPRINT_VALIDATION_READY_COMPLETION_AUDIT_LOCKED",
            "Blueprint lifecycle is ready for completion audit.",
        ),
        _check(
            "provenance_solver_locked",
            _solver_never_executed(updated),
            "Blueprint provenance confirms solver execution remains locked.",
        ),
        _check(
            "metadata_commit_locked",
            _metadata_locked(updated),
            "Blueprint metadata confirms mutation, acceptance, and live commit remain locked.",
        ),
    ]

    failed = [check for check in checks if not check["passed"]]
    passed = len(failed) == 0

    completion_audit = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": (
            "PASS_BLUEPRINT_ENGINEERING_COMPLETION_AUDIT"
            if passed
            else "FAIL_BLUEPRINT_ENGINEERING_COMPLETION_AUDIT"
        ),
        "complete": passed,
        "ready": passed,
        "checks": checks,
        "failed_checks": failed,
        "blueprint_completion_state": (
            "COMPLETE_ENGINEERING_BLUEPRINT_POPULATION_READY"
            if passed
            else "INCOMPLETE_ENGINEERING_BLUEPRINT"
        ),
        "next_phase": "12C.1_CANDIDATE_BLUEPRINT_POPULATION_BUILDER" if passed else None,
    }

    updated["blueprint_completion_audit"] = completion_audit
    updated["blueprint_completion_status"] = completion_audit["status"]
    updated["blueprint_lifecycle_state"] = (
        "BLUEPRINT_ENGINEERING_COMPLETE_POPULATION_LOCKED"
        if passed
        else "BLUEPRINT_ENGINEERING_COMPLETION_BLOCKED"
    )
    updated["blueprint_engineering_status"] = (
        "ENGINEERING_BLUEPRINT_COMPLETE_READY_FOR_POPULATION"
        if passed
        else "ENGINEERING_BLUEPRINT_INCOMPLETE"
    )

    metadata = dict(updated.get("metadata_record", {}))
    metadata.update({
        "engineering_completion_audit": OWNER_NAME,
        "engineering_completion_audit_complete": passed,
        "population_builder_allowed": passed,
        "solver_execution_allowed": False,
        "mutation_allowed": False,
        "candidate_acceptance_allowed": False,
        "live_geometry_commit_allowed": False,
    })
    updated["metadata_record"] = metadata

    return updated


def build_report(status, ready, audit, blueprints, blockers):
    lines = [
        "PHASE 12B.5 REGEN CANDIDATE BLUEPRINT ENGINEERING COMPLETION AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12C.1 Candidate Blueprint Population Builder: {ready}",
        f"Blueprint Count: {audit.get('blueprint_count')}",
        f"Failed Blueprint Count: {audit.get('failed_blueprint_count')}",
        f"Engineering State: {audit.get('blueprint_engineering_state')}",
        "",
    ]

    if blockers:
        lines.append("SYSTEM BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")
        lines.append("")

    lines.append("BLUEPRINT COMPLETION AUDITS")

    for blueprint in blueprints:
        completion = blueprint.get("blueprint_completion_audit", {})
        lines.append(
            "- {bid}: {status}; engineering={eng}; lifecycle={life}".format(
                bid=blueprint.get("blueprint_id"),
                status=completion.get("status"),
                eng=blueprint.get("blueprint_engineering_status"),
                life=blueprint.get("blueprint_lifecycle_state"),
            )
        )

        failed = completion.get("failed_checks", [])
        if failed:
            for check in failed:
                lines.append(f"  - FAIL {check.get('name')}: {check.get('message')}")

    if ready:
        lines.extend([
            "",
            "SAFETY STATE",
            "- Solver execution: locked",
            "- Real regen validation: locked",
            "- Mutation: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12B.5 candidate blueprint engineering completion audit is complete.",
            "Blueprint engineering objects are complete.",
            "12C.1 candidate blueprint population builder may begin.",
        ])
    else:
        lines.extend([
            "",
            "RESULT",
            "12B.5 candidate blueprint engineering completion audit is blocked.",
        ])

    return "\n".join(lines)


def _solver_never_executed(blueprint):
    geometry_prov = _safe_get(blueprint, "geometry_package", "geometry_provenance") or {}
    thermal_prov = _safe_get(blueprint, "thermal_package", "thermal_provenance") or {}
    validation_prov = _safe_get(blueprint, "validation_package", "validation_provenance") or {}

    checks = [
        geometry_prov.get("solver_executed") is False,
        geometry_prov.get("live_geometry_modified") is False,
        thermal_prov.get("solver_executed") is False,
        thermal_prov.get("bartz_executed") is False,
        thermal_prov.get("coolant_solver_executed") is False,
        thermal_prov.get("axial_marching_executed") is False,
        thermal_prov.get("live_geometry_modified") is False,
        validation_prov.get("real_solver_executed") is False,
        validation_prov.get("real_regen_validation_executed") is False,
        validation_prov.get("mutation_executed") is False,
        validation_prov.get("candidate_acceptance_executed") is False,
        validation_prov.get("live_geometry_modified") is False,
    ]

    return all(checks)


def _metadata_locked(blueprint):
    metadata = blueprint.get("metadata_record", {})
    if not isinstance(metadata, dict):
        return False

    return (
        metadata.get("solver_execution_allowed") is False
        and metadata.get("live_geometry_commit_allowed") is False
        and metadata.get("mutation_allowed") is False
        and metadata.get("candidate_acceptance_allowed") is False
    )


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


def _safe_get(data, *keys):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _check(name, passed, message):
    return {
        "name": name,
        "passed": bool(passed),
        "message": message,
    }
