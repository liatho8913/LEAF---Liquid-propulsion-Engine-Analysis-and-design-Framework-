from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    canvas_sig = "    def __init__(self, results):"
    viewer_sig = "    def __init__(self, results, parent=None, regeneration_callback=None):"

    canvas_start = text.find(canvas_sig)
    viewer_start = text.find(viewer_sig)

    if canvas_start == -1 or viewer_start == -1:
        print("FAIL_REGEN_CANVAS_CALLBACK_NAMEERROR_PHASE_16P7")
        print("Missing constructor signature.")
        raise SystemExit(1)

    canvas_block = text[canvas_start:viewer_start]
    viewer_block = text[viewer_start:viewer_start + 1200]

    failures = []

    if "regeneration_callback" in canvas_block:
        failures.append("Canvas constructor still references regeneration_callback")

    if "self.regeneration_callback = regeneration_callback" not in viewer_block:
        failures.append("Viewer constructor does not store regeneration_callback")

    if failures:
        print("FAIL_REGEN_CANVAS_CALLBACK_NAMEERROR_PHASE_16P7")
        for item in failures:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_CANVAS_CALLBACK_NAMEERROR_PHASE_16P7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
