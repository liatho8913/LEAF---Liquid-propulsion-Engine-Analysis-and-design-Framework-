"""
PHASE 13D
Channel Height Mutation Foundation
"""

OWNER_NAME = "REGEN_CHANNEL_HEIGHT_MUTATION_FOUNDATION"
PHASE = "13D"

PASS_STATUS = "PASS_REGEN_CHANNEL_HEIGHT_MUTATION_FOUNDATION_PHASE_13D"
FAIL_STATUS = "FAIL_REGEN_CHANNEL_HEIGHT_MUTATION_FOUNDATION_PHASE_13D"


def attach_regen_channel_height_mutation_foundation(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_channel_height_mutation_foundation(results))
    return results


def build_regen_channel_height_mutation_foundation(results):
    blockers = []

    allowed = (
        results.get("phase_13d_channel_height_mutation_allowed") is True
        and results.get("regen_channel_height_mutation_allowed") is True
    )

    if not allowed:
        blockers.append("13C channel width mutation foundation has not allowed channel height mutation.")

    width_foundation = results.get("regen_channel_width_mutation_foundation", {})
    population = results.get("regen_candidate_blueprint_population", {})
    blueprints = results.get("regen_candidate_blueprints", [])

    if not isinstance(width_foundation, dict) or width_foundation.get("ready") is not True:
        blockers.append("Channel width mutation foundation is missing or not ready.")

    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")

    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("Candidate blueprints are missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    foundation = None
    if ready:
        foundation = _build_channel_height_mutation_foundation(population, blueprints)

    return {
        "regen_channel_height_mutation_foundation_complete": True,
        "phase_13d_regen_channel_height_mutation_foundation_complete": True,
        "regen_channel_height_mutation_foundation_ready": ready,
        "regen_channel_height_mutation_foundation_status": status,
        "regen_channel_height_mutation_foundation_blockers": blockers,

        "regen_channel_height_mutation_foundation": foundation,
        "regen_channel_height_mutation_registry": (
            foundation.get("channel_height_mutation_registry") if isinstance(foundation, dict) else None
        ),
        "regen_channel_height_mutation_proposals": (
            foundation.get("channel_height_mutation_proposals") if isinstance(foundation, dict) else []
        ),
        "regen_channel_height_mutation_history": (
            foundation.get("channel_height_mutation_history") if isinstance(foundation, dict) else None
        ),
        "regen_channel_height_mutation_report": _report(status, ready, foundation, blockers),

        "phase_13e_rib_width_mutation_allowed": ready,
        "regen_rib_width_mutation_allowed": ready,

        "regen_channel_height_mutation_execution_allowed": False,
        "regen_real_geometry_mutation_allowed": False,
        "regen_solver_execution_from_mutation_allowed": False,
        "regen_candidate_acceptance_from_mutation_allowed": False,
        "regen_live_geometry_commit_from_mutation_allowed": False,

        "regen_candidate_blueprint_mutation_execution_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_channel_height_mutation_foundation(population, blueprints):
    proposals = []
    proposal_id = 1

    for blueprint in blueprints:
        blueprint_id = blueprint.get("blueprint_id")
        dims = _safe_get(blueprint, "geometry_package", "geometry_dimensions") or {}
        base_height = _float(dims.get("coolant_channel_height_m"), default=0.0)

        for step in [-0.00020, -0.00010, 0.00010, 0.00020]:
            proposed = base_height + step
            proposals.append(_build_proposal(proposal_id, blueprint_id, base_height, proposed, step))
            proposal_id += 1

    valid_count = len([p for p in proposals if p["proposal_validation"]["valid"]])
    invalid_count = len(proposals) - valid_count

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "channel_height_mutation_registry_id": f"CHANNEL_HEIGHT_MUTATION_REGISTRY_FOR_{population.get('population_id')}",
        "source_population_id": population.get("population_id"),
        "mutation_axis": "coolant_channel_height",
        "registered_steps_m": [-0.00020, -0.00010, 0.00010, 0.00020],
        "bounds": {
            "minimum_height_m": 0.00050,
            "maximum_height_m": 0.02000,
            "manufacturing_minimum_m": 0.00075,
            "positive_only": True,
        },
        "permissions": {
            "rib_width_mutation_allowed": True,
            "channel_height_mutation_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }

    history = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "history_state": "CHANNEL_HEIGHT_MUTATION_PROPOSALS_CREATED_NO_EXECUTION",
        "proposal_count": len(proposals),
        "valid_proposal_count": valid_count,
        "invalid_proposal_count": invalid_count,
        "mutation_execution_count": 0,
        "solver_execution_count": 0,
        "live_commit_count": 0,
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "channel_height_mutation_state": "CHANNEL_HEIGHT_MUTATION_FOUNDATION_CREATED_EXECUTION_LOCKED",
        "channel_height_mutation_registry": registry,
        "channel_height_mutation_proposals": proposals,
        "channel_height_mutation_history": history,
        "channel_height_mutation_readiness": {
            "ready_for_rib_width_mutation_foundation": True,
            "ready_for_real_mutation_execution": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "13E_RIB_WIDTH_MUTATION_FOUNDATION",
        },
    }


def _build_proposal(proposal_id, blueprint_id, base_height, proposed_height, step):
    valid = (
        proposed_height > 0.0
        and proposed_height >= 0.00050
        and proposed_height <= 0.02000
        and proposed_height >= 0.00075
    )

    blockers = []
    if proposed_height <= 0.0:
        blockers.append("Proposed channel height is not positive.")
    if proposed_height < 0.00050:
        blockers.append("Proposed channel height is below absolute minimum.")
    if proposed_height < 0.00075:
        blockers.append("Proposed channel height is below manufacturing minimum.")
    if proposed_height > 0.02000:
        blockers.append("Proposed channel height is above maximum bound.")

    return {
        "proposal_id": f"CHANNEL_HEIGHT_MUTATION_PROPOSAL_{proposal_id:04d}",
        "source_blueprint_id": blueprint_id,
        "mutation_axis": "coolant_channel_height",
        "base_value_m": base_height,
        "proposed_value_m": proposed_height,
        "mutation_step_m": step,
        "proposal_state": (
            "CHANNEL_HEIGHT_MUTATION_PROPOSAL_VALID_EXECUTION_LOCKED"
            if valid
            else "CHANNEL_HEIGHT_MUTATION_PROPOSAL_INVALID"
        ),
        "proposal_validation": {
            "valid": valid,
            "blockers": blockers,
            "positive_only": proposed_height > 0.0,
            "within_absolute_bounds": proposed_height >= 0.00050 and proposed_height <= 0.02000,
            "manufacturable": proposed_height >= 0.00075,
        },
        "execution_permissions": {
            "real_geometry_mutation_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }


def _require_locked(results, blockers):
    required_false = {
        "regen_channel_width_mutation_execution_allowed": "Channel width mutation execution is not safely locked.",
        "regen_real_geometry_mutation_allowed": "Real geometry mutation is not safely locked.",
        "regen_solver_execution_from_mutation_allowed": "Solver execution from mutation is not safely locked.",
        "regen_candidate_acceptance_from_mutation_allowed": "Candidate acceptance from mutation is not safely locked.",
        "regen_live_geometry_commit_from_mutation_allowed": "Live geometry commit from mutation is not safely locked.",
        "regen_candidate_blueprint_mutation_execution_allowed": "Candidate blueprint mutation execution is not safely locked.",
        "regen_optimisation_mutation_execution_allowed": "Optimisation mutation execution is not safely locked.",
        "regen_optimisation_live_geometry_commit_allowed": "Optimisation live geometry commit is not safely locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)


def _safe_get(data, *keys):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _float(value, default):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _report(status, ready, foundation, blockers):
    if not ready:
        return "PHASE 13D BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)

    history = foundation["channel_height_mutation_history"]
    return (
        "PHASE 13D REGEN CHANNEL HEIGHT MUTATION FOUNDATION\n"
        f"Status: {status}\n"
        f"Proposal Count: {history.get('proposal_count')}\n"
        f"Valid Proposals: {history.get('valid_proposal_count')}\n"
        "Real mutation execution remains locked.\n"
        "13E rib width mutation foundation may begin."
    )
