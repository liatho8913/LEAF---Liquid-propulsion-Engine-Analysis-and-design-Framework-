from regen_accept_recommendation_owner_phase_16n6 import (
    RegenAcceptRecommendationOwnerPhase16N6,
    attach_accept_recommendation_result_phase_16n6,
)


def main() -> int:
    owner = RegenAcceptRecommendationOwnerPhase16N6()

    blocked = owner.accept({})
    assert blocked.accepted is False
    assert blocked.status == "FAIL_ACCEPT_RECOMMENDATION_BLOCKED_PHASE_16N6"
    assert blocked.reasons

    results = {
        "regen_geometry_commit_candidate_ready": True,
        "regen_geometry_commit_requires_user_acceptance": True,
        "regen_geometry_commit_staged_geometry": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
        },
    }

    accepted = owner.accept(results)
    assert accepted.accepted is True
    assert accepted.status == "PASS_ACCEPT_RECOMMENDATION_RECORDED_PHASE_16N6"
    assert accepted.staged_geometry["number_of_coolant_channels"] == 80

    updated = attach_accept_recommendation_result_phase_16n6(dict(results))
    assert updated["phase_16n6_recommendation_accepted"] is True
    assert updated["phase_16n6_geometry_applied"] is False
    assert updated["phase_16n6_solver_regenerated"] is False
    assert updated["phase_16n6_live_geometry_modified"] is False

    print("PASS_REGEN_ACCEPT_RECOMMENDATION_OWNER_PHASE_16N6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
