from leaf_qt.status_presentation import status_severity
"""
PHASE 11C.5
Regen Optimisation Completion Audit

Final completion audit for Phase 11C architecture.

Does NOT:
- run optimisation
- advance generations
- execute mutation
- execute solver sweeps
- accept candidates
- commit geometry
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

OWNER_NAME = "REGEN_OPTIMISATION_COMPLETION_AUDIT"
PHASE = "11C.5"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_COMPLETION_AUDIT_PHASE_11C5"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_COMPLETION_AUDIT_PHASE_11C5"


def attach_regen_optimisation_completion_audit(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_optimisation_completion_audit(results))
    return results


def build_regen_optimisation_completion_audit(results):
    checks = [
        _check(
            "input_audit_complete",
            results.get("phase_11c_1_regen_autonomous_optimisation_input_audit_complete") is True
            and results.get("regen_autonomous_optimisation_input_audit_ready") is True,
            "11C.1 input audit is complete and ready.",
            "11C.1 input audit is incomplete or not ready.",
        ),
        _check(
            "session_owner_complete",
            results.get("phase_11c_2_regen_optimisation_session_owner_complete") is True
            and results.get("regen_optimisation_session_owner_ready") is True,
            "11C.2 session owner is complete and ready.",
            "11C.2 session owner is incomplete or not ready.",
        ),
        _check(
            "report_owner_complete",
            results.get("phase_11c_3_regen_optimisation_report_owner_complete") is True
            and results.get("regen_optimisation_report_owner_ready") is True,
            "11C.3 report owner is complete and ready.",
            "11C.3 report owner is incomplete or not ready.",
        ),
        _check(
            "registration_owner_complete",
            results.get("phase_11c_4_regen_optimisation_registration_owner_complete") is True
            and results.get("regen_optimisation_registration_owner_ready") is True,
            "11C.4 registration owner is complete and ready.",
            "11C.4 registration owner is incomplete or not ready.",
        ),
        _check(
            "session_object_exists",
            isinstance(results.get("regen_optimisation_session"), dict),
            "Optimisation session object exists.",
            "Optimisation session object missing.",
        ),
        _check(
            "report_bundle_exists",
            isinstance(results.get("regen_optimisation_report_bundle"), dict),
            "Optimisation report bundle exists.",
            "Optimisation report bundle missing.",
        ),
        _check(
            "registry_exists",
            isinstance(results.get("regen_optimisation_registry"), dict),
            "Optimisation registry exists.",
            "Optimisation registry missing.",
        ),
        _check(
            "runtime_locked",
            results.get("regen_optimisation_runtime_execution_allowed") is False,
            "Runtime execution remains locked.",
            "Runtime execution must remain locked until 11D.",
        ),
        _check(
            "live_commit_locked",
            results.get("regen_optimisation_live_geometry_commit_allowed") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked until 11D.",
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
        "input_audit_ready": results.get("regen_autonomous_optimisation_input_audit_ready") is True,
        "session_owner_ready": results.get("regen_optimisation_session_owner_ready") is True,
        "report_owner_ready": results.get("regen_optimisation_report_owner_ready") is True,
        "registration_owner_ready": results.get("regen_optimisation_registration_owner_ready") is True,
        "runtime_state": "LOCKED_UNTIL_11D",
        "next_phase": "11D_RUNTIME_OPTIMISATION_ARCHITECTURE" if ready else None,
    }

    return {
        "regen_optimisation_completion_audit_complete": True,
        "phase_11c_5_regen_optimisation_completion_audit_complete": True,
        "regen_optimisation_completion_audit_ready": ready,
        "regen_optimisation_completion_audit_status": status,
        "regen_optimisation_completion_audit": audit,
        "regen_optimisation_completion_audit_checks": checks,
        "regen_optimisation_completion_audit_failed_checks": failed,
        "regen_optimisation_completion_audit_report": build_report(status, ready, audit, checks, failed),
        "phase_11c_complete": ready,
        "regen_optimisation_architecture_complete": ready,
        "phase_11d_runtime_optimisation_architecture_allowed": ready,
        "regen_runtime_optimisation_architecture_allowed": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_report(status, ready, audit, checks, failed):
    lines = [
        "PHASE 11C.5 REGEN OPTIMISATION COMPLETION AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"11C Complete: {ready}",
        f"Next Phase: {audit.get('next_phase')}",
        "",
        "COMPLETION SNAPSHOT",
        f"Input Audit Ready: {audit.get('input_audit_ready')}",
        f"Session Owner Ready: {audit.get('session_owner_ready')}",
        f"Report Owner Ready: {audit.get('report_owner_ready')}",
        f"Registration Owner Ready: {audit.get('registration_owner_ready')}",
        f"Runtime State: {audit.get('runtime_state')}",
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
        lines.append("Phase 11C optimisation ownership architecture is complete.")
        lines.append("Phase 11D runtime optimisation architecture may begin.")
        lines.append("Runtime optimisation remains locked until explicitly enabled by 11D systems.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
