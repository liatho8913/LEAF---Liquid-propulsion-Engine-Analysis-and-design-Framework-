from pathlib import Path

text = Path(
    "foundation_verification_output.txt"
).read_text(errors="ignore")

capture = False

for line in text.splitlines():

    if "UNREGISTERED KEYS" in line:
        capture = True
        continue

    if capture:

        if (
            line.startswith("Visibility counts")
            or line.startswith("Possible Main Output")
            or line.startswith("Wrong prefix")
            or line.startswith("Known development")
        ):
            break

        if line.strip():
            print(line)
