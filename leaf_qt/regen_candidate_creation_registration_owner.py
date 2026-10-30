from leaf_qt.status_presentation import status_severity
"""
PHASE 11G.4
Candidate Creation Registration Owner

Registers candidate creation architecture state and reports.

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

OWNER_NAME = "REGEN_CANDIDATE_CREATION_REGISTRATION_OWNER"
PHASE = "11G.4"

PASS_STATUS = "PASS_REGEN_CANDIDATE_CREATION_REGISTRATION_OWNER_PHASE_11G4"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_CREATION_REGISTRATION_OWNER_PHASE_11G4"


def attach_regen_candidate_creation_registration_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_creation_registration_owner(results))
    return results


def build_regen_candidate_creation_registration_owner(results):
    report_ready = (
        results.get("regen_candidate_creation_report_owner_ready") is True
        and results.get("phase_11g_4_candidate_creation_registration_owner_allowed") is True
    )

    session = results.get("regen_candidate_creation_session", {})
    bundle = results.get("regen_candidate_creation_report_bundle", {})

    registry = _build_creation_registry(session, bundle)

    checks = [
        _check("report_owner_ready", report_ready, "11G.3 report owner allows registration.", "11G.3 report owner is not ready."),
        _check("registry_created", bool(registry), "Candidate creation registry created.", "Candidate creation registry missing."),
        _check("session_registered", registry.get("creation_session_registry", {}).get("creation_session_count") == 1, "Creation session registered.", "Creation session not registered."),
        _check("reports_registered", registry.get("creation_report_registry", {}).get("creation_report_count") == 5, "Creation reports registered.", "Creation reports not fully registered."),
        _check("state_registered", registry.get("creation_state_registry", {}).get("registered") is True, "Creation state registered.", "Creation state not registered."),
        _check("capabilities_registered", registry.get("creation_capability_registry", {}).get("registered") is True, "Creation capabilities registered.", "Creation capabilities not registered."),
        _check("creation_locked", registry.get("candidate_creation_enabled") is False, "Candidate creation remains locked.", "Candidate creation must remain locked in 11G.4."),
        _check("geometry_commit_locked", registry.get("live_geometry_commit_enabled") is False, "Geometry commit remains locked.", "Geometry commit must remain locked in 11G.4."),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_candidate_creation_registration_owner_complete": True,
        "phase_11g_4_regen_candidate_creation_registration_owner_complete": True,
        "regen_candidate_creation_registration_owner_ready": ready,
        "regen_candidate_creation_registration_owner_status": status,
        "regen_candidate_creation_registry": registry,
        "regen_candidate_creation_registration_owner_checks": checks,
        "regen_candidate_creation_registration_owner_failed_checks": failed,
        "regen_candidate_creation_registration_owner_report": build_report(status, ready, registry, checks, failed),
        "phase_11g_5_candidate_creation_completion_audit_allowed": ready,
        "regen_candidate_creation_completion_audit_allowed": ready,
        "regen_candidate_creation_registration_state_owned": ready,
        "regen_candidate_creation_execution_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_creation_registry(session, bundle):
    session_id = session.get("candidate_creation_session_id", "CANDIDATE_CREATION_SESSION_UNAVAILABLE")

    report_keys = (
        "candidate_creation_session_report",
        "candidate_creation_lifecycle_report",
        "candidate_creation_constraint_report",
        "candidate_creation_package_report",
        "candidate_creation_safety_report",
    )

    reports = []
    for key in report_keys:
        report = bundle.get(key)
        if isinstance(report, dict):
            reports.append({
                "report_key": key,
                "report_id": report.get("report_id"),
                "report_type": report.get("report_type"),
                "candidate_creation_session_id": report.get("candidate_creation_session_id", session_id),
                "registered": True,
            })

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "candidate_creation_registry_id": "CANDIDATE_CREATION_REGISTRY_0001",
        "candidate_creation_registry_status": "ARCHITECTURE_READY_CREATION_LOCKED",
        "creation_session_registry": {
            "registered_creation_sessions": [{
                "candidate_creation_session_id": session_id,
                "candidate_generation_session_id": session.get("candidate_generation_session_id"),
                "candidate_creation_state": session.get("candidate_creation_state"),
                "candidate_creation_lifecycle_state": session.get("candidate_creation_lifecycle_state"),
                "candidate_creation_pool_state": session.get("candidate_creation_pool_state"),
                "registered": True,
            }],
            "creation_session_count": 1,
        },
        "creation_report_registry": {
            "registered_creation_reports": reports,
            "creation_report_count": len(reports),
        },
        "creation_state_registry": {
            "created_candidate_count": session.get("created_candidate_count"),
            "accepted_candidate_count": session.get("accepted_candidate_count"),
            "rejected_candidate_count": session.get("rejected_candidate_count"),
            "created_candidate_ids": list(session.get("created_candidate_ids", [])),
            "accepted_candidate_ids": list(session.get("accepted_candidate_ids", [])),
            "rejected_candidate_ids": list(session.get("rejected_candidate_ids", [])),
            "current_creation_candidate_id": session.get("current_creation_candidate_id"),
            "registered": True,
        },
        "creation_capability_registry": {
            "candidate_creation_enabled": False,
            "candidate_creation_execution_enabled": False,
            "candidate_blueprint_creation_enabled": False,
            "mutation_execution_enabled": False,
            "candidate_scoring_enabled": False,
            "candidate_ranking_enabled": False,
            "candidate_acceptance_enabled": False,
            "solver_execution_enabled": False,
            "live_geometry_commit_enabled": False,
            "registered": True,
        },
        "candidate_creation_enabled": False,
        "candidate_creation_execution_enabled": False,
        "candidate_blueprint_creation_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_ranking_enabled": False,
        "candidate_acceptance_enabled": False,
        "solver_execution_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, registry, checks, failed):
    lines = [
        "PHASE 11G.4 REGEN CANDIDATE CREATION REGISTRATION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11G.5 Candidate Creation Completion Audit: {ready}",
        "",
        "REGISTRY SNAPSHOT",
        f"Registry ID: {registry.get('candidate_creation_registry_id')}",
        f"Registry Status: {registry.get('candidate_creation_registry_status')}",
        f"Registered Sessions: {registry.get('creation_session_registry', {}).get('creation_session_count')}",
        f"Registered Reports: {registry.get('creation_report_registry', {}).get('creation_report_count')}",
        f"State Registered: {registry.get('creation_state_registry', {}).get('registered')}",
        f"Capabilities Registered: {registry.get('creation_capability_registry', {}).get('registered')}",
        "",
        "SAFETY LOCKS",
        f"Candidate Creation Enabled: {registry.get('candidate_creation_enabled')}",
        f"Blueprint Creation Enabled: {registry.get('candidate_blueprint_creation_enabled')}",
        f"Mutation Enabled: {registry.get('mutation_execution_enabled')}",
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
        lines.append("11G.4 candidate creation registration owner is complete.")
        lines.append("11G.5 candidate creation completion audit may begin.")
        lines.append("Actual candidate creation, mutation, scoring, acceptance, solver execution, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {"name": name, "passed": bool(passed), "pass_message": pass_message, "fail_message": fail_message}
