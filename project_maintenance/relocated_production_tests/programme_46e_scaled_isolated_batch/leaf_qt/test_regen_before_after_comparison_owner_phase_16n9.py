from project_maintenance.production_historical_artifacts.leaf_qt.regen_before_after_comparison_owner_phase_16n9 import (
    RegenBeforeAfterComparisonOwnerPhase16N9,
    attach_before_after_comparison_phase_16n9,
)


def main() -> int:
    owner = RegenBeforeAfterComparisonOwnerPhase16N9()

    blocked = owner.compare({})
    assert blocked.available is False
    assert blocked.status == "FAIL_BEFORE_AFTER_COMPARISON_BLOCKED_PHASE_16N9"
    assert blocked.reasons

    results = {
        "regen_manual_geometry": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
            "rib_width": 0.001,
        },
        "regen_ui_applied_geometry": {
            "number_of_coolant_channels": 96,
            "coolant_channel_width": 0.0012,
            "rib_width": 0.0008,
        },
    }

    comparison = owner.compare(results)
    assert comparison.available is True
    assert comparison.status == "PASS_BEFORE_AFTER_COMPARISON_AVAILABLE_PHASE_16N9"
    assert len(comparison.changes) == 3

    report = owner.as_text(comparison)
    assert "REGEN BEFORE / AFTER GEOMETRY COMPARISON" in report
    assert "number_of_coolant_channels" in report
    assert "delta" in report

    updated = attach_before_after_comparison_phase_16n9(dict(results))
    assert updated["phase_16n9_before_after_comparison_available"] is True
    assert updated["phase_16n9_before_after_change_count"] == 3
    assert "coolant_channel_width" in updated["phase_16n9_before_after_comparison_report"]

    print("PASS_REGEN_BEFORE_AFTER_COMPARISON_OWNER_PHASE_16N9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
