from regen_optimisation_selection_ranking_engine import (
    attach_regen_optimisation_selection_ranking_engine,
)
from regen_optimisation_selection_registry import (
    attach_regen_optimisation_selection_registry,
)
from regen_optimisation_selection_validation_owner import (
    attach_regen_optimisation_selection_validation_owner,
)
from regen_optimisation_selection_parent_pool_builder import (
    attach_regen_optimisation_selection_parent_pool_builder,
)
from regen_optimisation_selection_state_owner import (
    attach_regen_optimisation_selection_state_owner,
)
from regen_optimisation_selection_history_owner import (
    attach_regen_optimisation_selection_history_owner,
)
from regen_optimisation_selection_report_owner import (
    attach_regen_optimisation_selection_report_owner,
)
from regen_optimisation_selection_completion_audit import (
    attach_regen_optimisation_selection_completion_audit,
)
from regen_optimisation_selection_master_gate import (
    attach_regen_optimisation_selection_master_gate,
)


def build_seed():
    return {
        "phase_13k_optimisation_selection_framework_allowed": True,
        "regen_optimisation_selection_framework_allowed": True,
        "regen_evolution_engine_foundation_ready": True,

        "regen_generation_registry": {
            "ready": True,
            "current_generation": {
                "generation_id": "GENERATION_0000",
                "ready_for_selection": True,
            },
        },
        "regen_evolution_registry": {
            "ready": True,
            "current_generation_id": "GENERATION_0000",
        },

        "regen_candidate_improvement_validation_records": [
            {
                "candidate_id": "CANDIDATE_A",
                "improvement_validation": {
                    "valid": True,
                    "improved_from_parent": True,
                    "thermal_margin_improved": True,
                    "pressure_drop_acceptable": True,
                },
            },
            {
                "candidate_id": "CANDIDATE_B",
                "improvement_validation": {
                    "valid": True,
                    "improved_from_parent": False,
                    "thermal_margin_improved": True,
                    "pressure_drop_acceptable": True,
                },
            },
            {
                "candidate_id": "CANDIDATE_C",
                "improvement_validation": {
                    "valid": False,
                    "improved_from_parent": False,
                    "thermal_margin_improved": False,
                    "pressure_drop_acceptable": False,
                },
            },
        ],

        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
        "regen_generation_advance_execution_allowed": False,
        "regen_evolution_engine_execution_allowed": False,
        "regen_solver_execution_from_mutation_allowed": False,
    }


def run_pipeline(seed):
    results = dict(seed)

    for attach in (
        attach_regen_optimisation_selection_ranking_engine,
        attach_regen_optimisation_selection_registry,
        attach_regen_optimisation_selection_validation_owner,
        attach_regen_optimisation_selection_parent_pool_builder,
        attach_regen_optimisation_selection_state_owner,
        attach_regen_optimisation_selection_history_owner,
        attach_regen_optimisation_selection_report_owner,
        attach_regen_optimisation_selection_completion_audit,
        attach_regen_optimisation_selection_master_gate,
    ):
        results = attach(results)

    return results


def main():
    results = run_pipeline(build_seed())

    assert results["regen_optimisation_selection_ranking_engine_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_RANKING_ENGINE_PHASE_13K"
    )

    assert results["regen_optimisation_selection_registry_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_REGISTRY_PHASE_13K"
    )

    assert results["regen_optimisation_selection_validation_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_VALIDATION_OWNER_PHASE_13K"
    )

    assert results["regen_optimisation_selection_parent_pool_builder_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_PARENT_POOL_BUILDER_PHASE_13K"
    )

    assert results["regen_optimisation_selection_state_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_STATE_OWNER_PHASE_13K"
    )

    assert results["regen_optimisation_selection_history_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_HISTORY_OWNER_PHASE_13K"
    )

    assert results["regen_optimisation_selection_report_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_REPORT_OWNER_PHASE_13K"
    )

    assert results["regen_optimisation_selection_completion_audit_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K"
    )

    assert results["regen_optimisation_selection_master_gate_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_MASTER_GATE_PHASE_13K"
    )

    assert results["phase_13k_status"] == (
        "PASS_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K"
    )

    assert results["phase_13l_optimisation_foundation_allowed"] is True

    assert results["regen_optimisation_runtime_execution_allowed"] is False
    assert results["regen_generation_advance_execution_allowed"] is False
    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False

    best = results["regen_optimisation_selection_best_candidate"]
    assert best["candidate_id"] == "CANDIDATE_A"
    assert best["selection_rank"] == 1
    assert best["survives_generation"] is True

    parent_pool_ids = results["regen_optimisation_parent_pool_candidate_ids"]
    assert "CANDIDATE_A" in parent_pool_ids
    assert "CANDIDATE_C" not in parent_pool_ids

    print("PASS_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K")


if __name__ == "__main__":
    main()
