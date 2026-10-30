#!/usr/bin/env bash
set -euo pipefail

OUT="LEAF_UPLOAD_FINAL_$(date +%Y%m%d_%H%M%S).zip"
STAGE="_leaf_upload_final_stage"

rm -rf "$STAGE"
mkdir -p "$STAGE"

copy_dir () {
  src="$1"
  if [ -d "$src" ]; then
    mkdir -p "$STAGE/$src"
    find "$src" -type f \
      ! -path "*/__pycache__/*" \
      ! -name "*.pyc" \
      ! -name "*.pyo" \
      ! -name "*.zip" \
      ! -name "*.dll" \
      ! -name "*.pyd" \
      ! -name "*.so" \
      ! -name "*.dylib" \
      ! -name "*.exe" \
      ! -name "*.dmg" \
      ! -name "*.mp4" \
      ! -name "*.mov" \
      ! -name "*.avi" \
      ! -name "*.phase_*_backup" \
      ! -name "*.bak" \
      ! -name "*.backup" \
      ! -name "*.old" \
      ! -path "*/_external_repository_quarantine/*" \
      ! -path "*/dist/*" \
      ! -path "*/dist_*/*" \
      ! -path "*/build/*" \
      ! -path "*/build_*/*" \
      -exec sh -c '
        for f do
          mkdir -p "$0/$(dirname "$f")"
          cp "$f" "$0/$f"
        done
      ' "$STAGE" {} +
  fi
}

copy_dir leaf_qt
copy_dir project_maintenance
copy_dir project_evidence/generated_artifacts
copy_dir project_evidence/phase_artifacts/project_maintenance
copy_dir project_evidence/phase_artifacts/leaf_qt
copy_dir artifacts
copy_dir _handover_exports
copy_dir tests
copy_dir test
copy_dir docs
copy_dir reports
copy_dir resources
copy_dir assets
copy_dir data

find . -maxdepth 1 -type f \( \
  -name "*.py" -o \
  -name "*.md" -o \
  -name "*.txt" -o \
  -name "*.json" -o \
  -name "*.toml" -o \
  -name "*.yaml" -o \
  -name "*.yml" -o \
  -name "requirements*.txt" \
\) \
  ! -name "*.zip" \
  ! -name "*.bak" \
  ! -name "*.backup" \
  ! -name "*.old" \
  -exec cp {} "$STAGE/" \;

{
  echo "LEAF FINAL CHAT UPLOAD"
  echo "Generated: $(date)"
  echo
  echo "Files included:"
  find "$STAGE" -type f | sort
  echo
  echo "Python version:"
  python --version 2>&1 || true
  echo
  echo "Git status:"
  git status --short 2>/dev/null || true
} > "$STAGE/LEAF_UPLOAD_MANIFEST.txt"

rm -f "$OUT"

if command -v ditto >/dev/null 2>&1; then
  ditto -c -k --sequesterRsrc --keepParent "$STAGE" "$OUT"
else
  zip -r -9 "$OUT" "$STAGE" >/dev/null
fi

echo
if [ -f "$OUT" ]; then
  echo "CREATED_OK: $OUT"
  du -h "$OUT"
else
  echo "FAILED: zip was not created"
  exit 1
fi

echo
echo "Largest included files:"
find "$STAGE" -type f -exec du -h {} + | sort -hr | head -30 || true

rm -rf "$STAGE"

echo
echo "UPLOAD_THIS_FILE:"
echo "$OUT"
