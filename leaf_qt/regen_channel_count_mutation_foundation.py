"""
PHASE 13B
Channel Count Mutation Foundation

Creates bounded mutation proposals for number_of_coolant_channels.

Does NOT:
- run solver
- accept candidates
- commit geometry
- mutate live design state
"""

OWNER_NAME = "REGEN_CHANNEL_COUNT_MUTATION_FOUNDATION"
PHASE = "13B"

PASS_STATUS = "PASS_REGEN_CHANNEL_COUNT_MUTATION_FOUNDATION_PHASE_13B"
FAIL_STATUS = "FAIL_REGEN_CHANNEL_COUNT_MUTATION_FOUNDATION_PHASE_13B"


def attach_regen_channel_count_mutation_foundation(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_channel_count_mutation_foundation(results))
    return results


def build_regen_channel_count_mutation_foundation(results):
    blockers = []

    allowed = (
        results.get("phase_13b_channel_count_mutation_allowed") is True
        and results.get("regen_channel_count_mutation_allowed") is True
    )

    if not allowed:
        blockers.append("13A mutation execution foundation has not allowed channel count mutation.")

    execution_foundation = results.get("regen_autonomous_blueprint_mutation_execution_foundation", {})
    population = results.get("regen_candidate_blueprint_population", {})
    blueprints = results.get("regen_candidate_blueprints", [])

    if not isinstance(execution_foundation, dict) or execution_foundation.get("ready") is not True:
        blockers.append("Mutation execution foundation is missing or not ready.")

    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")

    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("Candidate blueprints are missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    foundation = None
    if ready:
        foundation = _build_channel_count_mutation_foundation(population, blueprints)

    return {
        "regen_channel_count_mutation_foundation_complete": True,
        "phase_13b_regen_channel_count_mutation_foundation_complete": True,
        "regen_channel_count_mutation_foundation_ready": ready,
        "regen_channel_count_mutation_foundation_status": status,
        "regen_channel_count_mutation_foundation_blockers": blockers,

        "regen_channel_count_mutation_foundation": foundation,
        "regen_channel_count_mutation_registry": (
            foundation.get("channel_count_mutation_registry") if isinstance(foundation, dict) else None
        ),
        "regen_channel_count_mutation_proposals": (
            foundation.get("channel_count_mutation_proposals") if isinstance(foundation, dict) else []
        ),
        "regen_channel_count_mutation_history": (
            foundation.get("channel_count_mutation_history") if isinstance(foundation, dict) else None
        ),
        "regen_channel_count_mutation_report": _report(status, ready, foundation, blockers),

        "phase_13c_channel_width_mutation_allowed": ready,
        "regen_channel_width_mutation_allowed": ready,

        "regen_channel_count_mutation_execution_allowed": False,
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


def _build_channel_count_mutation_foundation(population, blueprints):
    proposals = []
    proposal_id = 1

    for blueprint in blueprints:
        blueprint_id = blueprint.get("blueprint_id")
        dims = _safe_get(blueprint, "geometry_package", "geometry_dimensions") or {}
        base_channels = _int(dims.get("number_of_coolant_channels"), default=0)

        for step in [-4, -2, 2, 4]:
            proposed = base_channels + step
            proposal = _build_proposal(proposal_id, blueprint_id, base_channels, proposed, step)
            proposals.append(proposal)
            proposal_id += 1

    valid_count = len([p for p in proposals if p["proposal_validation"]["valid"]])
    invalid_count = len(proposals) - valid_count

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "channel_count_mutation_registry_id": f"CHANNEL_COUNT_MUTATION_REGISTRY_FOR_{population.get('population_id')}",
        "source_population_id": population.get("population_id"),
        "mutation_axis": "number_of_coolant_channels",
        "registered_steps": [-4, -2, 2, 4],
        "bounds": {
            "minimum_channels": 8,
            "maximum_channels": 512,
            "integer_only": True,
            "even_only": True,
        },
        "permissions": {
            "channel_width_mutation_allowed": True,
            "channel_count_mutation_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }

    history = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "history_state": "CHANNEL_COUNT_MUTATION_PROPOSALS_CREATED_NO_EXECUTION",
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
        "channel_count_mutation_state": "CHANNEL_COUNT_MUTATION_FOUNDATION_CREATED_EXECUTION_LOCKED",
        "channel_count_mutation_registry": registry,
        "channel_count_mutation_proposals": proposals,
        "channel_count_mutation_history": history,
        "channel_count_mutation_readiness": {
            "ready_for_channel_width_mutation_foundation": True,
            "ready_for_real_mutation_execution": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "13C_CHANNEL_WIDTH_MUTATION_FOUNDATION",
        },
    }


def _build_proposal(proposal_id, blueprint_id, base_channels, proposed_channels, step):
    valid = (
        isinstance(proposed_channels, int)
        and proposed_channels >= 8
        and proposed_channels <= 512
        and proposed_channels % 2 == 0
    )

    blockers = []
    if proposed_channels < 8:
        blockers.append("Proposed channel count is below minimum bound.")
    if proposed_channels > 512:
        blockers.append("Proposed channel count is above maximum bound.")
    if proposed_channels % 2 != 0:
        blockers.append("Proposed channel count is not even.")

    return {
        "proposal_id": f"CHANNEL_COUNT_MUTATION_PROPOSAL_{proposal_id:04d}",
        "source_blueprint_id": blueprint_id,
        "mutation_axis": "number_of_coolant_channels",
        "base_value": base_channels,
        "proposed_value": proposed_channels,
        "mutation_step": step,
        "proposal_state": (
            "CHANNEL_COUNT_MUTATION_PROPOSAL_VALID_EXECUTION_LOCKED"
            if valid
            else "CHANNEL_COUNT_MUTATION_PROPOSAL_INVALID"
        ),
        "proposal_validation": {
            "valid": valid,
            "blockers": blockers,
            "integer_only": isinstance(proposed_channels, int),
            "within_bounds": proposed_channels >= 8 and proposed_channels <= 512,
            "even_only": proposed_channels % 2 == 0,
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
        "regen_candidate_blueprint_mutation_execution_allowed": "Candidate blueprint mutation execution is not safely locked.",
        "regen_real_geometry_mutation_allowed": "Real geometry mutation is not safely locked.",
        "regen_solver_execution_from_mutation_allowed": "Solver execution from mutation is not safely locked.",
        "regen_candidate_acceptance_from_mutation_allowed": "Candidate acceptance from mutation is not safely locked.",
        "regen_live_geometry_commit_from_mutation_allowed": "Live geometry commit from mutation is not safely locked.",
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


def _int(value, default):
    try:
        if value is None:
            return default
        return int(round(float(value)))
    except Exception:
        return default


def _report(status, ready, foundation, blockers):
    if not ready:
        return "PHASE 13B BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)

    history = foundation["channel_count_mutation_history"]
    return (
        "PHASE 13B REGEN CHANNEL COUNT MUTATION FOUNDATION\n"
        f"Status: {status}\n"
        f"Proposal Count: {history.get('proposal_count')}\n"
        f"Valid Proposals: {history.get('valid_proposal_count')}\n"
        "Real mutation execution remains locked.\n"
        "13C channel width mutation foundation may begin."
    )
