from pathlib import Path
import py_compile

ROOT = Path.cwd()

TARGETS = [
    ROOT / "leaf_qt" / "failure_root_cause_owner.py",
    ROOT / "leaf_qt" / "regen_completion_gate_validation_owner.py",
    ROOT / "leaf_qt" / "regen_system_signoff_validation_owner.py",
    ROOT / "leaf_qt" / "regen_optimisation_scoring_owner.py",
]

FALLBACK_CLASS = '''

    class LegacyCompatibilityProducer:
        """
        Phase 16U shared presentation compatibility fallback.

        This local fallback is only used when leaf_qt.status_presentation
        cannot be imported. Normal production execution should use the shared
        status_presentation implementation.
        """

        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity == "FAIL":
                return "FAIL"
            if severity == "WARN":
                return "WARN"
            if severity == "PASS":
                return "PASS"
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)
'''

changed = []

for path in TARGETS:
    if not path.exists():
        raise SystemExit(f"FAIL_PHASE_16U114_REPAIR: missing {path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    original = text

    if "LegacyCompatibilityProducer" not in text:
        text = text.replace(
            "from leaf_qt.status_presentation import status_severity",
            "from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity",
            1,
        )

        marker = '    def status_severity(value):\n'
        idx = text.find(marker)
        if idx == -1:
            raise SystemExit(f"FAIL_PHASE_16U114_REPAIR: fallback status_severity block not found in {path}")

        # Insert fallback class directly before fallback status_severity.
        text = text[:idx] + FALLBACK_CLASS + "\n" + text[idx:]

    path.write_text(text, encoding="utf-8")
    py_compile.compile(str(path), doraise=True)

    if text != original:
        changed.append(str(path.relative_to(ROOT)))

print("PASS_PHASE_16U114_CLOSED_TARGET_LEGACY_PRODUCER_IMPORT_REPAIR")
print(f"changed={changed}")
