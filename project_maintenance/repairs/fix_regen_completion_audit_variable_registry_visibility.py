from pathlib import Path

path = Path("leaf_qt/variable_registry.py")
text = path.read_text()

text = text.replace(
    'if key_l.startswith("regen_completion_audit_"):\n        return "VALIDATION_ONLY"',
    'if key_l.startswith("regen_completion_audit_"):\n        return "DIAGNOSTIC_ONLY"',
)

keys = [
    "regen_completion_audit_status",
    "regen_completion_audit_complete",
    "regen_completion_audit_missing_keys",
    "regen_completion_audit_failures",
    "regen_completion_audit_warnings",
    "regen_completion_audit_text",
]

for key in keys:
    text = text.replace(
        f'key="{key}",\n            output_visibility="VALIDATION_ONLY"',
        f'key="{key}",\n            output_visibility="DIAGNOSTIC_ONLY"',
    )
    text = text.replace(
        f'key="{key}",\n            visibility="VALIDATION_ONLY"',
        f'key="{key}",\n            visibility="DIAGNOSTIC_ONLY"',
    )

path.write_text(text)
print("REGEN_COMPLETION_AUDIT_VARIABLE_REGISTRY_VISIBILITY_FIXED")
