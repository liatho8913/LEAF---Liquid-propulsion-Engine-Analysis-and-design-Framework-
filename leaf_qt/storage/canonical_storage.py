from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_CANONICAL_STORAGE_PHASE_25A_V1"

CANONICAL_PROJECT_ROOT = "LEAF_Projects"
CANONICAL_DESIGN_ROOT = "LEAF_Designs"
CANONICAL_REPORT_ROOT = "LEAF_Reports"
CANONICAL_EXPORT_ROOT = "LEAF_Exports"
CANONICAL_VALIDATION_ROOT = "LEAF_Validation"

CANONICAL_ROOTS = {
    "projects": CANONICAL_PROJECT_ROOT,
    "designs": CANONICAL_DESIGN_ROOT,
    "reports": CANONICAL_REPORT_ROOT,
    "exports": CANONICAL_EXPORT_ROOT,
    "validation": CANONICAL_VALIDATION_ROOT,
}

LEGACY_IMPORT_ONLY_ROOTS = {
    "leaf_qt",
    "project_evidence",
    "_leaf_repository_cleanup_candidates",
    "_external_repository_quarantine",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def paths_match(
    left: str | Path | None,
    right: str | Path | None,
) -> bool:
    """
    Return whether two path references identify the same
    resolved filesystem location.

    This is the canonical LEAF path-equivalence mechanism.
    It is intentionally independent of storage-root
    membership.
    """
    if left is None or right is None:
        return False

    try:
        return (
            Path(left).resolve()
            == Path(right).resolve()
        )

    except OSError:
        return (
            str(
                Path(left).absolute()
            )
            ==
            str(
                Path(right).absolute()
            )
        )


@dataclass(frozen=True)
class CanonicalStorageRoot:
    key: str
    name: str
    path: str
    authoritative: bool
    user_facing: bool
    created_at: str = field(default_factory=utc_now)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_CANONICAL_STORAGE_ROOT_PHASE_25A_V1"
        return payload


class CanonicalStorageOwner:
    """
    Authoritative owner for user-facing LEAF storage roots.

    This owns paths and folder creation only.

    It does not own:
    - project manifests
    - design manifests
    - save/load payloads
    - report payloads
    - Qt widgets
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()

    def canonical_path(self, key: str) -> Path:
        if key not in CANONICAL_ROOTS:
            raise KeyError(f"canonical_storage_key_not_allowed:{key}")
        return self.root / CANONICAL_ROOTS[key]

    def resolve_ref(self, reference: str | Path) -> Path:
        """
        Resolve a stored canonical reference.

        Absolute references remain supported for backward compatibility.
        Relative references are interpreted from the LEAF repository root.
        """
        candidate = Path(reference)

        if candidate.is_absolute():
            return candidate

        return self.root / candidate

    def portable_ref(self, path: str | Path) -> str:
        """
        Return a repository-relative reference when the target belongs to
        this LEAF repository. External paths remain absolute.
        """
        candidate = Path(path)

        if not candidate.is_absolute():
            candidate = self.root / candidate

        try:
            return candidate.resolve().relative_to(
                self.root.resolve()
            ).as_posix()
        except ValueError:
            return str(candidate.resolve())

    def ensure_roots(self) -> list[CanonicalStorageRoot]:
        records: list[CanonicalStorageRoot] = []

        for key, folder_name in CANONICAL_ROOTS.items():
            path = self.root / folder_name
            path.mkdir(parents=True, exist_ok=True)

            records.append(
                CanonicalStorageRoot(
                    key=key,
                    name=folder_name,
                    path=str(path),
                    authoritative=True,
                    user_facing=True,
                )
            )

        return records

    def root_status(self) -> dict[str, dict[str, Any]]:
        status: dict[str, dict[str, Any]] = {}

        for key, folder_name in CANONICAL_ROOTS.items():
            path = self.root / folder_name
            status[key] = {
                "path": str(path),
                "exists": path.exists(),
                "is_dir": path.is_dir(),
                "authoritative": True,
                "user_facing": True,
            }

        return status

    def is_canonical_path(self, path: str | Path) -> bool:
        candidate = Path(path)

        if not candidate.is_absolute():
            candidate = self.root / candidate

        try:
            resolved_candidate = candidate.resolve()
        except FileNotFoundError:
            resolved_candidate = candidate.absolute()

        for folder_name in CANONICAL_ROOTS.values():
            root_path = (self.root / folder_name).resolve()
            if resolved_candidate == root_path or root_path in resolved_candidate.parents:
                return True

        return False

    def is_legacy_import_only_path(self, path: str | Path) -> bool:
        candidate = Path(path)

        if candidate.is_absolute():
            try:
                candidate = candidate.relative_to(self.root)
            except ValueError:
                return False

        return bool(candidate.parts and candidate.parts[0] in LEGACY_IMPORT_ONLY_ROOTS)

    def storage_policy(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "canonical_roots": dict(CANONICAL_ROOTS),
            "legacy_import_only_roots": sorted(LEGACY_IMPORT_ONLY_ROOTS),
            "canonical_storage_authoritative": True,
            "legacy_storage_authoritative": False,
            "quarantine_storage_authoritative": False,
            "qt_storage_authoritative": False,
            "user_facing_storage_at_root": True,
            "auto_delete_enabled": False,
            "auto_archive_enabled": False,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "root": str(self.root),
            "root_status": self.root_status(),
            "storage_policy": self.storage_policy(),
            "owns_project_manifest_payloads": False,
            "owns_design_manifest_payloads": False,
            "owns_report_payloads": False,
            "owns_export_payloads": False,
            "qt_owns_storage": False,
        }


canonical_storage_owner = CanonicalStorageOwner()
