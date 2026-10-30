from leaf_qt.status_presentation import status_severity
"""
PHASE 11G.1
Candidate Creation Input Audit

Audits whether candidate creation architecture may begin.

Does NOT:
- create candidates
- mutate geometry
- score candidates
- rank candidates
- accept candidates
- commit geometry
- execute solvers
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

OWNER_NAME = "REGEN_CANDIDATE_CREATION_INPUT_AUDIT"
PHASE = "11G.1"

PASS_STATUS = "PASS_REGEN_CANDIDATE_CREATION_INPUT_AUDIT_PHASE_11G1"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_CREATION_INPUT_AUDIT_PHASE_11G1"


def attach_regen_candidate_creation_input_audit(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_creation_input_audit(results))
    return results


def build_regen_candidate_creation_input_audit(results):
    candidate_session = results.get("regen_candidate_generation_session", {})
    candidate_registry = results.get("regen_candidate_generation_registry", {})

    checks = [
        _check(
            "phase_11f_complete",
            results.get("phase_11f_complete") is True
            and results.get("regen_candidate_generation_architecture_complete") is True,
            "11F candidate generation architecture is complete.",
            "11F candidate generation architecture is not complete.",
        ),
        _check(
            "candidate_creation_architecture_allowed",
            results.get("phase_11g_candidate_creation_architecture_allowed") is True
            and results.get("regen_candidate_creation_architecture_allowed") is True,
            "11G candidate creation architecture may begin.",
            "11G candidate creation architecture is not allowed.",
        ),
        _check(
            "candidate_generation_session_exists",
            isinstance(candidate_session, dict)
            and bool(candidate_session.get("candidate_generation_session_id")),
            "Candidate generation session exists.",
            "Candidate generation session missing.",
        ),
        _check(
            "candidate_generation_registry_exists",
            isinstance(candidate_registry, dict)
            and bool(candidate_registry.get("candidate_generation_registry_id")),
            "Candidate generation registry exists.",
            "Candidate generation registry missing.",
        ),
        _check(
            "candidate_type_scope_available",
            len(candidate_session.get("candidate_type_scope", [])) >= 1,
            "Candidate type scope is available.",
            "Candidate type scope missing.",
        ),
        _check(
            "objective_available",
            bool(candidate_session.get("objective_mode")),
            "Objective mode is available.",
            "Objective mode missing.",
        ),
        _check(
            "population_size_valid",
            isinstance(candidate_session.get("population_size"), int)
            and candidate_session.get("population_size") >= 4,
            "Population size is valid.",
            "Population size invalid.",
        ),
        _check(
            "generation_limit_valid",
            isinstance(candidate_session.get("generation_limit"), int)
            and candidate_session.get("generation_limit") >= 1,
            "Generation limit is valid.",
            "Generation limit invalid.",
        ),
        _check(
            "candidate_pool_clean",
            candidate_session.get("candidate_count") == 0
            and candidate_session.get("population_count") == 0
            and candidate_session.get("generation_count") == 0,
            "Candidate pool is clean before creation architecture.",
            "Candidate pool should be empty before 11G.1.",
        ),
        _check(
            "required_geometry_inputs_present",
            _has_any_key(results, [
                "channel_geometry_valid",
                "regen_geometry_constraint_validation_status",
                "regen_geometry_output_architecture_status",
                "coolant_channel_width_m",
                "rib_width_m",
                "coolant_channel_height_m",
                "channel_count",
            ]),
            "Geometry-related input signals exist for future candidate creation.",
            "Geometry-related input signals missing.",
        ),
        _check(
            "required_validation_inputs_present",
            _has_any_key(results, [
                "stage_u_regen_validation_complete",
                "stage_v_regen_scalability_complete",
                "stage_w_real_engine_benchmark_complete",
                "regen_validation_status",
                "regen_scalability_completion_audit_status",
                "real_engine_benchmark_completion_audit_status",
            ]),
            "Validation input signals exist for future candidate creation.",
            "Validation input signals missing.",
        ),
        _check(
            "candidate_creation_locked",
            results.get("regen_candidate_generation_create_candidates_allowed") is False,
            "Candidate creation remains locked.",
            "Candidate creation must remain locked in 11G.1.",
        ),
        _check(
            "geometry_commit_locked",
            results.get("regen_optimisation_live_geometry_commit_allowed") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11G.1.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    audit = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "ready": ready,
        "candidate_generation_session_id": candidate_session.get("candidate_generation_session_id"),
        "candidate_generation_registry_id": candidate_registry.get("candidate_generation_registry_id"),
        "candidate_creation_state": "INPUT_AUDIT_READY_CREATION_LOCKED" if ready else "BLOCKED",
        "required_input_groups": [
            "candidate_generation_architecture",
            "geometry_inputs",
            "material_inputs",
            "coating_inputs",
            "thermal_inputs",
            "coolant_inputs",
            "validation_inputs",
            "source_quality_inputs",
        ],
        "next_phase": "11G.2_CANDIDATE_CREATION_SESSION_OWNER" if ready else None,
    }

    return {
        "regen_candidate_creation_input_audit_complete": True,
        "phase_11g_1_regen_candidate_creation_input_audit_complete": True,
        "regen_candidate_creation_input_audit_ready": ready,
        "regen_candidate_creation_input_audit_status": status,
        "regen_candidate_creation_input_audit": audit,
        "regen_candidate_creation_input_audit_checks": checks,
        "regen_candidate_creation_input_audit_failed_checks": failed,
        "regen_candidate_creation_input_audit_report": build_report(status, ready, audit, checks, failed),
        "phase_11g_2_candidate_creation_session_owner_allowed": ready,
        "regen_candidate_creation_session_owner_allowed": ready,
        "regen_candidate_creation_input_audit_passed": ready,
        "regen_candidate_creation_execution_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _has_any_key(results, keys):
    for key in keys:
        if key in results:
            return True
    return False


def build_report(status, ready, audit, checks, failed):
    lines = [
        "PHASE 11G.1 REGEN CANDIDATE CREATION INPUT AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11G.2 Candidate Creation Session Owner: {ready}",
        "",
        "INPUT AUDIT SNAPSHOT",
        f"Candidate Generation Session ID: {audit.get('candidate_generation_session_id')}",
        f"Candidate Generation Registry ID: {audit.get('candidate_generation_registry_id')}",
        f"Candidate Creation State: {audit.get('candidate_creation_state')}",
        f"Required Input Groups: {', '.join(audit.get('required_input_groups', []))}",
        "",
        "CHECKS",
    ]

    for check in checks:
        marker = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        message = check["pass_message"] if check["passed"] else check["fail_message"]
        lines.append(f"[{marker}] {check['name']} - {message}")

    if failed:
        lines.append("")
        lines.append("BLOCKERS")
        for check in failed:
            lines.append(f"- {check['name']}: {check['fail_message']}")
    else:
        lines.append("")
        lines.append("RESULT")
        lines.append("11G.1 candidate creation input audit is complete.")
        lines.append("11G.2 candidate creation session ownership may begin.")
        lines.append("Actual candidate creation, mutation, scoring, acceptance, solver execution, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
