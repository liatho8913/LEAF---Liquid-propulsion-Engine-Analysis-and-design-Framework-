from regen_runtime_optimisation_completion_registry import (
    attach_regen_runtime_optimisation_completion_registry,
)
from regen_runtime_optimisation_completion_audit import (
    attach_regen_runtime_optimisation_completion_audit,
)
from regen_runtime_optimisation_completion_validation_owner import (
    attach_regen_runtime_optimisation_completion_validation_owner,
)
from regen_runtime_optimisation_completion_history_owner import (
    attach_regen_runtime_optimisation_completion_history_owner,
)
from regen_runtime_optimisation_completion_report_owner import (
    attach_regen_runtime_optimisation_completion_report_owner,
)
from regen_runtime_optimisation_completion_master_gate import (
    attach_regen_runtime_optimisation_completion_master_gate,
)


def main():
    results = {
        "phase_14e_complete": True,
        "phase_14e_status": "PASS_REGEN_RUNTIME_CONVERGENCE_PHASE_14E",
        "phase_14f_runtime_optimisation_audit_allowed": True,

        "runtime_stop_condition_checked": True,
        "runtime_stop_recommended": True,
        "runtime_convergence_detected": True,
        "runtime_max_generation_reached": False,
        "runtime_current_best_score": 130.0,
        "runtime_generation_advance_to": 4,

        "phase_14_runtime_optimisation_allowed": False,
    }

    for attach in (
        attach_regen_runtime_optimisation_completion_registry,
        attach_regen_runtime_optimisation_completion_audit,
        attach_regen_runtime_optimisation_completion_validation_owner,
        attach_regen_runtime_optimisation_completion_history_owner,
        attach_regen_runtime_optimisation_completion_report_owner,
        attach_regen_runtime_optimisation_completion_master_gate,
    ):
        results = attach(results)

    assert results["regen_runtime_optimisation_completion_registry_status"] == (
        "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_REGISTRY_PHASE_14F"
    )
    assert results["regen_runtime_optimisation_completion_audit_status"] == (
        "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_AUDIT_PHASE_14F"
    )
    assert results["regen_runtime_optimisation_completion_validation_owner_status"] == (
        "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_VALIDATION_OWNER_PHASE_14F"
    )
    assert results["regen_runtime_optimisation_completion_history_owner_status"] == (
        "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_HISTORY_OWNER_PHASE_14F"
    )
    assert results["regen_runtime_optimisation_completion_report_owner_status"] == (
        "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_REPORT_OWNER_PHASE_14F"
    )
    assert results["regen_runtime_optimisation_completion_master_gate_status"] == (
        "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_PHASE_14F"
    )

    assert results["phase_14f_status"] == "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_PHASE_14F"
    assert results["phase_14_runtime_backend_complete"] is True
    assert results["regen_runtime_optimisation_backend_complete"] is True
    assert results["regen_runtime_optimisation_complete"] is True
    assert results["phase_15a_optimisation_viewer_backend_allowed"] is True
    assert results["regen_runtime_final_live_geometry_committed"] is False

    print("PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_PHASE_14F")


if __name__ == "__main__":
    main()
