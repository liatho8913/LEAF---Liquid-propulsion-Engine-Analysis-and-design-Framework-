OWNER_NAME = "REGEN_EVOLUTION_TREE_HISTORY_OWNER"
PHASE = "15C"

PASS_STATUS = "PASS_REGEN_EVOLUTION_TREE_HISTORY_OWNER_PHASE_15C"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_TREE_HISTORY_OWNER_PHASE_15C"


def attach_regen_evolution_tree_history_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_evolution_tree_path_owner_ready") is not True:
        blockers.append("Evolution tree path owner is not ready.")

    summary = results.get("evolution_tree_summary")
    if not isinstance(summary, dict) or not summary:
        blockers.append("Evolution tree summary is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None
    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "EVOLUTION_TREE_BACKEND_ASSEMBLED",
            "entries": [
                {
                    "entry_id": "EVOLUTION_TREE_HISTORY_15C_GENERATIONS",
                    "event": "GENERATION_NODES_CREATED",
                    "count": summary.get("generation_count"),
                },
                {
                    "entry_id": "EVOLUTION_TREE_HISTORY_15C_PARENT_LINKS",
                    "event": "PARENT_LINKS_CREATED",
                    "count": summary.get("parent_link_count"),
                },
                {
                    "entry_id": "EVOLUTION_TREE_HISTORY_15C_MUTATION_LINKS",
                    "event": "MUTATION_LINKS_CREATED",
                    "count": summary.get("mutation_link_count"),
                },
                {
                    "entry_id": "EVOLUTION_TREE_HISTORY_15C_PATHS",
                    "event": "EVOLUTION_PATHS_CREATED",
                    "count": summary.get("path_count"),
                },
            ],
            "qt_tree_view_count": 0,
            "node_graph_render_count": 0,
        }

    results.update({
        "regen_evolution_tree_history_owner_complete": True,
        "phase_15c_evolution_tree_history_owner_complete": True,
        "regen_evolution_tree_history_owner_ready": ready,
        "regen_evolution_tree_history_owner_status": status,
        "regen_evolution_tree_history_owner_blockers": blockers,

        "evolution_tree_history": history if ready else {},
    })

    return results
