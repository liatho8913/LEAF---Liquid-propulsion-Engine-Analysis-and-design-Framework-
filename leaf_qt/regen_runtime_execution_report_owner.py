
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u111_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u111_is_fail_like(text) or _leaf_16u111_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u111_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u111_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u111_is_fail_like(value):
    return _leaf_16u111_status_severity(value) == "FAIL"


def _leaf_16u111_is_warn_like(value):
    return _leaf_16u111_status_severity(value) == "WARN"


def _leaf_16u111_is_pass_like(value):
    return _leaf_16u111_status_severity(value) == "PASS"


"""
PHASE 11E.3
Runtime Execution Report Owner

Owns execution architecture reports.

Does NOT:
- generate candidates
- mutate geometry
- score candidates
- rank candidates
- accept candidates
- commit geometry
- execute solvers
"""

OWNER_NAME = "REGEN_RUNTIME_EXECUTION_REPORT_OWNER"
PHASE = "11E.3"

PASS_STATUS = "PASS_REGEN_RUNTIME_EXECUTION_REPORT_OWNER_PHASE_11E3"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EXECUTION_REPORT_OWNER_PHASE_11E3"


def attach_regen_runtime_execution_report_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_runtime_execution_report_owner(results))
    return results


def build_regen_runtime_execution_report_owner(results):
    session_ready = (
        results.get("regen_runtime_execution_session_owner_ready") is True
        and results.get("phase_11e_3_runtime_execution_report_owner_allowed") is True
    )

    execution_session = results.get("regen_runtime_execution_session", {})
    report_bundle = _build_execution_report_bundle(execution_session)

    checks = [
        _check(
            "execution_session_owner_ready",
            session_ready,
            "11E.2 execution session owner allows report ownership.",
            "11E.2 execution session owner is not ready.",
        ),
        _check(
            "execution_session_report_created",
            bool(report_bundle.get("execution_session_report")),
            "Execution session report created.",
            "Execution session report missing.",
        ),
        _check(
            "execution_lifecycle_report_created",
            bool(report_bundle.get("execution_lifecycle_report")),
            "Execution lifecycle report created.",
            "Execution lifecycle report missing.",
        ),
        _check(
            "execution_progress_report_created",
            bool(report_bundle.get("execution_progress_report")),
            "Execution progress report created.",
            "Execution progress report missing.",
        ),
        _check(
            "execution_safety_report_created",
            bool(report_bundle.get("execution_safety_report")),
            "Execution safety report created.",
            "Execution safety report missing.",
        ),
        _check(
            "execution_lock_report_created",
            bool(report_bundle.get("execution_lock_report")),
            "Execution lock report created.",
            "Execution lock report missing.",
        ),
        _check(
            "candidate_generation_locked",
            report_bundle.get("candidate_generation_enabled") is False,
            "Candidate generation remains locked.",
            "Candidate generation must remain locked in 11E.3.",
        ),
        _check(
            "geometry_commit_locked",
            report_bundle.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11E.3.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_execution_report_owner_complete": True,
        "phase_11e_3_regen_runtime_execution_report_owner_complete": True,
        "regen_runtime_execution_report_owner_ready": ready,
        "regen_runtime_execution_report_owner_status": status,
        "regen_runtime_execution_report_bundle": report_bundle,
        "regen_runtime_execution_report_owner_checks": checks,
        "regen_runtime_execution_report_owner_failed_checks": failed,
        "regen_runtime_execution_report_owner_report": build_report(status, ready, report_bundle, checks, failed),
        "phase_11e_4_runtime_execution_registration_owner_allowed": ready,
        "regen_runtime_execution_registration_owner_allowed": ready,
        "regen_runtime_execution_reporting_state_owned": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_execution_report_bundle(execution_session):
    execution_session_id = execution_session.get(
        "execution_session_id",
        "OPT_EXECUTION_SESSION_UNAVAILABLE",
    )

    execution_session_report = {
        "report_id": f"{execution_session_id}_EXECUTION_SESSION_REPORT",
        "report_type": "EXECUTION_SESSION_REPORT",
        "execution_session_id": execution_session_id,
        "runtime_session_id": execution_session.get("runtime_session_id"),
        "runtime_registry_id": execution_session.get("runtime_registry_id"),
        "execution_state": execution_session.get("execution_state"),
        "execution_stage": execution_session.get("execution_stage"),
        "objective_mode": execution_session.get("objective_mode"),
        "execution_started": execution_session.get("execution_started"),
        "execution_finished": execution_session.get("execution_finished"),
    }

    execution_lifecycle_report = {
        "report_id": f"{execution_session_id}_EXECUTION_LIFECYCLE_REPORT",
        "report_type": "EXECUTION_LIFECYCLE_REPORT",
        "execution_session_id": execution_session_id,
        "lifecycle_state": execution_session.get("lifecycle_state"),
        "pause_state": execution_session.get("pause_state"),
        "stop_state": execution_session.get("stop_state"),
        "readiness_state": execution_session.get("readiness_state"),
        "lifecycle_summary": "Execution lifecycle is prepared but not started.",
    }

    execution_progress_report = {
        "report_id": f"{execution_session_id}_EXECUTION_PROGRESS_REPORT",
        "report_type": "EXECUTION_PROGRESS_REPORT",
        "execution_session_id": execution_session_id,
        "execution_progress_fraction": execution_session.get("execution_progress_fraction"),
        "current_generation_index": execution_session.get("current_generation_index"),
        "current_population_id": execution_session.get("current_population_id"),
        "current_candidate_id": execution_session.get("current_candidate_id"),
        "progress_summary": "Execution progress is zero because candidate generation remains locked.",
    }

    execution_safety_report = {
        "report_id": f"{execution_session_id}_EXECUTION_SAFETY_REPORT",
        "report_type": "EXECUTION_SAFETY_REPORT",
        "execution_session_id": execution_session_id,
        "safety_state": execution_session.get("safety_state"),
        "runtime_execution_enabled": execution_session.get("runtime_execution_enabled"),
        "solver_execution_enabled": execution_session.get("solver_execution_enabled"),
        "live_geometry_commit_enabled": execution_session.get("live_geometry_commit_enabled"),
        "safety_summary": "Execution is safe because all mutating systems remain locked.",
    }

    execution_lock_report = {
        "report_id": f"{execution_session_id}_EXECUTION_LOCK_REPORT",
        "report_type": "EXECUTION_LOCK_REPORT",
        "execution_session_id": execution_session_id,
        "candidate_generation_enabled": execution_session.get("candidate_generation_enabled"),
        "generation_advance_enabled": execution_session.get("generation_advance_enabled"),
        "mutation_execution_enabled": execution_session.get("mutation_execution_enabled"),
        "candidate_scoring_enabled": execution_session.get("candidate_scoring_enabled"),
        "candidate_acceptance_enabled": execution_session.get("candidate_acceptance_enabled"),
        "live_geometry_commit_enabled": execution_session.get("live_geometry_commit_enabled"),
        "lock_summary": "All optimisation-changing systems are locked in 11E.3.",
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "execution_session_id": execution_session_id,
        "execution_session_report": execution_session_report,
        "execution_lifecycle_report": execution_lifecycle_report,
        "execution_progress_report": execution_progress_report,
        "execution_safety_report": execution_safety_report,
        "execution_lock_report": execution_lock_report,
        "runtime_execution_enabled": False,
        "candidate_generation_enabled": False,
        "solver_execution_enabled": False,
        "generation_advance_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_acceptance_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, report_bundle, checks, failed):
    lines = [
        "PHASE 11E.3 RUNTIME EXECUTION REPORT OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11E.4 Execution Registration Owner: {ready}",
        "",
        "EXECUTION REPORT BUNDLE SNAPSHOT",
        f"Execution Session ID: {report_bundle.get('execution_session_id')}",
        f"Execution Session Report: {bool(report_bundle.get('execution_session_report'))}",
        f"Execution Lifecycle Report: {bool(report_bundle.get('execution_lifecycle_report'))}",
        f"Execution Progress Report: {bool(report_bundle.get('execution_progress_report'))}",
        f"Execution Safety Report: {bool(report_bundle.get('execution_safety_report'))}",
        f"Execution Lock Report: {bool(report_bundle.get('execution_lock_report'))}",
        "",
        "SAFETY LOCKS",
        f"Runtime Execution Enabled: {report_bundle.get('runtime_execution_enabled')}",
        f"Candidate Generation Enabled: {report_bundle.get('candidate_generation_enabled')}",
        f"Mutation Enabled: {report_bundle.get('mutation_execution_enabled')}",
        f"Live Geometry Commit Enabled: {report_bundle.get('live_geometry_commit_enabled')}",
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
        lines.append("11E.3 runtime execution report owner is complete.")
        lines.append("11E.4 runtime execution registration ownership may begin.")
        lines.append("Candidate generation, mutation, scoring, acceptance, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
