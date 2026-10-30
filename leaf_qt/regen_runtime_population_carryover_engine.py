OWNER_NAME = "REGEN_RUNTIME_POPULATION_CARRYOVER_ENGINE"
PHASE = "14D"

PASS_STATUS = "PASS_REGEN_RUNTIME_POPULATION_CARRYOVER_ENGINE_PHASE_14D"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_POPULATION_CARRYOVER_ENGINE_PHASE_14D"


def attach_regen_runtime_population_carryover_engine(results):
    if not isinstance(results, dict):
        return results

    population = results.get("regen_runtime_generation_population", [])
    parent_pool = results.get("regen_runtime_parent_pool", [])
    blockers = []

    if results.get("regen_runtime_generation_creation_engine_ready") is not True:
        blockers.append("Runtime generation creation engine is not ready.")

    if not isinstance(population, list) or not population:
        blockers.append("Runtime generation population is missing.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Runtime parent pool is missing.")

    lineage = []

    if isinstance(population, list):
        for index, item in enumerate(population):
            if not isinstance(item, dict):
                blockers.append(f"Population item at index {index} is not a dictionary.")
                continue

            parent_id = item.get("source_parent_runtime_candidate_id")
            child_id = item.get("runtime_generation_candidate_id")

            if not parent_id or not child_id:
                blockers.append(f"Population lineage item at index {index} is missing IDs.")
                continue

            lineage.append({
                "runtime_parent_lineage_id": f"RUNTIME_PARENT_LINEAGE_14D_{index:04d}",
                "parent_runtime_candidate_id": parent_id,
                "child_runtime_generation_candidate_id": child_id,
                "relationship": "PARENT_CARRYOVER_TO_NEXT_GENERATION",
                "generation_number": item.get("runtime_generation_number"),
            })

    if not lineage:
        blockers.append("Runtime parent lineage was not created.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_population_carryover_engine_complete": True,
        "phase_14d_runtime_population_carryover_engine_complete": True,
        "regen_runtime_population_carryover_engine_ready": ready,
        "regen_runtime_population_carryover_engine_status": status,
        "regen_runtime_population_carryover_engine_blockers": blockers,

        "runtime_parent_lineage": lineage if ready else [],
        "regen_runtime_parent_lineage": lineage if ready else [],
        "regen_runtime_parent_lineage_count": len(lineage) if ready else 0,
    })

    return results
