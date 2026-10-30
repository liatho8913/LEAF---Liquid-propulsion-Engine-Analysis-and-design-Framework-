OWNER_NAME = "REGEN_EVOLUTION_TREE_GENERATION_LINEAGE_OWNER"
PHASE = "15C"

PASS_STATUS = "PASS_REGEN_EVOLUTION_TREE_GENERATION_LINEAGE_OWNER_PHASE_15C"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_TREE_GENERATION_LINEAGE_OWNER_PHASE_15C"


def attach_regen_evolution_tree_generation_lineage_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_evolution_tree_registry_ready") is not True:
        blockers.append("Evolution tree registry is not ready.")

    runtime_history = results.get("runtime_generation_history", [])
    optimisation_generations = results.get("optimisation_viewer_generations", [])

    if not isinstance(runtime_history, list):
        runtime_history = []

    if not isinstance(optimisation_generations, list):
        optimisation_generations = []

    generations = _build_generation_nodes(
        runtime_history=runtime_history,
        optimisation_generations=optimisation_generations,
        results=results,
    )

    if not generations:
        blockers.append("No evolution tree generation nodes could be built.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_evolution_tree_generation_lineage_owner_complete": True,
        "phase_15c_evolution_tree_generation_lineage_owner_complete": True,
        "regen_evolution_tree_generation_lineage_owner_ready": ready,
        "regen_evolution_tree_generation_lineage_owner_status": status,
        "regen_evolution_tree_generation_lineage_owner_blockers": blockers,

        "evolution_tree_generations": generations if ready else [],
        "evolution_tree_generation_count": len(generations) if ready else 0,
    })

    return results


def _build_generation_nodes(runtime_history, optimisation_generations, results):
    nodes = []

    seen = set()

    for item in optimisation_generations:
        if not isinstance(item, dict):
            continue

        number = item.get("generation_number")
        if number is None:
            number = item.get("runtime_generation_number")

        if number is None:
            continue

        key = f"GENERATION_{number}"
        if key in seen:
            continue

        seen.add(key)

        nodes.append({
            "generation_node_id": key,
            "generation_number": number,
            "best_score": item.get("best_score"),
            "population_count": item.get("population_count", 0),
            "source": "optimisation_viewer_generations",
        })

    for item in runtime_history:
        if not isinstance(item, dict):
            continue

        to_generation = item.get("to_generation")
        from_generation = item.get("from_generation")

        for number in (from_generation, to_generation):
            if number is None:
                continue

            key = f"GENERATION_{number}"
            if key in seen:
                continue

            seen.add(key)

            nodes.append({
                "generation_node_id": key,
                "generation_number": number,
                "best_score": results.get("runtime_optimisation_final_best_score"),
                "population_count": results.get("regen_runtime_generation_population_count", 0),
                "source": "runtime_generation_history",
            })

    if not nodes:
        number = results.get("runtime_optimisation_final_generation", 0)
        nodes.append({
            "generation_node_id": f"GENERATION_{number}",
            "generation_number": number,
            "best_score": results.get("runtime_optimisation_final_best_score"),
            "population_count": results.get("regen_runtime_generation_population_count", 0),
            "source": "fallback_runtime_state",
        })

    return sorted(nodes, key=lambda node: node.get("generation_number", 0))
