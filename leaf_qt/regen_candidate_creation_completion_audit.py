from leaf_qt.status_presentation import status_severity
"""
PHASE 11G.5
Candidate Creation Completion Audit

Final audit for candidate creation ownership architecture.

Does NOT:
- create candidates
- create blueprints
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

OWNER_NAME = "REGEN_CANDIDATE_CREATION_COMPLETION_AUDIT"
PHASE = "11G.5"

PASS_STATUS = "PASS_REGEN_CANDIDATE_CREATION_COMPLETION_AUDIT_PHASE_11G5"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_CREATION_COMPLETION_AUDIT_PHASE_11G5"


def attach_regen_candidate_creation_completion_audit(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_creation_completion_audit(results))
    return results


def build_regen_candidate_creation_completion_audit(results):
    registry = results.get("regen_candidate_creation_registry", {})

    checks = [
        _check(
            "candidate_creation_input_audit_complete",
            results.get("phase_11g_1_regen_candidate_creation_input_audit_complete") is True
            and results.get("regen_candidate_creation_input_audit_ready") is True,
            "11G.1 candidate creation input audit is complete and ready.",
            "11G.1 candidate creation input audit is incomplete or not ready.",
        ),
        _check(
            "candidate_creation_session_owner_complete",
            results.get("phase_11g_2_regen_candidate_creation_session_owner_complete") is True
            and results.get("regen_candidate_creation_session_owner_ready") is True,
            "11G.2 candidate creation session owner is complete and ready.",
            "11G.2 candidate creation session owner is incomplete or not ready.",
        ),
        _check(
            "candidate_creation_report_owner_complete",
            results.get("phase_11g_3_regen_candidate_creation_report_owner_complete") is True
            and results.get("regen_candidate_creation_report_owner_ready") is True,
            "11G.3 candidate creation report owner is complete and ready.",
            "11G.3 candidate creation report owner is incomplete or not ready.",
        ),
        _check(
            "candidate_creation_registration_owner_complete",
            results.get("phase_11g_4_regen_candidate_creation_registration_owner_complete") is True
            and results.get("regen_candidate_creation_registration_owner_ready") is True,
            "11G.4 candidate creation registration owner is complete and ready.",
            "11G.4 candidate creation registration owner is incomplete or not ready.",
        ),
        _check(
            "candidate_creation_session_exists",
            isinstance(results.get("regen_candidate_creation_session"), dict),
            "Candidate creation session object exists.",
            "Candidate creation session object missing.",
        ),
        _check(
            "candidate_creation_report_bundle_exists",
            isinstance(results.get("regen_candidate_creation_report_bundle"), dict),
            "Candidate creation report bundle exists.",
            "Candidate creation report bundle missing.",
        ),
        _check(
            "candidate_creation_registry_exists",
            isinstance(registry, dict) and bool(registry.get("candidate_creation_registry_id")),
            "Candidate creation registry exists.",
            "Candidate creation registry missing.",
        ),
        _check(
            "creation_registry_has_session",
            registry.get("creation_session_registry", {}).get("creation_session_count") == 1,
            "Creation registry contains one creation session.",
            "Creation registry does not contain the expected creation session.",
        ),
        _check(
            "creation_registry_has_reports",
            registry.get("creation_report_registry", {}).get("creation_report_count") == 5,
            "Creation registry contains all five creation reports.",
            "Creation registry does not contain all creation reports.",
        ),
        _check(
            "creation_state_registered",
            registry.get("creation_state_registry", {}).get("registered") is True,
            "Creation state registry is registered.",
            "Creation state registry is not registered.",
        ),
        _check(
            "creation_capabilities_registered",
            registry.get("creation_capability_registry", {}).get("registered") is True,
            "Creation capability registry is registered.",
            "Creation capability registry is not registered.",
        ),
        _check(
            "candidate_creation_locked",
            results.get("regen_candidate_creation_create_candidates_allowed") is False,
            "Candidate creation remains locked.",
            "Candidate creation must remain locked until Phase 12A.",
        ),
        _check(
            "blueprint_creation_locked",
            registry.get("candidate_blueprint_creation_enabled") is False,
            "Candidate blueprint creation remains locked.",
            "Candidate blueprint creation must remain locked until Phase 12A.",
        ),
        _check(
            "mutation_locked",
            results.get("regen_optimisation_mutation_execution_allowed") is False,
            "Mutation remains locked.",
            "Mutation must remain locked.",
        ),
        _check(
            "candidate_acceptance_locked",
            results.get("regen_optimisation_candidate_acceptance_allowed") is False,
            "Candidate acceptance remains locked.",
            "Candidate acceptance must remain locked.",
        ),
        _check(
            "live_geometry_commit_locked",
            results.get("regen_optimisation_live_geometry_commit_allowed") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    audit = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "complete": ready,
        "candidate_creation_input_audit_ready": results.get("regen_candidate_creation_input_audit_ready") is True,
        "candidate_creation_session_owner_ready": results.get("regen_candidate_creation_session_owner_ready") is True,
        "candidate_creation_report_owner_ready": results.get("regen_candidate_creation_report_owner_ready") is True,
        "candidate_creation_registration_owner_ready": results.get("regen_candidate_creation_registration_owner_ready") is True,
        "candidate_creation_state": "ARCHITECTURE_COMPLETE_CREATION_LOCKED" if ready else "BLOCKED",
        "next_phase": "12A_CANDIDATE_BLUEPRINT_GENERATION" if ready else None,
    }

    return {
        "regen_candidate_creation_completion_audit_complete": True,
        "phase_11g_5_regen_candidate_creation_completion_audit_complete": True,
        "regen_candidate_creation_completion_audit_ready": ready,
        "regen_candidate_creation_completion_audit_status": status,
        "regen_candidate_creation_completion_audit": audit,
        "regen_candidate_creation_completion_audit_checks": checks,
        "regen_candidate_creation_completion_audit_failed_checks": failed,
        "regen_candidate_creation_completion_audit_report": build_report(status, ready, audit, checks, failed),
        "phase_11g_complete": ready,
        "regen_candidate_creation_architecture_complete": ready,
        "phase_12a_candidate_blueprint_generation_allowed": ready,
        "regen_candidate_blueprint_generation_allowed": ready,
        "regen_candidate_creation_execution_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_blueprint_create_blueprints_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_report(status, ready, audit, checks, failed):
    lines = [
        "PHASE 11G.5 REGEN CANDIDATE CREATION COMPLETION AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"11G Complete: {ready}",
        f"Next Phase: {audit.get('next_phase')}",
        "",
        "COMPLETION SNAPSHOT",
        f"Input Audit Ready: {audit.get('candidate_creation_input_audit_ready')}",
        f"Session Owner Ready: {audit.get('candidate_creation_session_owner_ready')}",
        f"Report Owner Ready: {audit.get('candidate_creation_report_owner_ready')}",
        f"Registration Owner Ready: {audit.get('candidate_creation_registration_owner_ready')}",
        f"Candidate Creation State: {audit.get('candidate_creation_state')}",
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
        lines.append("Phase 11G candidate creation ownership architecture is complete.")
        lines.append("Phase 12A candidate blueprint generation may begin.")
        lines.append("Actual candidate creation, mutation, scoring, acceptance, solver execution, and geometry commit remain locked until explicitly added by later systems.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
