from regen_unified_viewer_integration_registry import attach_regen_unified_viewer_integration_registry
from regen_unified_viewer_routing_owner import attach_regen_unified_viewer_routing_owner
from regen_unified_viewer_synchronisation_owner import attach_regen_unified_viewer_synchronisation_owner
from regen_unified_viewer_session_owner import attach_regen_unified_viewer_session_owner
from regen_unified_viewer_state_owner import attach_regen_unified_viewer_state_owner
from regen_unified_viewer_integration_completion_audit import attach_regen_unified_viewer_integration_completion_audit
from regen_unified_viewer_integration_master_gate import attach_regen_unified_viewer_integration_master_gate


def main():
    results = {
        "phase_16a_complete": True,
        "phase_16a_status": "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A",
        "phase_16b_viewer_integration_allowed": True,

        "unified_regen_registered_viewers": [
            {"viewer_id": "CROSS_SECTION_VIEWER", "backend_key": "regen_cross_section_viewer"},
            {"viewer_id": "STATION_VIEWER", "backend_key": "station_table"},
            {"viewer_id": "OPTIMISATION_VIEWER", "backend_key": "optimisation_viewer_backend_payload"},
            {"viewer_id": "CANDIDATE_COMPARISON_VIEWER", "backend_key": "candidate_comparison_summary"},
            {"viewer_id": "EVOLUTION_TREE_VIEWER", "backend_key": "evolution_tree_summary"},
            {"viewer_id": "OPTIMISATION_REPORT_VIEWER", "backend_key": "optimisation_report_backend_summary"},
        ],
    }

    for attach in (
        attach_regen_unified_viewer_integration_registry,
        attach_regen_unified_viewer_routing_owner,
        attach_regen_unified_viewer_synchronisation_owner,
        attach_regen_unified_viewer_session_owner,
        attach_regen_unified_viewer_state_owner,
        attach_regen_unified_viewer_integration_completion_audit,
        attach_regen_unified_viewer_integration_master_gate,
    ):
        results = attach(results)

    assert results["regen_unified_viewer_integration_registry_status"] == (
        "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_REGISTRY_PHASE_16B"
    )
    assert results["regen_unified_viewer_routing_owner_status"] == (
        "PASS_REGEN_UNIFIED_VIEWER_ROUTING_OWNER_PHASE_16B"
    )
    assert results["regen_unified_viewer_synchronisation_owner_status"] == (
        "PASS_REGEN_UNIFIED_VIEWER_SYNCHRONISATION_OWNER_PHASE_16B"
    )
    assert results["regen_unified_viewer_session_owner_status"] == (
        "PASS_REGEN_UNIFIED_VIEWER_SESSION_OWNER_PHASE_16B"
    )
    assert results["regen_unified_viewer_state_owner_status"] == (
        "PASS_REGEN_UNIFIED_VIEWER_STATE_OWNER_PHASE_16B"
    )
    assert results["regen_unified_viewer_integration_completion_audit_status"] == (
        "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B"
    )
    assert results["regen_unified_viewer_integration_master_gate_status"] == (
        "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_MASTER_GATE_PHASE_16B"
    )

    assert results["phase_16b_status"] == "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B"
    assert results["phase_16c_report_integration_allowed"] is True
    assert results["unified_regen_viewer_route_count"] == 6
    assert results["unified_regen_viewer_sync_link_count"] == 6
    assert results["unified_regen_viewer_session_active"] is True
    assert results["unified_regen_viewer_integration_ready"] is True
    assert results["unified_regen_viewer_qt_window_created"] is False
    assert results["unified_regen_viewer_rendering_performed"] is False

    print("PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B")


if __name__ == "__main__":
    main()
