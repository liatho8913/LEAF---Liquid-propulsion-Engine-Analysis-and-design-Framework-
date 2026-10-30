from pathlib import Path
import re

log_file = Path("foundation_verification_output.txt")

if not log_file.exists():
    print("foundation_verification_output.txt not found.")
    print("Run:")
    print("python leaf_qt/run_foundation_verification.py > foundation_verification_output.txt")
    raise SystemExit

text = log_file.read_text(errors="ignore")

keys = sorted(set(
    re.findall(
        r"- ([A-Za-z0-9_]+)",
        text
    )
))

print("\nPOSSIBLE UNREGISTERED KEYS\n")
for key in keys:
    print(key)
