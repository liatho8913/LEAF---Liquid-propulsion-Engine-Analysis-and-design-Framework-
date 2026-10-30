OWNER_NAME = "REGEN_RUNTIME_EVOLUTION_HISTORY_OWNER"
PHASE = "14D"

PASS_STATUS = "PASS_REGEN_RUNTIME_EVOLUTION_HISTORY_OWNER_PHASE_14D"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EVOLUTION_HISTORY_OWNER_PHASE_14D"


def attach_regen_runtime_evolution_history_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_evolution_validation_owner_ready") is not True:
        blockers.append("Runtime evolution validation owner is not ready.")

    advance = results.get("regen_runtime_generation_advance_record")
    population = results.get("regen_runtime_generation_population", [])
    lineage = results.get("regen_runtime_parent_lineage", [])

    if not isinstance(advance, dict):
        blockers.append("Runtime generation advance record is missing.")

    if not isinstance(population, list) or not population:
        blockers.append("Runtime generation population is missing.")

    if not isinstance(lineage, list) or not lineage:
        blockers.append("Runtime parent lineage is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None

    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "RUNTIME_GENERATION_ADVANCED_NO_CONVERGENCE",
            "runtime_generation_history": [
                {
                    "entry_id": "RUNTIME_EVOLUTION_HISTORY_14D_ADVANCE",
                    "event": "GENERATION_ADVANCED",
                    "from_generation": advance.get("from_generation"),
                    "to_generation": advance.get("to_generation"),
                },
                {
                    "entry_id": "RUNTIME_EVOLUTION_HISTORY_14D_POPULATION",
                    "event": "NEXT_GENERATION_POPULATION_CREATED",
                    "population_count": len(population),
                },
                {
                    "entry_id": "RUNTIME_EVOLUTION_HISTORY_14D_LINEAGE",
                    "event": "PARENT_LINEAGE_RECORDED",
                    "lineage_count": len(lineage),
                },
            ],
            "convergence_check_count": 0,
            "termination_check_count": 0,
            "live_geometry_commit_count": 0,
        }

    results.update({
        "regen_runtime_evolution_history_owner_complete": True,
        "phase_14d_runtime_evolution_history_owner_complete": True,
        "regen_runtime_evolution_history_owner_ready": ready,
        "regen_runtime_evolution_history_owner_status": status,
        "regen_runtime_evolution_history_owner_blockers": blockers,
        "regen_runtime_evolution_history": history,
        "runtime_generation_history": history.get("runtime_generation_history") if isinstance(history, dict) else [],
    })

    return results
