from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_final_completion_declaration_phase_16q7 import (
    evaluate_final_viewer_completion_declaration,
    build_final_completion_declaration_report,
    attach_final_completion_declaration,
)


def main() -> int:
    passing = {
        "phase_16p23_final_completion_lock_pass": True,
        "phase_16q3_manufacturability_pass": True,
        "phase_16q5_manufacturability_overlay_pass": True,
        "phase_16q6_manufacturability_retest_pass": True,
        "regen_viewer_completion_lock": "PASS",
        "regen_viewer_complete_locked": True,
        "phase_16p19_runtime_proof_stale_old_nudge": False,
        "phase_16p19_runtime_proof_width": 0.0012,
        "phase_16p19_runtime_proof_height": 0.0025,
        "phase_16q3_channel_aspect_ratio": 2.083,
        "viewer_channel_fit_ratio": 1.327,
        "viewer_cooling_coverage": 0.754,
        "viewer_effective_rib_width": 0.00075,
        "viewer_channel_geometry_valid": 1.0,
    }

    verdict = evaluate_final_viewer_completion_declaration(passing)

    assert verdict["passed"] is True
    assert verdict["status"] == "PASS_REGEN_VIEWER_FINAL_COMPLETION_DECLARATION_PHASE_16Q7"
    assert verdict["blockers"] == []

    report = build_final_completion_declaration_report(passing)

    assert "FINAL REGEN VIEWER COMPLETION DECLARATION" in report
    assert "BLOCKERS" in report
    assert "- None" in report

    attach_final_completion_declaration(passing)

    assert passing["phase_16q7_final_completion_declaration_pass"] is True
    assert passing["regen_viewer_final_complete"] is True
    assert passing["regen_viewer_final_completion_status"] == "PASS"

    failing = dict(passing)
    failing["phase_16q6_manufacturability_retest_pass"] = False
    failing["viewer_cooling_coverage"] = 0.95

    bad = evaluate_final_viewer_completion_declaration(failing)

    assert bad["passed"] is False
    assert bad["status"] == "FAIL_REGEN_VIEWER_FINAL_COMPLETION_DECLARATION_PHASE_16Q7"
    assert len(bad["blockers"]) >= 2

    print("PASS_REGEN_VIEWER_FINAL_COMPLETION_DECLARATION_PHASE_16Q7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
