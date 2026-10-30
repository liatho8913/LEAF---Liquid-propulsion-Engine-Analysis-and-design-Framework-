from regen_runtime_candidate_evaluation_registry import (
    attach_regen_runtime_candidate_evaluation_registry,
)
from regen_runtime_candidate_evaluation_engine import (
    attach_regen_runtime_candidate_evaluation_engine,
)
from regen_runtime_candidate_evaluation_validation_owner import (
    attach_regen_runtime_candidate_evaluation_validation_owner,
)
from regen_runtime_candidate_evaluation_history_owner import (
    attach_regen_runtime_candidate_evaluation_history_owner,
)
from regen_runtime_candidate_evaluation_report_owner import (
    attach_regen_runtime_candidate_evaluation_report_owner,
)
from regen_runtime_candidate_evaluation_completion_audit import (
    attach_regen_runtime_candidate_evaluation_completion_audit,
)
from regen_runtime_candidate_evaluation_master_gate import (
    attach_regen_runtime_candidate_evaluation_master_gate,
)


def main():
    results = {
        "phase_14a_complete": True,
        "phase_14a_status": "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A",
        "phase_14b_runtime_candidate_evaluation_allowed": True,

        "regen_runtime_candidate_records": [
            {
                "runtime_candidate_id": "RUNTIME_A",
                "runtime_mutation_execution_id": "MUT_EXEC_A",
                "mutation_vector": {
                    "coolant_channel_count": 96,
                    "coolant_channel_width": 0.0012,
                    "coolant_channel_height": 0.0025,
                },
            },
            {
                "runtime_candidate_id": "RUNTIME_B",
                "runtime_mutation_execution_id": "MUT_EXEC_B",
                "mutation_vector": {
                    "wall_thickness": 0.0011,
                    "coolant_channel_width": 0.0015,
                },
            },
        ],

        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_generation_advance_execution_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }

    for attach in (
        attach_regen_runtime_candidate_evaluation_registry,
        attach_regen_runtime_candidate_evaluation_engine,
        attach_regen_runtime_candidate_evaluation_validation_owner,
        attach_regen_runtime_candidate_evaluation_history_owner,
        attach_regen_runtime_candidate_evaluation_report_owner,
        attach_regen_runtime_candidate_evaluation_completion_audit,
        attach_regen_runtime_candidate_evaluation_master_gate,
    ):
        results = attach(results)

    assert results["regen_runtime_candidate_evaluation_registry_status"] == (
        "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_REGISTRY_PHASE_14B"
    )
    assert results["regen_runtime_candidate_evaluation_engine_status"] == (
        "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_ENGINE_PHASE_14B"
    )
    assert results["regen_runtime_candidate_evaluation_validation_owner_status"] == (
        "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_VALIDATION_OWNER_PHASE_14B"
    )
    assert results["regen_runtime_candidate_evaluation_history_owner_status"] == (
        "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_HISTORY_OWNER_PHASE_14B"
    )
    assert results["regen_runtime_candidate_evaluation_report_owner_status"] == (
        "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_REPORT_OWNER_PHASE_14B"
    )
    assert results["regen_runtime_candidate_evaluation_completion_audit_status"] == (
        "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B"
    )
    assert results["regen_runtime_candidate_evaluation_master_gate_status"] == (
        "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_MASTER_GATE_PHASE_14B"
    )

    assert results["phase_14b_status"] == (
        "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B"
    )
    assert results["phase_14c_runtime_selection_allowed"] is True
    assert results["phase_14_runtime_optimisation_allowed"] is False

    assert results["regen_runtime_candidate_evaluation_record_count"] == 2
    assert results["regen_runtime_candidate_solver_executed"] is True

    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_generation_advance_execution_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False

    print("PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B")


if __name__ == "__main__":
    main()
