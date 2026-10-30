from regen_population_diversity_controller import (
    attach_regen_population_diversity_controller,
)
from regen_population_diversity_history_owner import (
    attach_regen_population_diversity_history_owner,
)
from regen_population_diversity_report_owner import (
    attach_regen_population_diversity_report_owner,
)
from regen_population_diversity_master_gate import (
    attach_regen_population_diversity_master_gate,
)


def build_population():
    base = {
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
        "coolant_flow_fraction": 1.0,
    }

    population = []

    for index, scale in enumerate([0.95, 1.0, 1.05, 1.10], start=1):
        geometry = dict(base)
        geometry["coolant_channel_width"] *= scale
        geometry["coolant_channel_height"] *= scale
        geometry["number_of_coolant_channels"] = int(
            round(base["number_of_coolant_channels"] * scale)
        )

        population.append({
            "candidate_id": f"RGEN2-{index:04d}",
            "candidate_generation": 2,
            "candidate_geometry": geometry,
        })

    return population


def test_population_diversity_passes_for_varied_population():
    results = {
        "regen_generation_population": build_population(),
    }

    results = attach_regen_population_diversity_controller(results)
    results = attach_regen_population_diversity_history_owner(results)
    results = attach_regen_population_diversity_report_owner(results)
    results = attach_regen_population_diversity_master_gate(results)

    assert results["phase_11b_1w_regen_population_diversity_complete"] is True
    assert results["phase_11b_1w_regen_population_diversity_history_complete"] is True
    assert results["phase_11b_1w_regen_population_diversity_report_complete"] is True
    assert results["phase_11b_1w_regen_population_diversity_master_gate_complete"] is True

    assert results["regen_population_diversity_status"] == (
        "PASS_REGEN_POPULATION_DIVERSITY_HEALTHY"
    )
    assert results["regen_population_diversity_master_gate_status"] == (
        "PASS_REGEN_POPULATION_DIVERSITY_GATE_READY"
    )

    metrics = results["regen_population_diversity_metrics"]

    assert metrics["population_count"] == 4
    assert metrics["unique_candidate_count"] == 4
    assert metrics["duplicate_candidate_count"] == 0

    assert results["regen_population_diversity_solver_executed"] is False
    assert results["regen_population_diversity_live_geometry_modified"] is False
    assert results["regen_population_diversity_candidate_committed"] is False


def test_population_diversity_blocks_empty_population():
    results = {}

    results = attach_regen_population_diversity_controller(results)
    results = attach_regen_population_diversity_history_owner(results)
    results = attach_regen_population_diversity_report_owner(results)
    results = attach_regen_population_diversity_master_gate(results)

    assert results["regen_population_diversity_ready"] is False
    assert results["regen_population_diversity_master_gate_ready"] is False


def test_population_diversity_fails_collapsed_population():
    geometry = {
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
        "coolant_flow_fraction": 1.0,
    }

    results = {
        "regen_generation_population": [
            {
                "candidate_id": f"RGEN2-{index:04d}",
                "candidate_generation": 2,
                "candidate_geometry": dict(geometry),
            }
            for index in range(1, 5)
        ]
    }

    results = attach_regen_population_diversity_controller(results)
    results = attach_regen_population_diversity_history_owner(results)
    results = attach_regen_population_diversity_report_owner(results)
    results = attach_regen_population_diversity_master_gate(results)

    assert results["regen_population_diversity_ready"] is False
    assert results["regen_population_diversity_master_gate_ready"] is False
    assert results["regen_population_diversity_metrics"]["unique_candidate_count"] == 1


if __name__ == "__main__":
    test_population_diversity_passes_for_varied_population()
    test_population_diversity_blocks_empty_population()
    test_population_diversity_fails_collapsed_population()
    print("PASS_REGEN_POPULATION_DIVERSITY_PHASE_11B1W")