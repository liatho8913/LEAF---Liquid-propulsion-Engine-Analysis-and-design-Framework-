from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_integration_completion_gate_phase_16n1 import (
    RegenViewerIntegrationCompletionGatePhase16N1,
)


def main() -> int:
    gate = RegenViewerIntegrationCompletionGatePhase16N1()

    result = gate.evaluate(
        {
            "Candidate Ranking Window": {
                "candidate_id": "TEST-CANDIDATE",
                "rank": 1,
                "score": 99.0,
            },
            "Cross Section Viewer": {
                "geometry": {
                    "number_of_coolant_channels": 80,
                    "coolant_channel_width": 0.0015,
                }
            },
            "Station Viewer": [
                {"x": 0.0, "radius": 0.01},
                {"x": 0.1, "radius": 0.02},
            ],
            "Recommendation Viewer": {
                "recommendation": "Use ranked candidate geometry",
                "candidate_id": "TEST-CANDIDATE",
            },
        }
    )

    assert result.status == "PASS_REGEN_VIEWER_INTEGRATION_COMPLETION_GATE_PHASE_16N1"
    assert not result.missing_viewers

    print("PASS_REGEN_VIEWER_INTEGRATION_COMPLETION_GATE_PHASE_16N1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
