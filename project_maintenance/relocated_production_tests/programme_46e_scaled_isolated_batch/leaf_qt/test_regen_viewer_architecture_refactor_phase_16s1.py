from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_architecture_refactor_phase_16s1 import (
    build_viewer_architecture_spec,
    evaluate_viewer_architecture,
    attach_viewer_architecture_status,
)


def main() -> int:
    spec = build_viewer_architecture_spec()

    assert spec["phase"] == "16S.1"
    assert "toolbar" in spec["regions"]
    assert "side_profile" in spec["regions"]
    assert "engineering_summary" in spec["regions"]

    passing = {
        "phase_16s1_region_toolbar_available": True,
        "phase_16s1_region_main_cross_section_available": True,
        "phase_16s1_region_side_profile_available": True,
        "phase_16s1_region_engineering_summary_available": True,
        "phase_16s1_region_status_strip_available": True,
    }

    verdict = evaluate_viewer_architecture(passing)

    assert verdict["passed"] is True
    assert verdict["status"] == "PASS_REGEN_VIEWER_ARCHITECTURE_REFACTOR_PHASE_16S1"

    attach_viewer_architecture_status(passing)

    assert passing["phase_16s1_architecture_pass"] is True

    failing = dict(passing)
    failing["phase_16s1_region_side_profile_available"] = False

    bad = evaluate_viewer_architecture(failing)

    assert bad["passed"] is False
    assert bad["status"] == "FAIL_REGEN_VIEWER_ARCHITECTURE_REFACTOR_PHASE_16S1"
    assert len(bad["blockers"]) == 1

    print("PASS_REGEN_VIEWER_ARCHITECTURE_REFACTOR_PHASE_16S1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
