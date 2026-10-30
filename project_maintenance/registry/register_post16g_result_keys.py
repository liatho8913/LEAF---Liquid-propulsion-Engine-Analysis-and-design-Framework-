from pathlib import Path

FILES = [
    Path("leaf_qt/foundation_result_key_audit.py"),
    Path("leaf_qt/variable_registry.py"),
]

PREFIXES = [
    "regen_candidate_population_inspector_",
]

for path in FILES:
    if not path.exists():
        print(f"SKIP {path}")
        continue

    text = path.read_text()

    if "KNOWN_DEVELOPMENT_KEYS = {" in text:
        additions = "\n".join(f'    "{p}",' for p in PREFIXES)
        if '"regen_candidate_population_inspector_",' not in text:
            text = text.replace(
                "KNOWN_DEVELOPMENT_KEYS = {",
                "KNOWN_DEVELOPMENT_KEYS = {\n" + additions
            )

    if "EXPECTED_PREFIX_VISIBILITY = {" in text:
        additions = "\n".join(f'    "{p}": "DIAGNOSTIC_ONLY",' for p in PREFIXES)
        if '"regen_candidate_population_inspector_": "DIAGNOSTIC_ONLY",' not in text:
            text = text.replace(
                "EXPECTED_PREFIX_VISIBILITY = {",
                "EXPECTED_PREFIX_VISIBILITY = {\n" + additions
            )

    path.write_text(text)
    print(f"PATCHED {path}")

print("POST16G_RESULT_KEYS_REGISTERED")
