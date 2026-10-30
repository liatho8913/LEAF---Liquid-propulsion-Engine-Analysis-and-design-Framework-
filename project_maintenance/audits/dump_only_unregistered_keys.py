from pathlib import Path
import re

path = Path("foundation_verification_output.txt")

if not path.exists():
    print(
        "Run:\n"
        "python leaf_qt/run_foundation_verification.py "
        "> foundation_verification_output.txt"
    )
    raise SystemExit

text = path.read_text(errors="ignore")

capture = False

for line in text.splitlines():

    if line.strip() == "UNREGISTERED KEYS":
        capture = True
        continue

    if capture:

        if (
            line.startswith("Known development")
            or line.startswith("Visibility counts")
            or line.startswith("Possible Main Output")
            or line.startswith("Wrong prefix")
        ):
            break

        if line.strip():
            print(line)
