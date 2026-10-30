from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_workspace_restoration_phase_16s2 import (
    attach_workspace_restoration_status,
    evaluate_workspace_restoration,
)


def main() -> int:
    results = {
        "phase_16s2_controlled_layout_hidden": True,
        "phase_16s2_original_layout_primary": True,
    }

    verdict = evaluate_workspace_restoration(results)

    assert verdict["passed"] is True
    assert verdict["status"] == "PASS_REGEN_VIEWER_WORKSPACE_RESTORATION_PHASE_16S2"

    attach_workspace_restoration_status(results)

    assert results["phase_16s2_workspace_restoration_pass"] is True

    failing = {
        "phase_16s2_controlled_layout_hidden": False,
        "phase_16s2_original_layout_primary": True,
    }

    bad = evaluate_workspace_restoration(failing)

    assert bad["passed"] is False
    assert len(bad["blockers"]) == 1

    print("PASS_REGEN_VIEWER_WORKSPACE_RESTORATION_PHASE_16S2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
