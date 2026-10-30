from leaf_qt.status_presentation import status_severity
"""
PHASE 11E.5
Runtime Execution Completion Audit

Final audit for runtime execution architecture ownership.

Does NOT:
- generate candidates
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

OWNER_NAME = "REGEN_RUNTIME_EXECUTION_COMPLETION_AUDIT"
PHASE = "11E.5"

PASS_STATUS = "PASS_REGEN_RUNTIME_EXECUTION_COMPLETION_AUDIT_PHASE_11E5"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EXECUTION_COMPLETION_AUDIT_PHASE_11E5"


def attach_regen_runtime_execution_completion_audit(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_runtime_execution_completion_audit(results))
    return results


def build_regen_runtime_execution_completion_audit(results):
    registry = results.get("regen_runtime_execution_registry", {})

    checks = [
        _check(
            "execution_input_gate_complete",
            results.get("phase_11e_1_regen_runtime_execution_input_gate_complete") is True
            and results.get("regen_runtime_execution_input_gate_ready") is True,
            "11E.1 execution input gate is complete and ready.",
            "11E.1 execution input gate is incomplete or not ready.",
        ),
        _check(
            "execution_session_owner_complete",
            results.get("phase_11e_2_regen_runtime_execution_session_owner_complete") is True
            and results.get("regen_runtime_execution_session_owner_ready") is True,
            "11E.2 execution session owner is complete and ready.",
            "11E.2 execution session owner is incomplete or not ready.",
        ),
        _check(
            "execution_report_owner_complete",
            results.get("phase_11e_3_regen_runtime_execution_report_owner_complete") is True
            and results.get("regen_runtime_execution_report_owner_ready") is True,
            "11E.3 execution report owner is complete and ready.",
            "11E.3 execution report owner is incomplete or not ready.",
        ),
        _check(
            "execution_registration_owner_complete",
            results.get("phase_11e_4_regen_runtime_execution_registration_owner_complete") is True
            and results.get("regen_runtime_execution_registration_owner_ready") is True,
            "11E.4 execution registration owner is complete and ready.",
            "11E.4 execution registration owner is incomplete or not ready.",
        ),
        _check(
            "execution_session_exists",
            isinstance(results.get("regen_runtime_execution_session"), dict),
            "Execution session object exists.",
            "Execution session object missing.",
        ),
        _check(
            "execution_report_bundle_exists",
            isinstance(results.get("regen_runtime_execution_report_bundle"), dict),
            "Execution report bundle exists.",
            "Execution report bundle missing.",
        ),
        _check(
            "execution_registry_exists",
            isinstance(registry, dict) and bool(registry.get("execution_registry_id")),
            "Execution registry exists.",
            "Execution registry missing.",
        ),
        _check(
            "execution_registry_has_session",
            registry.get("execution_session_registry", {}).get("execution_session_count") == 1,
            "Execution registry contains one execution session.",
            "Execution registry does not contain the expected execution session.",
        ),
        _check(
            "execution_registry_has_reports",
            registry.get("execution_report_registry", {}).get("execution_report_count") == 5,
            "Execution registry contains all five execution reports.",
            "Execution registry does not contain all execution reports.",
        ),
        _check(
            "execution_state_registered",
            registry.get("execution_state_registry", {}).get("registered") is True,
            "Execution state registry is registered.",
            "Execution state registry is not registered.",
        ),
        _check(
            "execution_capabilities_registered",
            registry.get("execution_capability_registry", {}).get("registered") is True,
            "Execution capability registry is registered.",
            "Execution capability registry is not registered.",
        ),
        _check(
            "runtime_execution_locked",
            results.get("regen_optimisation_runtime_execution_allowed") is False,
            "Runtime execution remains locked.",
            "Runtime execution must remain locked until candidate-generation architecture begins.",
        ),
        _check(
            "generation_mutation_locked",
            results.get("regen_optimisation_generation_advance_allowed") is False
            and results.get("regen_optimisation_mutation_execution_allowed") is False,
            "Generation advancement and mutation remain locked.",
            "Generation advancement and mutation must remain locked.",
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
        "execution_input_gate_ready": results.get("regen_runtime_execution_input_gate_ready") is True,
        "execution_session_owner_ready": results.get("regen_runtime_execution_session_owner_ready") is True,
        "execution_report_owner_ready": results.get("regen_runtime_execution_report_owner_ready") is True,
        "execution_registration_owner_ready": results.get("regen_runtime_execution_registration_owner_ready") is True,
        "execution_state": "ARCHITECTURE_COMPLETE_EXECUTION_LOCKED" if ready else "BLOCKED",
        "next_phase": "11F_CANDIDATE_GENERATION_ARCHITECTURE" if ready else None,
    }

    return {
        "regen_runtime_execution_completion_audit_complete": True,
        "phase_11e_5_regen_runtime_execution_completion_audit_complete": True,
        "regen_runtime_execution_completion_audit_ready": ready,
        "regen_runtime_execution_completion_audit_status": status,
        "regen_runtime_execution_completion_audit": audit,
        "regen_runtime_execution_completion_audit_checks": checks,
        "regen_runtime_execution_completion_audit_failed_checks": failed,
        "regen_runtime_execution_completion_audit_report": build_report(status, ready, audit, checks, failed),
        "phase_11e_complete": ready,
        "regen_runtime_execution_architecture_complete": ready,
        "phase_11f_candidate_generation_architecture_allowed": ready,
        "regen_candidate_generation_architecture_allowed": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_report(status, ready, audit, checks, failed):
    lines = [
        "PHASE 11E.5 RUNTIME EXECUTION COMPLETION AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"11E Complete: {ready}",
        f"Next Phase: {audit.get('next_phase')}",
        "",
        "COMPLETION SNAPSHOT",
        f"Execution Input Gate Ready: {audit.get('execution_input_gate_ready')}",
        f"Execution Session Owner Ready: {audit.get('execution_session_owner_ready')}",
        f"Execution Report Owner Ready: {audit.get('execution_report_owner_ready')}",
        f"Execution Registration Owner Ready: {audit.get('execution_registration_owner_ready')}",
        f"Execution State: {audit.get('execution_state')}",
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
        lines.append("Phase 11E runtime execution architecture is complete.")
        lines.append("Phase 11F candidate generation architecture may begin.")
        lines.append("Candidate generation, mutation, scoring, acceptance, and geometry commit remain locked until explicitly added by later systems.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
