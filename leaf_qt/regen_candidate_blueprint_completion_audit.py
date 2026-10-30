from leaf_qt.status_presentation import status_severity
"""
PHASE 12A.5
Candidate Blueprint Completion Audit

Audits the candidate blueprint ownership stack.

This is the final ownership-layer sign-off before actual blueprint generation
can begin in Phase 12B.1.

Does NOT:
- create blueprints
- create candidates
- mutate geometry
- score candidates
- rank candidates
- evolve populations
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

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_COMPLETION_AUDIT"
PHASE = "12A.5"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_COMPLETION_AUDIT_PHASE_12A5"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_COMPLETION_AUDIT_PHASE_12A5"


def attach_regen_candidate_blueprint_completion_audit(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_completion_audit(results))
    return results


def build_regen_candidate_blueprint_completion_audit(results):
    checks = [
        _check(
            "input_gate_complete",
            results.get("phase_12a_1_regen_candidate_blueprint_generation_input_gate_complete") is True
            and results.get("regen_candidate_blueprint_generation_input_gate_ready") is True,
            "12A.1 blueprint input gate is complete and ready.",
            "12A.1 blueprint input gate is missing or not ready.",
        ),
        _check(
            "session_owner_complete",
            results.get("phase_12a_2_regen_candidate_blueprint_session_owner_complete") is True
            and results.get("regen_candidate_blueprint_session_owner_ready") is True
            and isinstance(results.get("regen_candidate_blueprint_session"), dict),
            "12A.2 blueprint session owner is complete and ready.",
            "12A.2 blueprint session owner is missing or not ready.",
        ),
        _check(
            "registration_owner_complete",
            results.get("phase_12a_3_regen_candidate_blueprint_registration_owner_complete") is True
            and results.get("regen_candidate_blueprint_registration_owner_ready") is True
            and isinstance(results.get("regen_candidate_blueprint_registry"), dict),
            "12A.3 blueprint registration owner is complete and ready.",
            "12A.3 blueprint registration owner is missing or not ready.",
        ),
        _check(
            "report_owner_complete",
            results.get("phase_12a_4_regen_candidate_blueprint_report_owner_complete") is True
            and results.get("regen_candidate_blueprint_report_owner_ready") is True
            and isinstance(results.get("regen_candidate_blueprint_report_bundle"), dict),
            "12A.4 blueprint report owner is complete and ready.",
            "12A.4 blueprint report owner is missing or not ready.",
        ),
        _check(
            "session_id_exists",
            bool(results.get("regen_candidate_blueprint_session_id")),
            "Blueprint session ID exists.",
            "Blueprint session ID is missing.",
        ),
        _check(
            "registry_id_exists",
            bool(results.get("regen_candidate_blueprint_registry_id")),
            "Blueprint registry ID exists.",
            "Blueprint registry ID is missing.",
        ),
        _check(
            "registry_links_session",
            _registry_links_session(results),
            "Blueprint registry links to the blueprint session.",
            "Blueprint registry does not link to the blueprint session.",
        ),
        _check(
            "report_links_registry",
            _report_links_registry(results),
            "Blueprint report links to the blueprint registry.",
            "Blueprint report does not link to the blueprint registry.",
        ),
        _check(
            "future_generation_linkage_exists",
            _future_linkage_exists(results),
            "Future blueprint generation linkage exists.",
            "Future blueprint generation linkage is missing.",
        ),
        _check(
            "safety_locks_all_closed",
            _all_safety_locks_closed(results),
            "All blueprint and optimisation execution locks remain closed.",
            "One or more blueprint or optimisation execution locks are open.",
        ),
    ]

    failed = [check for check in checks if not check["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    audit = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "complete": ready,
        "ready": ready,
        "checked_phases": [
            "12A.1_candidate_blueprint_generation_input_gate",
            "12A.2_candidate_blueprint_session_owner",
            "12A.3_candidate_blueprint_registration_owner",
            "12A.4_candidate_blueprint_report_owner",
        ],
        "failed_checks": [check["name"] for check in failed],
        "blueprint_architecture_state": (
            "BLUEPRINT_OWNERSHIP_ARCHITECTURE_COMPLETE_GENERATION_LOCKED"
            if ready
            else "BLUEPRINT_OWNERSHIP_ARCHITECTURE_INCOMPLETE"
        ),
        "next_phase": "12B.1_CANDIDATE_BLUEPRINT_GENERATION_ENGINE" if ready else None,
    }

    report = build_report(status, ready, audit, checks, failed)

    return {
        "regen_candidate_blueprint_completion_audit_complete": True,
        "phase_12a_5_regen_candidate_blueprint_completion_audit_complete": True,
        "regen_candidate_blueprint_completion_audit_ready": ready,
        "regen_candidate_blueprint_completion_audit_status": status,
        "regen_candidate_blueprint_completion_audit": audit,
        "regen_candidate_blueprint_completion_audit_checks": checks,
        "regen_candidate_blueprint_completion_audit_failed_checks": failed,
        "regen_candidate_blueprint_completion_audit_report": report,

        "phase_12a_blueprint_ownership_architecture_complete": ready,
        "regen_candidate_blueprint_ownership_architecture_complete": ready,

        "phase_12b_1_candidate_blueprint_generation_engine_allowed": ready,
        "regen_candidate_blueprint_generation_engine_allowed": ready,

        "regen_candidate_blueprint_generation_execution_allowed": False,
        "regen_candidate_blueprint_create_blueprints_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_report(status, ready, audit, checks, failed):
    lines = [
        "PHASE 12A.5 REGEN CANDIDATE BLUEPRINT COMPLETION AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Blueprint Ownership Architecture Complete: {ready}",
        f"Blueprint Architecture State: {audit.get('blueprint_architecture_state')}",
        "",
        "CHECKED PHASES",
    ]

    for phase in audit.get("checked_phases", []):
        lines.append(f"- {phase}")

    lines.extend(["", "CHECKS"])

    for check in checks:
        marker = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        message = check["pass_message"] if check["passed"] else check["fail_message"]
        lines.append(f"[{marker}] {check['name']} - {message}")

    if failed:
        lines.extend(["", "BLOCKERS"])
        for check in failed:
            lines.append(f"- {check['name']}: {check['fail_message']}")
    else:
        lines.extend([
            "",
            "RESULT",
            "12A.5 candidate blueprint completion audit is complete.",
            "Blueprint ownership architecture is complete.",
            "12B.1 candidate blueprint generation engine may begin.",
            "Blueprint creation remains locked until the generation engine explicitly opens it.",
        ])

    return "\n".join(lines)


def _registry_links_session(results):
    registry = results.get("regen_candidate_blueprint_registry", {})
    if not isinstance(registry, dict):
        return False
    return (
        bool(results.get("regen_candidate_blueprint_session_id"))
        and registry.get("candidate_blueprint_session_id")
        == results.get("regen_candidate_blueprint_session_id")
    )


def _report_links_registry(results):
    bundle = results.get("regen_candidate_blueprint_report_bundle", {})
    if not isinstance(bundle, dict):
        return False
    return (
        bool(results.get("regen_candidate_blueprint_registry_id"))
        and bundle.get("registry_id")
        == results.get("regen_candidate_blueprint_registry_id")
    )


def _future_linkage_exists(results):
    registry = results.get("regen_candidate_blueprint_registry", {})
    bundle = results.get("regen_candidate_blueprint_report_bundle", {})
    if not isinstance(registry, dict) or not isinstance(bundle, dict):
        return False

    return (
        bool(registry.get("future_generation_key"))
        and bool(bundle.get("future_generation_key"))
        and registry.get("future_generation_key") == bundle.get("future_generation_key")
    )


def _all_safety_locks_closed(results):
    required_false = [
        "regen_candidate_blueprint_generation_execution_allowed",
        "regen_candidate_blueprint_create_blueprints_allowed",
        "regen_candidate_creation_create_candidates_allowed",
        "regen_candidate_generation_create_candidates_allowed",
        "regen_optimisation_runtime_execution_allowed",
        "regen_optimisation_generation_advance_allowed",
        "regen_optimisation_mutation_execution_allowed",
        "regen_optimisation_candidate_acceptance_allowed",
        "regen_optimisation_live_geometry_commit_allowed",
    ]

    return all(results.get(key) is False for key in required_false)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
