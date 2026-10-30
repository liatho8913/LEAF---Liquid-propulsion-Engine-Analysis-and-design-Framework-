OWNER_NAME = "REGEN_RUNTIME_EVOLUTION_REGISTRY"
PHASE = "14D"

PASS_STATUS = "PASS_REGEN_RUNTIME_EVOLUTION_REGISTRY_PHASE_14D"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EVOLUTION_REGISTRY_PHASE_14D"


def attach_regen_runtime_evolution_registry(results):
    if not isinstance(results, dict):
        return results

    parent_pool = results.get("regen_runtime_parent_pool", [])
    blockers = []

    allowed = results.get("phase_14d_runtime_evolution_allowed") is True
    phase_14c_complete = (
        results.get("phase_14c_complete") is True
        or results.get("phase_14c_status") == "PASS_REGEN_RUNTIME_SELECTION_PHASE_14C"
    )

    if not allowed:
        blockers.append("Phase 14D has not been unlocked by Phase 14C.")

    if not phase_14c_complete:
        blockers.append("Phase 14C runtime selection is not complete.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Runtime parent pool is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    current_generation = _current_generation(results)
    next_generation = current_generation + 1

    results.update({
        "regen_runtime_evolution_registry_complete": True,
        "phase_14d_runtime_evolution_registry_complete": True,
        "regen_runtime_evolution_registry_ready": ready,
        "regen_runtime_evolution_registry_status": status,
        "regen_runtime_evolution_registry_blockers": blockers,
        "regen_runtime_evolution_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "current_generation_number": current_generation,
            "next_generation_number": next_generation,
            "parent_pool_size": len(parent_pool) if isinstance(parent_pool, list) else 0,
            "generation_advance_allowed": ready,
            "generation_creation_allowed": ready,
            "population_carryover_allowed": ready,
            "convergence_detection_allowed": False,
            "termination_logic_allowed": False,
            "live_geometry_commit_allowed": False,
            "full_runtime_optimisation_allowed": False,
        } if ready else None,

        "runtime_generation_number": current_generation,
        "runtime_next_generation_number": next_generation,
    })

    return results


def _current_generation(results):
    for key in (
        "runtime_generation_number",
        "regen_runtime_generation_number",
        "current_runtime_generation_number",
    ):
        value = results.get(key)
        if isinstance(value, int) and value >= 0:
            return value

    return 0
