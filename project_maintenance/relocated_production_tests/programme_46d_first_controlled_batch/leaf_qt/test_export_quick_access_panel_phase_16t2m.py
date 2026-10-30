from project_maintenance.production_historical_artifacts.leaf_qt.export_quick_access_panel_phase_16t2m import (
    PASS_STATUS,
    build_export_panel_stub_audit,
    open_path_in_file_manager,
)


def main() -> int:
    audit = build_export_panel_stub_audit()

    assert audit["status"] == PASS_STATUS
    assert audit["passed"] is True
    assert audit["category_count"] >= 8
    assert "summary" in audit

    assert open_path_in_file_manager("__definitely_missing_leaf_export_file__") is False

    print("PASS_EXPORT_QUICK_ACCESS_PANEL_STUB_PHASE_16T2M")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
