from regen_unified_validation_integration_registry import attach_regen_unified_validation_integration_registry
from regen_unified_validation_routing_owner import attach_regen_unified_validation_routing_owner
from regen_unified_validation_synchronisation_owner import attach_regen_unified_validation_synchronisation_owner
from regen_unified_validation_session_owner import attach_regen_unified_validation_session_owner
from regen_unified_validation_state_owner import attach_regen_unified_validation_state_owner
from regen_unified_validation_integration_completion_audit import attach_regen_unified_validation_integration_completion_audit
from regen_unified_validation_integration_master_gate import attach_regen_unified_validation_integration_master_gate


def main():
    results = {
        "phase_16c_complete": True,
        "phase_16c_status": "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C",
        "phase_16d_validation_integration_allowed": True,

        "unified_regen_registered_validations": [
            {"validation_id": "MATERIAL_VALIDATION", "source_key": "material_validation_pass"},
            {"validation_id": "COATING_VALIDATION", "source_key": "coating_validation_pass"},
            {"validation_id": "RUNTIME_CONVERGENCE_VALIDATION", "source_key": "regen_runtime_convergence_validation"},
            {"validation_id": "RUNTIME_OPTIMISATION_COMPLETION_VALIDATION", "source_key": "regen_runtime_optimisation_completion_validation"},
            {"validation_id": "OPTIMISATION_REPORT_BACKEND_AUDIT", "source_key": "regen_optimisation_report_backend_completion_audit_ready"},
        ],

        "unified_regen_validation_view_created": False,
    }

    for attach in (
        attach_regen_unified_validation_integration_registry,
        attach_regen_unified_validation_routing_owner,
        attach_regen_unified_validation_synchronisation_owner,
        attach_regen_unified_validation_session_owner,
        attach_regen_unified_validation_state_owner,
        attach_regen_unified_validation_integration_completion_audit,
        attach_regen_unified_validation_integration_master_gate,
    ):
        results = attach(results)

    assert results["regen_unified_validation_integration_registry_status"] == (
        "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_REGISTRY_PHASE_16D"
    )
    assert results["regen_unified_validation_routing_owner_status"] == (
        "PASS_REGEN_UNIFIED_VALIDATION_ROUTING_OWNER_PHASE_16D"
    )
    assert results["regen_unified_validation_synchronisation_owner_status"] == (
        "PASS_REGEN_UNIFIED_VALIDATION_SYNCHRONISATION_OWNER_PHASE_16D"
    )
    assert results["regen_unified_validation_session_owner_status"] == (
        "PASS_REGEN_UNIFIED_VALIDATION_SESSION_OWNER_PHASE_16D"
    )
    assert results["regen_unified_validation_state_owner_status"] == (
        "PASS_REGEN_UNIFIED_VALIDATION_STATE_OWNER_PHASE_16D"
    )
    assert results["regen_unified_validation_integration_completion_audit_status"] == (
        "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D"
    )
    assert results["regen_unified_validation_integration_master_gate_status"] == (
        "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_MASTER_GATE_PHASE_16D"
    )

    assert results["phase_16d_status"] == "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D"
    assert results["phase_16e_regen_signoff_allowed"] is True
    assert results["unified_regen_validation_route_count"] == 5
    assert results["unified_regen_validation_sync_link_count"] == 5
    assert results["unified_regen_validation_session_active"] is True
    assert results["unified_regen_validation_integration_ready"] is True
    assert results["unified_regen_validation_view_created"] is False
    assert results["unified_regen_validation_rendering_performed"] is False

    print("PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D")


if __name__ == "__main__":
    main()
