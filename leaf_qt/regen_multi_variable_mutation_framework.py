OWNER_NAME = "REGEN_MULTI_VARIABLE_MUTATION_FRAMEWORK"
PHASE = "13H"
PASS_STATUS = "PASS_REGEN_MULTI_VARIABLE_MUTATION_FRAMEWORK_PHASE_13H"
FAIL_STATUS = "FAIL_REGEN_MULTI_VARIABLE_MUTATION_FRAMEWORK_PHASE_13H"

def attach_regen_multi_variable_mutation_framework(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_multi_variable_mutation_framework(results))
    return results

def build_regen_multi_variable_mutation_framework(results):
    blockers = []

    allowed = (
        results.get("phase_13h_multi_variable_mutation_framework_allowed") is True
        and results.get("regen_multi_variable_mutation_framework_allowed") is True
    )
    if not allowed:
        blockers.append("13G coolant split mutation foundation has not allowed multi-variable mutation.")

    coolant_foundation = results.get("regen_coolant_split_mutation_foundation", {})
    population = results.get("regen_candidate_blueprint_population", {})
    blueprints = results.get("regen_candidate_blueprints", [])

    required_proposal_keys = [
        "regen_channel_count_mutation_proposals",
        "regen_channel_width_mutation_proposals",
        "regen_channel_height_mutation_proposals",
        "regen_rib_width_mutation_proposals",
        "regen_wall_thickness_mutation_proposals",
        "regen_coolant_split_mutation_proposals",
    ]

    if not isinstance(coolant_foundation, dict) or coolant_foundation.get("ready") is not True:
        blockers.append("Coolant split mutation foundation is missing or not ready.")
    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")
    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("Candidate blueprints are missing.")

    for key in required_proposal_keys:
        proposals = results.get(key, [])
        if not isinstance(proposals, list) or not proposals:
            blockers.append(f"Missing mutation proposal list: {key}")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    framework = _build_framework(results, population, blueprints) if ready else None

    return {
        "regen_multi_variable_mutation_framework_complete": True,
        "phase_13h_regen_multi_variable_mutation_framework_complete": True,
        "regen_multi_variable_mutation_framework_ready": ready,
        "regen_multi_variable_mutation_framework_status": status,
        "regen_multi_variable_mutation_framework_blockers": blockers,

        "regen_multi_variable_mutation_framework": framework,
        "regen_multi_variable_mutation_registry": framework.get("multi_variable_mutation_registry") if framework else None,
        "regen_multi_variable_mutation_packages": framework.get("multi_variable_mutation_packages") if framework else [],
        "regen_multi_variable_mutation_history": framework.get("multi_variable_mutation_history") if framework else None,
        "regen_multi_variable_mutation_report": _report(status, ready, framework, blockers),

        "phase_13i_candidate_improvement_validation_allowed": ready,
        "regen_candidate_improvement_validation_allowed": ready,

        "regen_multi_variable_mutation_execution_allowed": False,
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

def _build_framework(results, population, blueprints):
    packages = []
    package_id = 1

    proposal_sets = {
        "channel_count": results.get("regen_channel_count_mutation_proposals", []),
        "channel_width": results.get("regen_channel_width_mutation_proposals", []),
        "channel_height": results.get("regen_channel_height_mutation_proposals", []),
        "rib_width": results.get("regen_rib_width_mutation_proposals", []),
        "wall_thickness": results.get("regen_wall_thickness_mutation_proposals", []),
        "coolant_split": results.get("regen_coolant_split_mutation_proposals", []),
    }

    for blueprint in blueprints:
        blueprint_id = blueprint.get("blueprint_id")
        package = _build_package_for_blueprint(package_id, blueprint_id, proposal_sets)
        packages.append(package)
        package_id += 1

    valid_count = len([p for p in packages if p["package_validation"]["valid"]])

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "multi_variable_mutation_registry_id": f"MULTI_VARIABLE_MUTATION_REGISTRY_FOR_{population.get('population_id')}",
        "source_population_id": population.get("population_id"),
        "mutation_axes": [
            "number_of_coolant_channels",
            "coolant_channel_width",
            "coolant_channel_height",
            "rib_width",
            "hot_gas_wall_thickness",
            "coolant_flow_fraction",
        ],
        "package_policy": {
            "one_package_per_blueprint": True,
            "valid_sub_proposals_required": True,
            "baseline_preservation_required": True,
            "execution_locked": True,
        },
        "permissions": {
            "candidate_improvement_validation_allowed": True,
            "multi_variable_mutation_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }

    history = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "history_state": "MULTI_VARIABLE_MUTATION_PACKAGES_CREATED_NO_EXECUTION",
        "package_count": len(packages),
        "valid_package_count": valid_count,
        "invalid_package_count": len(packages) - valid_count,
        "mutation_execution_count": 0,
        "solver_execution_count": 0,
        "live_commit_count": 0,
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "multi_variable_mutation_state": "MULTI_VARIABLE_MUTATION_FRAMEWORK_CREATED_EXECUTION_LOCKED",
        "multi_variable_mutation_registry": registry,
        "multi_variable_mutation_packages": packages,
        "multi_variable_mutation_history": history,
        "multi_variable_mutation_readiness": {
            "ready_for_candidate_improvement_validation": True,
            "ready_for_real_mutation_execution": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "13I_CANDIDATE_IMPROVEMENT_VALIDATION",
        },
    }

def _build_package_for_blueprint(package_id, blueprint_id, proposal_sets):
    selected = {}
    blockers = []

    axis_map = {
        "channel_count": "number_of_coolant_channels",
        "channel_width": "coolant_channel_width",
        "channel_height": "coolant_channel_height",
        "rib_width": "rib_width",
        "wall_thickness": "hot_gas_wall_thickness",
        "coolant_split": "coolant_flow_fraction",
    }

    for short_axis, proposal_list in proposal_sets.items():
        proposal = _select_first_valid_for_blueprint(proposal_list, blueprint_id)
        if proposal is None:
            blockers.append(f"No valid proposal found for {short_axis}.")
            continue
        selected[axis_map[short_axis]] = proposal

    valid = len(blockers) == 0 and len(selected) == len(axis_map)

    return {
        "package_id": f"MULTI_VARIABLE_MUTATION_PACKAGE_{package_id:04d}",
        "source_blueprint_id": blueprint_id,
        "mutation_axes": list(selected.keys()),
        "selected_proposals": selected,
        "package_state": (
            "MULTI_VARIABLE_MUTATION_PACKAGE_VALID_EXECUTION_LOCKED"
            if valid else
            "MULTI_VARIABLE_MUTATION_PACKAGE_INVALID"
        ),
        "package_validation": {
            "valid": valid,
            "blockers": blockers,
            "selected_axis_count": len(selected),
            "required_axis_count": len(axis_map),
            "all_required_axes_present": len(selected) == len(axis_map),
        },
        "execution_permissions": {
            "real_geometry_mutation_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }

def _select_first_valid_for_blueprint(proposals, blueprint_id):
    for proposal in proposals:
        if proposal.get("source_blueprint_id") != blueprint_id:
            continue
        validation = proposal.get("proposal_validation", {})
        if validation.get("valid") is True:
            return proposal
    return None

def _require_locked(results, blockers):
    required_false = {
        "regen_coolant_split_mutation_execution_allowed": "Coolant split mutation execution is not safely locked.",
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

def _report(status, ready, framework, blockers):
    if not ready:
        return "PHASE 13H BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)
    history = framework["multi_variable_mutation_history"]
    return (
        "PHASE 13H REGEN MULTI-VARIABLE MUTATION FRAMEWORK\n"
        f"Status: {status}\n"
        f"Package Count: {history.get('package_count')}\n"
        f"Valid Packages: {history.get('valid_package_count')}\n"
        "Real mutation execution remains locked.\n"
        "13I candidate improvement validation may begin."
    )
