from regen_candidate_population_generation_owner import build_regen_candidate_population_generation_owner
from regen_candidate_population_report_owner import build_regen_candidate_population_report_owner
from regen_candidate_population_registration_owner import build_regen_candidate_population_registration_owner
from regen_candidate_population_completion_audit import build_regen_candidate_population_completion_audit
from regen_candidate_population_master_gate import build_regen_candidate_population_master_gate
from regen_candidate_ranking_input_audit import build_regen_candidate_ranking_input_audit
from regen_candidate_ranking_owner import build_regen_candidate_ranking_owner
from regen_candidate_ranking_report_owner import build_regen_candidate_ranking_report_owner
from regen_candidate_ranking_registration_owner import build_regen_candidate_ranking_registration_owner
from regen_candidate_ranking_completion_audit import build_regen_candidate_ranking_completion_audit
from regen_candidate_ranking_master_gate import build_regen_candidate_ranking_master_gate
from regen_candidate_mutation_input_audit import build_regen_candidate_mutation_input_audit
from regen_candidate_mutation_owner import build_regen_candidate_mutation_owner
from regen_candidate_mutation_report_owner import build_regen_candidate_mutation_report_owner


def run_test():
    results = {
        "phase_11b_2t_regen_objective_decision_master_gate_complete": True,
        "regen_objective_decision_architecture_complete": True,
        "regen_candidate_ranking_objective_requested": "BALANCED",
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
        "coolant_flow_fraction": 1.0,
        "regen_population_requested_size": 16,
    }

    results.update(build_regen_candidate_population_generation_owner(results))
    results.update(build_regen_candidate_population_report_owner(results))
    results.update(build_regen_candidate_population_registration_owner(results))
    results.update(build_regen_candidate_population_completion_audit(results))
    results.update(build_regen_candidate_population_master_gate(results))
    results.update(build_regen_candidate_ranking_input_audit(results))
    results.update(build_regen_candidate_ranking_owner(results))
    results.update(build_regen_candidate_ranking_report_owner(results))
    results.update(build_regen_candidate_ranking_registration_owner(results))
    results.update(build_regen_candidate_ranking_completion_audit(results))
    results.update(build_regen_candidate_ranking_master_gate(results))
    results.update(build_regen_candidate_mutation_input_audit(results))
    results.update(build_regen_candidate_mutation_owner(results))
    results.update(build_regen_candidate_mutation_report_owner(results))

    assert results["regen_candidate_mutation_report_owner_complete"] is True
    assert results["phase_11b_5c_regen_candidate_mutation_report_owner_complete"] is True
    assert results["regen_candidate_mutation_report_owner_ready"] is True

    assert (
        results["regen_candidate_mutation_report_owner_status"]
        == "PASS_REGEN_CANDIDATE_MUTATION_REPORT_OWNER_PHASE_11B5C"
    )

    summary = results["regen_candidate_mutation_summary"]
    explanation = results["regen_candidate_mutation_explanation"]
    bundle = results["regen_candidate_mutation_report_bundle"]
    export_bundle = results["regen_candidate_mutation_export_bundle"]
    text = results["regen_candidate_mutation_report_text"]

    assert summary["parent_candidate_id"] == results["regen_candidate_parent_candidate"]["candidate_id"]
    assert summary["offspring_candidate_id"] == results["regen_candidate_offspring_candidate"]["candidate_id"]
    assert summary["mutation_safety_status"] == "PASS_MUTATION_SAFETY"

    assert "parent_to_offspring_reason" in explanation
    assert "delta_reason" in explanation
    assert "safety_reason" in explanation
    assert "architecture_reason" in explanation

    assert bundle["report_key"] == "regen_candidate_mutation_report"
    assert bundle["owner"] == "REGEN_CANDIDATE_MUTATION_REPORT_OWNER"
    assert bundle["phase"] == "11B.5C"
    assert bundle["ready"] is True
    assert bundle["complete"] is True
    assert bundle["architecture"]["mutation_report_owner_complete"] is True
    assert bundle["architecture"]["mutation_registration_owner_complete"] is False
    assert bundle["architecture"]["offspring_ranking_allowed"] is False
    assert bundle["architecture"]["evolution_allowed"] is False

    assert export_bundle["export_ready"] is True
    assert export_bundle["report_key"] == "regen_candidate_mutation_report"

    assert "LEAF PHASE 11B.5C" in text
    assert "Parent Geometry" in text
    assert "Offspring Geometry" in text
    assert "Mutation Delta" in text
    assert "Offspring ranked: False" in text
    assert "Evolution executed: False" in text

    assert results["regen_candidate_mutation_report_registered"] is False
    assert results["regen_candidate_mutation_report_viewer_registered"] is False
    assert results["regen_candidate_mutation_report_export_registered"] is False

    assert results["regen_candidate_mutation_registration_owner_allowed"] is True
    assert results["phase_11b_5d_candidate_mutation_registration_owner_allowed"] is True

    print("PASS_REGEN_CANDIDATE_MUTATION_REPORT_OWNER_PHASE_11B5C")
    return True


if __name__ == "__main__":
    run_test()
