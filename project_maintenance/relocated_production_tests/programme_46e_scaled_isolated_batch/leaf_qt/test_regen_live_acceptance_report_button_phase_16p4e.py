from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "self.live_acceptance_report_button = QPushButton",
        "view_layout.addWidget(self.live_acceptance_report_button)",
        "show_live_acceptance_report_phase_16p4e",
        "phase_16p4d_live_ui_acceptance_report",
        "Live Acceptance Report",
        "Copy Report",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_LIVE_ACCEPTANCE_REPORT_BUTTON_PHASE_16P4E")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_LIVE_ACCEPTANCE_REPORT_BUTTON_PHASE_16P4E")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
