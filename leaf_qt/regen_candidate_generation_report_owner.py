
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u101_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u101_is_fail_like(text) or _leaf_16u101_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u101_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u101_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u101_is_fail_like(value):
    return _leaf_16u101_status_severity(value) == "FAIL"


def _leaf_16u101_is_warn_like(value):
    return _leaf_16u101_status_severity(value) == "WARN"


def _leaf_16u101_is_pass_like(value):
    return _leaf_16u101_status_severity(value) == "PASS"


"""
PHASE 11F.3
Candidate Generation Report Owner

Owns candidate generation reports and visibility.

Does NOT:
- create candidates
- mutate geometry
- score candidates
- rank candidates
- accept candidates
- commit geometry
- execute solvers
"""

OWNER_NAME = "REGEN_CANDIDATE_GENERATION_REPORT_OWNER"
PHASE = "11F.3"

PASS_STATUS = "PASS_REGEN_CANDIDATE_GENERATION_REPORT_OWNER_PHASE_11F3"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_GENERATION_REPORT_OWNER_PHASE_11F3"


def attach_regen_candidate_generation_report_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_generation_report_owner(results))
    return results


def build_regen_candidate_generation_report_owner(results):
    session_ready = (
        results.get("regen_candidate_generation_session_owner_ready") is True
        and results.get("phase_11f_3_candidate_generation_report_owner_allowed") is True
    )

    candidate_session = results.get("regen_candidate_generation_session", {})
    report_bundle = _build_candidate_generation_report_bundle(candidate_session)

    checks = [
        _check(
            "candidate_generation_session_owner_ready",
            session_ready,
            "11F.2 candidate generation session owner allows report ownership.",
            "11F.2 candidate generation session owner is not ready.",
        ),
        _check(
            "candidate_session_report_created",
            bool(report_bundle.get("candidate_session_report")),
            "Candidate session report created.",
            "Candidate session report missing.",
        ),
        _check(
            "candidate_pool_report_created",
            bool(report_bundle.get("candidate_pool_report")),
            "Candidate pool report created.",
            "Candidate pool report missing.",
        ),
        _check(
            "candidate_population_report_created",
            bool(report_bundle.get("candidate_population_report")),
            "Candidate population report created.",
            "Candidate population report missing.",
        ),
        _check(
            "candidate_generation_state_report_created",
            bool(report_bundle.get("candidate_generation_state_report")),
            "Candidate generation-state report created.",
            "Candidate generation-state report missing.",
        ),
        _check(
            "candidate_lifecycle_report_created",
            bool(report_bundle.get("candidate_lifecycle_report")),
            "Candidate lifecycle report created.",
            "Candidate lifecycle report missing.",
        ),
        _check(
            "candidate_creation_locked",
            report_bundle.get("candidate_creation_enabled") is False,
            "Candidate creation remains locked.",
            "Candidate creation must remain locked in 11F.3.",
        ),
        _check(
            "geometry_commit_locked",
            report_bundle.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11F.3.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_candidate_generation_report_owner_complete": True,
        "phase_11f_3_regen_candidate_generation_report_owner_complete": True,
        "regen_candidate_generation_report_owner_ready": ready,
        "regen_candidate_generation_report_owner_status": status,
        "regen_candidate_generation_report_bundle": report_bundle,
        "regen_candidate_generation_report_owner_checks": checks,
        "regen_candidate_generation_report_owner_failed_checks": failed,
        "regen_candidate_generation_report_owner_report": build_report(status, ready, report_bundle, checks, failed),
        "phase_11f_4_candidate_generation_registration_owner_allowed": ready,
        "regen_candidate_generation_registration_owner_allowed": ready,
        "regen_candidate_generation_reporting_state_owned": ready,
        "regen_candidate_generation_execution_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_candidate_generation_report_bundle(candidate_session):
    session_id = candidate_session.get(
        "candidate_generation_session_id",
        "CANDIDATE_GENERATION_SESSION_UNAVAILABLE",
    )

    candidate_session_report = {
        "report_id": f"{session_id}_SESSION_REPORT",
        "report_type": "CANDIDATE_GENERATION_SESSION_REPORT",
        "candidate_generation_session_id": session_id,
        "execution_session_id": candidate_session.get("execution_session_id"),
        "candidate_generation_state": candidate_session.get("candidate_generation_state"),
        "objective_mode": candidate_session.get("objective_mode"),
        "population_size": candidate_session.get("population_size"),
        "generation_limit": candidate_session.get("generation_limit"),
    }

    candidate_pool_report = {
        "report_id": f"{session_id}_POOL_REPORT",
        "report_type": "CANDIDATE_POOL_REPORT",
        "candidate_generation_session_id": session_id,
        "candidate_pool_state": candidate_session.get("candidate_pool_state"),
        "candidate_count": candidate_session.get("candidate_count"),
        "candidate_ids": list(candidate_session.get("candidate_ids", [])),
        "candidate_type_scope": list(candidate_session.get("candidate_type_scope", [])),
        "pool_summary": "Candidate pool is empty because candidate creation remains locked.",
    }

    candidate_population_report = {
        "report_id": f"{session_id}_POPULATION_REPORT",
        "report_type": "CANDIDATE_POPULATION_REPORT",
        "candidate_generation_session_id": session_id,
        "population_count": candidate_session.get("population_count"),
        "population_ids": list(candidate_session.get("population_ids", [])),
        "current_population_id": candidate_session.get("current_population_id"),
        "population_summary": "No populations exist yet because generation is not active.",
    }

    candidate_generation_state_report = {
        "report_id": f"{session_id}_GENERATION_STATE_REPORT",
        "report_type": "CANDIDATE_GENERATION_STATE_REPORT",
        "candidate_generation_session_id": session_id,
        "generation_count": candidate_session.get("generation_count"),
        "generation_ids": list(candidate_session.get("generation_ids", [])),
        "current_generation_id": candidate_session.get("current_generation_id"),
        "generation_summary": "No candidate generations exist yet.",
    }

    candidate_lifecycle_report = {
        "report_id": f"{session_id}_LIFECYCLE_REPORT",
        "report_type": "CANDIDATE_LIFECYCLE_REPORT",
        "candidate_generation_session_id": session_id,
        "candidate_lifecycle_state": candidate_session.get("candidate_lifecycle_state"),
        "current_candidate_id": candidate_session.get("current_candidate_id"),
        "candidate_creation_enabled": candidate_session.get("candidate_creation_enabled"),
        "mutation_execution_enabled": candidate_session.get("mutation_execution_enabled"),
        "candidate_scoring_enabled": candidate_session.get("candidate_scoring_enabled"),
        "candidate_ranking_enabled": candidate_session.get("candidate_ranking_enabled"),
        "candidate_acceptance_enabled": candidate_session.get("candidate_acceptance_enabled"),
        "solver_execution_enabled": candidate_session.get("solver_execution_enabled"),
        "live_geometry_commit_enabled": candidate_session.get("live_geometry_commit_enabled"),
        "lifecycle_summary": "Candidate lifecycle is owned but not started.",
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "candidate_generation_session_id": session_id,
        "candidate_session_report": candidate_session_report,
        "candidate_pool_report": candidate_pool_report,
        "candidate_population_report": candidate_population_report,
        "candidate_generation_state_report": candidate_generation_state_report,
        "candidate_lifecycle_report": candidate_lifecycle_report,
        "candidate_creation_enabled": False,
        "candidate_generation_execution_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_ranking_enabled": False,
        "candidate_acceptance_enabled": False,
        "solver_execution_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, report_bundle, checks, failed):
    lines = [
        "PHASE 11F.3 REGEN CANDIDATE GENERATION REPORT OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11F.4 Candidate Generation Registration Owner: {ready}",
        "",
        "CANDIDATE REPORT BUNDLE SNAPSHOT",
        f"Candidate Session ID: {report_bundle.get('candidate_generation_session_id')}",
        f"Session Report: {bool(report_bundle.get('candidate_session_report'))}",
        f"Pool Report: {bool(report_bundle.get('candidate_pool_report'))}",
        f"Population Report: {bool(report_bundle.get('candidate_population_report'))}",
        f"Generation State Report: {bool(report_bundle.get('candidate_generation_state_report'))}",
        f"Lifecycle Report: {bool(report_bundle.get('candidate_lifecycle_report'))}",
        "",
        "SAFETY LOCKS",
        f"Candidate Creation Enabled: {report_bundle.get('candidate_creation_enabled')}",
        f"Mutation Enabled: {report_bundle.get('mutation_execution_enabled')}",
        f"Solver Execution Enabled: {report_bundle.get('solver_execution_enabled')}",
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
        lines.append("11F.3 candidate generation report owner is complete.")
        lines.append("11F.4 candidate generation registration ownership may begin.")
        lines.append("Actual candidate creation, mutation, scoring, acceptance, solver execution, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
