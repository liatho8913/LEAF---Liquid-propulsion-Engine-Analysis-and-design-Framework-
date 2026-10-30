from regen_autonomous_optimisation_input_audit import (
    attach_regen_autonomous_optimisation_input_audit,
)
from regen_optimisation_session_owner import (
    attach_regen_optimisation_session_owner,
)
from regen_optimisation_report_owner import (
    attach_regen_optimisation_report_owner,
)
from regen_optimisation_registration_owner import (
    attach_regen_optimisation_registration_owner,
)
from regen_optimisation_completion_audit import (
    PASS_STATUS,
    attach_regen_optimisation_completion_audit,
)


def test_regen_optimisation_completion_audit():
    results = {
        "phase_11b_6f_regen_evolution_loop_master_gate_complete": True,
        "regen_evolution_loop_master_gate_ready": True,
    }

    results = attach_regen_autonomous_optimisation_input_audit(results)
    results = attach_regen_optimisation_session_owner(results)
    results = attach_regen_optimisation_report_owner(results)
    results = attach_regen_optimisation_registration_owner(results)
    results = attach_regen_optimisation_completion_audit(results)

    assert results["phase_11c_5_regen_optimisation_completion_audit_complete"] is True
    assert results["regen_optimisation_completion_audit_ready"] is True
    assert results["regen_optimisation_completion_audit_status"] == PASS_STATUS
    assert results["phase_11c_complete"] is True
    assert results["regen_optimisation_architecture_complete"] is True
    assert results["phase_11d_runtime_optimisation_architecture_allowed"] is True
    assert results["regen_runtime_optimisation_architecture_allowed"] is True
    assert results["regen_optimisation_runtime_execution_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


if __name__ == "__main__":
    test_regen_optimisation_completion_audit()
    print("PASS_REGEN_OPTIMISATION_COMPLETION_AUDIT_PHASE_11C5")
