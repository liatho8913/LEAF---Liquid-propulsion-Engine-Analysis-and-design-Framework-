from project_maintenance.production_historical_artifacts.leaf_qt.regen_viewer_clean_handover_export_phase_16q11 import (
    build_clean_handover_export,
    attach_clean_handover_export,
)


def main() -> int:
    results = {
        "phase_16q8_geometry_realism_pass": True,
        "phase_16q9_realism_runtime_report_available": True,
        "phase_16q9_realism_runtime_pass": True,
        "phase_16q9_realism_runtime_score": 87.76,
        "phase_16q9_realism_runtime_status": "PASS_REGEN_VIEWER_REALISM_RUNTIME_REPORT_PHASE_16Q9",
        "viewer_channel_fit_ratio": 1.142,
        "viewer_cooling_coverage": 0.876,
        "viewer_effective_rib_width": 0.00065,
        "viewer_channel_geometry_valid": 1.0,
        "phase_16p19_runtime_proof_stale_old_nudge": False,
        "phase_16p19_runtime_proof_width": 0.0012,
        "phase_16p19_runtime_proof_height": 0.0025,
        "number_of_coolant_channels": 40,
    }

    report = build_clean_handover_export(results)

    assert "LEAF REGEN VIEWER CLEAN HANDOVER EXPORT" in report
    assert "Confirmed Automatic Geometry" in report
    assert "Blockers" in report
    assert "- None" in report

    attach_clean_handover_export(results)

    assert results["phase_16q11_clean_handover_export_available"] is True
    assert results["phase_16q11_clean_handover_export_status"] == (
        "PASS_REGEN_VIEWER_CLEAN_HANDOVER_EXPORT_PHASE_16Q11"
    )
    assert "phase_16q11_clean_handover_export" in results

    print("PASS_REGEN_VIEWER_CLEAN_HANDOVER_EXPORT_PHASE_16Q11")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
