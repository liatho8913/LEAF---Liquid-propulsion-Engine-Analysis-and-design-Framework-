from regen_viewer_payload_trace import RegenViewerPayloadTracer


def main() -> int:
    tracer = RegenViewerPayloadTracer()

    tracer.inspect_payload("missing_payload", None)
    tracer.inspect_payload("recommendation_payload", {
        "candidate_id": "TEST-001",
        "score": 99.0,
        "geometry": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
        },
    })
    tracer.inspect_payload("station_payload", [
        {"x": 0.0, "radius": 0.01},
        {"x": 0.1, "radius": 0.02},
    ])

    report = tracer.as_text_report()

    assert "missing_payload" in report
    assert "recommendation_payload" in report
    assert "station_payload" in report
    assert "PRESENT_DICT" in report
    assert "PRESENT_LIST" in report
    assert "MISSING" in report

    print("PASS_REGEN_VIEWER_PAYLOAD_TRACE_PHASE_16N1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
