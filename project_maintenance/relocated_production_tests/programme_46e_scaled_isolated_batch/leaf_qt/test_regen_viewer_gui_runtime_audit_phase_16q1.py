from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_gui_runtime_audit_phase_16q1 import (
    build_gui_runtime_audit,
    build_gui_runtime_audit_report,
    attach_gui_runtime_audit,
)


def main() -> int:
    passing = {
        "phase_16p19_runtime_proof_banner": "AUTOMATIC GEOMETRY: NEW 16P.14 FIT-SOLVED — PASS",
        "phase_16p19_runtime_proof_stale_old_nudge": False,
        "phase_16p19_runtime_proof_fit_solved": True,
        "phase_16p19_runtime_proof_width": 0.00055,
        "phase_16p19_runtime_proof_height": 0.004,
        "phase_16p20_final_runtime_signoff_status": "PASS_REGEN_VIEWER_FINAL_RUNTIME_SIGNOFF_GATE_PHASE_16P20",
        "phase_16p21_runtime_signoff_report_available": True,
        "phase_16p22_gui_runtime_checklist_status": "PASS_REGEN_VIEWER_GUI_RUNTIME_CHECKLIST_PHASE_16P22",
        "phase_16p23_final_completion_lock_status": "PASS_REGEN_VIEWER_FINAL_COMPLETION_LOCK_PHASE_16P23",
        "regen_viewer_completion_lock": "PASS",
        "regen_viewer_complete_locked": True,
        "viewer_channel_fit_ratio": 1.12,
        "viewer_cooling_coverage": 0.89,
        "viewer_effective_rib_width": 0.00025,
        "viewer_channel_geometry_valid": 1.0,
    }

    audit = build_gui_runtime_audit(passing)

    assert audit["passed"] is True
    assert audit["status"] == "PASS_REGEN_VIEWER_GUI_RUNTIME_AUDIT_PHASE_16Q1"
    assert audit["blockers"] == []

    report = build_gui_runtime_audit_report(passing)

    assert "REGEN VIEWER GUI RUNTIME AUDIT" in report
    assert "BLOCKERS" in report
    assert "- None" in report

    attach_gui_runtime_audit(passing)

    assert passing["phase_16q1_gui_runtime_audit_pass"] is True

    failing = dict(passing)
    failing["regen_viewer_completion_lock"] = "FAIL"
    failing["phase_16p19_runtime_proof_stale_old_nudge"] = True
    failing["phase_16p19_runtime_proof_fit_solved"] = False

    bad = build_gui_runtime_audit(failing)

    assert bad["passed"] is False
    assert bad["status"] == "FAIL_REGEN_VIEWER_GUI_RUNTIME_AUDIT_PHASE_16Q1"
    assert len(bad["blockers"]) >= 2

    print("PASS_REGEN_VIEWER_GUI_RUNTIME_AUDIT_PHASE_16Q1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
