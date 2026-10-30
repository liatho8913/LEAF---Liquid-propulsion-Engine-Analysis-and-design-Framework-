OWNER_NAME = "REGEN_EVOLUTION_TREE_COMPLETION_AUDIT"
PHASE = "15C"

PASS_STATUS = "PASS_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C"


def attach_regen_evolution_tree_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_evolution_tree_registry_ready": "Evolution tree registry is not ready.",
        "regen_evolution_tree_generation_lineage_owner_ready": "Generation lineage owner is not ready.",
        "regen_evolution_tree_parent_relationship_owner_ready": "Parent relationship owner is not ready.",
        "regen_evolution_tree_mutation_lineage_owner_ready": "Mutation lineage owner is not ready.",
        "regen_evolution_tree_path_owner_ready": "Evolution path owner is not ready.",
        "regen_evolution_tree_history_owner_ready": "Evolution tree history owner is not ready.",
        "regen_evolution_tree_report_owner_ready": "Evolution tree report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("evolution_tree_qt_viewer_created") is not False:
        blockers.append("Qt tree viewer was illegally created in 15C.")

    if results.get("evolution_tree_node_graph_rendered") is not False:
        blockers.append("Node graph was illegally rendered in 15C.")

    if results.get("evolution_tree_ui_widget_created") is not False:
        blockers.append("UI widget was illegally created in 15C.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_evolution_tree_completion_audit_complete": True,
        "phase_15c_evolution_tree_completion_audit_complete": True,
        "regen_evolution_tree_completion_audit_ready": ready,
        "regen_evolution_tree_completion_audit_status": status,
        "regen_evolution_tree_completion_audit_blockers": blockers,

        "phase_15c_complete": ready,
        "phase_15c_status": status,
        "phase_15d_optimisation_report_backend_allowed": ready,
    })

    return results
