from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    forbidden = [
        'if source == "automatic":\n        return False',
        '"automatic": "automatic_button"',
        'out.setdefault("automatic", button)',
    ]

    required = [
        'if source == "automatic":\n        return True',
        "Production Automatic Geometry is an action button",
    ]

    missing = [item for item in required if item not in text]
    hits = [item for item in forbidden if item in text]

    if missing or hits:
        print("FAIL_REGEN_AUTOMATIC_AVAILABILITY_PHASE_16P7D")
        for item in missing:
            print("Missing:", item)
        for item in hits:
            print("Forbidden:", item)
        raise SystemExit(1)

    print("PASS_REGEN_AUTOMATIC_AVAILABILITY_PHASE_16P7D")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
