OWNER_NAME = "REGEN_EVOLUTION_TREE_MUTATION_LINEAGE_OWNER"
PHASE = "15C"

PASS_STATUS = "PASS_REGEN_EVOLUTION_TREE_MUTATION_LINEAGE_OWNER_PHASE_15C"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_TREE_MUTATION_LINEAGE_OWNER_PHASE_15C"


def attach_regen_evolution_tree_mutation_lineage_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_evolution_tree_parent_relationship_owner_ready") is not True:
        blockers.append("Evolution tree parent relationship owner is not ready.")

    runtime_mutations = results.get("regen_runtime_mutation_execution_records", [])
    runtime_candidates = results.get("regen_runtime_candidate_records", [])

    if not isinstance(runtime_mutations, list):
        runtime_mutations = []

    if not isinstance(runtime_candidates, list):
        runtime_candidates = []

    links = []

    for index, item in enumerate(runtime_mutations):
        if not isinstance(item, dict):
            continue

        links.append({
            "mutation_link_id": f"EVOLUTION_TREE_MUTATION_LINK_15C_{index:04d}",
            "source_mutation_execution_id": item.get("runtime_mutation_execution_id"),
            "source_candidate_id": item.get("source_candidate_id"),
            "mutated_candidate_id": item.get("runtime_candidate_id") or item.get("candidate_id"),
            "mutation_vector": item.get("mutation_vector"),
            "source": "regen_runtime_mutation_execution_records",
        })

    if not links:
        for index, item in enumerate(runtime_candidates):
            if not isinstance(item, dict):
                continue

            links.append({
                "mutation_link_id": f"EVOLUTION_TREE_RUNTIME_CANDIDATE_LINK_15C_{index:04d}",
                "source_mutation_execution_id": item.get("runtime_mutation_execution_id"),
                "source_candidate_id": item.get("source_candidate_id"),
                "mutated_candidate_id": item.get("runtime_candidate_id") or item.get("candidate_id"),
                "mutation_vector": item.get("mutation_vector"),
                "source": "regen_runtime_candidate_records",
            })

    if not links:
        links.append({
            "mutation_link_id": "EVOLUTION_TREE_MUTATION_LINK_15C_PLACEHOLDER",
            "source_mutation_execution_id": None,
            "source_candidate_id": None,
            "mutated_candidate_id": None,
            "mutation_vector": {},
            "source": "no_runtime_mutation_records_available",
        })

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_evolution_tree_mutation_lineage_owner_complete": True,
        "phase_15c_evolution_tree_mutation_lineage_owner_complete": True,
        "regen_evolution_tree_mutation_lineage_owner_ready": ready,
        "regen_evolution_tree_mutation_lineage_owner_status": status,
        "regen_evolution_tree_mutation_lineage_owner_blockers": blockers,

        "evolution_tree_mutation_links": links if ready else [],
        "evolution_tree_mutation_link_count": len(links) if ready else 0,
    })

    return results
