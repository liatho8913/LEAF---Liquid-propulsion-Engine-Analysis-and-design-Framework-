from regen_evolution_tree_registry import attach_regen_evolution_tree_registry
from regen_evolution_tree_generation_lineage_owner import attach_regen_evolution_tree_generation_lineage_owner
from regen_evolution_tree_parent_relationship_owner import attach_regen_evolution_tree_parent_relationship_owner
from regen_evolution_tree_mutation_lineage_owner import attach_regen_evolution_tree_mutation_lineage_owner
from regen_evolution_tree_path_owner import attach_regen_evolution_tree_path_owner
from regen_evolution_tree_history_owner import attach_regen_evolution_tree_history_owner
from regen_evolution_tree_report_owner import attach_regen_evolution_tree_report_owner
from regen_evolution_tree_completion_audit import attach_regen_evolution_tree_completion_audit
from regen_evolution_tree_master_gate import attach_regen_evolution_tree_master_gate


def main():
    results = {
        "phase_15b_complete": True,
        "phase_15b_status": "PASS_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B",
        "phase_15c_evolution_tree_backend_allowed": True,

        "runtime_generation_history": [
            {
                "entry_id": "GEN_0_TO_1",
                "event": "GENERATION_ADVANCED",
                "from_generation": 0,
                "to_generation": 1,
            },
        ],
        "optimisation_viewer_generations": [
            {
                "generation_number": 0,
                "best_score": 100.0,
                "population_count": 2,
            },
            {
                "generation_number": 1,
                "best_score": 135.0,
                "population_count": 2,
            },
        ],

        "regen_runtime_parent_lineage": [
            {
                "runtime_parent_lineage_id": "LINEAGE_A",
                "parent_runtime_candidate_id": "BASELINE_A",
                "child_runtime_generation_candidate_id": "GEN_1_CANDIDATE_0000",
                "relationship": "PARENT_CARRYOVER_TO_NEXT_GENERATION",
                "generation_number": 1,
            },
        ],

        "regen_runtime_mutation_execution_records": [
            {
                "runtime_mutation_execution_id": "MUT_EXEC_A",
                "source_candidate_id": "BASELINE_A",
                "runtime_candidate_id": "BEST_C",
                "mutation_vector": {"coolant_channel_width": 0.0012},
            },
        ],

        "candidate_comparison_best": {
            "runtime_candidate_id": "BEST_C",
            "score": 135.0,
        },

        "evolution_tree_qt_viewer_created": False,
        "evolution_tree_node_graph_rendered": False,
        "evolution_tree_ui_widget_created": False,
    }

    for attach in (
        attach_regen_evolution_tree_registry,
        attach_regen_evolution_tree_generation_lineage_owner,
        attach_regen_evolution_tree_parent_relationship_owner,
        attach_regen_evolution_tree_mutation_lineage_owner,
        attach_regen_evolution_tree_path_owner,
        attach_regen_evolution_tree_history_owner,
        attach_regen_evolution_tree_report_owner,
        attach_regen_evolution_tree_completion_audit,
        attach_regen_evolution_tree_master_gate,
    ):
        results = attach(results)

    assert results["regen_evolution_tree_registry_status"] == (
        "PASS_REGEN_EVOLUTION_TREE_REGISTRY_PHASE_15C"
    )
    assert results["regen_evolution_tree_generation_lineage_owner_status"] == (
        "PASS_REGEN_EVOLUTION_TREE_GENERATION_LINEAGE_OWNER_PHASE_15C"
    )
    assert results["regen_evolution_tree_parent_relationship_owner_status"] == (
        "PASS_REGEN_EVOLUTION_TREE_PARENT_RELATIONSHIP_OWNER_PHASE_15C"
    )
    assert results["regen_evolution_tree_mutation_lineage_owner_status"] == (
        "PASS_REGEN_EVOLUTION_TREE_MUTATION_LINEAGE_OWNER_PHASE_15C"
    )
    assert results["regen_evolution_tree_path_owner_status"] == (
        "PASS_REGEN_EVOLUTION_TREE_PATH_OWNER_PHASE_15C"
    )
    assert results["regen_evolution_tree_history_owner_status"] == (
        "PASS_REGEN_EVOLUTION_TREE_HISTORY_OWNER_PHASE_15C"
    )
    assert results["regen_evolution_tree_report_owner_status"] == (
        "PASS_REGEN_EVOLUTION_TREE_REPORT_OWNER_PHASE_15C"
    )
    assert results["regen_evolution_tree_completion_audit_status"] == (
        "PASS_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C"
    )
    assert results["regen_evolution_tree_master_gate_status"] == (
        "PASS_REGEN_EVOLUTION_TREE_MASTER_GATE_PHASE_15C"
    )

    assert results["phase_15c_status"] == "PASS_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C"
    assert results["phase_15d_optimisation_report_backend_allowed"] is True

    assert results["evolution_tree_generation_count"] == 2
    assert results["evolution_tree_parent_link_count"] == 1
    assert results["evolution_tree_mutation_link_count"] == 1
    assert results["evolution_tree_path_count"] == 1
    assert results["evolution_tree_summary"]["best_candidate_id"] == "BEST_C"

    print("PASS_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C")


if __name__ == "__main__":
    main()
