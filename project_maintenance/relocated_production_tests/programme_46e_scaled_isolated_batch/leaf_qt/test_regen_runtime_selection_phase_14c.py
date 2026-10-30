from regen_runtime_selection_registry import attach_regen_runtime_selection_registry
from regen_runtime_selection_ranking_engine import attach_regen_runtime_selection_ranking_engine
from regen_runtime_selection_parent_pool_builder import attach_regen_runtime_selection_parent_pool_builder
from regen_runtime_selection_validation_owner import attach_regen_runtime_selection_validation_owner
from regen_runtime_selection_history_owner import attach_regen_runtime_selection_history_owner
from regen_runtime_selection_report_owner import attach_regen_runtime_selection_report_owner
from regen_runtime_selection_completion_audit import attach_regen_runtime_selection_completion_audit
from regen_runtime_selection_master_gate import attach_regen_runtime_selection_master_gate


def main():
    results = {
        "phase_14b_complete": True,
        "phase_14b_status": "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B",
        "phase_14c_runtime_selection_allowed": True,

        "regen_runtime_candidate_evaluation_records": [
            {
                "runtime_candidate_id": "RUNTIME_A",
                "candidate_score": 130.0,
                "evaluation_complete": True,
                "solver_executed": True,
            },
            {
                "runtime_candidate_id": "RUNTIME_B",
                "candidate_score": 110.0,
                "evaluation_complete": True,
                "solver_executed": True,
            },
            {
                "runtime_candidate_id": "RUNTIME_C",
                "candidate_score": 0.0,
                "evaluation_complete": True,
                "solver_executed": True,
            },
        ],

        "regen_generation_advance_execution_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }

    for attach in (
        attach_regen_runtime_selection_registry,
        attach_regen_runtime_selection_ranking_engine,
        attach_regen_runtime_selection_parent_pool_builder,
        attach_regen_runtime_selection_validation_owner,
        attach_regen_runtime_selection_history_owner,
        attach_regen_runtime_selection_report_owner,
        attach_regen_runtime_selection_completion_audit,
        attach_regen_runtime_selection_master_gate,
    ):
        results = attach(results)

    assert results["regen_runtime_selection_registry_status"] == (
        "PASS_REGEN_RUNTIME_SELECTION_REGISTRY_PHASE_14C"
    )
    assert results["regen_runtime_selection_ranking_engine_status"] == (
        "PASS_REGEN_RUNTIME_SELECTION_RANKING_ENGINE_PHASE_14C"
    )
    assert results["regen_runtime_selection_parent_pool_builder_status"] == (
        "PASS_REGEN_RUNTIME_SELECTION_PARENT_POOL_BUILDER_PHASE_14C"
    )
    assert results["regen_runtime_selection_validation_owner_status"] == (
        "PASS_REGEN_RUNTIME_SELECTION_VALIDATION_OWNER_PHASE_14C"
    )
    assert results["regen_runtime_selection_history_owner_status"] == (
        "PASS_REGEN_RUNTIME_SELECTION_HISTORY_OWNER_PHASE_14C"
    )
    assert results["regen_runtime_selection_report_owner_status"] == (
        "PASS_REGEN_RUNTIME_SELECTION_REPORT_OWNER_PHASE_14C"
    )
    assert results["regen_runtime_selection_completion_audit_status"] == (
        "PASS_REGEN_RUNTIME_SELECTION_PHASE_14C"
    )
    assert results["regen_runtime_selection_master_gate_status"] == (
        "PASS_REGEN_RUNTIME_SELECTION_MASTER_GATE_PHASE_14C"
    )

    assert results["phase_14c_status"] == "PASS_REGEN_RUNTIME_SELECTION_PHASE_14C"
    assert results["phase_14d_runtime_evolution_allowed"] is True
    assert results["phase_14_runtime_optimisation_allowed"] is False

    assert results["regen_runtime_selection_best_candidate"]["runtime_candidate_id"] == "RUNTIME_A"
    assert results["regen_runtime_parent_pool_candidate_ids"][0] == "RUNTIME_A"
    assert "RUNTIME_C" not in results["regen_runtime_parent_pool_candidate_ids"]

    assert results["regen_generation_advance_execution_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False

    print("PASS_REGEN_RUNTIME_SELECTION_PHASE_14C")


if __name__ == "__main__":
    main()
