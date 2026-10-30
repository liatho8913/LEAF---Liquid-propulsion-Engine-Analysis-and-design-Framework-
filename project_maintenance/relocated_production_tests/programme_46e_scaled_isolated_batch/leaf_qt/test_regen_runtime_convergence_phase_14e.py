from regen_runtime_convergence_registry import attach_regen_runtime_convergence_registry
from regen_runtime_improvement_tracking_engine import attach_regen_runtime_improvement_tracking_engine
from regen_runtime_stagnation_detection_engine import attach_regen_runtime_stagnation_detection_engine
from regen_runtime_convergence_detection_engine import attach_regen_runtime_convergence_detection_engine
from regen_runtime_stop_condition_engine import attach_regen_runtime_stop_condition_engine
from regen_runtime_convergence_validation_owner import attach_regen_runtime_convergence_validation_owner
from regen_runtime_convergence_history_owner import attach_regen_runtime_convergence_history_owner
from regen_runtime_convergence_report_owner import attach_regen_runtime_convergence_report_owner
from regen_runtime_convergence_completion_audit import attach_regen_runtime_convergence_completion_audit
from regen_runtime_convergence_master_gate import attach_regen_runtime_convergence_master_gate


def main():
    results = {
        "phase_14d_complete": True,
        "phase_14d_status": "PASS_REGEN_RUNTIME_EVOLUTION_PHASE_14D",
        "phase_14e_runtime_convergence_allowed": True,

        "runtime_generation_number": 1,
        "runtime_generation_advance_to": 1,
        "runtime_generation_history": [
            {"entry_id": "GEN_0_TO_1", "event": "GENERATION_ADVANCED"},
        ],

        "regen_runtime_parent_pool": [
            {"runtime_candidate_id": "RUNTIME_A", "runtime_selection_score": 130.0},
            {"runtime_candidate_id": "RUNTIME_B", "runtime_selection_score": 110.0},
        ],

        "runtime_previous_best_score": 120.0,
        "runtime_previous_stagnation_count": 0,
        "runtime_convergence_improvement_tolerance": 0.001,
        "runtime_stagnation_limit": 3,
        "runtime_max_generations": 50,

        "phase_14_runtime_optimisation_allowed": False,
    }

    for attach in (
        attach_regen_runtime_convergence_registry,
        attach_regen_runtime_improvement_tracking_engine,
        attach_regen_runtime_stagnation_detection_engine,
        attach_regen_runtime_convergence_detection_engine,
        attach_regen_runtime_stop_condition_engine,
        attach_regen_runtime_convergence_validation_owner,
        attach_regen_runtime_convergence_history_owner,
        attach_regen_runtime_convergence_report_owner,
        attach_regen_runtime_convergence_completion_audit,
        attach_regen_runtime_convergence_master_gate,
    ):
        results = attach(results)

    assert results["regen_runtime_convergence_registry_status"] == (
        "PASS_REGEN_RUNTIME_CONVERGENCE_REGISTRY_PHASE_14E"
    )
    assert results["regen_runtime_improvement_tracking_engine_status"] == (
        "PASS_REGEN_RUNTIME_IMPROVEMENT_TRACKING_ENGINE_PHASE_14E"
    )
    assert results["regen_runtime_stagnation_detection_engine_status"] == (
        "PASS_REGEN_RUNTIME_STAGNATION_DETECTION_ENGINE_PHASE_14E"
    )
    assert results["regen_runtime_convergence_detection_engine_status"] == (
        "PASS_REGEN_RUNTIME_CONVERGENCE_DETECTION_ENGINE_PHASE_14E"
    )
    assert results["regen_runtime_stop_condition_engine_status"] == (
        "PASS_REGEN_RUNTIME_STOP_CONDITION_ENGINE_PHASE_14E"
    )
    assert results["regen_runtime_convergence_validation_owner_status"] == (
        "PASS_REGEN_RUNTIME_CONVERGENCE_VALIDATION_OWNER_PHASE_14E"
    )
    assert results["regen_runtime_convergence_history_owner_status"] == (
        "PASS_REGEN_RUNTIME_CONVERGENCE_HISTORY_OWNER_PHASE_14E"
    )
    assert results["regen_runtime_convergence_report_owner_status"] == (
        "PASS_REGEN_RUNTIME_CONVERGENCE_REPORT_OWNER_PHASE_14E"
    )
    assert results["regen_runtime_convergence_completion_audit_status"] == (
        "PASS_REGEN_RUNTIME_CONVERGENCE_PHASE_14E"
    )
    assert results["regen_runtime_convergence_master_gate_status"] == (
        "PASS_REGEN_RUNTIME_CONVERGENCE_MASTER_GATE_PHASE_14E"
    )

    assert results["phase_14e_status"] == "PASS_REGEN_RUNTIME_CONVERGENCE_PHASE_14E"
    assert results["phase_14f_runtime_optimisation_audit_allowed"] is True

    assert results["runtime_current_best_score"] == 130.0
    assert results["runtime_generation_improvement"] == 10.0
    assert results["runtime_improvement_detected"] is True
    assert results["runtime_stop_condition_checked"] is True
    assert results["regen_runtime_optimisation_complete"] is False

    print("PASS_REGEN_RUNTIME_CONVERGENCE_PHASE_14E")


if __name__ == "__main__":
    main()
