OWNER_NAME = "REGEN_RIB_WIDTH_MUTATION_FOUNDATION"
PHASE = "13E"
PASS_STATUS = "PASS_REGEN_RIB_WIDTH_MUTATION_FOUNDATION_PHASE_13E"
FAIL_STATUS = "FAIL_REGEN_RIB_WIDTH_MUTATION_FOUNDATION_PHASE_13E"

def attach_regen_rib_width_mutation_foundation(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_rib_width_mutation_foundation(results))
    return results

def build_regen_rib_width_mutation_foundation(results):
    blockers = []

    allowed = (
        results.get("phase_13e_rib_width_mutation_allowed") is True
        and results.get("regen_rib_width_mutation_allowed") is True
    )
    if not allowed:
        blockers.append("13D channel height mutation foundation has not allowed rib width mutation.")

    height_foundation = results.get("regen_channel_height_mutation_foundation", {})
    population = results.get("regen_candidate_blueprint_population", {})
    blueprints = results.get("regen_candidate_blueprints", [])

    if not isinstance(height_foundation, dict) or height_foundation.get("ready") is not True:
        blockers.append("Channel height mutation foundation is missing or not ready.")
    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")
    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("Candidate blueprints are missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    foundation = _build_foundation(population, blueprints) if ready else None

    return {
        "regen_rib_width_mutation_foundation_complete": True,
        "phase_13e_regen_rib_width_mutation_foundation_complete": True,
        "regen_rib_width_mutation_foundation_ready": ready,
        "regen_rib_width_mutation_foundation_status": status,
        "regen_rib_width_mutation_foundation_blockers": blockers,
        "regen_rib_width_mutation_foundation": foundation,
        "regen_rib_width_mutation_registry": foundation.get("rib_width_mutation_registry") if foundation else None,
        "regen_rib_width_mutation_proposals": foundation.get("rib_width_mutation_proposals") if foundation else [],
        "regen_rib_width_mutation_history": foundation.get("rib_width_mutation_history") if foundation else None,
        "regen_rib_width_mutation_report": _report(status, ready, foundation, blockers),
        "phase_13f_wall_thickness_mutation_allowed": ready,
        "regen_wall_thickness_mutation_allowed": ready,
        "regen_rib_width_mutation_execution_allowed": False,
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

def _build_foundation(population, blueprints):
    proposals = []
    proposal_id = 1

    for blueprint in blueprints:
        blueprint_id = blueprint.get("blueprint_id")
        dims = _safe_get(blueprint, "geometry_package", "geometry_dimensions") or {}
        base = _float(dims.get("rib_width_m"), 0.0)

        for step in [-0.00010, -0.00005, 0.00005, 0.00010]:
            proposed = base + step
            proposals.append(_proposal(proposal_id, blueprint_id, base, proposed, step))
            proposal_id += 1

    valid_count = len([p for p in proposals if p["proposal_validation"]["valid"]])

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "rib_width_mutation_registry_id": f"RIB_WIDTH_MUTATION_REGISTRY_FOR_{population.get('population_id')}",
        "source_population_id": population.get("population_id"),
        "mutation_axis": "rib_width",
        "registered_steps_m": [-0.00010, -0.00005, 0.00005, 0.00010],
        "bounds": {
            "minimum_rib_width_m": 0.00020,
            "maximum_rib_width_m": 0.01000,
            "manufacturing_minimum_m": 0.00030,
            "positive_only": True,
        },
        "permissions": {
            "wall_thickness_mutation_allowed": True,
            "rib_width_mutation_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }

    history = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "history_state": "RIB_WIDTH_MUTATION_PROPOSALS_CREATED_NO_EXECUTION",
        "proposal_count": len(proposals),
        "valid_proposal_count": valid_count,
        "invalid_proposal_count": len(proposals) - valid_count,
        "mutation_execution_count": 0,
        "solver_execution_count": 0,
        "live_commit_count": 0,
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "rib_width_mutation_state": "RIB_WIDTH_MUTATION_FOUNDATION_CREATED_EXECUTION_LOCKED",
        "rib_width_mutation_registry": registry,
        "rib_width_mutation_proposals": proposals,
        "rib_width_mutation_history": history,
        "rib_width_mutation_readiness": {
            "ready_for_wall_thickness_mutation_foundation": True,
            "ready_for_real_mutation_execution": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "13F_WALL_THICKNESS_MUTATION_FOUNDATION",
        },
    }

def _proposal(proposal_id, blueprint_id, base, proposed, step):
    valid = proposed > 0.0 and proposed >= 0.00020 and proposed <= 0.01000 and proposed >= 0.00030
    blockers = []
    if proposed <= 0.0:
        blockers.append("Proposed rib width is not positive.")
    if proposed < 0.00020:
        blockers.append("Proposed rib width is below absolute minimum.")
    if proposed < 0.00030:
        blockers.append("Proposed rib width is below manufacturing minimum.")
    if proposed > 0.01000:
        blockers.append("Proposed rib width is above maximum bound.")

    return {
        "proposal_id": f"RIB_WIDTH_MUTATION_PROPOSAL_{proposal_id:04d}",
        "source_blueprint_id": blueprint_id,
        "mutation_axis": "rib_width",
        "base_value_m": base,
        "proposed_value_m": proposed,
        "mutation_step_m": step,
        "proposal_state": "RIB_WIDTH_MUTATION_PROPOSAL_VALID_EXECUTION_LOCKED" if valid else "RIB_WIDTH_MUTATION_PROPOSAL_INVALID",
        "proposal_validation": {
            "valid": valid,
            "blockers": blockers,
            "positive_only": proposed > 0.0,
            "within_absolute_bounds": proposed >= 0.00020 and proposed <= 0.01000,
            "manufacturable": proposed >= 0.00030,
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
        "regen_channel_height_mutation_execution_allowed": "Channel height mutation execution is not safely locked.",
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
        return "PHASE 13E BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)
    history = foundation["rib_width_mutation_history"]
    return (
        "PHASE 13E REGEN RIB WIDTH MUTATION FOUNDATION\n"
        f"Status: {status}\n"
        f"Proposal Count: {history.get('proposal_count')}\n"
        f"Valid Proposals: {history.get('valid_proposal_count')}\n"
        "Real mutation execution remains locked.\n"
        "13F wall thickness mutation foundation may begin."
    )
