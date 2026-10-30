#!/usr/bin/env bash
set -euo pipefail

OUT="LEAF_STRICT_STATUS_CHAT_UPLOAD_$(date +%Y%m%d_%H%M%S).zip"
STAGE="_leaf_strict_chat_upload_stage"

rm -rf "$STAGE"
mkdir -p "$STAGE"

rsync -a . "$STAGE/" \
  --exclude ".git" \
  --exclude ".venv" \
  --exclude "venv" \
  --exclude "__pycache__" \
  --exclude ".pytest_cache" \
  --exclude ".mypy_cache" \
  --exclude ".ruff_cache" \
  --exclude "*.pyc" \
  --exclude "*.pyo" \
  --exclude "*.zip" \
  --exclude "*.mp4" \
  --exclude "*.mov" \
  --exclude "*.avi" \
  --exclude "*.dmg" \
  --exclude "*.exe" \
  --exclude "*.app" \
  --exclude "*.dll" \
  --exclude "*.pyd" \
  --exclude "*.so" \
  --exclude "*.dylib" \
  --exclude "dist" \
  --exclude "dist_*" \
  --exclude "build" \
  --exclude "build_*" \
  --exclude "_leaf_*_stage" \
  --exclude "_external_repository_quarantine" \
  --exclude "_external_repository_quarantine/***" \
  --exclude "project_evidence/phase_artifacts/_external_repository_quarantine" \
  --exclude "project_evidence/phase_artifacts/_external_repository_quarantine/***" \
  --exclude "project_evidence/**/_external_repository_quarantine" \
  --exclude "project_evidence/**/_external_repository_quarantine/***" \
  --exclude "LEAF_PY_AUDIT_*" \
  --exclude "leaf_qt/*.phase_*_backup" \
  --exclude "project_maintenance/*.phase_*_backup"

{
  echo "LEAF STRICT CHAT UPLOAD STATUS"
  echo "Generated: $(date)"
  echo
  echo "Git status:"
  git status --short 2>/dev/null || true
  echo
  echo "Useful top-level files:"
  find . -maxdepth 3 -type f \
    ! -path "./.git/*" \
    ! -path "./.venv/*" \
    ! -path "./venv/*" \
    ! -path "./_external_repository_quarantine/*" \
    ! -path "./dist_*/*" \
    ! -path "./build_*/*" \
    ! -path "./LEAF_PY_AUDIT_*/*" \
    ! -name "*.zip" \
    ! -name "*.pyc" \
    ! -name "*.dll" \
    ! -name "*.pyd" | sort
} > "$STAGE/LEAF_STRICT_UPLOAD_INVENTORY.txt"

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
echo "Upload this strict zip:"
echo "$OUT"
