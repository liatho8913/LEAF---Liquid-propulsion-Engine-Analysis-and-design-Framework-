from regen_recommendation_payload_ui_owner_phase_16n3 import (
    RegenRecommendationPayloadUIOwnerPhase16N3,
)


def main() -> int:
    owner = RegenRecommendationPayloadUIOwnerPhase16N3()

    payload = owner.build(
        {
            "regen_candidate_ranking_winner": {
                "candidate_id": "RPOP-G0-0011",
                "rank": 1,
                "score": 99.172,
            },
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
    )

    assert payload.available is True
    assert payload.ready_for_user_acceptance is True
    assert payload.status == "PASS_RECOMMENDATION_UI_PAYLOAD_READY_PHASE_16N3"
    assert payload.candidate_id == "RPOP-G0-0011"
    assert payload.rank == 1
    assert payload.score == 99.172
    assert payload.staged_geometry["number_of_coolant_channels"] == 80

    report = owner.as_text(payload)
    assert "REGEN RECOMMENDATION UI PAYLOAD" in report
    assert "RPOP-G0-0011" in report
    assert "number_of_coolant_channels" in report

    missing = owner.build({})
    assert missing.available is False
    assert missing.status == "FAIL_RECOMMENDATION_UI_PAYLOAD_MISSING_PHASE_16N3"

    print("PASS_REGEN_RECOMMENDATION_PAYLOAD_UI_OWNER_PHASE_16N3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
