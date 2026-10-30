from pathlib import Path

FILES = [
    Path("leaf_qt/foundation_result_key_audit.py"),
    Path("leaf_qt/variable_registry.py"),
]

PREFIXES = [
    "phase_15b_",
    "phase_15c_",
    "regen_candidate_comparison_",
    "candidate_comparison_",
]

for path in FILES:
    if not path.exists():
        print(f"SKIP {path}")
        continue

    text = path.read_text()

    if "KNOWN_DEVELOPMENT_KEYS = {" in text:
        additions = "\n".join(f'    "{p}",' for p in PREFIXES)
        if '"regen_candidate_comparison_",' not in text:
            text = text.replace(
                "KNOWN_DEVELOPMENT_KEYS = {",
                "KNOWN_DEVELOPMENT_KEYS = {\n" + additions
            )

    if "EXPECTED_PREFIX_VISIBILITY = {" in text:
        additions = "\n".join(f'    "{p}": "DIAGNOSTIC_ONLY",' for p in PREFIXES)
        if '"regen_candidate_comparison_": "DIAGNOSTIC_ONLY",' not in text:
            text = text.replace(
                "EXPECTED_PREFIX_VISIBILITY = {",
                "EXPECTED_PREFIX_VISIBILITY = {\n" + additions
            )

    path.write_text(text)
    print(f"PATCHED {path}")

print("PHASE_15B_RESULT_KEYS_REGISTERED")
