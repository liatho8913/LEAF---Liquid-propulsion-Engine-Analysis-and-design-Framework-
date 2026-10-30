from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_auto_geometry_handover_lock_phase_16q10 import (
    evaluate_auto_geometry_handover_lock,
    build_auto_geometry_handover_lock_report,
    attach_auto_geometry_handover_lock,
)


def main() -> int:
    passing = {
        "phase_16q8_geometry_realism_pass": True,
        "phase_16q9_realism_runtime_report_available": True,
        "phase_16q9_realism_runtime_pass": True,
        "phase_16q9_realism_runtime_score": 87.76,
        "viewer_channel_fit_ratio": 1.142,
        "viewer_cooling_coverage": 0.876,
        "viewer_effective_rib_width": 0.00065,
        "phase_16p19_runtime_proof_stale_old_nudge": False,
        "phase_16p19_runtime_proof_width": 0.0012,
        "phase_16p19_runtime_proof_height": 0.0025,
        "number_of_coolant_channels": 40,
    }

    verdict = evaluate_auto_geometry_handover_lock(passing)

    assert verdict["passed"] is True
    assert verdict["status"] == "PASS_REGEN_VIEWER_AUTO_GEOMETRY_HANDOVER_LOCK_PHASE_16Q10"
    assert verdict["blockers"] == []

    report = build_auto_geometry_handover_lock_report(passing)

    assert "AUTO GEOMETRY HANDOVER LOCK" in report
    assert "BLOCKERS" in report
    assert "- None" in report

    attach_auto_geometry_handover_lock(passing)

    assert passing["phase_16q10_auto_geometry_handover_lock_pass"] is True
    assert passing["regen_viewer_auto_geometry_handover_ready"] is True
    assert passing["regen_viewer_auto_geometry_handover_status"] == "PASS"

    failing = dict(passing)
    failing["phase_16q9_realism_runtime_score"] = 40.0
    failing["viewer_cooling_coverage"] = 0.95

    bad = evaluate_auto_geometry_handover_lock(failing)

    assert bad["passed"] is False
    assert bad["status"] == "FAIL_REGEN_VIEWER_AUTO_GEOMETRY_HANDOVER_LOCK_PHASE_16Q10"
    assert len(bad["blockers"]) >= 2

    print("PASS_REGEN_VIEWER_AUTO_GEOMETRY_HANDOVER_LOCK_PHASE_16Q10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
