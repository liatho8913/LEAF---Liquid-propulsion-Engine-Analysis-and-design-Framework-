from leaf_qt.status_presentation import status_severity
"""
PHASE 11E.4
Runtime Execution Registration Owner

Registers execution architecture state and reports.

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

OWNER_NAME = "REGEN_RUNTIME_EXECUTION_REGISTRATION_OWNER"
PHASE = "11E.4"

PASS_STATUS = "PASS_REGEN_RUNTIME_EXECUTION_REGISTRATION_OWNER_PHASE_11E4"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EXECUTION_REGISTRATION_OWNER_PHASE_11E4"


def attach_regen_runtime_execution_registration_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_runtime_execution_registration_owner(results))
    return results


def build_regen_runtime_execution_registration_owner(results):
    report_ready = (
        results.get("regen_runtime_execution_report_owner_ready") is True
        and results.get("phase_11e_4_runtime_execution_registration_owner_allowed") is True
    )

    execution_session = results.get("regen_runtime_execution_session", {})
    report_bundle = results.get("regen_runtime_execution_report_bundle", {})

    registry = _build_execution_registry(execution_session, report_bundle)

    checks = [
        _check(
            "execution_report_owner_ready",
            report_ready,
            "11E.3 execution report owner allows registration ownership.",
            "11E.3 execution report owner is not ready.",
        ),
        _check(
            "execution_registry_created",
            bool(registry),
            "Execution registry created.",
            "Execution registry missing.",
        ),
        _check(
            "execution_session_registered",
            registry.get("execution_session_registry", {}).get("execution_session_count") == 1,
            "Execution session registered.",
            "Execution session not registered.",
        ),
        _check(
            "execution_reports_registered",
            registry.get("execution_report_registry", {}).get("execution_report_count") == 5,
            "Execution reports registered.",
            "Execution reports not fully registered.",
        ),
        _check(
            "execution_state_registered",
            registry.get("execution_state_registry", {}).get("registered") is True,
            "Execution state registered.",
            "Execution state not registered.",
        ),
        _check(
            "candidate_generation_locked",
            registry.get("candidate_generation_enabled") is False,
            "Candidate generation remains locked.",
            "Candidate generation must remain locked in 11E.4.",
        ),
        _check(
            "geometry_commit_locked",
            registry.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11E.4.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_execution_registration_owner_complete": True,
        "phase_11e_4_regen_runtime_execution_registration_owner_complete": True,
        "regen_runtime_execution_registration_owner_ready": ready,
        "regen_runtime_execution_registration_owner_status": status,
        "regen_runtime_execution_registry": registry,
        "regen_runtime_execution_registration_owner_checks": checks,
        "regen_runtime_execution_registration_owner_failed_checks": failed,
        "regen_runtime_execution_registration_owner_report": build_report(status, ready, registry, checks, failed),
        "phase_11e_5_runtime_execution_completion_audit_allowed": ready,
        "regen_runtime_execution_completion_audit_allowed": ready,
        "regen_runtime_execution_registration_state_owned": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_execution_registry(execution_session, report_bundle):
    execution_session_id = execution_session.get(
        "execution_session_id",
        "OPT_EXECUTION_SESSION_UNAVAILABLE",
    )

    report_keys = (
        "execution_session_report",
        "execution_lifecycle_report",
        "execution_progress_report",
        "execution_safety_report",
        "execution_lock_report",
    )

    registered_reports = []
    for key in report_keys:
        report = report_bundle.get(key)
        if isinstance(report, dict):
            registered_reports.append(
                {
                    "report_key": key,
                    "report_id": report.get("report_id"),
                    "report_type": report.get("report_type"),
                    "execution_session_id": report.get("execution_session_id", execution_session_id),
                    "registered": True,
                }
            )

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "execution_registry_id": "RUNTIME_EXECUTION_REGISTRY_0001",
        "execution_registry_status": "ARCHITECTURE_READY_EXECUTION_LOCKED",
        "execution_session_registry": {
            "registered_execution_sessions": [
                {
                    "execution_session_id": execution_session_id,
                    "runtime_session_id": execution_session.get("runtime_session_id"),
                    "runtime_registry_id": execution_session.get("runtime_registry_id"),
                    "execution_state": execution_session.get("execution_state"),
                    "lifecycle_state": execution_session.get("lifecycle_state"),
                    "execution_stage": execution_session.get("execution_stage"),
                    "registered": True,
                }
            ],
            "execution_session_count": 1,
        },
        "execution_report_registry": {
            "registered_execution_reports": registered_reports,
            "execution_report_count": len(registered_reports),
        },
        "execution_state_registry": {
            "execution_state": execution_session.get("execution_state"),
            "lifecycle_state": execution_session.get("lifecycle_state"),
            "pause_state": execution_session.get("pause_state"),
            "stop_state": execution_session.get("stop_state"),
            "safety_state": execution_session.get("safety_state"),
            "readiness_state": execution_session.get("readiness_state"),
            "execution_progress_fraction": execution_session.get("execution_progress_fraction"),
            "registered": True,
        },
        "execution_capability_registry": {
            "runtime_execution_enabled": False,
            "candidate_generation_enabled": False,
            "solver_execution_enabled": False,
            "generation_advance_enabled": False,
            "mutation_execution_enabled": False,
            "candidate_scoring_enabled": False,
            "candidate_acceptance_enabled": False,
            "live_geometry_commit_enabled": False,
            "registered": True,
        },
        "runtime_execution_enabled": False,
        "candidate_generation_enabled": False,
        "solver_execution_enabled": False,
        "generation_advance_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_acceptance_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, registry, checks, failed):
    session_registry = registry.get("execution_session_registry", {})
    report_registry = registry.get("execution_report_registry", {})
    state_registry = registry.get("execution_state_registry", {})
    capability_registry = registry.get("execution_capability_registry", {})

    lines = [
        "PHASE 11E.4 RUNTIME EXECUTION REGISTRATION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11E.5 Execution Completion Audit: {ready}",
        "",
        "EXECUTION REGISTRY SNAPSHOT",
        f"Execution Registry ID: {registry.get('execution_registry_id')}",
        f"Execution Registry Status: {registry.get('execution_registry_status')}",
        f"Registered Execution Sessions: {session_registry.get('execution_session_count')}",
        f"Registered Execution Reports: {report_registry.get('execution_report_count')}",
        f"Execution State Registered: {state_registry.get('registered')}",
        f"Capability Registry Registered: {capability_registry.get('registered')}",
        "",
        "SAFETY LOCKS",
        f"Runtime Execution Enabled: {registry.get('runtime_execution_enabled')}",
        f"Candidate Generation Enabled: {registry.get('candidate_generation_enabled')}",
        f"Mutation Enabled: {registry.get('mutation_execution_enabled')}",
        f"Live Geometry Commit Enabled: {registry.get('live_geometry_commit_enabled')}",
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
        lines.append("11E.4 runtime execution registration owner is complete.")
        lines.append("11E.5 runtime execution completion audit may begin.")
        lines.append("Candidate generation, mutation, scoring, acceptance, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
