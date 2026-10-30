import importlib
import re
from pathlib import Path


def main() -> int:
    module = importlib.import_module("regen_cross_section_viewer")
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    attach_names = sorted(set(re.findall(r"\battach_[a-zA-Z0-9_]+", text)))

    missing = [
        name for name in attach_names
        if not hasattr(module, name)
    ]

    required_fallbacks = [
        "fallback_apply_geometry_result_phase_16p8",
        "fallback_solver_regeneration_request_phase_16p9",
        "fallback_before_after_comparison_phase_16p10",
    ]

    missing_fallbacks = [
        name for name in required_fallbacks
        if not hasattr(module, name)
    ]

    if missing or missing_fallbacks:
        print("FAIL_REGEN_MISSING_OWNER_RUNTIME_AUDIT_PHASE_16P10")
        if missing:
            print("Undefined attach_* names:")
            for name in missing:
                print("-", name)
        if missing_fallbacks:
            print("Missing fallbacks:")
            for name in missing_fallbacks:
                print("-", name)
        raise SystemExit(1)

    print("PASS_REGEN_MISSING_OWNER_RUNTIME_AUDIT_PHASE_16P10")
    print(f"Checked attach owner symbols: {len(attach_names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
