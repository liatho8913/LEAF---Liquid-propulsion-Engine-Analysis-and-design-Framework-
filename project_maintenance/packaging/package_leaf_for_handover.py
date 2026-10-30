from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT = ROOT / f"LEAF_HANDOVER_PACKAGE_{STAMP}.zip"

INCLUDE_EXTS = {
    ".py", ".txt", ".md", ".json", ".csv", ".yml", ".yaml",
    ".toml", ".ini", ".cfg", ".bat", ".sh"
}

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "dist", "build", ".idea",
    ".DS_Store"
}

EXCLUDE_FILES = {
    OUT.name,
}

def should_include(path: Path) -> bool:
    parts = set(path.parts)

    if parts & EXCLUDE_DIRS:
        return False

    if path.name in EXCLUDE_FILES:
        return False

    if path.name.endswith(".pyc"):
        return False

    return path.suffix.lower() in INCLUDE_EXTS

files = [
    p for p in ROOT.rglob("*")
    if p.is_file() and should_include(p.relative_to(ROOT))
]

with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
    for file in files:
        z.write(file, file.relative_to(ROOT))

print("Created package:")
print(OUT)
print()
print(f"Files included: {len(files)}")
