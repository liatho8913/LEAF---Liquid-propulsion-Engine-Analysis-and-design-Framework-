from regen_viewer_integration_report_owner import RegenViewerIntegrationReportOwner


def main() -> int:
    owner = RegenViewerIntegrationReportOwner()

    owner.check_viewer_payload(
        viewer_name="Candidate Ranking Window",
        payload_name="candidate_ranking_payload",
        payload={
            "rank": 1,
            "candidate_id": "TEST-CANDIDATE",
            "score": 99.0,
        },
    )

    owner.check_viewer_payload(
        viewer_name="Cross Section Viewer",
        payload_name="cross_section_payload",
        payload={
            "geometry": {
                "number_of_coolant_channels": 80,
                "coolant_channel_width": 0.0015,
            }
        },
    )

    owner.check_viewer_payload(
        viewer_name="Station Viewer",
        payload_name="station_payload",
        payload=[
            {"x": 0.0, "radius": 0.01},
            {"x": 0.1, "radius": 0.02},
        ],
    )

    report = owner.as_text_report()

    assert "Candidate Ranking Window" in report
    assert "Cross Section Viewer" in report
    assert "Station Viewer" in report
    assert owner.overall_status() == "PASS_REGEN_VIEWER_INTEGRATION_PHASE_16N1"

    print("PASS_REGEN_VIEWER_INTEGRATION_REPORT_OWNER_PHASE_16N1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
