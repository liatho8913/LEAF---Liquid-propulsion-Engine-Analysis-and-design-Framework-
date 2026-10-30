from leaf_qt.status_presentation import status_severity
"""
PHASE 11D.4
Runtime Regen Optimisation Registration Owner

Owns runtime optimisation registration.

Does NOT:
- advance generations
- create mutations
- execute solver sweeps
- score candidates
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

OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_REGISTRATION_OWNER"
PHASE = "11D.4"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_REGISTRATION_OWNER_PHASE_11D4"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_REGISTRATION_OWNER_PHASE_11D4"


def attach_regen_runtime_optimisation_registration_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_runtime_optimisation_registration_owner(results))
    return results


def build_regen_runtime_optimisation_registration_owner(results):
    report_ready = (
        results.get("regen_runtime_optimisation_report_owner_ready") is True
        and results.get("phase_11d_4_runtime_registration_owner_allowed") is True
    )

    runtime_session = results.get("regen_runtime_optimisation_session", {})
    report_bundle = results.get("regen_runtime_optimisation_report_bundle", {})

    registry = _build_runtime_registry(runtime_session, report_bundle)

    checks = [
        _check(
            "runtime_report_owner_ready",
            report_ready,
            "11D.3 runtime report owner allows runtime registration ownership.",
            "11D.3 runtime report owner is not ready.",
        ),
        _check(
            "runtime_registry_created",
            bool(registry),
            "Runtime registry created.",
            "Runtime registry missing.",
        ),
        _check(
            "runtime_session_registered",
            bool(registry.get("runtime_session_registry", {}).get("registered_runtime_sessions")),
            "Runtime session registered.",
            "Runtime session not registered.",
        ),
        _check(
            "runtime_reports_registered",
            registry.get("runtime_report_registry", {}).get("runtime_report_count") == 5,
            "Runtime reports registered.",
            "Runtime reports not fully registered.",
        ),
        _check(
            "runtime_state_registered",
            bool(registry.get("runtime_state_registry")),
            "Runtime state registry created.",
            "Runtime state registry missing.",
        ),
        _check(
            "execution_locked",
            registry.get("runtime_execution_enabled") is False,
            "Runtime execution remains locked.",
            "Runtime execution must remain locked in 11D.4.",
        ),
        _check(
            "geometry_commit_locked",
            registry.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11D.4.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_optimisation_registration_owner_complete": True,
        "phase_11d_4_regen_runtime_optimisation_registration_owner_complete": True,
        "regen_runtime_optimisation_registration_owner_ready": ready,
        "regen_runtime_optimisation_registration_owner_status": status,
        "regen_runtime_optimisation_registry": registry,
        "regen_runtime_optimisation_registration_owner_checks": checks,
        "regen_runtime_optimisation_registration_owner_failed_checks": failed,
        "regen_runtime_optimisation_registration_owner_report": build_report(status, ready, registry, checks, failed),
        "phase_11d_5_runtime_completion_audit_allowed": ready,
        "regen_runtime_optimisation_completion_audit_allowed": ready,
        "regen_runtime_optimisation_registration_state_owned": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_runtime_registry(runtime_session, report_bundle):
    runtime_session_id = runtime_session.get(
        "runtime_session_id",
        "OPT_RUNTIME_SESSION_UNAVAILABLE",
    )

    runtime_report_keys = (
        "runtime_session_report",
        "runtime_generation_report",
        "runtime_candidate_report",
        "runtime_convergence_report",
        "runtime_audit_trail",
    )

    registered_reports = []
    for key in runtime_report_keys:
        report = report_bundle.get(key)
        if isinstance(report, dict):
            registered_reports.append(
                {
                    "report_key": key,
                    "report_id": report.get("report_id"),
                    "report_type": report.get("report_type"),
                    "runtime_session_id": report.get("runtime_session_id", runtime_session_id),
                    "registered": True,
                }
            )

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "runtime_registry_id": "RUNTIME_OPT_REGISTRY_0001",
        "runtime_registry_status": "ARCHITECTURE_READY_EXECUTION_LOCKED",
        "runtime_session_registry": {
            "registered_runtime_sessions": [
                {
                    "runtime_session_id": runtime_session_id,
                    "base_session_id": runtime_session.get("base_session_id"),
                    "registry_id": runtime_session.get("registry_id"),
                    "runtime_state": runtime_session.get("runtime_state"),
                    "execution_state": runtime_session.get("execution_state"),
                    "registered": True,
                }
            ],
            "runtime_session_count": 1,
        },
        "runtime_report_registry": {
            "registered_runtime_reports": registered_reports,
            "runtime_report_count": len(registered_reports),
        },
        "runtime_state_registry": {
            "current_generation_index": runtime_session.get("current_generation_index"),
            "current_population_id": runtime_session.get("current_population_id"),
            "current_candidate_id": runtime_session.get("current_candidate_id"),
            "best_candidate_id": runtime_session.get("best_candidate_id"),
            "best_score": runtime_session.get("best_score"),
            "termination_state": runtime_session.get("termination_state"),
            "convergence_state": runtime_session.get("convergence_state"),
            "registered": True,
        },
        "runtime_candidate_registry": {
            "registered_runtime_candidates": [],
            "runtime_candidate_count": 0,
            "candidate_registration_state": "LOCKED_UNTIL_RUNTIME_EXECUTION",
        },
        "runtime_generation_registry": {
            "registered_runtime_generations": [],
            "runtime_generation_count": 0,
            "generation_registration_state": "LOCKED_UNTIL_RUNTIME_EXECUTION",
        },
        "runtime_execution_enabled": False,
        "solver_execution_enabled": False,
        "generation_advance_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_auto_accept_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, registry, checks, failed):
    session_registry = registry.get("runtime_session_registry", {})
    report_registry = registry.get("runtime_report_registry", {})
    state_registry = registry.get("runtime_state_registry", {})
    candidate_registry = registry.get("runtime_candidate_registry", {})
    generation_registry = registry.get("runtime_generation_registry", {})

    lines = [
        "PHASE 11D.4 RUNTIME REGEN OPTIMISATION REGISTRATION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11D.5 Runtime Completion Audit: {ready}",
        "",
        "RUNTIME REGISTRY SNAPSHOT",
        f"Runtime Registry ID: {registry.get('runtime_registry_id')}",
        f"Runtime Registry Status: {registry.get('runtime_registry_status')}",
        f"Registered Runtime Sessions: {session_registry.get('runtime_session_count')}",
        f"Registered Runtime Reports: {report_registry.get('runtime_report_count')}",
        f"Runtime State Registered: {state_registry.get('registered')}",
        f"Registered Runtime Candidates: {candidate_registry.get('runtime_candidate_count')}",
        f"Registered Runtime Generations: {generation_registry.get('runtime_generation_count')}",
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
        lines.append("11D.4 runtime optimisation registration owner is complete.")
        lines.append("11D.5 runtime completion audit may begin.")
        lines.append("Runtime optimisation remains locked until later execution systems.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
