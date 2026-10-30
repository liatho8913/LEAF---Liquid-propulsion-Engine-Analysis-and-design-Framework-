OWNER_NAME = "REGEN_EVOLUTION_TREE_PATH_OWNER"
PHASE = "15C"

PASS_STATUS = "PASS_REGEN_EVOLUTION_TREE_PATH_OWNER_PHASE_15C"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_TREE_PATH_OWNER_PHASE_15C"


def attach_regen_evolution_tree_path_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_evolution_tree_mutation_lineage_owner_ready") is not True:
        blockers.append("Evolution tree mutation lineage owner is not ready.")

    generations = results.get("evolution_tree_generations", [])
    parent_links = results.get("evolution_tree_parent_links", [])
    mutation_links = results.get("evolution_tree_mutation_links", [])

    if not isinstance(generations, list) or not generations:
        blockers.append("Evolution tree generations are missing.")

    if not isinstance(parent_links, list) or not parent_links:
        blockers.append("Evolution tree parent links are missing.")

    if not isinstance(mutation_links, list) or not mutation_links:
        blockers.append("Evolution tree mutation links are missing.")

    paths = []

    if not blockers:
        generation_numbers = [g.get("generation_number") for g in generations]
        generation_numbers = [g for g in generation_numbers if g is not None]

        paths.append({
            "evolution_tree_path_id": "EVOLUTION_TREE_PATH_15C_PRIMARY",
            "generation_numbers": generation_numbers,
            "parent_link_count": len(parent_links),
            "mutation_link_count": len(mutation_links),
            "best_candidate_id": _best_candidate_id(results),
            "path_state": "BACKEND_ONLY_NO_TREE_RENDERING",
        })

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    summary = {
        "generation_count": len(generations) if isinstance(generations, list) else 0,
        "parent_link_count": len(parent_links) if isinstance(parent_links, list) else 0,
        "mutation_link_count": len(mutation_links) if isinstance(mutation_links, list) else 0,
        "path_count": len(paths),
        "best_candidate_id": _best_candidate_id(results),
    } if ready else {}

    results.update({
        "regen_evolution_tree_path_owner_complete": True,
        "phase_15c_evolution_tree_path_owner_complete": True,
        "regen_evolution_tree_path_owner_ready": ready,
        "regen_evolution_tree_path_owner_status": status,
        "regen_evolution_tree_path_owner_blockers": blockers,

        "evolution_tree_paths": paths if ready else [],
        "evolution_tree_path_count": len(paths) if ready else 0,
        "evolution_tree_summary": summary,
    })

    return results


def _best_candidate_id(results):
    best = results.get("candidate_comparison_best")
    if isinstance(best, dict):
        return best.get("runtime_candidate_id")

    best = results.get("regen_runtime_selection_best_candidate")
    if isinstance(best, dict):
        return best.get("runtime_candidate_id")

    return None
