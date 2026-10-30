from regen_mutation_engine import (
    attach_regen_mutation_engine,
    build_mutation_plan,
    create_candidates_from_mutation_plan,
)
from regen_mutation_history_owner import attach_regen_mutation_history_owner
from regen_mutation_report_owner import attach_regen_mutation_report_owner
from regen_mutation_master_gate import attach_regen_mutation_master_gate


def test_mutation_engine_creates_safe_mutation_plan():
    results = {
        "regen_generation_evolution_seed_geometry": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.0020,
            "rib_width": 0.0010,
            "hot_gas_wall_thickness": 0.0012,
            "coolant_flow_fraction": 1.0,
        }
    }

    results = attach_regen_mutation_engine(results)
    results = attach_regen_mutation_history_owner(results)
    results = attach_regen_mutation_report_owner(results)
    results = attach_regen_mutation_master_gate(results)

    assert results["phase_11b_1v_regen_mutation_engine_complete"] is True
    assert results["phase_11b_1v_regen_mutation_history_complete"] is True
    assert results["phase_11b_1v_regen_mutation_report_complete"] is True
    assert results["phase_11b_1v_regen_mutation_master_gate_complete"] is True

    assert results["regen_mutation_engine_status"] == (
        "PASS_REGEN_MUTATION_ENGINE_PLAN_CREATED"
    )
    assert results["regen_mutation_master_gate_status"] == (
        "PASS_REGEN_MUTATION_GATE_READY"
    )

    assert results["regen_mutation_plan_count"] > 0
    assert results["regen_mutation_solver_executed"] is False
    assert results["regen_mutation_live_geometry_modified"] is False
    assert results["regen_mutation_candidate_committed"] is False


def test_mutation_engine_builds_generation_candidates():
    base_geometry = {
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
        "coolant_flow_fraction": 1.0,
    }

    mutation_plan = build_mutation_plan(base_geometry)
    candidates = create_candidates_from_mutation_plan(
        mutation_plan=mutation_plan,
        generation=2,
        parent="BEST_SO_FAR",
        population_size=10,
    )

    assert len(candidates) == 10
    assert candidates[0]["candidate_id"] == "RGEN2-0001"
    assert candidates[0]["candidate_source"] == "regen_mutation_engine"
    assert isinstance(candidates[0]["candidate_geometry"], dict)


def test_mutation_engine_blocks_without_geometry():
    results = {}

    results = attach_regen_mutation_engine(results)
    results = attach_regen_mutation_history_owner(results)
    results = attach_regen_mutation_report_owner(results)
    results = attach_regen_mutation_master_gate(results)

    assert results["regen_mutation_engine_ready"] is False
    assert results["regen_mutation_plan_count"] == 0
    assert results["regen_mutation_master_gate_ready"] is False


if __name__ == "__main__":
    test_mutation_engine_creates_safe_mutation_plan()
    test_mutation_engine_builds_generation_candidates()
    test_mutation_engine_blocks_without_geometry()
    print("PASS_REGEN_MUTATION_ENGINE_PHASE_11B1V")