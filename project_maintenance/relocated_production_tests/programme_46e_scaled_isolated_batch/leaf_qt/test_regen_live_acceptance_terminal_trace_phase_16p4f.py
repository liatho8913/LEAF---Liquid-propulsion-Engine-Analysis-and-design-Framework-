from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "print(report)",
        "phase_16p4d_live_ui_acceptance_after_geometry",
        "LIVE UI ACCEPTANCE VALIDATION",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_LIVE_ACCEPTANCE_TERMINAL_TRACE_PHASE_16P4F")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_LIVE_ACCEPTANCE_TERMINAL_TRACE_PHASE_16P4F")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
