from pathlib import Path

path = Path("leaf_qt/variable_registry.py")
text = path.read_text()

keys = [
    "regen_completion_audit_status",
    "regen_completion_audit_complete",
    "regen_completion_audit_missing_keys",
    "regen_completion_audit_failures",
    "regen_completion_audit_warnings",
    "regen_completion_audit_text",
]

for key in keys:
    marker = f'key="{key}",'
    start = text.find(marker)
    if start == -1:
        raise SystemExit(f"Missing key: {key}")

    next_def = text.find("VariableDefinition(", start + 1)
    end = next_def if next_def != -1 else len(text)

    block = text[start:end]
    block_new = block.replace(
        "output_visibility=OUTPUT_VISIBILITY_VALIDATION",
        "output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC",
    )

    text = text[:start] + block_new + text[end:]

path.write_text(text)
print("REGEN_COMPLETION_AUDIT_VARIABLE_DEFINITIONS_FIXED")
