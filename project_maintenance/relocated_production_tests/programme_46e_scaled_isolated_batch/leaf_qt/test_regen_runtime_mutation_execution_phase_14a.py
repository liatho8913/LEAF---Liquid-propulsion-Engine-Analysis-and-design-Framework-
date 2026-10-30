from regen_runtime_mutation_execution_registry import (
    attach_regen_runtime_mutation_execution_registry,
)
from regen_runtime_mutation_execution_engine import (
    attach_regen_runtime_mutation_execution_engine,
)
from regen_runtime_mutation_execution_validation_owner import (
    attach_regen_runtime_mutation_execution_validation_owner,
)
from regen_runtime_mutation_execution_history_owner import (
    attach_regen_runtime_mutation_execution_history_owner,
)
from regen_runtime_mutation_execution_report_owner import (
    attach_regen_runtime_mutation_execution_report_owner,
)
from regen_runtime_mutation_execution_completion_audit import (
    attach_regen_runtime_mutation_execution_completion_audit,
)
from regen_runtime_mutation_execution_master_gate import (
    attach_regen_runtime_mutation_execution_master_gate,
)


def build_seed():
    return {
        "phase_13l_complete": True,
        "regen_optimisation_foundation_complete": True,
        "phase_13l_status": "PASS_REGEN_OPTIMISATION_FOUNDATION_PHASE_13L",
        "phase_14a_runtime_mutation_execution_allowed": True,

        "regen_multi_variable_mutation_packages": [
            {
                "mutation_package_id": "MUTATION_PACKAGE_A",
                "parent_candidate_id": "CANDIDATE_A",
                "mutation_vector": {
                    "coolant_channel_count": 96,
                    "coolant_channel_width": 0.0012,
                    "coolant_channel_height": 0.0025,
                },
            },
            {
                "mutation_package_id": "MUTATION_PACKAGE_B",
                "parent_candidate_id": "CANDIDATE_B",
                "mutation_vector": {
                    "rib_width": 0.0008,
                    "wall_thickness": 0.0011,
                    "coolant_flow_fraction": 0.42,
                },
            },
        ],

        "regen_optimisation_runtime_execution_allowed": False,
        "regen_generation_advance_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def run_pipeline(seed):
    results = dict(seed)

    for attach in (
        attach_regen_runtime_mutation_execution_registry,
        attach_regen_runtime_mutation_execution_engine,
        attach_regen_runtime_mutation_execution_validation_owner,
        attach_regen_runtime_mutation_execution_history_owner,
        attach_regen_runtime_mutation_execution_report_owner,
        attach_regen_runtime_mutation_execution_completion_audit,
        attach_regen_runtime_mutation_execution_master_gate,
    ):
        results = attach(results)

    return results


def main():
    results = run_pipeline(build_seed())

    assert results["regen_runtime_mutation_execution_registry_status"] == (
        "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_REGISTRY_PHASE_14A"
    )

    assert results["regen_runtime_mutation_execution_engine_status"] == (
        "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_ENGINE_PHASE_14A"
    )

    assert results["regen_runtime_mutation_execution_validation_owner_status"] == (
        "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_VALIDATION_OWNER_PHASE_14A"
    )

    assert results["regen_runtime_mutation_execution_history_owner_status"] == (
        "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_HISTORY_OWNER_PHASE_14A"
    )

    assert results["regen_runtime_mutation_execution_report_owner_status"] == (
        "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_REPORT_OWNER_PHASE_14A"
    )

    assert results["regen_runtime_mutation_execution_completion_audit_status"] == (
        "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A"
    )

    assert results["regen_runtime_mutation_execution_master_gate_status"] == (
        "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_MASTER_GATE_PHASE_14A"
    )

    assert results["phase_14a_status"] == (
        "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A"
    )

    assert results["phase_14b_runtime_candidate_evaluation_allowed"] is True
    assert results["phase_14_runtime_optimisation_allowed"] is False

    assert results["regen_runtime_candidate_record_count"] == 2
    assert results["regen_runtime_mutation_execution_performed"] is True

    assert results["regen_runtime_mutation_solver_executed"] is False
    assert results["regen_runtime_mutation_candidate_evaluated"] is False
    assert results["regen_runtime_mutation_candidate_accepted"] is False
    assert results["regen_runtime_mutation_generation_advanced"] is False
    assert results["regen_runtime_mutation_live_geometry_committed"] is False

    print("PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A")


if __name__ == "__main__":
    main()
