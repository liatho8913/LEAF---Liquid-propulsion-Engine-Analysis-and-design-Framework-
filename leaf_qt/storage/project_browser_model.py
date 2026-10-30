from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from leaf_qt.storage.canonical_storage import CanonicalStorageOwner
from leaf_qt.storage.design_manifest import DESIGN_MANIFEST_FILENAME, DesignManifest
from leaf_qt.storage.project_manifest import PROJECT_MANIFEST_FILENAME, ProjectManifest
from leaf_qt.storage.storage_validation_repair import StorageValidationRepairOwner
from leaf_qt.encrypted_container import (
    DESIGN_MANIFEST_RESOURCE,
    PROJECT_ROOT_RESOURCE,
    SCHEMA as ENCRYPTED_CONTAINER_SCHEMA,
)

SCHEMA = "LEAF_PROJECT_BROWSER_MODEL_PHASE_25I_V1"


@dataclass(frozen=True)
class DesignBrowserItem:
    design_id: str
    design_name: str
    path: str
    parent_project_id: str
    engine_type: str
    dirty_state: str
    validation_refs: list[str] = field(default_factory=list)
    report_refs: list[str] = field(default_factory=list)
    export_refs: list[str] = field(default_factory=list)
    runtime_last_opened: str = ""
    broken_links: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_DESIGN_BROWSER_ITEM_PHASE_25I_V1"
        return payload


@dataclass(frozen=True)
class ProjectBrowserItem:
    project_id: str
    project_name: str
    path: str
    active_designs: list[str] = field(default_factory=list)
    linked_reports: list[str] = field(default_factory=list)
    linked_exports: list[str] = field(default_factory=list)
    designs: list[DesignBrowserItem] = field(default_factory=list)
    broken_links: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_PROJECT_BROWSER_ITEM_PHASE_25I_V1"
        payload["designs"] = [design.snapshot() for design in self.designs]
        return payload


class ProjectBrowserModel:
    """
    Non-Qt project browser model.

    This owns browse/read-only model assembly only.

    It does not own:
    - Qt widgets
    - project creation
    - save/load execution
    - report generation
    - solver payloads
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.storage = CanonicalStorageOwner(self.root)
        self.validation = StorageValidationRepairOwner(self.root)

    def project_manifest_paths(self) -> list[Path]:
        projects_root = self.storage.canonical_path("projects")
        if not projects_root.exists():
            return []
        return sorted(projects_root.rglob(PROJECT_MANIFEST_FILENAME))

    def design_manifest_paths(self) -> list[Path]:
        designs_root = self.storage.canonical_path("designs")
        if not designs_root.exists():
            return []
        return sorted(designs_root.rglob(DESIGN_MANIFEST_FILENAME))

    def build(self) -> dict[str, Any]:
        validation_result = self.validation.validate(repair=False)
        issues = validation_result.get("issues", [])

        issues_by_path: dict[str, list[str]] = {}
        for issue in issues:
            path = issue.get("path", "")
            message = issue.get("message", "")
            if path:
                issues_by_path.setdefault(path, []).append(message)

        designs_by_path: dict[str, DesignBrowserItem] = {}

        for design_path in self.design_manifest_paths():
            try:
                design_payload = json.loads(
                    design_path.read_text(
                        encoding="utf-8"
                    )
                )

                if (
                    isinstance(
                        design_payload,
                        dict,
                    )
                    and
                    design_payload.get(
                        "schema"
                    )
                    ==
                    ENCRYPTED_CONTAINER_SCHEMA
                    and
                    design_payload.get(
                        "resource_type"
                    )
                    ==
                    DESIGN_MANIFEST_RESOURCE
                ):

                    encrypted_design_id = str(
                        design_payload.get(
                            "resource_id",
                            "",
                        )
                    ).strip()

                    encrypted_project_id = str(
                        design_payload.get(
                            "project_id",
                            "",
                        )
                    ).strip()


                    if not encrypted_design_id.startswith(
                        "design_"
                    ):

                        raise ValueError(
                            "encrypted_design_id_invalid"
                        )


                    if not encrypted_project_id.startswith(
                        "project_"
                    ):

                        raise ValueError(
                            "encrypted_design_parent_project_id_invalid"
                        )


                    locked_issues = [
                        "encrypted_design_locked"
                    ]

                    locked_issues.extend(
                        issues_by_path.get(
                            str(
                                design_path
                            ),
                            [],
                        )
                    )


                    designs_by_path[
                        str(
                            design_path.resolve()
                        )
                    ] = DesignBrowserItem(
                        design_id=
                            encrypted_design_id,

                        design_name=
                            "Encrypted Design (Locked)",

                        path=
                            str(
                                design_path
                            ),

                        parent_project_id=
                            encrypted_project_id,

                        engine_type=
                            "",

                        dirty_state=
                            "locked",

                        broken_links=
                            sorted(
                                set(
                                    locked_issues
                                )
                            ),
                    )

                    continue


                design = (
                    DesignManifest.from_dict(
                        design_payload
                    )
                )

            except Exception as exc:
                designs_by_path[str(design_path.resolve())] = DesignBrowserItem(
                    design_id="unreadable",
                    design_name=design_path.parent.name,
                    path=str(design_path),
                    parent_project_id="",
                    engine_type="",
                    dirty_state="unknown",
                    broken_links=[repr(exc)],
                )
                continue

            broken_links = list(issues_by_path.get(str(design_path), []))

            for ref in design.report_refs + design.export_refs + design.validation_refs:
                if ref and not Path(ref).exists():
                    broken_links.append(f"missing_link:{ref}")

            designs_by_path[str(design_path.resolve())] = DesignBrowserItem(
                design_id=design.design_id,
                design_name=design.design_name,
                path=str(design_path),
                parent_project_id=design.parent_project_id,
                engine_type=design.engine_type,
                dirty_state=design.dirty_state,
                validation_refs=list(design.validation_refs),
                report_refs=list(design.report_refs),
                export_refs=list(design.export_refs),
                runtime_last_opened=design.runtime_last_opened,
                broken_links=sorted(set(broken_links)),
            )

        projects: list[ProjectBrowserItem] = []

        for project_path in self.project_manifest_paths():
            try:
                project_payload = json.loads(
                    project_path.read_text(
                        encoding="utf-8"
                    )
                )

                if (
                    isinstance(
                        project_payload,
                        dict,
                    )
                    and
                    project_payload.get(
                        "schema"
                    )
                    ==
                    ENCRYPTED_CONTAINER_SCHEMA
                    and
                    project_payload.get(
                        "resource_type"
                    )
                    ==
                    PROJECT_ROOT_RESOURCE
                ):

                    encrypted_project_id = str(
                        project_payload.get(
                            "project_id",
                            "",
                        )
                    ).strip()

                    if not encrypted_project_id.startswith(
                        "project_"
                    ):
                        raise ValueError(
                            "encrypted_project_id_invalid"
                        )

                    encrypted_project_designs = [
                        item
                        for item
                        in designs_by_path.values()
                        if (
                            item.parent_project_id
                            ==
                            encrypted_project_id
                        )
                    ]


                    locked_project_issues = [
                        "encrypted_project_locked"
                    ]

                    locked_project_issues.extend(
                        issues_by_path.get(
                            str(
                                project_path
                            ),
                            [],
                        )
                    )


                    projects.append(
                        ProjectBrowserItem(
                            project_id=
                                encrypted_project_id,

                            project_name=
                                "Encrypted Project (Locked)",

                            path=
                                str(
                                    project_path
                                ),

                            active_designs=[
                                item.path
                                for item
                                in encrypted_project_designs
                            ],

                            designs=
                                encrypted_project_designs,

                            broken_links=
                                sorted(
                                    set(
                                        locked_project_issues
                                    )
                                ),
                        )
                    )

                    continue

                project = (
                    ProjectManifest.from_dict(
                        project_payload
                    )
                )

            except Exception as exc:
                projects.append(
                    ProjectBrowserItem(
                        project_id="unreadable",
                        project_name=project_path.parent.name,
                        path=str(project_path),
                        broken_links=[repr(exc)],
                    )
                )
                continue

            project_designs = []

            for design_ref in project.active_designs:
                resolved_design_ref = str(
                    self.storage.resolve_ref(
                        design_ref
                    ).resolve()
                )

                design_item = designs_by_path.get(
                    resolved_design_ref
                )

                if design_item is not None:
                    project_designs.append(design_item)

            broken_links = list(issues_by_path.get(str(project_path), []))

            for ref in project.active_designs:
                if (
                    ref
                    and not self.storage.resolve_ref(ref).exists()
                ):
                    broken_links.append(
                        f"missing_link:{ref}"
                    )

            for ref in project.linked_reports + project.linked_exports:
                if ref and not Path(ref).exists():
                    broken_links.append(f"missing_link:{ref}")

            projects.append(
                ProjectBrowserItem(
                    project_id=project.project_id,
                    project_name=project.project_name,
                    path=str(project_path),
                    active_designs=list(project.active_designs),
                    linked_reports=list(project.linked_reports),
                    linked_exports=list(project.linked_exports),
                    designs=project_designs,
                    broken_links=sorted(set(broken_links)),
                )
            )

        return {
            "schema": SCHEMA,
            "root": str(self.root),
            "projects": [project.snapshot() for project in projects],
            "project_count": len(projects),
            "design_count": len(designs_by_path),
            "issue_count": validation_result.get("issue_count", 0),
            "error_count": validation_result.get("error_count", 0),
            "qt_owns_project_browser": False,
            "model_only": True,
            "read_only": True,
            "stores_solver_payloads": False,
            "stores_report_payloads": False,
            "stores_validation_payloads": False,
        }

    def resolve_project_manifest_for_design(
        self,
        design_manifest_path: str | Path,
    ) -> Path | None:
        """
        Resolve the canonical project manifest owning a design manifest.

        The design's parent_project_id is the primary identity relationship.
        active_designs is used as the explicit project-side relationship when
        its stored path representation still resolves to the selected design.
        """
        design_manifest_path = Path(
            design_manifest_path
        ).resolve()

        design_manifest = DesignManifest.from_dict(
            json.loads(
                design_manifest_path.read_text(
                    encoding="utf-8",
                )
            )
        )

        parent_matches: list[Path] = []

        for project_manifest_path in self.project_manifest_paths():

            try:
                project_manifest = ProjectManifest.from_dict(
                    json.loads(
                        project_manifest_path.read_text(
                            encoding="utf-8",
                        )
                    )
                )

            except (
                OSError,
                ValueError,
                KeyError,
                TypeError,
                json.JSONDecodeError,
            ):
                continue

            if (
                project_manifest.project_id
                != design_manifest.parent_project_id
            ):
                continue

            parent_matches.append(
                project_manifest_path
            )

            for design_ref in project_manifest.active_designs:

                ref_path = self.storage.resolve_ref(
                    design_ref
                )

                if (
                    str(ref_path)
                    == str(design_manifest_path)
                ):
                    return project_manifest_path

                try:
                    if (
                        ref_path.resolve()
                        == design_manifest_path
                    ):
                        return project_manifest_path
                except OSError:
                    continue

        if len(parent_matches) == 1:
            return parent_matches[0]

        return None

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "root": str(self.root),
            "lists_projects": True,
            "lists_designs": True,
            "shows_linked_reports": True,
            "shows_linked_exports": True,
            "shows_dirty_state": True,
            "shows_validation_refs": True,
            "shows_broken_links": True,
            "qt_owns_project_browser": False,
            "model_only": True,
            "read_only": True,
        }


project_browser_model = ProjectBrowserModel()
