from leaf_qt.status_presentation import status_severity
"""
PHASE 11F.5
Candidate Generation Completion Audit

Final audit for candidate generation ownership architecture.

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

OWNER_NAME = "REGEN_CANDIDATE_GENERATION_COMPLETION_AUDIT"
PHASE = "11F.5"

PASS_STATUS = "PASS_REGEN_CANDIDATE_GENERATION_COMPLETION_AUDIT_PHASE_11F5"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_GENERATION_COMPLETION_AUDIT_PHASE_11F5"


def attach_regen_candidate_generation_completion_audit(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_generation_completion_audit(results))
    return results


def build_regen_candidate_generation_completion_audit(results):
    registry = results.get("regen_candidate_generation_registry", {})

    checks = [
        _check(
            "candidate_input_gate_complete",
            results.get("phase_11f_1_regen_candidate_generation_input_gate_complete") is True
            and results.get("regen_candidate_generation_input_gate_ready") is True,
            "11F.1 candidate generation input gate is complete and ready.",
            "11F.1 candidate generation input gate is incomplete or not ready.",
        ),
        _check(
            "candidate_session_owner_complete",
            results.get("phase_11f_2_regen_candidate_generation_session_owner_complete") is True
            and results.get("regen_candidate_generation_session_owner_ready") is True,
            "11F.2 candidate generation session owner is complete and ready.",
            "11F.2 candidate generation session owner is incomplete or not ready.",
        ),
        _check(
            "candidate_report_owner_complete",
            results.get("phase_11f_3_regen_candidate_generation_report_owner_complete") is True
            and results.get("regen_candidate_generation_report_owner_ready") is True,
            "11F.3 candidate generation report owner is complete and ready.",
            "11F.3 candidate generation report owner is incomplete or not ready.",
        ),
        _check(
            "candidate_registration_owner_complete",
            results.get("phase_11f_4_regen_candidate_generation_registration_owner_complete") is True
            and results.get("regen_candidate_generation_registration_owner_ready") is True,
            "11F.4 candidate generation registration owner is complete and ready.",
            "11F.4 candidate generation registration owner is incomplete or not ready.",
        ),
        _check(
            "candidate_session_exists",
            isinstance(results.get("regen_candidate_generation_session"), dict),
            "Candidate generation session object exists.",
            "Candidate generation session object missing.",
        ),
        _check(
            "candidate_report_bundle_exists",
            isinstance(results.get("regen_candidate_generation_report_bundle"), dict),
            "Candidate generation report bundle exists.",
            "Candidate generation report bundle missing.",
        ),
        _check(
            "candidate_registry_exists",
            isinstance(registry, dict) and bool(registry.get("candidate_generation_registry_id")),
            "Candidate generation registry exists.",
            "Candidate generation registry missing.",
        ),
        _check(
            "candidate_registry_has_session",
            registry.get("candidate_session_registry", {}).get("candidate_session_count") == 1,
            "Candidate registry contains one candidate generation session.",
            "Candidate registry does not contain the expected candidate generation session.",
        ),
        _check(
            "candidate_registry_has_reports",
            registry.get("candidate_report_registry", {}).get("candidate_report_count") == 5,
            "Candidate registry contains all five candidate reports.",
            "Candidate registry does not contain all candidate reports.",
        ),
        _check(
            "candidate_state_registered",
            registry.get("candidate_state_registry", {}).get("registered") is True,
            "Candidate state registry is registered.",
            "Candidate state registry is not registered.",
        ),
        _check(
            "candidate_capabilities_registered",
            registry.get("candidate_capability_registry", {}).get("registered") is True,
            "Candidate capability registry is registered.",
            "Candidate capability registry is not registered.",
        ),
        _check(
            "candidate_creation_locked",
            results.get("regen_candidate_generation_create_candidates_allowed") is False,
            "Candidate creation remains locked.",
            "Candidate creation must remain locked until later candidate-creation architecture.",
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
        "candidate_input_gate_ready": results.get("regen_candidate_generation_input_gate_ready") is True,
        "candidate_session_owner_ready": results.get("regen_candidate_generation_session_owner_ready") is True,
        "candidate_report_owner_ready": results.get("regen_candidate_generation_report_owner_ready") is True,
        "candidate_registration_owner_ready": results.get("regen_candidate_generation_registration_owner_ready") is True,
        "candidate_generation_state": "ARCHITECTURE_COMPLETE_CREATION_LOCKED" if ready else "BLOCKED",
        "next_phase": "11G_CANDIDATE_CREATION_ARCHITECTURE" if ready else None,
    }

    return {
        "regen_candidate_generation_completion_audit_complete": True,
        "phase_11f_5_regen_candidate_generation_completion_audit_complete": True,
        "regen_candidate_generation_completion_audit_ready": ready,
        "regen_candidate_generation_completion_audit_status": status,
        "regen_candidate_generation_completion_audit": audit,
        "regen_candidate_generation_completion_audit_checks": checks,
        "regen_candidate_generation_completion_audit_failed_checks": failed,
        "regen_candidate_generation_completion_audit_report": build_report(status, ready, audit, checks, failed),
        "phase_11f_complete": ready,
        "regen_candidate_generation_architecture_complete": ready,
        "phase_11g_candidate_creation_architecture_allowed": ready,
        "regen_candidate_creation_architecture_allowed": ready,
        "regen_candidate_generation_execution_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_report(status, ready, audit, checks, failed):
    lines = [
        "PHASE 11F.5 REGEN CANDIDATE GENERATION COMPLETION AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"11F Complete: {ready}",
        f"Next Phase: {audit.get('next_phase')}",
        "",
        "COMPLETION SNAPSHOT",
        f"Candidate Input Gate Ready: {audit.get('candidate_input_gate_ready')}",
        f"Candidate Session Owner Ready: {audit.get('candidate_session_owner_ready')}",
        f"Candidate Report Owner Ready: {audit.get('candidate_report_owner_ready')}",
        f"Candidate Registration Owner Ready: {audit.get('candidate_registration_owner_ready')}",
        f"Candidate Generation State: {audit.get('candidate_generation_state')}",
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
        lines.append("Phase 11F candidate generation ownership architecture is complete.")
        lines.append("Phase 11G candidate creation architecture may begin.")
        lines.append("Actual candidate creation, mutation, scoring, acceptance, solver execution, and geometry commit remain locked until explicitly added by later systems.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
