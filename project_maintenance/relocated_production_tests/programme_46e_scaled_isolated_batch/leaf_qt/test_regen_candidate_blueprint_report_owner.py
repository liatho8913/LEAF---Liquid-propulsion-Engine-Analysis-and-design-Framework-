from project_maintenance.production_historical_artifacts.leaf_qt.regen_candidate_blueprint_generation_input_gate import attach_regen_candidate_blueprint_generation_input_gate
from regen_candidate_blueprint_session_owner import attach_regen_candidate_blueprint_session_owner
from regen_candidate_blueprint_registration_owner import attach_regen_candidate_blueprint_registration_owner
from regen_candidate_blueprint_report_owner import (
    PASS_STATUS,
    attach_regen_candidate_blueprint_report_owner,
)


def build_ready_12a3_results():
    results = {
        "phase_11g_complete": True,
        "regen_candidate_creation_architecture_complete": True,
        "phase_12a_candidate_blueprint_generation_allowed": True,
        "regen_candidate_blueprint_generation_allowed": True,

        "regen_candidate_creation_completion_audit": {"complete": True},
        "regen_candidate_creation_registry": {
            "candidate_creation_registry_id": "CANDIDATE_CREATION_REGISTRY_TEST"
        },
        "regen_candidate_creation_session": {
            "candidate_creation_session_id": "CANDIDATE_CREATION_SESSION_TEST"
        },

        "channel_geometry_valid": True,
        "coolant_channel_width_m": 0.0015,
        "coolant_channel_height_m": 0.002,
        "rib_width_m": 0.001,
        "channel_count": 80,

        "stage_u_regen_validation_complete": True,
        "regen_validation_status": "PASS_REGEN_VALIDATION",
        "regen_heat_flux": 5.0e6,
        "regen_pressure_drop": 150000.0,

        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_blueprint_create_blueprints_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }

    results = attach_regen_candidate_blueprint_generation_input_gate(results)
    results = attach_regen_candidate_blueprint_session_owner(results)
    results = attach_regen_candidate_blueprint_registration_owner(results)
    return results


def test_regen_candidate_blueprint_report_owner():
    results = build_ready_12a3_results()
    results = attach_regen_candidate_blueprint_report_owner(results)

    bundle = results["regen_candidate_blueprint_report_bundle"]
    report = results["regen_candidate_blueprint_report"]

    assert results["phase_12a_4_regen_candidate_blueprint_report_owner_complete"] is True
    assert results["regen_candidate_blueprint_report_owner_ready"] is True
    assert results["regen_candidate_blueprint_report_owner_status"] == PASS_STATUS

    assert bundle["owner"] == "REGEN_CANDIDATE_BLUEPRINT_REPORT_OWNER"
    assert bundle["phase"] == "12A.4"
    assert bundle["ready"] is True
    assert bundle["registry_id"] == results["regen_candidate_blueprint_registry_id"]
    assert bundle["session_id"] == results["regen_candidate_blueprint_session_id"]

    assert "ownership_summary" in bundle["report_sections"]
    assert "registry_summary" in bundle["report_sections"]
    assert "permission_summary" in bundle["report_sections"]
    assert "safety_lock_summary" in bundle["report_sections"]

    assert "12A.4 candidate blueprint report ownership is complete." in report

    assert results["phase_12a_5_candidate_blueprint_completion_audit_allowed"] is True
    assert results["regen_candidate_blueprint_completion_audit_allowed"] is True

    assert results["regen_candidate_blueprint_generation_execution_allowed"] is False
    assert results["regen_candidate_blueprint_create_blueprints_allowed"] is False
    assert results["regen_candidate_creation_create_candidates_allowed"] is False
    assert results["regen_candidate_generation_create_candidates_allowed"] is False
    assert results["regen_optimisation_runtime_execution_allowed"] is False
    assert results["regen_optimisation_generation_advance_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


def test_regen_candidate_blueprint_report_owner_blocks_without_12a3():
    results = attach_regen_candidate_blueprint_report_owner({})

    assert results["phase_12a_4_regen_candidate_blueprint_report_owner_complete"] is True
    assert results["regen_candidate_blueprint_report_owner_ready"] is False
    assert results["regen_candidate_blueprint_report_bundle"] is None
    assert results["phase_12a_5_candidate_blueprint_completion_audit_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_blueprint_report_owner()
    test_regen_candidate_blueprint_report_owner_blocks_without_12a3()
    print("PASS_REGEN_CANDIDATE_BLUEPRINT_REPORT_OWNER_PHASE_12A4")
