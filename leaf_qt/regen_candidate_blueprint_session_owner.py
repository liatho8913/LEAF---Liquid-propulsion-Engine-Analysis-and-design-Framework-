"""
PHASE 12A.2
Candidate Blueprint Session Owner

Creates the ownership session for future candidate blueprint generation.

Does NOT:
- create blueprints
- create candidates
- mutate geometry
- score candidates
- rank candidates
- evolve populations
- commit geometry
"""

from datetime import datetime, timezone

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_SESSION_OWNER"
PHASE = "12A.2"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_SESSION_OWNER_PHASE_12A2"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_SESSION_OWNER_PHASE_12A2"


def attach_regen_candidate_blueprint_session_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_session_owner(results))
    return results


def build_regen_candidate_blueprint_session_owner(results):
    gate_ready = (
        results.get("regen_candidate_blueprint_generation_input_gate_ready") is True
        and results.get("regen_candidate_blueprint_session_owner_allowed") is True
    )

    blockers = []

    if not gate_ready:
        blockers.append("12A.1 blueprint generation input gate is not ready.")

    if results.get("regen_candidate_blueprint_create_blueprints_allowed") is not False:
        blockers.append("Blueprint creation is not safely locked.")

    if results.get("regen_candidate_creation_create_candidates_allowed") is not False:
        blockers.append("Candidate creation is not safely locked.")

    if results.get("regen_optimisation_mutation_execution_allowed") is not False:
        blockers.append("Mutation execution is not safely locked.")

    if results.get("regen_optimisation_live_geometry_commit_allowed") is not False:
        blockers.append("Live geometry commit is not safely locked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    session_id = None
    session = None

    if ready:
        session_id = _build_session_id(results)
        session = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": True,
            "candidate_blueprint_session_id": session_id,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "lifecycle_state": "BLUEPRINT_SESSION_CREATED_BLUEPRINT_CREATION_LOCKED",
            "source_gate_status": results.get(
                "regen_candidate_blueprint_generation_input_gate_status"
            ),
            "source_candidate_creation_session_id": _safe_get(
                results,
                "regen_candidate_creation_session",
                "candidate_creation_session_id",
            ),
            "source_candidate_creation_registry_id": _safe_get(
                results,
                "regen_candidate_creation_registry",
                "candidate_creation_registry_id",
            ),
            "next_phase": "12A.3_CANDIDATE_BLUEPRINT_REGISTRATION_OWNER",
            "execution_locks": {
                "blueprint_creation_allowed": False,
                "candidate_creation_allowed": False,
                "mutation_execution_allowed": False,
                "runtime_execution_allowed": False,
                "generation_advance_allowed": False,
                "candidate_acceptance_allowed": False,
                "live_geometry_commit_allowed": False,
            },
        }

    report = build_report(status, ready, session, blockers)

    return {
        "regen_candidate_blueprint_session_owner_complete": True,
        "phase_12a_2_regen_candidate_blueprint_session_owner_complete": True,
        "regen_candidate_blueprint_session_owner_ready": ready,
        "regen_candidate_blueprint_session_owner_status": status,
        "regen_candidate_blueprint_session_owner_blockers": blockers,
        "regen_candidate_blueprint_session": session,
        "regen_candidate_blueprint_session_id": session_id,
        "regen_candidate_blueprint_session_owner_report": report,

        "phase_12a_3_candidate_blueprint_registration_owner_allowed": ready,
        "regen_candidate_blueprint_registration_owner_allowed": ready,

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


def build_report(status, ready, session, blockers):
    lines = [
        "PHASE 12A.2 REGEN CANDIDATE BLUEPRINT SESSION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12A.3 Candidate Blueprint Registration Owner: {ready}",
        "",
    ]

    if session:
        lines.extend([
            "SESSION",
            f"Session ID: {session.get('candidate_blueprint_session_id')}",
            f"Created UTC: {session.get('created_utc')}",
            f"Lifecycle State: {session.get('lifecycle_state')}",
            f"Source Gate Status: {session.get('source_gate_status')}",
            f"Source Candidate Creation Session ID: {session.get('source_candidate_creation_session_id')}",
            f"Source Candidate Creation Registry ID: {session.get('source_candidate_creation_registry_id')}",
            "",
            "SAFETY LOCKS",
        ])

        for key, value in session.get("execution_locks", {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "RESULT",
            "12A.2 candidate blueprint session ownership is complete.",
            "12A.3 candidate blueprint registration ownership may begin.",
            "Blueprint creation remains locked.",
        ])

    else:
        lines.append("BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")

    return "\n".join(lines)


def _build_session_id(results):
    source_session_id = _safe_get(
        results,
        "regen_candidate_creation_session",
        "candidate_creation_session_id",
    )

    if source_session_id:
        return f"BLUEPRINT_SESSION_FROM_{source_session_id}"

    return "BLUEPRINT_SESSION_12A2"


def _safe_get(results, container_key, value_key):
    container = results.get(container_key, {})
    if isinstance(container, dict):
        return container.get(value_key)
    return None
