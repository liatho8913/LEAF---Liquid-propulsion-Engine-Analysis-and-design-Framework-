"""
PHASE 12A.3
Candidate Blueprint Registration Owner

Registers the candidate blueprint generation session into a formal ownership
registry.

Does NOT:
- create blueprints
- create candidates
- mutate geometry
- score candidates
- rank candidates
- evolve populations
- commit geometry
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_REGISTRATION_OWNER"
PHASE = "12A.3"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_REGISTRATION_OWNER_PHASE_12A3"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_REGISTRATION_OWNER_PHASE_12A3"


def attach_regen_candidate_blueprint_registration_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_registration_owner(results))
    return results


def build_regen_candidate_blueprint_registration_owner(results):
    session = results.get("regen_candidate_blueprint_session", {})
    session_allowed = (
        results.get("regen_candidate_blueprint_registration_owner_allowed") is True
        and results.get("phase_12a_3_candidate_blueprint_registration_owner_allowed") is True
    )

    blockers = []

    if not session_allowed:
        blockers.append("12A.2 blueprint session owner has not allowed registration.")

    if not isinstance(session, dict) or not session:
        blockers.append("Blueprint session is missing.")

    if isinstance(session, dict) and session.get("ready") is not True:
        blockers.append("Blueprint session is not ready.")

    if isinstance(session, dict) and not session.get("candidate_blueprint_session_id"):
        blockers.append("Blueprint session ID is missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    registry = None
    registry_id = None

    if ready:
        session_id = session.get("candidate_blueprint_session_id")
        registry_id = f"BLUEPRINT_REGISTRY_FOR_{session_id}"

        registry = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": True,
            "candidate_blueprint_registry_id": registry_id,
            "candidate_blueprint_session_id": session_id,
            "source_session_owner": session.get("owner"),
            "source_session_phase": session.get("phase"),
            "source_session_lifecycle_state": session.get("lifecycle_state"),
            "registered_items": [
                "candidate_blueprint_session",
                "future_blueprint_report_owner",
                "future_blueprint_completion_audit",
                "future_blueprint_generation_engine",
                "future_blueprint_history_owner",
            ],
            "future_report_key": "regen_candidate_blueprint_report",
            "future_audit_key": "regen_candidate_blueprint_completion_audit",
            "future_generation_key": "regen_candidate_blueprint_generation_engine",
            "generation_permissions": {
                "blueprint_generation_execution_allowed": False,
                "blueprint_create_blueprints_allowed": False,
                "candidate_creation_allowed": False,
                "mutation_execution_allowed": False,
                "runtime_execution_allowed": False,
                "generation_advance_allowed": False,
                "candidate_acceptance_allowed": False,
                "live_geometry_commit_allowed": False,
            },
            "next_phase": "12A.4_CANDIDATE_BLUEPRINT_REPORT_OWNER",
        }

    report = build_report(status, ready, registry, blockers)

    return {
        "regen_candidate_blueprint_registration_owner_complete": True,
        "phase_12a_3_regen_candidate_blueprint_registration_owner_complete": True,
        "regen_candidate_blueprint_registration_owner_ready": ready,
        "regen_candidate_blueprint_registration_owner_status": status,
        "regen_candidate_blueprint_registration_owner_blockers": blockers,
        "regen_candidate_blueprint_registry": registry,
        "regen_candidate_blueprint_registry_id": registry_id,
        "regen_candidate_blueprint_registration_owner_report": report,

        "phase_12a_4_candidate_blueprint_report_owner_allowed": ready,
        "regen_candidate_blueprint_report_owner_allowed": ready,

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


def build_report(status, ready, registry, blockers):
    lines = [
        "PHASE 12A.3 REGEN CANDIDATE BLUEPRINT REGISTRATION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12A.4 Candidate Blueprint Report Owner: {ready}",
        "",
    ]

    if registry:
        lines.extend([
            "REGISTRY",
            f"Registry ID: {registry.get('candidate_blueprint_registry_id')}",
            f"Session ID: {registry.get('candidate_blueprint_session_id')}",
            f"Source Session Owner: {registry.get('source_session_owner')}",
            f"Source Session Phase: {registry.get('source_session_phase')}",
            f"Source Session Lifecycle: {registry.get('source_session_lifecycle_state')}",
            "",
            "REGISTERED ITEMS",
        ])

        for item in registry.get("registered_items", []):
            lines.append(f"- {item}")

        lines.extend([
            "",
            "FUTURE LINKAGE",
            f"Report Key: {registry.get('future_report_key')}",
            f"Audit Key: {registry.get('future_audit_key')}",
            f"Generation Key: {registry.get('future_generation_key')}",
            "",
            "GENERATION PERMISSIONS",
        ])

        for key, value in registry.get("generation_permissions", {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "RESULT",
            "12A.3 candidate blueprint registration ownership is complete.",
            "12A.4 candidate blueprint report ownership may begin.",
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
