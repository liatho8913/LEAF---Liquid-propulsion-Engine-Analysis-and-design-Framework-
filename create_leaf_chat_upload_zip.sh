#!/usr/bin/env bash
set -euo pipefail

OUT="LEAF_FULL_STATUS_CHAT_UPLOAD_$(date +%Y%m%d_%H%M%S).zip"
STAGE="_leaf_chat_upload_stage"

rm -rf "$STAGE"
mkdir -p "$STAGE"

echo "Creating LEAF status package..."

# Core source/runtime
for p in \
  leaf_qt \
  project_maintenance \
  tests \
  test \
  scripts \
  docs \
  reports \
  project_reports \
  project_evidence \
  architecture \
  data \
  resources \
  assets
do
  if [ -e "$p" ]; then
    rsync -a "$p" "$STAGE/" \
      --exclude "__pycache__" \
      --exclude ".pytest_cache" \
      --exclude ".mypy_cache" \
      --exclude ".ruff_cache" \
      --exclude ".venv" \
      --exclude "venv" \
      --exclude "*.pyc" \
      --exclude "*.pyo" \
      --exclude "*.log" \
      --exclude "*.tmp" \
      --exclude "*.bak" \
      --exclude "*.backup" \
      --exclude "*.old" \
      --exclude "*.zip" \
      --exclude "*.mp4" \
      --exclude "*.mov" \
      --exclude "*.avi" \
      --exclude "*.dmg" \
      --exclude "*.exe" \
      --exclude "*.app" \
      --exclude "dist" \
      --exclude "build"
  fi
done

# Important root files
find . -maxdepth 1 -type f \( \
  -name "*.py" -o \
  -name "*.md" -o \
  -name "*.txt" -o \
  -name "*.json" -o \
  -name "*.toml" -o \
  -name "*.yaml" -o \
  -name "*.yml" -o \
  -name "requirements*.txt" -o \
  -name "pyproject.toml" \
  -name "setup.py" \
\) -exec cp {} "$STAGE/" \;

# Add compact repository inventory
{
  echo "LEAF CHAT UPLOAD INVENTORY"
  echo "Generated: $(date)"
  echo
  echo "Git status:"
  git status --short 2>/dev/null || true
  echo
  echo "Tracked files:"
  git ls-files 2>/dev/null || true
  echo
  echo "All relevant files:"
  find . \
    -path "./.git" -prune -o \
    -path "./.venv" -prune -o \
    -path "./venv" -prune -o \
    -path "./__pycache__" -prune -o \
    -path "./$STAGE" -prune -o \
    -type f \
    ! -name "*.pyc" \
    ! -name "*.zip" \
    ! -name "*.mp4" \
    ! -name "*.mov" \
    ! -name "*.avi" \
    ! -name "*.exe" \
    ! -name "*.dmg" \
    -print | sort
} > "$STAGE/LEAF_REPOSITORY_INVENTORY.txt"

# Add quick Python compile status if possible
{
  echo "LEAF QUICK STATUS"
  echo "Generated: $(date)"
  echo
  python --version
  echo
  echo "Compile check:"
  python -m compileall -q leaf_qt project_maintenance . 2>&1 || true
} > "$STAGE/LEAF_QUICK_STATUS.txt"

# Create compressed zip
rm -f "$OUT"
zip -r -9 "$OUT" "$STAGE" >/dev/null

echo
echo "Created: $OUT"
du -h "$OUT"

echo
echo "Largest included files:"
find "$STAGE" -type f -exec du -h {} + | sort -hr | head -30

rm -rf "$STAGE"

echo
echo "Upload this zip into the chat:"
echo "$OUT"
