from regen_objective_weight_owner import attach_regen_objective_weight_owner


def test_objective_weight_owner_defaults_to_balanced():
    results = {}

    results = attach_regen_objective_weight_owner(results)

    assert results["phase_11b_2p_regen_objective_weight_owner_complete"] is True
    assert results["regen_objective_weight_selected_objective"] == "BALANCED"
    assert results["regen_objective_weight_sum"] == 1.0
    assert results["regen_objective_weight_solver_executed"] is False
    assert results["regen_objective_weight_live_geometry_modified"] is False
    assert results["regen_objective_weight_candidate_committed"] is False


def test_objective_weight_owner_thermal_prioritises_thermal():
    results = {
        "regen_automatic_geometry_objective": "THERMAL",
    }

    results = attach_regen_objective_weight_owner(results)

    weights = results["regen_objective_weight_map"]

    assert weights["thermal"] > weights["pressure"]
    assert weights["thermal"] > weights["geometry"]
    assert results["regen_objective_weight_sum"] == 1.0


def test_objective_weight_owner_mass_has_mass_weight():
    results = {
        "regen_automatic_geometry_objective": "MINIMUM_MASS",
    }

    results = attach_regen_objective_weight_owner(results)

    weights = results["regen_objective_weight_map"]

    assert weights["mass"] > 0.0
    assert results["regen_objective_weight_sum"] == 1.0


if __name__ == "__main__":
    test_objective_weight_owner_defaults_to_balanced()
    test_objective_weight_owner_thermal_prioritises_thermal()
    test_objective_weight_owner_mass_has_mass_weight()
    print("PASS_REGEN_OBJECTIVE_WEIGHT_OWNER_PHASE_11B2P")