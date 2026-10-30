from regen_runtime_evolution_registry import attach_regen_runtime_evolution_registry
from regen_runtime_generation_advance_engine import attach_regen_runtime_generation_advance_engine
from regen_runtime_generation_creation_engine import attach_regen_runtime_generation_creation_engine
from regen_runtime_population_carryover_engine import attach_regen_runtime_population_carryover_engine
from regen_runtime_evolution_validation_owner import attach_regen_runtime_evolution_validation_owner
from regen_runtime_evolution_history_owner import attach_regen_runtime_evolution_history_owner
from regen_runtime_evolution_report_owner import attach_regen_runtime_evolution_report_owner
from regen_runtime_evolution_completion_audit import attach_regen_runtime_evolution_completion_audit
from regen_runtime_evolution_master_gate import attach_regen_runtime_evolution_master_gate


def main():
    results = {
        "phase_14c_complete": True,
        "phase_14c_status": "PASS_REGEN_RUNTIME_SELECTION_PHASE_14C",
        "phase_14d_runtime_evolution_allowed": True,

        "runtime_generation_number": 0,

        "regen_runtime_parent_pool": [
            {
                "runtime_candidate_id": "RUNTIME_A",
                "runtime_selection_rank": 1,
                "runtime_selection_score": 130.0,
            },
            {
                "runtime_candidate_id": "RUNTIME_B",
                "runtime_selection_rank": 2,
                "runtime_selection_score": 110.0,
            },
        ],

        "phase_14_runtime_optimisation_allowed": False,
    }

    for attach in (
        attach_regen_runtime_evolution_registry,
        attach_regen_runtime_generation_advance_engine,
        attach_regen_runtime_generation_creation_engine,
        attach_regen_runtime_population_carryover_engine,
        attach_regen_runtime_evolution_validation_owner,
        attach_regen_runtime_evolution_history_owner,
        attach_regen_runtime_evolution_report_owner,
        attach_regen_runtime_evolution_completion_audit,
        attach_regen_runtime_evolution_master_gate,
    ):
        results = attach(results)

    assert results["regen_runtime_evolution_registry_status"] == (
        "PASS_REGEN_RUNTIME_EVOLUTION_REGISTRY_PHASE_14D"
    )
    assert results["regen_runtime_generation_advance_engine_status"] == (
        "PASS_REGEN_RUNTIME_GENERATION_ADVANCE_ENGINE_PHASE_14D"
    )
    assert results["regen_runtime_generation_creation_engine_status"] == (
        "PASS_REGEN_RUNTIME_GENERATION_CREATION_ENGINE_PHASE_14D"
    )
    assert results["regen_runtime_population_carryover_engine_status"] == (
        "PASS_REGEN_RUNTIME_POPULATION_CARRYOVER_ENGINE_PHASE_14D"
    )
    assert results["regen_runtime_evolution_validation_owner_status"] == (
        "PASS_REGEN_RUNTIME_EVOLUTION_VALIDATION_OWNER_PHASE_14D"
    )
    assert results["regen_runtime_evolution_history_owner_status"] == (
        "PASS_REGEN_RUNTIME_EVOLUTION_HISTORY_OWNER_PHASE_14D"
    )
    assert results["regen_runtime_evolution_report_owner_status"] == (
        "PASS_REGEN_RUNTIME_EVOLUTION_REPORT_OWNER_PHASE_14D"
    )
    assert results["regen_runtime_evolution_completion_audit_status"] == (
        "PASS_REGEN_RUNTIME_EVOLUTION_PHASE_14D"
    )
    assert results["regen_runtime_evolution_master_gate_status"] == (
        "PASS_REGEN_RUNTIME_EVOLUTION_MASTER_GATE_PHASE_14D"
    )

    assert results["phase_14d_status"] == "PASS_REGEN_RUNTIME_EVOLUTION_PHASE_14D"
    assert results["phase_14e_runtime_convergence_allowed"] is True
    assert results["phase_14_runtime_optimisation_allowed"] is False

    assert results["runtime_generation_advanced"] is True
    assert results["runtime_generation_advance_from"] == 0
    assert results["runtime_generation_advance_to"] == 1
    assert results["regen_runtime_generation_population_count"] == 2
    assert results["regen_runtime_parent_lineage_count"] == 2

    assert results["regen_runtime_evolution_convergence_checked"] is False
    assert results["regen_runtime_evolution_termination_checked"] is False
    assert results["regen_runtime_evolution_live_geometry_committed"] is False

    print("PASS_REGEN_RUNTIME_EVOLUTION_PHASE_14D")


if __name__ == "__main__":
    main()
