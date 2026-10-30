OWNER_NAME = "REGEN_RUNTIME_GENERATION_ADVANCE_ENGINE"
PHASE = "14D"

PASS_STATUS = "PASS_REGEN_RUNTIME_GENERATION_ADVANCE_ENGINE_PHASE_14D"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_GENERATION_ADVANCE_ENGINE_PHASE_14D"


def attach_regen_runtime_generation_advance_engine(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    registry = results.get("regen_runtime_evolution_registry")

    if not isinstance(registry, dict) or registry.get("ready") is not True:
        blockers.append("Runtime evolution registry is not ready.")

    current_generation = results.get("runtime_generation_number", 0)
    next_generation = results.get("runtime_next_generation_number", current_generation + 1)

    if not isinstance(current_generation, int) or current_generation < 0:
        blockers.append("Current runtime generation number is invalid.")

    if not isinstance(next_generation, int) or next_generation <= current_generation:
        blockers.append("Next runtime generation number is invalid.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    advance_record = None

    if ready:
        advance_record = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "runtime_generation_advance_id": f"RUNTIME_GENERATION_ADVANCE_{current_generation}_TO_{next_generation}",
            "from_generation": current_generation,
            "to_generation": next_generation,
            "runtime_generation_advanced": True,
            "convergence_checked": False,
            "termination_checked": False,
            "live_geometry_committed": False,
        }

    results.update({
        "regen_runtime_generation_advance_engine_complete": True,
        "phase_14d_runtime_generation_advance_engine_complete": True,
        "regen_runtime_generation_advance_engine_ready": ready,
        "regen_runtime_generation_advance_engine_status": status,
        "regen_runtime_generation_advance_engine_blockers": blockers,
        "regen_runtime_generation_advance_record": advance_record,

        "runtime_generation_advanced": ready,
        "regen_runtime_generation_advanced": ready,
        "runtime_generation_advance_from": current_generation,
        "runtime_generation_advance_to": next_generation,

        "regen_runtime_evolution_convergence_checked": False,
        "regen_runtime_evolution_termination_checked": False,
        "regen_runtime_evolution_live_geometry_committed": False,
    })

    return results
