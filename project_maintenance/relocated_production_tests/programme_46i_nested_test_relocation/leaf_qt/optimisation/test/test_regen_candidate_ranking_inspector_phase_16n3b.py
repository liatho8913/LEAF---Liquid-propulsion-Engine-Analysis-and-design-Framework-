from regen_candidate_ranking_inspector import format_ranking_details


def main() -> int:
    candidate = {
        "candidate_id": "RPOP-G0-0011",
        "rank": 1,
        "score": 99.172,
        "status": "RANKED_CONSERVATIVE",
        "winner": True,
        "geometry": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
        },
    }

    results = {
        "regen_candidate_ranking_winner": candidate,
        "regen_automatic_geometry_decision": "ACCEPT_AUTOMATIC_GEOMETRY",
        "regen_automatic_geometry_decision_reason": "Highest ranked conservative candidate.",
        "regen_geometry_commit_candidate_ready": True,
        "regen_geometry_commit_requires_user_acceptance": True,
        "regen_geometry_commit_staged_geometry": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
        },
    }

    report = format_ranking_details(candidate, 0, results)

    assert "CANDIDATE RANKING DETAILS" in report
    assert "RECOMMENDATION PAYLOAD" in report
    assert "PASS_RECOMMENDATION_UI_PAYLOAD_READY_PHASE_16N3" in report
    assert "Ready For User Acceptance: True" in report
    assert "ACCEPT_AUTOMATIC_GEOMETRY" in report
    assert "Staged Geometry For Acceptance" in report
    assert "number_of_coolant_channels" in report
    assert "It displays recommendation readiness but does not apply it." in report

    print("PASS_REGEN_CANDIDATE_RANKING_INSPECTOR_PHASE_16N3B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
