from regen_unified_report_integration_registry import attach_regen_unified_report_integration_registry
from regen_unified_report_routing_owner import attach_regen_unified_report_routing_owner
from regen_unified_report_synchronisation_owner import attach_regen_unified_report_synchronisation_owner
from regen_unified_report_session_owner import attach_regen_unified_report_session_owner
from regen_unified_report_state_owner import attach_regen_unified_report_state_owner
from regen_unified_report_integration_completion_audit import attach_regen_unified_report_integration_completion_audit
from regen_unified_report_integration_master_gate import attach_regen_unified_report_integration_master_gate


def main():
    results = {
        "phase_16b_complete": True,
        "phase_16b_status": "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B",
        "phase_16c_report_integration_allowed": True,

        "unified_regen_registered_reports": [
            {"report_id": "OPTIMISATION_VIEWER_REPORT", "source_key": "optimisation_viewer_backend_report"},
            {"report_id": "CANDIDATE_COMPARISON_REPORT", "source_key": "candidate_comparison_backend_report"},
            {"report_id": "EVOLUTION_TREE_REPORT", "source_key": "evolution_tree_report"},
            {"report_id": "OPTIMISATION_REPORT_BACKEND_REPORT", "source_key": "optimisation_report_backend_report"},
            {"report_id": "RUNTIME_OPTIMISATION_COMPLETION_REPORT", "source_key": "regen_runtime_optimisation_completion_report"},
            {"report_id": "RUNTIME_CONVERGENCE_REPORT", "source_key": "regen_runtime_convergence_report"},
        ],
    }

    for attach in (
        attach_regen_unified_report_integration_registry,
        attach_regen_unified_report_routing_owner,
        attach_regen_unified_report_synchronisation_owner,
        attach_regen_unified_report_session_owner,
        attach_regen_unified_report_state_owner,
        attach_regen_unified_report_integration_completion_audit,
        attach_regen_unified_report_integration_master_gate,
    ):
        results = attach(results)

    assert results["regen_unified_report_integration_registry_status"] == (
        "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_REGISTRY_PHASE_16C"
    )
    assert results["regen_unified_report_routing_owner_status"] == (
        "PASS_REGEN_UNIFIED_REPORT_ROUTING_OWNER_PHASE_16C"
    )
    assert results["regen_unified_report_synchronisation_owner_status"] == (
        "PASS_REGEN_UNIFIED_REPORT_SYNCHRONISATION_OWNER_PHASE_16C"
    )
    assert results["regen_unified_report_session_owner_status"] == (
        "PASS_REGEN_UNIFIED_REPORT_SESSION_OWNER_PHASE_16C"
    )
    assert results["regen_unified_report_state_owner_status"] == (
        "PASS_REGEN_UNIFIED_REPORT_STATE_OWNER_PHASE_16C"
    )
    assert results["regen_unified_report_integration_completion_audit_status"] == (
        "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C"
    )
    assert results["regen_unified_report_integration_master_gate_status"] == (
        "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_MASTER_GATE_PHASE_16C"
    )

    assert results["phase_16c_status"] == "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C"
    assert results["phase_16d_validation_integration_allowed"] is True
    assert results["unified_regen_report_route_count"] == 6
    assert results["unified_regen_report_sync_link_count"] == 6
    assert results["unified_regen_report_session_active"] is True
    assert results["unified_regen_report_integration_ready"] is True
    assert results["unified_regen_report_window_created"] is False
    assert results["unified_regen_report_rendering_performed"] is False
    assert results["unified_regen_report_export_performed"] is False

    print("PASS_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C")


if __name__ == "__main__":
    main()
