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
    PASS_STATUS,
    attach_regen_optimisation_registration_owner,
)


def test_regen_optimisation_registration_owner():
    results = {
        "phase_11b_6f_regen_evolution_loop_master_gate_complete": True,
        "regen_evolution_loop_master_gate_ready": True,
    }

    results = attach_regen_autonomous_optimisation_input_audit(results)
    results = attach_regen_optimisation_session_owner(results)
    results = attach_regen_optimisation_report_owner(results)
    results = attach_regen_optimisation_registration_owner(results)

    registry = results["regen_optimisation_registry"]

    assert results["phase_11c_4_regen_optimisation_registration_owner_complete"] is True
    assert results["regen_optimisation_registration_owner_ready"] is True
    assert results["regen_optimisation_registration_owner_status"] == PASS_STATUS

    assert registry["registry_id"] == "OPT_REGISTRY_0001"
    assert registry["session_registry"]["session_count"] == 1
    assert registry["report_registry"]["report_count"] == 4
    assert registry["candidate_registry"]["candidate_count"] == 0

    assert registry["runtime_execution_enabled"] is False
    assert registry["live_geometry_commit_enabled"] is False

    assert results["phase_11c_5_optimisation_completion_audit_allowed"] is True
    assert results["regen_optimisation_runtime_execution_allowed"] is False


if __name__ == "__main__":
    test_regen_optimisation_registration_owner()
    print("PASS_REGEN_OPTIMISATION_REGISTRATION_OWNER_PHASE_11C4")
