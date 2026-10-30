from regen_automatic_geometry_objective_selector import (
    attach_regen_automatic_geometry_objective_selector,
)


def test_objective_selector_defaults_to_balanced():
    results = {}

    results = attach_regen_automatic_geometry_objective_selector(results)

    assert results["phase_11b_2o_regen_automatic_geometry_objective_selector_complete"] is True
    assert results["regen_automatic_geometry_objective"] == "BALANCED"
    assert results["regen_optimisation_objective"] == "BALANCED"
    assert results["regen_automatic_geometry_objective_solver_executed"] is False
    assert results["regen_automatic_geometry_objective_live_geometry_modified"] is False
    assert results["regen_automatic_geometry_objective_candidate_committed"] is False


def test_objective_selector_normalises_aliases():
    results = {
        "regen_optimisation_objective": "wall temperature",
    }

    results = attach_regen_automatic_geometry_objective_selector(results)

    assert results["regen_automatic_geometry_objective"] == "THERMAL"


def test_objective_selector_rejects_unknown_to_balanced():
    results = {
        "regen_optimisation_objective": "random-objective",
    }

    results = attach_regen_automatic_geometry_objective_selector(results)

    assert results["regen_automatic_geometry_objective"] == "BALANCED"


if __name__ == "__main__":
    test_objective_selector_defaults_to_balanced()
    test_objective_selector_normalises_aliases()
    test_objective_selector_rejects_unknown_to_balanced()
    print("PASS_REGEN_AUTOMATIC_GEOMETRY_OBJECTIVE_SELECTOR_PHASE_11B2O")