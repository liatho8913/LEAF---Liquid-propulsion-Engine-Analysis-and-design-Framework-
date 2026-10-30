from pathlib import Path

FILES = [
    Path("leaf_qt/foundation_result_key_audit.py"),
    Path("leaf_qt/variable_registry.py"),
]

KEYS = [
    "regen_completion_audit_complete",
    "regen_completion_audit_failures",
    "regen_completion_audit_missing_keys",
    "regen_completion_audit_status",
    "regen_completion_audit_text",
    "regen_completion_audit_warnings",
]

for path in FILES:
    if not path.exists():
        print(f"SKIP {path}")
        continue

    text = path.read_text()

    for key in KEYS:
        text = text.replace(
            f'"{key}": "VALIDATION_ONLY"',
            f'"{key}": "DIAGNOSTIC_ONLY"'
        )
        text = text.replace(
            f"'{key}': 'VALIDATION_ONLY'",
            f"'{key}': 'DIAGNOSTIC_ONLY'"
        )

    path.write_text(text)
    print(f"PATCHED {path}")

print("PHASE_16F_VISIBILITY_AUDIT_REPAIR_COMPLETE")
