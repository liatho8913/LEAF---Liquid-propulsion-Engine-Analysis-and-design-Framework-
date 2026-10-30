from pathlib import Path

FILES = [
    Path("leaf_qt/foundation_result_key_audit.py"),
    Path("leaf_qt/variable_registry.py"),
]

KEYS = [
    "regen_runtime_parent_lineage",
    "regen_runtime_parent_lineage_count",
    "runtime_next_generation_number",
]

PREFIXES = [
    "regen_runtime_parent_lineage",
    "runtime_next_generation_",
]

for path in FILES:
    if not path.exists():
        print(f"SKIP {path}")
        continue

    text = path.read_text()

    if "KNOWN_DEVELOPMENT_KEYS = {" in text:
        additions = "\n".join(f'    "{k}",' for k in KEYS + PREFIXES)
        if '"runtime_next_generation_number",' not in text:
            text = text.replace(
                "KNOWN_DEVELOPMENT_KEYS = {",
                "KNOWN_DEVELOPMENT_KEYS = {\n" + additions
            )

    if "EXPECTED_PREFIX_VISIBILITY = {" in text:
        additions = "\n".join(
            f'    "{k}": "DIAGNOSTIC_ONLY",'
            for k in KEYS + PREFIXES
        )
        if '"runtime_next_generation_number": "DIAGNOSTIC_ONLY",' not in text:
            text = text.replace(
                "EXPECTED_PREFIX_VISIBILITY = {",
                "EXPECTED_PREFIX_VISIBILITY = {\n" + additions
            )

    path.write_text(text)
    print(f"PATCHED {path}")

print("PHASE_14D_REMAINING_RESULT_KEYS_REGISTERED")
