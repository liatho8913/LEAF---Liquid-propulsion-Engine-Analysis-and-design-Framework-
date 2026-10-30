from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_manufacturability_retest_phase_16q6 import (
    evaluate_manufacturability_retest,
    attach_manufacturability_retest,
)


def main() -> int:
    passing = {
        "phase_16q3_manufacturability_pass": True,
        "phase_16q5_manufacturability_overlay_pass": True,
        "phase_16q3_channel_aspect_ratio": 2.083,
        "viewer_channel_fit_ratio": 1.327,
        "viewer_cooling_coverage": 0.754,
        "viewer_effective_rib_width": 0.00075,
    }

    verdict = evaluate_manufacturability_retest(passing)

    assert verdict["passed"] is True
    assert verdict["status"] == "PASS_REGEN_VIEWER_MANUFACTURABILITY_RETEST_PHASE_16Q6"

    attach_manufacturability_retest(passing)

    assert passing["phase_16q6_manufacturability_retest_pass"] is True

    failing = dict(passing)
    failing["viewer_cooling_coverage"] = 0.95

    bad = evaluate_manufacturability_retest(failing)

    assert bad["passed"] is False
    assert bad["status"] == "FAIL_REGEN_VIEWER_MANUFACTURABILITY_RETEST_PHASE_16Q6"
    assert len(bad["blockers"]) >= 1

    print("PASS_REGEN_VIEWER_MANUFACTURABILITY_RETEST_PHASE_16Q6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
