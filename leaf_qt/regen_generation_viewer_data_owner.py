OWNER_NAME = "REGEN_GENERATION_VIEWER_DATA_OWNER"
PHASE = "15A"

PASS_STATUS = "PASS_REGEN_GENERATION_VIEWER_DATA_OWNER_PHASE_15A"
FAIL_STATUS = "FAIL_REGEN_GENERATION_VIEWER_DATA_OWNER_PHASE_15A"


def attach_regen_generation_viewer_data_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_optimisation_viewer_data_owner_ready") is not True:
        blockers.append("Optimisation viewer data owner is not ready.")

    generation_history = results.get("runtime_generation_history", [])
    generation_population = results.get("runtime_generation_population", [])

    if not isinstance(generation_history, list):
        generation_history = []

    if not isinstance(generation_population, list):
        generation_population = []

    generations = _build_generations(results, generation_history, generation_population)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_generation_viewer_data_owner_complete": True,
        "phase_15a_generation_viewer_data_owner_complete": True,
        "regen_generation_viewer_data_owner_ready": ready,
        "regen_generation_viewer_data_owner_status": status,
        "regen_generation_viewer_data_owner_blockers": blockers,

        "optimisation_viewer_generations": generations if ready else [],
        "optimisation_viewer_generation_count": len(generations) if ready else 0,
    })

    return results


def _build_generations(results, generation_history, generation_population):
    generation_number = results.get("runtime_optimisation_final_generation")
    if generation_number is None:
        generation_number = results.get("runtime_generation_number", 0)

    return [
        {
            "generation_number": generation_number,
            "history_entries": generation_history,
            "population": generation_population,
            "population_count": len(generation_population),
            "best_score": results.get("runtime_optimisation_final_best_score"),
            "source": "PHASE_14_RUNTIME_BACKEND",
        }
    ]
