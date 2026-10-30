from pathlib import Path
import re

text = Path("foundation_verification_output.txt").read_text(errors="ignore")

print("UNREGISTERED SUMMARY")
print("====================")

for line in text.splitlines():
    if "UNREGISTERED" in line or "Unregistered" in line:
        print(line)

print()
print("LIKELY UNREGISTERED KEY CANDIDATES")
print("==================================")

matches = re.findall(r"- ([A-Za-z0-9_]+)", text)

for key in sorted(set(matches)):
    if (
        "coolant_property_resolution" in key
        or "recommended_geometry_status_previous" in key
        or key.startswith("regen_coolant")
    ):
        print(key)
