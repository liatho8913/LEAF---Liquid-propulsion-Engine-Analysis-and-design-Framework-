from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT = ROOT / f"LEAF_AUDIT_FILES_{STAMP}.zip"

FILES = [
    "leaf_qt/foundation_result_key_audit.py",
    "leaf_qt/output_ownership_audit.py",
    "leaf_qt/foundation_attachment_pipeline.py",
    "leaf_qt/foundation_layer_controller.py",
    "leaf_qt/run_foundation_verification.py",
]

with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
    for rel in FILES:
        path = ROOT / rel
        if path.exists():
            z.write(path, rel)
            print(f"ADDED {rel}")
        else:
            print(f"MISSING {rel}")

print()
print("Created:")
print(OUT)
