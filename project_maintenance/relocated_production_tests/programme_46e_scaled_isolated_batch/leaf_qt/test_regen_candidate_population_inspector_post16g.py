from regen_candidate_population_inspector import (
    get_candidate_population,
    build_candidate_summary,
    format_candidate_details,
)


def main():
    results = {
        "regen_candidate_population_candidates": [
            {
                "candidate_id": "CANDIDATE_001",
                "candidate_generation": 1,
                "candidate_parent": "MANUAL_BASELINE",
                "candidate_status": "GENERATED_NOT_SOLVED",
                "candidate_geometry": {
                    "number_of_coolant_channels": 80,
                    "coolant_channel_width": 0.0015,
                    "coolant_channel_height": 0.002,
                    "rib_width": 0.001,
                    "hot_gas_wall_thickness": 0.001,
                    "coolant_flow_fraction": 0.35,
                },
                "candidate_metadata": {
                    "phase": "POST-16G",
                    "solver_execution_locked": True,
                    "live_commit_locked": True,
                },
            }
        ],
        "regen_candidate_population_master_gate_status": (
            "PASS_REGEN_CANDIDATE_POPULATION_MASTER_GATE_PHASE_11B3E"
        ),
        "regen_candidate_ranking_architecture_allowed": True,
    }

    population = get_candidate_population(results)
    assert len(population) == 1

    summary = build_candidate_summary(population[0])
    assert summary["candidate_id"] == "CANDIDATE_001"
    assert summary["channels"] == 80
    assert summary["width"] == 0.0015

    details = format_candidate_details(population[0])
    assert "CANDIDATE DETAILS" in details
    assert "coolant_channel_width" in details
    assert "solver_execution_locked" in details
    assert "read-only" in details.lower()

    print("PASS_REGEN_CANDIDATE_POPULATION_INSPECTOR_POST16G")


if __name__ == "__main__":
    main()
