from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_final_gui_runtime_closure_phase_16q12 import (
    evaluate_final_gui_runtime_closure,
    attach_final_gui_runtime_closure,
)


def main() -> int:
    passing = {
        "phase_16q8_geometry_realism_pass": True,
        "phase_16q9_realism_runtime_pass": True,
        "phase_16q10_auto_geometry_handover_lock_pass": True,
        "phase_16q11_clean_handover_export_available": True,
        "number_of_coolant_channels": 40,
        "phase_16p19_runtime_proof_width": 0.0012,
        "phase_16p19_runtime_proof_height": 0.0025,
        "viewer_channel_fit_ratio": 1.142,
        "viewer_cooling_coverage": 0.876,
        "viewer_effective_rib_width": 0.00065,
        "phase_16q9_realism_runtime_score": 87.76,
        "phase_16p19_runtime_proof_stale_old_nudge": False,
    }

    verdict = evaluate_final_gui_runtime_closure(passing)

    assert verdict["passed"] is True
    assert verdict["status"] == "PASS_REGEN_VIEWER_FINAL_GUI_RUNTIME_CLOSURE_PHASE_16Q12"
    assert verdict["blockers"] == []

    attach_final_gui_runtime_closure(passing)

    assert passing["phase_16q12_final_gui_runtime_closure_pass"] is True
    assert passing["regen_viewer_closed"] is True
    assert passing["regen_viewer_closure_status"] == "PASS"

    failing = dict(passing)
    failing["number_of_coolant_channels"] = 30
    failing["viewer_cooling_coverage"] = 0.95

    bad = evaluate_final_gui_runtime_closure(failing)

    assert bad["passed"] is False
    assert bad["status"] == "FAIL_REGEN_VIEWER_FINAL_GUI_RUNTIME_CLOSURE_PHASE_16Q12"
    assert len(bad["blockers"]) >= 2

    print("PASS_REGEN_VIEWER_FINAL_GUI_RUNTIME_CLOSURE_PHASE_16Q12")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
