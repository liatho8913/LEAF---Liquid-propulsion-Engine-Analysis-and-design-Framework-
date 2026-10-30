from regen_recommendation_payload_ui_owner_phase_16n3 import (
    RegenRecommendationPayloadUIOwnerPhase16N3,
)
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
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
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
            "hot_gas_wall_thickness": 0.001104,
        },
    }

    owner = RegenRecommendationPayloadUIOwnerPhase16N3()
    payload = owner.build(results)

    assert payload.available is True
    assert payload.ready_for_user_acceptance is True
    assert payload.status == "PASS_RECOMMENDATION_UI_PAYLOAD_READY_PHASE_16N3"
    assert payload.staged_geometry

    inspector_text = format_ranking_details(candidate, 0, results)

    required_fragments = [
        "CANDIDATE RANKING DETAILS",
        "RECOMMENDATION PAYLOAD",
        "PASS_RECOMMENDATION_UI_PAYLOAD_READY_PHASE_16N3",
        "Ready For User Acceptance: True",
        "ACCEPT_AUTOMATIC_GEOMETRY",
        "Staged Geometry For Acceptance",
        "hot_gas_wall_thickness",
        "It displays recommendation readiness but does not apply it.",
        "It does not commit geometry.",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in inspector_text]

    if missing:
        print("FAIL_REGEN_RECOMMENDATION_PAYLOAD_UI_COMPLETION_GATE_PHASE_16N3")
        print("Missing fragments:")
        for fragment in missing:
            print("-", fragment)
        raise SystemExit(1)

    print("PASS_REGEN_RECOMMENDATION_PAYLOAD_UI_COMPLETION_GATE_PHASE_16N3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
