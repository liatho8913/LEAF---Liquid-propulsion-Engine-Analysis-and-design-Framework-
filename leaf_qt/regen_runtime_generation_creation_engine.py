OWNER_NAME = "REGEN_RUNTIME_GENERATION_CREATION_ENGINE"
PHASE = "14D"

PASS_STATUS = "PASS_REGEN_RUNTIME_GENERATION_CREATION_ENGINE_PHASE_14D"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_GENERATION_CREATION_ENGINE_PHASE_14D"


def attach_regen_runtime_generation_creation_engine(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    advance_record = results.get("regen_runtime_generation_advance_record")
    parent_pool = results.get("regen_runtime_parent_pool", [])

    if not isinstance(advance_record, dict) or advance_record.get("runtime_generation_advanced") is not True:
        blockers.append("Runtime generation advance record is missing or not advanced.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Runtime parent pool is missing.")

    next_generation = results.get("runtime_generation_advance_to")

    if not isinstance(next_generation, int):
        blockers.append("Next runtime generation number is missing.")

    population = []

    if isinstance(parent_pool, list):
        for index, parent in enumerate(parent_pool):
            if not isinstance(parent, dict):
                blockers.append(f"Parent pool item at index {index} is not a dictionary.")
                continue

            parent_id = parent.get("runtime_candidate_id") or f"RUNTIME_PARENT_{index:04d}"

            population.append({
                "runtime_generation_candidate_id": f"GEN_{next_generation}_CANDIDATE_{index:04d}",
                "source_parent_runtime_candidate_id": parent_id,
                "runtime_generation_number": next_generation,
                "lineage_role": "PARENT_CARRYOVER",
                "source_parent": parent,
                "mutation_required_next": True,
                "evaluated": False,
                "selected": False,
                "accepted": False,
                "live_geometry_committed": False,
            })

    if not population:
        blockers.append("No runtime generation population was created.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    generation = None

    if ready:
        generation = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "runtime_generation_id": f"RUNTIME_GENERATION_{next_generation}",
            "runtime_generation_number": next_generation,
            "source_parent_pool_size": len(parent_pool),
            "population_size": len(population),
            "population": population,
            "convergence_detection_allowed": False,
            "termination_logic_allowed": False,
            "live_geometry_commit_allowed": False,
        }

    results.update({
        "regen_runtime_generation_creation_engine_complete": True,
        "phase_14d_runtime_generation_creation_engine_complete": True,
        "regen_runtime_generation_creation_engine_ready": ready,
        "regen_runtime_generation_creation_engine_status": status,
        "regen_runtime_generation_creation_engine_blockers": blockers,

        "regen_runtime_generation": generation,
        "regen_runtime_generation_population": population if ready else [],
        "regen_runtime_generation_population_count": len(population) if ready else 0,
        "runtime_generation_population": population if ready else [],
    })

    return results
