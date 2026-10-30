from regen_autonomous_geometry_commit_controller import (
    attach_regen_autonomous_geometry_commit_controller,
)


def main() -> int:
    results = {
        "regen_candidate_ranking_winner": {
            "candidate_id": "RANKED-TEST-001",
            "score": 99.0,
            "geometry": {
                "number_of_coolant_channels": 80,
                "coolant_channel_width": 0.0015,
                "coolant_channel_height": 0.002,
                "rib_width": 0.001,
                "hot_gas_wall_thickness": 0.0011,
            },
        }
    }

    updated = attach_regen_autonomous_geometry_commit_controller(results)

    assert updated["regen_autonomous_geometry_commit_complete"] is True
    assert updated["regen_geometry_commit_candidate_ready"] is True
    assert updated["regen_geometry_commit_requires_user_acceptance"] is True

    staged = updated["regen_geometry_commit_staged_geometry"]

    assert isinstance(staged, dict)
    assert staged
    assert staged["number_of_coolant_channels"] == 80
    assert staged["coolant_channel_width"] == 0.0015
    assert staged["coolant_channel_height"] == 0.002
    assert staged["rib_width"] == 0.001

    assert updated["regen_autonomous_geometry_commit_solver_executed"] is False
    assert updated["regen_autonomous_geometry_commit_live_geometry_modified"] is False
    assert updated["regen_autonomous_geometry_commit_candidate_committed"] is False

    print("PASS_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_CONTROLLER_PHASE_16N2A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
