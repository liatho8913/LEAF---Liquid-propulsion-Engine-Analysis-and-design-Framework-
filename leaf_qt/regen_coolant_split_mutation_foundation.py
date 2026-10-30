OWNER_NAME = "REGEN_COOLANT_SPLIT_MUTATION_FOUNDATION"
PHASE = "13G"
PASS_STATUS = "PASS_REGEN_COOLANT_SPLIT_MUTATION_FOUNDATION_PHASE_13G"
FAIL_STATUS = "FAIL_REGEN_COOLANT_SPLIT_MUTATION_FOUNDATION_PHASE_13G"

def attach_regen_coolant_split_mutation_foundation(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_coolant_split_mutation_foundation(results))
    return results

def build_regen_coolant_split_mutation_foundation(results):
    blockers = []

    allowed = (
        results.get("phase_13g_coolant_split_mutation_allowed") is True
        and results.get("regen_coolant_split_mutation_allowed") is True
    )
    if not allowed:
        blockers.append("13F wall thickness mutation foundation has not allowed coolant split mutation.")

    wall_foundation = results.get("regen_wall_thickness_mutation_foundation", {})
    population = results.get("regen_candidate_blueprint_population", {})
    blueprints = results.get("regen_candidate_blueprints", [])

    if not isinstance(wall_foundation, dict) or wall_foundation.get("ready") is not True:
        blockers.append("Wall thickness mutation foundation is missing or not ready.")
    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")
    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("Candidate blueprints are missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    foundation = _build_foundation(population, blueprints) if ready else None

    return {
        "regen_coolant_split_mutation_foundation_complete": True,
        "phase_13g_regen_coolant_split_mutation_foundation_complete": True,
        "regen_coolant_split_mutation_foundation_ready": ready,
        "regen_coolant_split_mutation_foundation_status": status,
        "regen_coolant_split_mutation_foundation_blockers": blockers,
        "regen_coolant_split_mutation_foundation": foundation,
        "regen_coolant_split_mutation_registry": foundation.get("coolant_split_mutation_registry") if foundation else None,
        "regen_coolant_split_mutation_proposals": foundation.get("coolant_split_mutation_proposals") if foundation else [],
        "regen_coolant_split_mutation_history": foundation.get("coolant_split_mutation_history") if foundation else None,
        "regen_coolant_split_mutation_report": _report(status, ready, foundation, blockers),
        "phase_13h_multi_variable_mutation_framework_allowed": ready,
        "regen_multi_variable_mutation_framework_allowed": ready,
        "regen_coolant_split_mutation_execution_allowed": False,
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
        base = _float(dims.get("coolant_flow_fraction"), 1.0)

        for step in [-0.10, -0.05, 0.05, 0.10]:
            proposed = base + step
            proposals.append(_proposal(proposal_id, blueprint_id, base, proposed, step))
            proposal_id += 1

    valid_count = len([p for p in proposals if p["proposal_validation"]["valid"]])

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "coolant_split_mutation_registry_id": f"COOLANT_SPLIT_MUTATION_REGISTRY_FOR_{population.get('population_id')}",
        "source_population_id": population.get("population_id"),
        "mutation_axis": "coolant_flow_fraction",
        "registered_steps_fraction": [-0.10, -0.05, 0.05, 0.10],
        "bounds": {
            "minimum_coolant_flow_fraction": 0.10,
            "maximum_coolant_flow_fraction": 1.00,
            "recommended_minimum_fraction": 0.25,
            "recommended_maximum_fraction": 1.00,
        },
        "permissions": {
            "multi_variable_mutation_framework_allowed": True,
            "coolant_split_mutation_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }

    history = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "history_state": "COOLANT_SPLIT_MUTATION_PROPOSALS_CREATED_NO_EXECUTION",
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
        "coolant_split_mutation_state": "COOLANT_SPLIT_MUTATION_FOUNDATION_CREATED_EXECUTION_LOCKED",
        "coolant_split_mutation_registry": registry,
        "coolant_split_mutation_proposals": proposals,
        "coolant_split_mutation_history": history,
        "coolant_split_mutation_readiness": {
            "ready_for_multi_variable_mutation_framework": True,
            "ready_for_real_mutation_execution": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "13H_MULTI_VARIABLE_MUTATION_FRAMEWORK",
        },
    }

def _proposal(proposal_id, blueprint_id, base, proposed, step):
    valid = proposed >= 0.10 and proposed <= 1.00
    blockers = []
    if proposed < 0.10:
        blockers.append("Proposed coolant flow fraction is below minimum.")
    if proposed > 1.00:
        blockers.append("Proposed coolant flow fraction is above maximum.")

    return {
        "proposal_id": f"COOLANT_SPLIT_MUTATION_PROPOSAL_{proposal_id:04d}",
        "source_blueprint_id": blueprint_id,
        "mutation_axis": "coolant_flow_fraction",
        "base_value_fraction": base,
        "proposed_value_fraction": proposed,
        "mutation_step_fraction": step,
        "proposal_state": "COOLANT_SPLIT_MUTATION_PROPOSAL_VALID_EXECUTION_LOCKED" if valid else "COOLANT_SPLIT_MUTATION_PROPOSAL_INVALID",
        "proposal_validation": {
            "valid": valid,
            "blockers": blockers,
            "within_bounds": proposed >= 0.10 and proposed <= 1.00,
            "below_or_equal_total_available_flow": proposed <= 1.00,
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
        "regen_wall_thickness_mutation_execution_allowed": "Wall thickness mutation execution is not safely locked.",
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
        return "PHASE 13G BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)
    history = foundation["coolant_split_mutation_history"]
    return (
        "PHASE 13G REGEN COOLANT SPLIT MUTATION FOUNDATION\n"
        f"Status: {status}\n"
        f"Proposal Count: {history.get('proposal_count')}\n"
        f"Valid Proposals: {history.get('valid_proposal_count')}\n"
        "Real mutation execution remains locked.\n"
        "13H multi-variable mutation framework may begin."
    )
