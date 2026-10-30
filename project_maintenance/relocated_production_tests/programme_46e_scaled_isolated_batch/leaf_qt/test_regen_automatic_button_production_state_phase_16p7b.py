from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    start = text.find("def refresh_automatic_geometry_button_state_phase_16n2")
    if start == -1:
        print("FAIL_REGEN_AUTOMATIC_BUTTON_PRODUCTION_STATE_PHASE_16P7B")
        print("Missing button-state method.")
        raise SystemExit(1)

    block = text[start:text.find("\n    def ", start + 1)]

    required = [
        "button.setEnabled(True)",
        'button.setText("Generate Automatic Geometry")',
        "PASS_AUTOMATIC_BUTTON_PRODUCTION_ENABLED_PHASE_16P7B",
        "conservative candidate",
    ]

    forbidden = [
        "setEnabled(False)",
        "Unavailable",
        "Automatic Geometry (Unavailable)",
    ]

    missing = [item for item in required if item not in block]
    forbidden_hits = [item for item in forbidden if item in block]

    if missing or forbidden_hits:
        print("FAIL_REGEN_AUTOMATIC_BUTTON_PRODUCTION_STATE_PHASE_16P7B")
        if missing:
            print("Missing:")
            for item in missing:
                print("-", item)
        if forbidden_hits:
            print("Forbidden:")
            for item in forbidden_hits:
                print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_AUTOMATIC_BUTTON_PRODUCTION_STATE_PHASE_16P7B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
