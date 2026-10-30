from pathlib import Path

path = Path("leaf_qt/foundation_result_key_audit.py")
text = path.read_text()

needle = 'KNOWN_DEVELOPMENT_KEYS = {'

if '"coolant_mass_flow_fraction",' not in text:
    text = text.replace(
        needle,
        needle + '\n    "coolant_mass_flow_fraction",'
    )

path.write_text(text)
print("REGISTERED_COOLANT_MASS_FLOW_FRACTION_AS_KNOWN_DEVELOPMENT_KEY")
