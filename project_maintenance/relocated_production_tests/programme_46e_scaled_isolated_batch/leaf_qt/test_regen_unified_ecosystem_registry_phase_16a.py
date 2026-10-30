from regen_unified_ecosystem_registry import attach_regen_unified_ecosystem_registry
from regen_unified_viewer_registration_owner import attach_regen_unified_viewer_registration_owner
from regen_unified_report_registration_owner import attach_regen_unified_report_registration_owner
from regen_unified_validation_registration_owner import attach_regen_unified_validation_registration_owner
from regen_unified_ecosystem_state_owner import attach_regen_unified_ecosystem_state_owner
from regen_unified_ecosystem_completion_audit import attach_regen_unified_ecosystem_completion_audit
from regen_unified_ecosystem_master_gate import attach_regen_unified_ecosystem_master_gate


def main():
    results = {
        "phase_15d_complete": True,
        "phase_15d_status": "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D",
        "phase_16_unified_regen_ecosystem_allowed": True,

        "phase_14_runtime_backend_complete": True,
        "phase_15a_complete": True,
        "phase_15b_complete": True,
        "phase_15c_complete": True,

        "optimisation_viewer_backend_payload": {},
        "candidate_comparison_summary": {},
        "evolution_tree_summary": {},
        "optimisation_report_backend_summary": {},

        "optimisation_viewer_backend_report": "viewer report",
        "candidate_comparison_backend_report": "comparison report",
        "evolution_tree_report": "tree report",
        "optimisation_report_backend_report": "optimisation report",
        "regen_runtime_optimisation_completion_report": "completion report",
        "regen_runtime_convergence_report": "convergence report",

        "material_validation_pass": True,
        "coating_validation_pass": True,
        "regen_runtime_convergence_validation": {},
        "regen_runtime_optimisation_completion_validation": {},
        "regen_optimisation_report_backend_completion_audit_ready": True,
    }

    for attach in (
        attach_regen_unified_ecosystem_registry,
        attach_regen_unified_viewer_registration_owner,
        attach_regen_unified_report_registration_owner,
        attach_regen_unified_validation_registration_owner,
        attach_regen_unified_ecosystem_state_owner,
        attach_regen_unified_ecosystem_completion_audit,
        attach_regen_unified_ecosystem_master_gate,
    ):
        results = attach(results)

    assert results["regen_unified_ecosystem_registry_status"] == (
        "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"
    )
    assert results["regen_unified_viewer_registration_owner_status"] == (
        "PASS_REGEN_UNIFIED_VIEWER_REGISTRATION_OWNER_PHASE_16A"
    )
    assert results["regen_unified_report_registration_owner_status"] == (
        "PASS_REGEN_UNIFIED_REPORT_REGISTRATION_OWNER_PHASE_16A"
    )
    assert results["regen_unified_validation_registration_owner_status"] == (
        "PASS_REGEN_UNIFIED_VALIDATION_REGISTRATION_OWNER_PHASE_16A"
    )
    assert results["regen_unified_ecosystem_state_owner_status"] == (
        "PASS_REGEN_UNIFIED_ECOSYSTEM_STATE_OWNER_PHASE_16A"
    )
    assert results["regen_unified_ecosystem_completion_audit_status"] == (
        "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"
    )
    assert results["regen_unified_ecosystem_master_gate_status"] == (
        "PASS_REGEN_UNIFIED_ECOSYSTEM_MASTER_GATE_PHASE_16A"
    )

    assert results["phase_16a_status"] == "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"
    assert results["phase_16b_viewer_integration_allowed"] is True
    assert results["unified_regen_registered_viewer_count"] == 6
    assert results["unified_regen_registered_report_count"] == 6
    assert results["unified_regen_registered_validation_count"] == 5
    assert results["unified_regen_qt_windows_created"] is False

    print("PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A")


if __name__ == "__main__":
    main()
