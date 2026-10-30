OWNER_NAME = "REGEN_EVOLUTION_TREE_PARENT_RELATIONSHIP_OWNER"
PHASE = "15C"

PASS_STATUS = "PASS_REGEN_EVOLUTION_TREE_PARENT_RELATIONSHIP_OWNER_PHASE_15C"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_TREE_PARENT_RELATIONSHIP_OWNER_PHASE_15C"


def attach_regen_evolution_tree_parent_relationship_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_evolution_tree_generation_lineage_owner_ready") is not True:
        blockers.append("Evolution tree generation lineage owner is not ready.")

    lineage = results.get("regen_runtime_parent_lineage", [])
    parent_pool = results.get("regen_runtime_parent_pool", [])

    if not isinstance(lineage, list):
        lineage = []

    if not isinstance(parent_pool, list):
        parent_pool = []

    links = []

    for index, item in enumerate(lineage):
        if not isinstance(item, dict):
            continue

        links.append({
            "parent_link_id": item.get(
                "runtime_parent_lineage_id",
                f"EVOLUTION_TREE_PARENT_LINK_15C_{index:04d}",
            ),
            "parent_runtime_candidate_id": item.get("parent_runtime_candidate_id"),
            "child_runtime_generation_candidate_id": item.get(
                "child_runtime_generation_candidate_id"
            ),
            "relationship": item.get("relationship", "PARENT_TO_CHILD"),
            "generation_number": item.get("generation_number"),
            "source": "regen_runtime_parent_lineage",
        })

    if not links:
        for index, item in enumerate(parent_pool):
            if not isinstance(item, dict):
                continue

            candidate_id = item.get("runtime_candidate_id")
            links.append({
                "parent_link_id": f"EVOLUTION_TREE_PARENT_POOL_LINK_15C_{index:04d}",
                "parent_runtime_candidate_id": candidate_id,
                "child_runtime_generation_candidate_id": None,
                "relationship": "PARENT_POOL_SURVIVOR",
                "generation_number": results.get("runtime_optimisation_final_generation"),
                "source": "regen_runtime_parent_pool",
            })

    if not links:
        blockers.append("No parent relationship links could be built.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_evolution_tree_parent_relationship_owner_complete": True,
        "phase_15c_evolution_tree_parent_relationship_owner_complete": True,
        "regen_evolution_tree_parent_relationship_owner_ready": ready,
        "regen_evolution_tree_parent_relationship_owner_status": status,
        "regen_evolution_tree_parent_relationship_owner_blockers": blockers,

        "evolution_tree_parent_links": links if ready else [],
        "evolution_tree_parent_link_count": len(links) if ready else 0,
    })

    return results
