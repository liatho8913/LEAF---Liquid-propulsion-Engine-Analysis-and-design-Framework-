from leaf_qt.status_presentation import status_severity
"""
PHASE 12D.6
Candidate Blueprint Optimisation Completion Audit
"""

try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity in {"PASS", "WARN", "FAIL"}:
                return severity
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_OPTIMISATION_COMPLETION_AUDIT"
PHASE = "12D.6"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_OPTIMISATION_COMPLETION_AUDIT_PHASE_12D6"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_OPTIMISATION_COMPLETION_AUDIT_PHASE_12D6"


def attach_regen_candidate_blueprint_optimisation_completion_audit(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_candidate_blueprint_optimisation_completion_audit(results))
    return results


def build_regen_candidate_blueprint_optimisation_completion_audit(results):
    blockers = []

    allowed = (
        results.get("phase_12d_6_candidate_blueprint_optimisation_completion_audit_allowed") is True
        and results.get("regen_candidate_blueprint_optimisation_completion_audit_allowed") is True
    )

    if not allowed:
        blockers.append("12D.5 termination owner has not allowed optimisation completion audit.")

    checks = _build_checks(results)
    failed_checks = [check for check in checks if not check["passed"]]

    _require_locked(results, blockers)

    ready = len(blockers) == 0 and len(failed_checks) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    audit = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "ready": ready,
        "complete": ready,
        "check_count": len(checks),
        "failed_check_count": len(failed_checks),
        "failed_checks": [check["name"] for check in failed_checks],
        "optimisation_foundation_state": (
            "CANDIDATE_BLUEPRINT_OPTIMISATION_FOUNDATION_COMPLETE_EXECUTION_LOCKED"
            if ready
            else "CANDIDATE_BLUEPRINT_OPTIMISATION_FOUNDATION_INCOMPLETE"
        ),
        "next_phase": "13A_AUTONOMOUS_BLUEPRINT_MUTATION_EXECUTION_FOUNDATION" if ready else None,
    }

    return {
        "regen_candidate_blueprint_optimisation_completion_audit_complete": True,
        "phase_12d_6_regen_candidate_blueprint_optimisation_completion_audit_complete": True,
        "regen_candidate_blueprint_optimisation_completion_audit_ready": ready,
        "regen_candidate_blueprint_optimisation_completion_audit_status": status,
        "regen_candidate_blueprint_optimisation_completion_audit_blockers": blockers,

        "regen_candidate_blueprint_optimisation_completion_audit": audit,
        "regen_candidate_blueprint_optimisation_completion_audit_checks": checks,
        "regen_candidate_blueprint_optimisation_completion_audit_failed_checks": failed_checks,
        "regen_candidate_blueprint_optimisation_completion_audit_report": _report(
            status, ready, audit, checks, failed_checks, blockers
        ),

        "phase_12_candidate_blueprint_optimisation_foundation_complete": ready,
        "regen_candidate_blueprint_optimisation_foundation_complete": ready,

        "phase_13a_autonomous_blueprint_mutation_execution_foundation_allowed": ready,
        "regen_autonomous_blueprint_mutation_execution_foundation_allowed": ready,

        "regen_candidate_blueprint_mutation_execution_allowed": False,
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


def _build_checks(results):
    return [
        _check(
            "population_architecture_complete",
            results.get("regen_candidate_blueprint_population_architecture_complete") is True,
            "12C population architecture is complete.",
        ),
        _check(
            "mutation_architecture_complete",
            results.get("phase_12d_1_regen_candidate_blueprint_mutation_architecture_complete") is True
            and results.get("regen_candidate_blueprint_mutation_architecture_ready") is True,
            "12D.1 mutation architecture is complete.",
        ),
        _check(
            "mutation_validation_complete",
            results.get("phase_12d_2_regen_candidate_blueprint_mutation_validation_complete") is True
            and results.get("regen_candidate_blueprint_mutation_validation_ready") is True,
            "12D.2 mutation validation is complete.",
        ),
        _check(
            "diversity_controller_complete",
            results.get("phase_12d_3_regen_candidate_blueprint_diversity_controller_complete") is True
            and results.get("regen_candidate_blueprint_diversity_controller_ready") is True,
            "12D.3 diversity controller is complete.",
        ),
        _check(
            "convergence_monitor_complete",
            results.get("phase_12d_4_regen_candidate_blueprint_convergence_monitor_complete") is True
            and results.get("regen_candidate_blueprint_convergence_monitor_ready") is True,
            "12D.4 convergence monitor is complete.",
        ),
        _check(
            "termination_owner_complete",
            results.get("phase_12d_5_regen_candidate_blueprint_termination_owner_complete") is True
            and results.get("regen_candidate_blueprint_termination_owner_ready") is True,
            "12D.5 termination owner is complete.",
        ),
        _check(
            "mutation_architecture_object_exists",
            isinstance(results.get("regen_candidate_blueprint_mutation_architecture"), dict),
            "Mutation architecture object exists.",
        ),
        _check(
            "mutation_validation_object_exists",
            isinstance(results.get("regen_candidate_blueprint_mutation_validation"), dict),
            "Mutation validation object exists.",
        ),
        _check(
            "diversity_controller_object_exists",
            isinstance(results.get("regen_candidate_blueprint_diversity_controller"), dict),
            "Diversity controller object exists.",
        ),
        _check(
            "convergence_monitor_object_exists",
            isinstance(results.get("regen_candidate_blueprint_convergence_monitor"), dict),
            "Convergence monitor object exists.",
        ),
        _check(
            "termination_owner_object_exists",
            isinstance(results.get("regen_candidate_blueprint_termination_owner"), dict),
            "Termination owner object exists.",
        ),
        _check(
            "execution_locks_closed",
            _global_execution_locks_closed(results),
            "All mutation, solver, acceptance, and live-commit execution locks remain closed.",
        ),
    ]


def _require_locked(results, blockers):
    required_false = {
        "regen_candidate_blueprint_mutation_execution_allowed": "Candidate blueprint mutation execution is not safely locked.",
        "regen_candidate_blueprint_generation_execution_allowed": "Blueprint generation execution is not safely locked.",
        "regen_candidate_blueprint_create_blueprints_allowed": "Blueprint creation is not safely locked.",
        "regen_candidate_creation_create_candidates_allowed": "Candidate creation is not safely locked.",
        "regen_candidate_generation_create_candidates_allowed": "Candidate generation is not safely locked.",
        "regen_optimisation_runtime_execution_allowed": "Runtime optimisation execution is not safely locked.",
        "regen_optimisation_generation_advance_allowed": "Population generation advance is not safely locked.",
        "regen_optimisation_mutation_execution_allowed": "Mutation execution is not safely locked.",
        "regen_optimisation_candidate_acceptance_allowed": "Candidate acceptance is not safely locked.",
        "regen_optimisation_live_geometry_commit_allowed": "Live geometry commit is not safely locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)


def _global_execution_locks_closed(results):
    keys = [
        "regen_candidate_blueprint_mutation_execution_allowed",
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
    return all(results.get(key) is False for key in keys)


def _check(name, passed, message):
    return {
        "name": name,
        "passed": bool(passed),
        "message": message,
    }


def _report(status, ready, audit, checks, failed_checks, blockers):
    lines = [
        "PHASE 12D.6 REGEN CANDIDATE BLUEPRINT OPTIMISATION COMPLETION AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Optimisation Foundation Complete: {ready}",
        f"Foundation State: {audit.get('optimisation_foundation_state')}",
        "",
        "COMPLETION CHECKS",
    ]

    for check in checks:
        marker = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        lines.append(f"[{marker}] {check['name']} - {check['message']}")

    if blockers:
        lines.append("")
        lines.append("BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")

    if failed_checks:
        lines.append("")
        lines.append("FAILED CHECKS")
        for check in failed_checks:
            lines.append(f"- {check['name']}")

    if ready:
        lines.extend([
            "",
            "RESULT",
            "Phase 12 candidate blueprint optimisation foundation is complete.",
            "Execution remains locked.",
            "Phase 13A autonomous blueprint mutation execution foundation may begin.",
        ])

    return "\n".join(lines)
