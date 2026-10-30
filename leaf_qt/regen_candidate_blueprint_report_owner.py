"""
PHASE 12A.4
Candidate Blueprint Report Owner

Creates the formal report layer for candidate blueprint generation ownership.

Does NOT:
- create blueprints
- create candidates
- mutate geometry
- score candidates
- rank candidates
- evolve populations
- commit geometry
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_REPORT_OWNER"
PHASE = "12A.4"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_REPORT_OWNER_PHASE_12A4"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_REPORT_OWNER_PHASE_12A4"


def attach_regen_candidate_blueprint_report_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_report_owner(results))
    return results


def build_regen_candidate_blueprint_report_owner(results):
    registry = results.get("regen_candidate_blueprint_registry", {})
    allowed = (
        results.get("regen_candidate_blueprint_report_owner_allowed") is True
        and results.get("phase_12a_4_candidate_blueprint_report_owner_allowed") is True
    )

    blockers = []

    if not allowed:
        blockers.append("12A.3 blueprint registration owner has not allowed reporting.")

    if not isinstance(registry, dict) or not registry:
        blockers.append("Blueprint registry is missing.")

    if isinstance(registry, dict) and registry.get("ready") is not True:
        blockers.append("Blueprint registry is not ready.")

    if isinstance(registry, dict) and not registry.get("candidate_blueprint_registry_id"):
        blockers.append("Blueprint registry ID is missing.")

    if isinstance(registry, dict) and not registry.get("candidate_blueprint_session_id"):
        blockers.append("Blueprint session linkage is missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report_bundle = None

    if ready:
        report_bundle = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": True,
            "report_id": f"BLUEPRINT_REPORT_FOR_{registry.get('candidate_blueprint_registry_id')}",
            "registry_id": registry.get("candidate_blueprint_registry_id"),
            "session_id": registry.get("candidate_blueprint_session_id"),
            "report_sections": [
                "ownership_summary",
                "registry_summary",
                "session_summary",
                "permission_summary",
                "future_linkage_summary",
                "safety_lock_summary",
            ],
            "future_audit_key": registry.get("future_audit_key"),
            "future_generation_key": registry.get("future_generation_key"),
            "blueprint_creation_state": "REPORT_READY_BLUEPRINT_CREATION_LOCKED",
            "next_phase": "12A.5_CANDIDATE_BLUEPRINT_COMPLETION_AUDIT",
        }

    report_text = build_report(status, ready, registry, report_bundle, blockers)

    return {
        "regen_candidate_blueprint_report_owner_complete": True,
        "phase_12a_4_regen_candidate_blueprint_report_owner_complete": True,
        "regen_candidate_blueprint_report_owner_ready": ready,
        "regen_candidate_blueprint_report_owner_status": status,
        "regen_candidate_blueprint_report_owner_blockers": blockers,
        "regen_candidate_blueprint_report_bundle": report_bundle,
        "regen_candidate_blueprint_report": report_text,
        "regen_candidate_blueprint_report_owner_report": report_text,

        "phase_12a_5_candidate_blueprint_completion_audit_allowed": ready,
        "regen_candidate_blueprint_completion_audit_allowed": ready,

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


def build_report(status, ready, registry, report_bundle, blockers):
    lines = [
        "PHASE 12A.4 REGEN CANDIDATE BLUEPRINT REPORT OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12A.5 Candidate Blueprint Completion Audit: {ready}",
        "",
    ]

    if ready:
        permissions = registry.get("generation_permissions", {})

        lines.extend([
            "OWNERSHIP SUMMARY",
            f"Report ID: {report_bundle.get('report_id')}",
            f"Registry ID: {report_bundle.get('registry_id')}",
            f"Session ID: {report_bundle.get('session_id')}",
            f"Blueprint Creation State: {report_bundle.get('blueprint_creation_state')}",
            "",
            "REGISTRY SUMMARY",
            f"Registry Owner: {registry.get('owner')}",
            f"Registry Phase: {registry.get('phase')}",
            f"Registry Status: {registry.get('status')}",
            "",
            "SESSION SUMMARY",
            f"Source Session Owner: {registry.get('source_session_owner')}",
            f"Source Session Phase: {registry.get('source_session_phase')}",
            f"Source Session Lifecycle: {registry.get('source_session_lifecycle_state')}",
            "",
            "REPORT SECTIONS",
        ])

        for section in report_bundle.get("report_sections", []):
            lines.append(f"- {section}")

        lines.extend([
            "",
            "FUTURE LINKAGE SUMMARY",
            f"Future Audit Key: {report_bundle.get('future_audit_key')}",
            f"Future Generation Key: {report_bundle.get('future_generation_key')}",
            "",
            "PERMISSION SUMMARY",
        ])

        for key, value in permissions.items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "RESULT",
            "12A.4 candidate blueprint report ownership is complete.",
            "12A.5 candidate blueprint completion audit may begin.",
            "Blueprint creation remains locked.",
        ])

    else:
        lines.append("BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")

    return "\n".join(lines)


def _require_locked(results, blockers):
    required_false = {
        "regen_candidate_blueprint_generation_execution_allowed":
            "Blueprint generation execution is not safely locked.",
        "regen_candidate_blueprint_create_blueprints_allowed":
            "Blueprint creation is not safely locked.",
        "regen_candidate_creation_create_candidates_allowed":
            "Candidate creation is not safely locked.",
        "regen_candidate_generation_create_candidates_allowed":
            "Candidate generation is not safely locked.",
        "regen_optimisation_runtime_execution_allowed":
            "Runtime optimisation execution is not safely locked.",
        "regen_optimisation_generation_advance_allowed":
            "Population generation advance is not safely locked.",
        "regen_optimisation_mutation_execution_allowed":
            "Mutation execution is not safely locked.",
        "regen_optimisation_candidate_acceptance_allowed":
            "Candidate acceptance is not safely locked.",
        "regen_optimisation_live_geometry_commit_allowed":
            "Live geometry commit is not safely locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)
