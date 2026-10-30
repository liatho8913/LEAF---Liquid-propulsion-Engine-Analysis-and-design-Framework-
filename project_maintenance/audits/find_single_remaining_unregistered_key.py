from pathlib import Path
import re

text = Path(
    "leaf_qt/foundation_result_key_audit.py"
).read_text(errors="ignore")

print("VERIFYING AUDIT FILE EXISTS")

audit_text = Path(
    "leaf_qt/foundation_result_key_audit.py"
).read_text(errors="ignore")

print("DONE")
