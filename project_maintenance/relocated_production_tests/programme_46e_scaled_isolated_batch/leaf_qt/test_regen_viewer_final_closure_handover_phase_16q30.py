from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_final_closure_handover_phase_16q30 import (
    evaluate_final_closure_handover,
    build_final_closure_handover,
    attach_final_closure_handover,
)


def main() -> int:
    results = {
        "phase_16q20_final_runtime_consistency_pass": True,
        "phase_16q21_panel_cleanup_pass": True,
        "phase_16q24_real_button_toggle_pass": True,
        "phase_16q25_auto_geometry_cache_available": True,
        "phase_16q26_toggle_cache_audit_pass": True,
        "phase_16q27_toggle_ux_pass": True,
        "phase_16q28_gui_runtime_acceptance_pass": True,
    }

    verdict = evaluate_final_closure_handover(results)

    assert verdict["passed"] is True
    assert verdict["status"] == "PASS_REGEN_VIEWER_FINAL_CLOSURE_HANDOVER_PHASE_16Q30"

    handover = build_final_closure_handover(results)

    assert "LEAF REGEN VIEWER FINAL CLOSURE HANDOVER" in handover
    assert "Completed Regen Viewer Systems" in handover
    assert "- None" in handover

    attach_final_closure_handover(results)

    assert results["phase_16q30_final_closure_handover_pass"] is True
    assert results["regen_viewer_closure_handover_ready"] is True

    print("PASS_REGEN_VIEWER_FINAL_CLOSURE_HANDOVER_PHASE_16Q30")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
