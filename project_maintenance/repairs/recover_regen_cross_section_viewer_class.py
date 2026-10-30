from pathlib import Path
import shutil

target = Path("leaf_qt/regen_cross_section_viewer.py")

candidates = sorted(
    list(Path("leaf_qt").glob("regen_cross_section_viewer*.py*")),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)

print("SEARCHING CANDIDATES:")
for p in candidates:
    print("-", p)

for p in candidates:
    text = p.read_text(errors="ignore")
    if "class RegenCrossSectionViewer" in text:
        backup = target.with_suffix(".py.broken_missing_viewer_class")
        shutil.copy2(target, backup)
        shutil.copy2(p, target)
        print(f"\nRESTORED FROM: {p}")
        print(f"BROKEN COPY SAVED AS: {backup}")
        break
else:
    print("\nNO BACKUP CONTAINS class RegenCrossSectionViewer")
    print("Run:")
    print("grep -n '^class ' leaf_qt/regen_cross_section_viewer.py")
    raise SystemExit(1)

print("\nVERIFYING:")
text = target.read_text(errors="ignore")
print("HAS RegenCrossSectionViewer:", "class RegenCrossSectionViewer" in text)
print("HAS RegenCrossSectionCanvas:", "class RegenCrossSectionCanvas" in text)
