from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from leaf_qt.storage.canonical_storage import CANONICAL_ROOTS, LEGACY_IMPORT_ONLY_ROOTS

SCHEMA = "LEAF_LEGACY_IMPORT_SEARCH_LOCATIONS_PHASE_25G_V1"

DEFAULT_LEGACY_SEARCH_ROOTS = {
    "leaf_qt": "legacy_application_tree_import_only",
    "project_evidence": "generated_evidence_import_only",
    "_leaf_repository_cleanup_candidates": "cleanup_candidate_import_only",
    "_external_repository_quarantine": "external_quarantine_import_only",
}


@dataclass(frozen=True)
class LegacyImportLocation:
    root_name: str
    path: str
    reason: str
    import_only: bool = True
    authoritative: bool = False
    auto_delete_enabled: bool = False
    auto_archive_enabled: bool = False

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_LEGACY_IMPORT_LOCATION_PHASE_25G_V1"
        return payload


class LegacyImportSearchLocations:
    """
    Defines legacy paths that may be searched/imported from.

    This owns boundary policy only.

    It does not:
    - move files
    - delete files
    - archive files
    - treat legacy paths as canonical storage
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()

    def locations(self) -> list[LegacyImportLocation]:
        return [
            LegacyImportLocation(
                root_name=root_name,
                path=str(self.root / root_name),
                reason=reason,
            )
            for root_name, reason in sorted(DEFAULT_LEGACY_SEARCH_ROOTS.items())
        ]

    def is_legacy_import_only(self, path: str | Path) -> bool:
        candidate = Path(path)

        if candidate.is_absolute():
            try:
                candidate = candidate.relative_to(self.root)
            except ValueError:
                return False

        return bool(candidate.parts and candidate.parts[0] in DEFAULT_LEGACY_SEARCH_ROOTS)

    def is_authoritative_storage(self, path: str | Path) -> bool:
        candidate = Path(path)

        if candidate.is_absolute():
            try:
                candidate = candidate.relative_to(self.root)
            except ValueError:
                return False

        return bool(candidate.parts and candidate.parts[0] in CANONICAL_ROOTS.values())

    def classify_path(self, path: str | Path) -> dict[str, Any]:
        candidate = Path(path)
        is_legacy = self.is_legacy_import_only(candidate)
        is_authoritative = self.is_authoritative_storage(candidate)

        return {
            "schema": "LEAF_STORAGE_PATH_CLASSIFICATION_PHASE_25G_V1",
            "path": str(path),
            "legacy_import_only": is_legacy,
            "authoritative_storage": is_authoritative,
            "safe_for_import_search": is_legacy or is_authoritative,
            "safe_for_auto_delete": False,
            "safe_for_auto_archive": False,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "legacy_locations": [location.snapshot() for location in self.locations()],
            "canonical_roots": dict(CANONICAL_ROOTS),
            "legacy_import_only_roots": sorted(DEFAULT_LEGACY_SEARCH_ROOTS),
            "legacy_storage_authoritative": False,
            "quarantine_storage_authoritative": False,
            "leaf_qt_storage_authoritative": False,
            "project_evidence_authoritative": False,
            "auto_delete_enabled": False,
            "auto_archive_enabled": False,
            "moves_files": False,
            "deletes_files": False,
            "archives_files": False,
        }


legacy_import_search_locations = LegacyImportSearchLocations()
