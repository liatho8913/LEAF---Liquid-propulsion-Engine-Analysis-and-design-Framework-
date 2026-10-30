from leaf_qt.status_presentation import status_severity
"""
PHASE 11C.4
Regen Optimisation Registration Owner

Creates architecture-only optimisation registry ownership.

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

OWNER_NAME = "REGEN_OPTIMISATION_REGISTRATION_OWNER"
PHASE = "11C.4"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REGISTRATION_OWNER_PHASE_11C4"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REGISTRATION_OWNER_PHASE_11C4"


def attach_regen_optimisation_registration_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_optimisation_registration_owner(results))
    return results


def build_regen_optimisation_registration_owner(results):
    report_ready = (
        results.get("regen_optimisation_report_owner_ready") is True
        and results.get("phase_11c_4_optimisation_registration_owner_allowed") is True
    )

    session = results.get("regen_optimisation_session", {})
    report_bundle = results.get("regen_optimisation_report_bundle", {})

    registry = _build_registry(session, report_bundle)

    checks = [
        _check(
            "report_owner_ready",
            report_ready,
            "11C.3 report owner allows registration ownership.",
            "11C.3 report owner is not ready.",
        ),
        _check(
            "registry_created",
            bool(registry),
            "Optimisation registry created.",
            "Optimisation registry missing.",
        ),
        _check(
            "session_registered",
            bool(registry.get("session_registry", {}).get("registered_sessions")),
            "Session registered.",
            "No session registered.",
        ),
        _check(
            "report_bundle_registered",
            bool(registry.get("report_registry", {}).get("registered_reports")),
            "Report bundle registered.",
            "Report bundle not registered.",
        ),
        _check(
            "runtime_locked",
            registry.get("runtime_execution_enabled") is False,
            "Runtime execution remains locked.",
            "Runtime execution must remain locked in 11C.4.",
        ),
        _check(
            "live_commit_locked",
            registry.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11C.4.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_registration_owner_complete": True,
        "phase_11c_4_regen_optimisation_registration_owner_complete": True,
        "regen_optimisation_registration_owner_ready": ready,
        "regen_optimisation_registration_owner_status": status,
        "regen_optimisation_registry": registry,
        "regen_optimisation_registration_owner_checks": checks,
        "regen_optimisation_registration_owner_failed_checks": failed,
        "regen_optimisation_registration_owner_report": build_report(status, ready, registry, checks, failed),
        "phase_11c_5_optimisation_completion_audit_allowed": ready,
        "regen_optimisation_completion_audit_architecture_allowed": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_registry(session, report_bundle):
    session_id = session.get("session_id", "OPT_SESSION_UNAVAILABLE")

    registered_reports = []
    for key in (
        "session_report",
        "generation_report",
        "candidate_report",
        "convergence_report",
    ):
        report = report_bundle.get(key)
        if isinstance(report, dict):
            registered_reports.append(
                {
                    "report_key": key,
                    "report_id": report.get("report_id"),
                    "report_type": report.get("report_type"),
                    "session_id": report.get("session_id", session_id),
                    "registered": True,
                }
            )

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "registry_id": "OPT_REGISTRY_0001",
        "registry_status": "ARCHITECTURE_READY_RUNTIME_LOCKED",
        "session_registry": {
            "registered_sessions": [
                {
                    "session_id": session_id,
                    "session_status": session.get("session_status"),
                    "objective_mode": session.get("objective_mode"),
                    "generation_count": session.get("generation_count"),
                    "registered": True,
                }
            ],
            "session_count": 1,
        },
        "report_registry": {
            "registered_reports": registered_reports,
            "report_count": len(registered_reports),
        },
        "candidate_registry": {
            "registered_candidates": [],
            "candidate_count": 0,
            "candidate_registration_state": "LOCKED_UNTIL_RUNTIME_EXECUTION",
        },
        "generation_registry": {
            "registered_generations": [],
            "generation_count": 0,
            "generation_registration_state": "LOCKED_UNTIL_RUNTIME_EXECUTION",
        },
        "runtime_execution_enabled": False,
        "solver_execution_enabled": False,
        "generation_advance_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_auto_accept_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, registry, checks, failed):
    session_registry = registry.get("session_registry", {})
    report_registry = registry.get("report_registry", {})
    candidate_registry = registry.get("candidate_registry", {})

    lines = [
        "PHASE 11C.4 REGEN OPTIMISATION REGISTRATION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11C.5 Completion Audit: {ready}",
        "",
        "REGISTRY SNAPSHOT",
        f"Registry ID: {registry.get('registry_id')}",
        f"Registry Status: {registry.get('registry_status')}",
        f"Registered Sessions: {session_registry.get('session_count')}",
        f"Registered Reports: {report_registry.get('report_count')}",
        f"Registered Candidates: {candidate_registry.get('candidate_count')}",
        "",
        "SAFETY LOCKS",
        f"Runtime Execution Enabled: {registry.get('runtime_execution_enabled')}",
        f"Solver Execution Enabled: {registry.get('solver_execution_enabled')}",
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
        lines.append("11C.4 optimisation registration owner is complete.")
        lines.append("11C.5 optimisation completion audit may begin.")
        lines.append("Runtime optimisation remains locked until 11D.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
