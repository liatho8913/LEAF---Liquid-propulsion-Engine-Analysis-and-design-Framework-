
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u96_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u96_is_fail_like(text) or _leaf_16u96_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u96_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u96_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u96_is_fail_like(value):
    return _leaf_16u96_status_severity(value) == "FAIL"


def _leaf_16u96_is_warn_like(value):
    return _leaf_16u96_status_severity(value) == "WARN"


def _leaf_16u96_is_pass_like(value):
    return _leaf_16u96_status_severity(value) == "PASS"


"""
PHASE 11G.3
Candidate Creation Report Owner

Owns candidate creation reports and diagnostics.

Does NOT:
- create candidates
- mutate geometry
- score candidates
- rank candidates
- accept candidates
- commit geometry
- execute solvers
"""

OWNER_NAME = "REGEN_CANDIDATE_CREATION_REPORT_OWNER"
PHASE = "11G.3"

PASS_STATUS = "PASS_REGEN_CANDIDATE_CREATION_REPORT_OWNER_PHASE_11G3"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_CREATION_REPORT_OWNER_PHASE_11G3"


def attach_regen_candidate_creation_report_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_creation_report_owner(results))
    return results


def build_regen_candidate_creation_report_owner(results):
    session_ready = (
        results.get("regen_candidate_creation_session_owner_ready") is True
        and results.get("phase_11g_3_candidate_creation_report_owner_allowed") is True
    )

    creation_session = results.get("regen_candidate_creation_session", {})
    report_bundle = _build_creation_report_bundle(creation_session)

    checks = [
        _check(
            "candidate_creation_session_owner_ready",
            session_ready,
            "11G.2 candidate creation session owner allows report ownership.",
            "11G.2 candidate creation session owner is not ready.",
        ),
        _check(
            "creation_session_report_created",
            bool(report_bundle.get("candidate_creation_session_report")),
            "Candidate creation session report created.",
            "Candidate creation session report missing.",
        ),
        _check(
            "creation_lifecycle_report_created",
            bool(report_bundle.get("candidate_creation_lifecycle_report")),
            "Candidate creation lifecycle report created.",
            "Candidate creation lifecycle report missing.",
        ),
        _check(
            "creation_constraint_report_created",
            bool(report_bundle.get("candidate_creation_constraint_report")),
            "Candidate creation constraint report created.",
            "Candidate creation constraint report missing.",
        ),
        _check(
            "creation_package_report_created",
            bool(report_bundle.get("candidate_creation_package_report")),
            "Candidate creation package report created.",
            "Candidate creation package report missing.",
        ),
        _check(
            "creation_safety_report_created",
            bool(report_bundle.get("candidate_creation_safety_report")),
            "Candidate creation safety report created.",
            "Candidate creation safety report missing.",
        ),
        _check(
            "candidate_creation_locked",
            report_bundle.get("candidate_creation_enabled") is False,
            "Candidate creation remains locked.",
            "Candidate creation must remain locked in 11G.3.",
        ),
        _check(
            "geometry_commit_locked",
            report_bundle.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11G.3.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_candidate_creation_report_owner_complete": True,
        "phase_11g_3_regen_candidate_creation_report_owner_complete": True,
        "regen_candidate_creation_report_owner_ready": ready,
        "regen_candidate_creation_report_owner_status": status,
        "regen_candidate_creation_report_bundle": report_bundle,
        "regen_candidate_creation_report_owner_checks": checks,
        "regen_candidate_creation_report_owner_failed_checks": failed,
        "regen_candidate_creation_report_owner_report": build_report(status, ready, report_bundle, checks, failed),
        "phase_11g_4_candidate_creation_registration_owner_allowed": ready,
        "regen_candidate_creation_registration_owner_allowed": ready,
        "regen_candidate_creation_reporting_state_owned": ready,
        "regen_candidate_creation_execution_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_creation_report_bundle(creation_session):
    session_id = creation_session.get(
        "candidate_creation_session_id",
        "CANDIDATE_CREATION_SESSION_UNAVAILABLE",
    )

    candidate_creation_session_report = {
        "report_id": f"{session_id}_SESSION_REPORT",
        "report_type": "CANDIDATE_CREATION_SESSION_REPORT",
        "candidate_creation_session_id": session_id,
        "candidate_generation_session_id": creation_session.get("candidate_generation_session_id"),
        "candidate_creation_state": creation_session.get("candidate_creation_state"),
        "objective_mode": creation_session.get("objective_mode"),
        "population_size": creation_session.get("population_size"),
        "generation_limit": creation_session.get("generation_limit"),
    }

    candidate_creation_lifecycle_report = {
        "report_id": f"{session_id}_LIFECYCLE_REPORT",
        "report_type": "CANDIDATE_CREATION_LIFECYCLE_REPORT",
        "candidate_creation_session_id": session_id,
        "candidate_creation_lifecycle_state": creation_session.get("candidate_creation_lifecycle_state"),
        "candidate_creation_pool_state": creation_session.get("candidate_creation_pool_state"),
        "created_candidate_count": creation_session.get("created_candidate_count"),
        "accepted_candidate_count": creation_session.get("accepted_candidate_count"),
        "rejected_candidate_count": creation_session.get("rejected_candidate_count"),
        "lifecycle_summary": "Candidate creation lifecycle is owned but not started.",
    }

    candidate_creation_constraint_report = {
        "report_id": f"{session_id}_CONSTRAINT_REPORT",
        "report_type": "CANDIDATE_CREATION_CONSTRAINT_REPORT",
        "candidate_creation_session_id": session_id,
        "required_input_groups": list(creation_session.get("required_input_groups", [])),
        "constraint_context": dict(creation_session.get("constraint_context", {})),
        "constraint_summary": "Creation constraints are carried forward for future candidate blueprint generation.",
    }

    candidate_creation_package_report = {
        "report_id": f"{session_id}_PACKAGE_REPORT",
        "report_type": "CANDIDATE_CREATION_PACKAGE_REPORT",
        "candidate_creation_session_id": session_id,
        "creation_package": dict(creation_session.get("creation_package", {})),
        "created_candidate_ids": list(creation_session.get("created_candidate_ids", [])),
        "current_creation_candidate_id": creation_session.get("current_creation_candidate_id"),
        "package_summary": "Creation package is empty because candidate creation remains locked.",
    }

    candidate_creation_safety_report = {
        "report_id": f"{session_id}_SAFETY_REPORT",
        "report_type": "CANDIDATE_CREATION_SAFETY_REPORT",
        "candidate_creation_session_id": session_id,
        "candidate_creation_enabled": creation_session.get("candidate_creation_enabled"),
        "candidate_blueprint_creation_enabled": creation_session.get("candidate_blueprint_creation_enabled"),
        "mutation_execution_enabled": creation_session.get("mutation_execution_enabled"),
        "candidate_scoring_enabled": creation_session.get("candidate_scoring_enabled"),
        "candidate_ranking_enabled": creation_session.get("candidate_ranking_enabled"),
        "candidate_acceptance_enabled": creation_session.get("candidate_acceptance_enabled"),
        "solver_execution_enabled": creation_session.get("solver_execution_enabled"),
        "live_geometry_commit_enabled": creation_session.get("live_geometry_commit_enabled"),
        "safety_summary": "All candidate-changing and geometry-changing systems are locked.",
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "candidate_creation_session_id": session_id,
        "candidate_creation_session_report": candidate_creation_session_report,
        "candidate_creation_lifecycle_report": candidate_creation_lifecycle_report,
        "candidate_creation_constraint_report": candidate_creation_constraint_report,
        "candidate_creation_package_report": candidate_creation_package_report,
        "candidate_creation_safety_report": candidate_creation_safety_report,
        "candidate_creation_enabled": False,
        "candidate_blueprint_creation_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_ranking_enabled": False,
        "candidate_acceptance_enabled": False,
        "solver_execution_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, report_bundle, checks, failed):
    lines = [
        "PHASE 11G.3 REGEN CANDIDATE CREATION REPORT OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11G.4 Candidate Creation Registration Owner: {ready}",
        "",
        "CANDIDATE CREATION REPORT BUNDLE SNAPSHOT",
        f"Creation Session ID: {report_bundle.get('candidate_creation_session_id')}",
        f"Session Report: {bool(report_bundle.get('candidate_creation_session_report'))}",
        f"Lifecycle Report: {bool(report_bundle.get('candidate_creation_lifecycle_report'))}",
        f"Constraint Report: {bool(report_bundle.get('candidate_creation_constraint_report'))}",
        f"Package Report: {bool(report_bundle.get('candidate_creation_package_report'))}",
        f"Safety Report: {bool(report_bundle.get('candidate_creation_safety_report'))}",
        "",
        "SAFETY LOCKS",
        f"Candidate Creation Enabled: {report_bundle.get('candidate_creation_enabled')}",
        f"Blueprint Creation Enabled: {report_bundle.get('candidate_blueprint_creation_enabled')}",
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
        lines.append("11G.3 candidate creation report owner is complete.")
        lines.append("11G.4 candidate creation registration ownership may begin.")
        lines.append("Actual candidate creation, mutation, scoring, acceptance, solver execution, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
