from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from leaf_qt.runtime.dirty_state_manager import DirtyStateManager
from leaf_qt.runtime.notification_centre import RuntimeNotificationCentre
from leaf_qt.runtime.report_router import RuntimeReportRouter
from leaf_qt.runtime.session_lifecycle import RuntimeSessionLifecycle
from leaf_qt.runtime.state_registry import RuntimeStateRegistry
from leaf_qt.storage.canonical_storage import CanonicalStorageOwner, paths_match
from leaf_qt.storage.design_manifest import DesignManifest, DesignManifestValidator
from leaf_qt.storage.project_manifest import PROJECT_MANIFEST_FILENAME, ProjectManifest, ProjectManifestValidator
from leaf_qt.security_context import SecurityContextOwner
import os
from uuid import uuid4
from leaf_qt.encrypted_container import (
    EncryptedContainerOwner,
)
from leaf_qt.key_custody import KeyCustodyOwner

SCHEMA = "LEAF_SAVE_LOAD_RUNTIME_BRIDGE_PHASE_25E_V1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


ENGINEERING_STATE_FILENAME = "engineering_state.json"


@dataclass(frozen=True)
class SaveLoadResult:
    action: str
    project_manifest_path: str
    design_manifest_path: str
    project_id: str
    design_id: str
    timestamp: str = field(default_factory=utc_now)

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": "LEAF_SAVE_LOAD_RESULT_PHASE_25E_V1",
            "action": self.action,
            "project_manifest_path": self.project_manifest_path,
            "design_manifest_path": self.design_manifest_path,
            "project_id": self.project_id,
            "design_id": self.design_id,
            "timestamp": self.timestamp,
        }


class SaveLoadRuntimeBridge:
    """
    Connects canonical storage to Programme 24 runtime services.

    This owns bridge behaviour only.

    It does not own:
    - Qt widgets
    - solver payloads
    - report payloads
    - validation execution
    """

    def __init__(
        self,
        session_lifecycle: RuntimeSessionLifecycle,
        state_registry: RuntimeStateRegistry,
        dirty_state_manager: DirtyStateManager,
        report_router: RuntimeReportRouter,
        notification_centre: RuntimeNotificationCentre,
        security_context: SecurityContextOwner | None = None,
        key_custody: KeyCustodyOwner | None = None,
        encrypted_container_owner: EncryptedContainerOwner | None = None,
    ) -> None:

        self.session_lifecycle = (
            session_lifecycle
        )

        self.state_registry = (
            state_registry
        )

        self.dirty_state_manager = (
            dirty_state_manager
        )

        self.report_router = (
            report_router
        )

        self.notification_centre = (
            notification_centre
        )

        self.security_context = (
            security_context
            or
            SecurityContextOwner()
        )

        self.key_custody = (
            key_custody
        )

        self.encrypted_container_owner = (
            encrypted_container_owner
        )

        self.project_validator = (
            ProjectManifestValidator()
        )

        self.design_validator = (
            DesignManifestValidator()
        )
        self._require_or_create_session()


    @staticmethod
    def _route_container_payload(
        path: str | Path,
    ) -> dict[str, Any] | None:

        from leaf_qt.encrypted_container import (
            SCHEMA as ENCRYPTED_CONTAINER_SCHEMA,
        )


        path = Path(
            path
        )


        try:

            payload = json.loads(
                path.read_text(
                    encoding="utf-8",
                )
            )

        except Exception:

            return None


        if not isinstance(
            payload,
            dict,
        ):

            return None


        if (
            payload.get(
                "schema"
            )
            !=
            ENCRYPTED_CONTAINER_SCHEMA
        ):

            return None


        return payload


    @classmethod
    def _route_is_encrypted(
        cls,
        path: str | Path,
    ) -> bool:

        return (
            cls._route_container_payload(
                path
            )
            is not None
        )


    def load_design(
        self,
        project_manifest_path: str | Path,
        design_manifest_path: str | Path,
        source: str = "save_load_runtime_bridge",
    ) -> SaveLoadResult:

        project_encrypted = (
            self._route_is_encrypted(
                project_manifest_path
            )
        )


        design_encrypted = (
            self._route_is_encrypted(
                design_manifest_path
            )
        )


        if (
            project_encrypted
            !=
            design_encrypted
        ):

            raise ValueError(
                "mixed_plaintext_encrypted_project_design_denied"
            )


        if project_encrypted:

            return (
                self._load_encrypted_design(
                    project_manifest_path,
                    design_manifest_path,
                    source=
                        source,
                )
            )


        return (
            self._load_plaintext_design(
                project_manifest_path,
                design_manifest_path,
                source=
                    source,
            )
        )


    def save_design(
        self,
        project_manifest_path: str | Path,
        design_manifest_path: str | Path,
        updates: dict[str, Any] | None = None,
        source: str = "save_load_runtime_bridge",
        engineering_state: dict[str, Any] | None = None,
    ) -> SaveLoadResult:

        project_encrypted = (
            self._route_is_encrypted(
                project_manifest_path
            )
        )


        design_encrypted = (
            self._route_is_encrypted(
                design_manifest_path
            )
        )


        if (
            project_encrypted
            !=
            design_encrypted
        ):

            raise ValueError(
                "mixed_plaintext_encrypted_project_design_denied"
            )


        if project_encrypted:

            return (
                self._save_encrypted_design(
                    project_manifest_path,
                    design_manifest_path,
                    updates=
                        updates,

                    source=
                        source,

                    engineering_state=
                        engineering_state,
                )
            )


        return (
            self._save_plaintext_design(
                project_manifest_path,
                design_manifest_path,
                updates=
                    updates,

                source=
                    source,

                engineering_state=
                    engineering_state,
            )
        )


    def load_design_engineering_state(
        self,
        design_manifest_path: str | Path,
    ) -> dict[str, Any]:

        if self._route_is_encrypted(
            design_manifest_path
        ):

            return (
                self
                ._load_encrypted_design_engineering_state(
                    design_manifest_path
                )
            )


        return (
            self
            ._load_plaintext_design_engineering_state(
                design_manifest_path
            )
        )


    def _open_encrypted_project_manifest(
        self,
        project_manifest_path: str | Path,
    ) -> tuple[
        ProjectManifest,
        dict[str, Any],
    ]:

        from leaf_qt.encrypted_container import (
            PROJECT_ROOT_RESOURCE,
        )


        project_manifest_path = Path(
            project_manifest_path
        )


        container = (
            self._route_container_payload(
                project_manifest_path
            )
        )


        if container is None:

            raise ValueError(
                "encrypted_project_container_required"
            )


        project_id = str(
            container.get(
                "project_id",
                "",
            )
        ).strip()


        classification = str(
            container.get(
                "security_classification",
                "",
            )
        ).strip()


        payload = (
            self.load_encrypted_resource(
                project_manifest_path,

                expected_project_id=
                    project_id,

                expected_security_classification=
                    classification,

                expected_resource_type=
                    PROJECT_ROOT_RESOURCE,

                expected_resource_id=
                    project_id,
            )
        )


        manifest = (
            ProjectManifest.from_dict(
                payload
            )
        )


        validation = (
            self.project_validator
            .validate(
                manifest
            )
        )


        if (
            validation.get(
                "passed"
            )
            is not True
        ):

            raise ValueError(
                "encrypted_project_manifest_invalid:"
                f"{validation.get('failures')}"
            )


        if (
            manifest.project_id
            !=
            project_id
        ):

            raise ValueError(
                "encrypted_project_clear_identity_mismatch"
            )


        return (
            manifest,
            container,
        )


    def _open_encrypted_design_manifest(
        self,
        design_manifest_path: str | Path,
        *,
        expected_project_id: str,
        expected_security_classification: str,
    ) -> tuple[
        DesignManifest,
        dict[str, Any],
    ]:

        from leaf_qt.encrypted_container import (
            DESIGN_MANIFEST_RESOURCE,
        )


        design_manifest_path = Path(
            design_manifest_path
        )


        container = (
            self._route_container_payload(
                design_manifest_path
            )
        )


        if container is None:

            raise ValueError(
                "encrypted_design_container_required"
            )


        design_id = str(
            container.get(
                "resource_id",
                "",
            )
        ).strip()


        payload = (
            self.load_encrypted_resource(
                design_manifest_path,

                expected_project_id=
                    expected_project_id,

                expected_security_classification=
                    expected_security_classification,

                expected_resource_type=
                    DESIGN_MANIFEST_RESOURCE,

                expected_resource_id=
                    design_id,
            )
        )


        manifest = (
            DesignManifest.from_dict(
                payload
            )
        )


        validation = (
            self.design_validator
            .validate(
                manifest
            )
        )


        if (
            validation.get(
                "passed"
            )
            is not True
        ):

            raise ValueError(
                "encrypted_design_manifest_invalid:"
                f"{validation.get('failures')}"
            )


        if (
            manifest.design_id
            !=
            design_id
        ):

            raise ValueError(
                "encrypted_design_clear_identity_mismatch"
            )


        return (
            manifest,
            container,
        )


    @staticmethod
    def _encrypted_project_manifest_path_for_design(design_manifest_path: str | Path, project_id: str) -> Path:
        storage = CanonicalStorageOwner(Path(design_manifest_path).resolve().parents[2])
        return storage.canonical_path("projects") / project_id / PROJECT_MANIFEST_FILENAME

    @staticmethod
    def _require_design_parent_project(design_manifest: DesignManifest, project_manifest: ProjectManifest) -> None:
        if design_manifest.parent_project_id != project_manifest.project_id:
            raise ValueError("design_parent_project_id_does_not_match_project")


    def _load_encrypted_design_engineering_state(
        self,
        design_manifest_path: str | Path,
    ) -> dict[str, Any]:

        from leaf_qt.encrypted_container import (
            ENGINEERING_STATE_RESOURCE,
        )

        design_manifest_path = Path(
            design_manifest_path
        )


        design_container = (
            self._route_container_payload(
                design_manifest_path
            )
        )


        if design_container is None:

            raise ValueError(
                "encrypted_design_container_required"
            )


        project_id = str(
            design_container.get(
                "project_id",
                "",
            )
        ).strip()


        classification = str(
            design_container.get(
                "security_classification",
                "",
            )
        ).strip()


        design_id = str(
            design_container.get(
                "resource_id",
                "",
            )
        ).strip()


        project_manifest_path = self._encrypted_project_manifest_path_for_design(
            design_manifest_path, project_id
        )


        project_manifest, _ = (
            self._open_encrypted_project_manifest(
                project_manifest_path
            )
        )


        self.security_context.require_project_access(
            project_manifest
        )


        design_manifest, _ = (
            self._open_encrypted_design_manifest(
                design_manifest_path,

                expected_project_id=
                    project_id,

                expected_security_classification=
                    classification,
            )
        )


        if (
            design_manifest.parent_project_id
            !=
            project_id
        ):

            raise ValueError(
                "encrypted_design_parent_project_id_does_not_match_project"
            )


        state_ref = str(
            design_manifest.engineering_state_ref
            or
            ""
        ).strip()


        if not state_ref:

            raise FileNotFoundError(
                "design_engineering_state_reference_missing"
            )


        state_ref_path = Path(
            state_ref
        )


        if (
            state_ref_path.is_absolute()
            or
            state_ref_path.name
            !=
            state_ref
        ):

            raise ValueError(
                "engineering_state_ref_must_be_design_local_filename"
            )


        state_path = (
            design_manifest_path.parent
            /
            state_ref_path
        )


        return (
            self.load_encrypted_resource(
                state_path,

                expected_project_id=
                    project_id,

                expected_security_classification=
                    classification,

                expected_resource_type=
                    ENGINEERING_STATE_RESOURCE,

                expected_resource_id=
                    design_id,
            )
        )


    def _load_encrypted_design(
        self,
        project_manifest_path: str | Path,
        design_manifest_path: str | Path,
        source: str = "save_load_runtime_bridge",
    ) -> SaveLoadResult:

        from leaf_qt.encrypted_container import (
            DESIGN_MANIFEST_RESOURCE,
        )


        project_manifest_path = Path(
            project_manifest_path
        )


        design_manifest_path = Path(
            design_manifest_path
        )


        (
            project_manifest,
            project_container,
        ) = (
            self._open_encrypted_project_manifest(
                project_manifest_path
            )
        )


        classification = (
            project_manifest
            .security_classification
        )


        (
            design_manifest,
            _,
        ) = (
            self._open_encrypted_design_manifest(
                design_manifest_path,

                expected_project_id=
                    project_manifest.project_id,

                expected_security_classification=
                    classification,
            )
        )


        self.security_context.require_project_access(
            project_manifest
        )


        if (
            design_manifest.parent_project_id
            !=
            project_manifest.project_id
        ):

            raise ValueError(
                "design_parent_project_id_does_not_match_project"
            )


        if str(
            design_manifest.engineering_state_ref
            or
            ""
        ).strip():

            self._load_encrypted_design_engineering_state(
                design_manifest_path
            )


        self._require_or_create_session()


        self.session_lifecycle.set_active_project(
            str(
                project_manifest_path
            )
        )


        self.session_lifecycle.set_active_design(
            str(
                design_manifest_path
            )
        )


        self.session_lifecycle.set_active_workspace(
            "engineering_workspace"
        )


        self.session_lifecycle.open_document(
            str(
                design_manifest_path
            ),
            "design_manifest",
        )


        self.state_registry.set(
            "active_project",
            str(
                project_manifest_path
            ),
            source=
                source,
        )


        self.state_registry.set(
            "active_design",
            str(
                design_manifest_path
            ),
            source=
                source,
        )


        self.state_registry.set(
            "current_workspace",
            "engineering_workspace",
            source=
                source,
        )


        design_manifest.mark_opened()

        design_manifest.dirty_state = (
            "saved"
        )


        self.save_encrypted_resource(
            design_manifest_path,
            design_manifest.snapshot(),

            project_id=
                project_manifest.project_id,

            security_classification=
                classification,

            resource_type=
                DESIGN_MANIFEST_RESOURCE,

            resource_id=
                design_manifest.design_id,

            portable_key_envelope=
                None,
        )


        self.dirty_state_manager.mark_saved(
            str(
                design_manifest_path
            ),
            "design",
            reason=
                "design_loaded",
            source=
                source,
        )


        self.report_router.diagnostic(
            source=
                source,

            title=
                "Design Loaded",

            summary=
                f"Loaded encrypted design manifest "
                f"{design_manifest.design_name}.",

            target_id=
                str(
                    design_manifest_path
                ),

            target_type=
                "design",

            payload_ref=
                str(
                    design_manifest_path
                ),
        )


        self.notification_centre.notify(
            category=
                "runtime",

            level=
                "success",

            title=
                "Design Loaded",

            message=
                f"{design_manifest.design_name} is now active.",

            source=
                source,

            target_id=
                str(
                    design_manifest_path
                ),

            target_type=
                "design",

            action_ref=
                str(
                    design_manifest_path
                ),
        )


        return SaveLoadResult(
            action=
                "load_design",

            project_manifest_path=
                str(
                    project_manifest_path
                ),

            design_manifest_path=
                str(
                    design_manifest_path
                ),

            project_id=
                project_manifest.project_id,

            design_id=
                design_manifest.design_id,
        )


    def _save_encrypted_design(
        self,
        project_manifest_path: str | Path,
        design_manifest_path: str | Path,
        updates: dict[str, Any] | None = None,
        source: str = "save_load_runtime_bridge",
        engineering_state: dict[str, Any] | None = None,
    ) -> SaveLoadResult:

        from leaf_qt.encrypted_container import (
            DESIGN_MANIFEST_RESOURCE,
            ENGINEERING_STATE_RESOURCE,
            PROJECT_ROOT_RESOURCE,
        )


        project_manifest_path = Path(
            project_manifest_path
        )


        design_manifest_path = Path(
            design_manifest_path
        )


        (
            project_manifest,
            project_container,
        ) = (
            self._open_encrypted_project_manifest(
                project_manifest_path
            )
        )


        classification = (
            project_manifest
            .security_classification
        )


        (
            design_manifest,
            _,
        ) = (
            self._open_encrypted_design_manifest(
                design_manifest_path,

                expected_project_id=
                    project_manifest.project_id,

                expected_security_classification=
                    classification,
            )
        )


        self.security_context.require_project_modify(
            project_manifest
        )


        if (
            design_manifest.parent_project_id
            !=
            project_manifest.project_id
        ):

            raise ValueError(
                "design_parent_project_id_does_not_match_project"
            )


        updates = dict(
            updates
            or
            {}
        )


        for key, value in (
            updates.items()
        ):

            if not hasattr(
                design_manifest,
                key,
            ):

                raise KeyError(
                    "design_manifest_update_key_not_allowed:"
                    f"{key}"
                )


            setattr(
                design_manifest,
                key,
                value,
            )


        if engineering_state is not None:

            if not isinstance(
                engineering_state,
                dict,
            ):

                raise TypeError(
                    "engineering_state_payload_must_be_dict"
                )


            engineering_state_path = (
                design_manifest_path.parent
                /
                ENGINEERING_STATE_FILENAME
            )


            self.save_encrypted_resource(
                engineering_state_path,
                engineering_state,

                project_id=
                    project_manifest.project_id,

                security_classification=
                    classification,

                resource_type=
                    ENGINEERING_STATE_RESOURCE,

                resource_id=
                    design_manifest.design_id,

                portable_key_envelope=
                    None,
            )


            design_manifest.engineering_state_ref = (
                ENGINEERING_STATE_FILENAME
            )


        design_manifest.dirty_state = (
            "saved"
        )


        design_manifest.touch()


        self.save_encrypted_resource(
            design_manifest_path,
            design_manifest.snapshot(),

            project_id=
                project_manifest.project_id,

            security_classification=
                classification,

            resource_type=
                DESIGN_MANIFEST_RESOURCE,

            resource_id=
                design_manifest.design_id,

            portable_key_envelope=
                None,
        )


        storage_root = (
            project_manifest_path
            .resolve()
            .parents[
                2
            ]
        )


        storage = (
            CanonicalStorageOwner(
                storage_root
            )
        )


        portable_design_ref = (
            storage.portable_ref(
                design_manifest_path
            )
        )


        resolved_design_path = (
            design_manifest_path
            .resolve()
        )


        normalised_active_designs = []

        matching_design_found = False


        for existing_ref in (
            project_manifest.active_designs
        ):

            existing_path = (
                storage.resolve_ref(
                    existing_ref
                )
            )


            try:

                is_same_design = (
                    existing_path.resolve()
                    ==
                    resolved_design_path
                )

            except OSError:

                is_same_design = False


            if is_same_design:

                if not matching_design_found:

                    normalised_active_designs.append(
                        portable_design_ref
                    )

                    matching_design_found = True


                continue


            normalised_active_designs.append(
                existing_ref
            )


        if not matching_design_found:

            normalised_active_designs.append(
                portable_design_ref
            )


        if (
            normalised_active_designs
            !=
            project_manifest.active_designs
        ):

            project_manifest.active_designs = (
                normalised_active_designs
            )


            project_manifest.touch()


            portable_key_envelope = (
                project_container.get(
                    "portable_key_envelope"
                )
            )


            if not isinstance(
                portable_key_envelope,
                dict,
            ):

                raise ValueError(
                    "encrypted_project_portable_key_envelope_missing"
                )


            self.save_encrypted_resource(
                project_manifest_path,
                project_manifest.snapshot(),

                project_id=
                    project_manifest.project_id,

                security_classification=
                    classification,

                resource_type=
                    PROJECT_ROOT_RESOURCE,

                resource_id=
                    project_manifest.project_id,

                portable_key_envelope=
                    portable_key_envelope,
            )


        self._require_or_create_session()


        self.session_lifecycle.set_active_project(
            str(
                project_manifest_path
            )
        )


        self.session_lifecycle.set_active_design(
            str(
                design_manifest_path
            )
        )


        self.state_registry.set(
            "active_project",
            str(
                project_manifest_path
            ),
            source=
                source,
        )


        self.state_registry.set(
            "active_design",
            str(
                design_manifest_path
            ),
            source=
                source,
        )


        self.dirty_state_manager.mark_saved(
            str(
                design_manifest_path
            ),
            "design",
            reason=
                "design_saved",
            source=
                source,
        )


        self.report_router.report(
            source=
                source,

            title=
                "Design Saved",

            summary=
                f"Saved encrypted design manifest "
                f"{design_manifest.design_name}.",

            target_id=
                str(
                    design_manifest_path
                ),

            target_type=
                "design",

            payload_ref=
                str(
                    design_manifest_path
                ),
        )


        self.notification_centre.notify(
            category=
                "save",

            level=
                "success",

            title=
                "Design Saved",

            message=
                f"{design_manifest.design_name} was saved.",

            source=
                source,

            target_id=
                str(
                    design_manifest_path
                ),

            target_type=
                "design",

            action_ref=
                str(
                    design_manifest_path
                ),
        )


        return SaveLoadResult(
            action=
                "save_design",

            project_manifest_path=
                str(
                    project_manifest_path
                ),

            design_manifest_path=
                str(
                    design_manifest_path
                ),

            project_id=
                project_manifest.project_id,

            design_id=
                design_manifest.design_id,
        )


    def _load_plaintext_design(
        self,
        project_manifest_path: str | Path,
        design_manifest_path: str | Path,
        source: str = "save_load_runtime_bridge",
    ) -> SaveLoadResult:
        project_manifest_path = Path(project_manifest_path)
        design_manifest_path = Path(design_manifest_path)

        project_manifest = ProjectManifest.from_dict(
            json.loads(project_manifest_path.read_text(encoding="utf-8"))
        )
        design_manifest = DesignManifest.from_dict(
            json.loads(design_manifest_path.read_text(encoding="utf-8"))
        )

        project_validation = self.project_validator.validate(project_manifest)
        design_validation = self.design_validator.validate(design_manifest)

        if project_validation.get("passed") is not True:
            raise ValueError(f"project_manifest_invalid:{project_validation.get('failures')}")

        if design_validation.get("passed") is not True:
            raise ValueError(f"design_manifest_invalid:{design_validation.get('failures')}")

        self._require_design_parent_project(design_manifest, project_manifest)
        self.security_context.require_project_access(
            project_manifest
        )

        if str(
            design_manifest.engineering_state_ref
            or ""
        ).strip():
            self.load_design_engineering_state(
                design_manifest_path
            )

        self._require_or_create_session()

        self.session_lifecycle.set_active_project(str(project_manifest_path))
        self.session_lifecycle.set_active_design(str(design_manifest_path))
        self.session_lifecycle.set_active_workspace("engineering_workspace")
        self.session_lifecycle.open_document(str(design_manifest_path), "design_manifest")

        self.state_registry.set("active_project", str(project_manifest_path), source=source)
        self.state_registry.set("active_design", str(design_manifest_path), source=source)
        self.state_registry.set("current_workspace", "engineering_workspace", source=source)

        design_manifest.mark_opened()
        design_manifest.dirty_state = "saved"
        self._write_json(design_manifest_path, design_manifest.snapshot())

        self.dirty_state_manager.mark_saved(
            str(design_manifest_path),
            "design",
            reason="design_loaded",
            source=source,
        )

        self.report_router.diagnostic(
            source=source,
            title="Design Loaded",
            summary=f"Loaded design manifest {design_manifest.design_name}.",
            target_id=str(design_manifest_path),
            target_type="design",
            payload_ref=str(design_manifest_path),
        )

        self.notification_centre.notify(
            category="runtime",
            level="success",
            title="Design Loaded",
            message=f"{design_manifest.design_name} is now active.",
            source=source,
            target_id=str(design_manifest_path),
            target_type="design",
            action_ref=str(design_manifest_path),
        )

        return SaveLoadResult(
            action="load_design",
            project_manifest_path=str(project_manifest_path),
            design_manifest_path=str(design_manifest_path),
            project_id=project_manifest.project_id,
            design_id=design_manifest.design_id,
        )

    def _save_plaintext_design(
        self,
        project_manifest_path: str | Path,
        design_manifest_path: str | Path,
        updates: dict[str, Any] | None = None,
        source: str = "save_load_runtime_bridge",
        engineering_state: dict[str, Any] | None = None,
    ) -> SaveLoadResult:
        project_manifest_path = Path(project_manifest_path)
        design_manifest_path = Path(design_manifest_path)

        project_manifest = ProjectManifest.from_dict(
            json.loads(project_manifest_path.read_text(encoding="utf-8"))
        )
        design_manifest = DesignManifest.from_dict(
            json.loads(design_manifest_path.read_text(encoding="utf-8"))
        )

        self._require_design_parent_project(design_manifest, project_manifest)
        self.security_context.require_project_modify(
            project_manifest
        )

        updates = dict(updates or {})

        for key, value in updates.items():
            if not hasattr(design_manifest, key):
                raise KeyError(f"design_manifest_update_key_not_allowed:{key}")
            setattr(design_manifest, key, value)

        if engineering_state is not None:
            engineering_state_path = (
                design_manifest_path.parent
                / ENGINEERING_STATE_FILENAME
            )

            self.save_engineering_state(
                engineering_state_path,
                engineering_state,
            )

            design_manifest.engineering_state_ref = (
                ENGINEERING_STATE_FILENAME
            )

        design_manifest.dirty_state = "saved"
        design_manifest.touch()

        self._write_json(design_manifest_path, design_manifest.snapshot())

        storage_root = project_manifest_path.resolve().parents[2]
        storage = CanonicalStorageOwner(storage_root)

        portable_design_ref = storage.portable_ref(
            design_manifest_path
        )
        resolved_design_path = design_manifest_path.resolve()

        normalised_active_designs: list[str] = []
        matching_design_found = False

        for existing_ref in project_manifest.active_designs:
            existing_path = storage.resolve_ref(existing_ref)

            try:
                is_same_design = (
                    existing_path.resolve()
                    == resolved_design_path
                )
            except OSError:
                is_same_design = False

            if is_same_design:
                if not matching_design_found:
                    normalised_active_designs.append(
                        portable_design_ref
                    )
                    matching_design_found = True
                continue

            normalised_active_designs.append(existing_ref)

        if not matching_design_found:
            normalised_active_designs.append(
                portable_design_ref
            )

        if (
            normalised_active_designs
            != project_manifest.active_designs
        ):
            project_manifest.active_designs = (
                normalised_active_designs
            )
            project_manifest.touch()

            self._write_json(
                project_manifest_path,
                project_manifest.snapshot(),
            )

        self._require_or_create_session()

        self.session_lifecycle.set_active_project(str(project_manifest_path))
        self.session_lifecycle.set_active_design(str(design_manifest_path))

        self.state_registry.set("active_project", str(project_manifest_path), source=source)
        self.state_registry.set("active_design", str(design_manifest_path), source=source)

        self.dirty_state_manager.mark_saved(
            str(design_manifest_path),
            "design",
            reason="design_saved",
            source=source,
        )

        self.report_router.report(
            source=source,
            title="Design Saved",
            summary=f"Saved design manifest {design_manifest.design_name}.",
            target_id=str(design_manifest_path),
            target_type="design",
            payload_ref=str(design_manifest_path),
        )

        self.notification_centre.notify(
            category="save",
            level="success",
            title="Design Saved",
            message=f"{design_manifest.design_name} was saved.",
            source=source,
            target_id=str(design_manifest_path),
            target_type="design",
            action_ref=str(design_manifest_path),
        )

        return SaveLoadResult(
            action="save_design",
            project_manifest_path=str(project_manifest_path),
            design_manifest_path=str(design_manifest_path),
            project_id=project_manifest.project_id,
            design_id=design_manifest.design_id,
        )

    def _load_plaintext_design_engineering_state(
        self,
        design_manifest_path: str | Path,
    ) -> dict[str, Any]:
        """Load the engineering-state payload referenced by a design manifest."""
        design_manifest_path = Path(
            design_manifest_path
        )

        design_manifest = DesignManifest.from_dict(
            json.loads(
                design_manifest_path.read_text(
                    encoding="utf-8",
                )
            )
        )

        design_validation = self.design_validator.validate(design_manifest)
        if design_validation.get("passed") is not True:
            raise ValueError(f"design_manifest_invalid:{design_validation.get('failures')}")

        from leaf_qt.storage.project_browser_model import (
            ProjectBrowserModel,
        )

        project_manifest_path = (
            ProjectBrowserModel(
                design_manifest_path.resolve().parents[2]
            )
            .resolve_project_manifest_for_design(
                design_manifest_path
            )
        )

        if project_manifest_path is None:
            raise FileNotFoundError(
                "owning_project_manifest_not_found"
            )
        project_manifest = ProjectManifest.from_dict(
            json.loads(project_manifest_path.read_text(encoding="utf-8"))
        )
        project_validation = self.project_validator.validate(project_manifest)
        if project_validation.get("passed") is not True:
            raise ValueError(f"project_manifest_invalid:{project_validation.get('failures')}")

        self._require_design_parent_project(design_manifest, project_manifest)
        self.security_context.require_project_access(project_manifest)

        state_ref = str(
            design_manifest.engineering_state_ref
            or ""
        ).strip()

        if not state_ref:
            raise FileNotFoundError(
                "design_engineering_state_reference_missing"
            )

        state_ref_path = Path(
            state_ref
        )

        if (
            state_ref_path.is_absolute()
            or state_ref_path.name != state_ref
        ):
            raise ValueError(
                "engineering_state_ref_must_be_design_local_filename"
            )

        state_path = (
            design_manifest_path.parent
            / state_ref_path
        )

        return self.load_engineering_state(
            state_path
        )


    def save_encrypted_resource(
        self,
        path: str | Path,
        payload: dict[str, Any],
        *,
        project_id: str,
        security_classification: str,
        resource_type: str,
        resource_id: str,
        portable_key_envelope: dict[str, Any] | None = None,
    ) -> str:

        path = Path(
            path
        )


        principal_id = (
            self.security_context
            .principal_id
        )


        project_key = (
            self
            ._require_key_custody()
            .retrieve_project_key(
                principal_id,
                project_id,
            )
        )


        container = (
            self
            ._require_encrypted_container_owner()
            .seal(
                payload=
                    payload,

                project_id=
                    project_id,

                owner_principal_id=
                    principal_id,

                security_classification=
                    security_classification,

                resource_type=
                    resource_type,

                resource_id=
                    resource_id,

                project_key=
                    project_key,

                portable_key_envelope=
                    portable_key_envelope,
            )
        )


        self._write_json(
            path,
            container,
        )


        return str(
            path
        )


    def load_encrypted_resource(
        self,
        path: str | Path,
        *,
        expected_project_id: str,
        expected_security_classification: str,
        expected_resource_type: str,
        expected_resource_id: str,
    ) -> dict[str, Any]:

        path = Path(
            path
        )


        container = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )


        if not isinstance(
            container,
            dict,
        ):

            raise ValueError(
                "encrypted_resource_container_must_be_json_object"
            )


        principal_id = (
            self.security_context
            .principal_id
        )




        project_key = (
            self
            ._require_key_custody()
            .retrieve_project_key(
                principal_id,
                expected_project_id,
            )
        )


        return (
            self
            ._require_encrypted_container_owner()
            .open(
                container=
                    container,

                project_key=
                    project_key,

                expected_project_id=
                    expected_project_id,

                expected_owner_principal_id=
                    principal_id,

                expected_security_classification=
                    expected_security_classification,

                expected_resource_type=
                    expected_resource_type,

                expected_resource_id=
                    expected_resource_id,
            )
        )


    def _require_key_custody(
        self,
    ) -> KeyCustodyOwner:

        if self.key_custody is None:

            self.key_custody = (
                KeyCustodyOwner()
            )


        return self.key_custody


    def _require_encrypted_container_owner(
        self,
    ) -> EncryptedContainerOwner:

        if (
            self.encrypted_container_owner
            is None
        ):

            self.encrypted_container_owner = (
                EncryptedContainerOwner()
            )


        return (
            self.encrypted_container_owner
        )


    def _require_or_create_session(self):
        """
        Return the current runtime session, creating and securing
        it when necessary.
        """
        try:
            return (
                self.session_lifecycle
                .require_session()
            )

        except RuntimeError as exc:
            if (
                str(exc)
                !=
                "runtime_session_not_open"
            ):
                raise

        session = (
            self.session_lifecycle
            .create_session()
        )

        try:
            self.security_context.initialise_runtime_security(
                self.session_lifecycle
            )

        except Exception:
            # A new runtime session defaults to UNLOCKED.
            # Never leave it alive if authentication startup
            # policy could not be applied.
            try:
                self.session_lifecycle.close_session()

            finally:
                raise

        return session


    @staticmethod
    def load_engineering_state(
        path: str | Path,
    ) -> dict[str, Any]:
        """Load a standalone LEAF engineering-state document."""
        path = Path(path)

        payload = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "engineering_state_payload_must_be_json_object"
            )

        return payload

    @staticmethod
    def save_engineering_state(
        path: str | Path,
        payload: dict[str, Any],
    ) -> str:
        """Persist a standalone LEAF engineering-state document."""

        if not isinstance(
            payload,
            dict,
        ):
            raise TypeError(
                "engineering_state_payload_must_be_dict"
            )


        path = Path(
            path
        )


        SaveLoadRuntimeBridge._write_json(
            path,
            payload,
            indent=4,
        )


        return str(
            path
        )

    def synchronise_renamed_reference(
        self,
        old_path: str | Path,
        new_path: str | Path,
        entity_type: str,
        source: str = "save_load_runtime_bridge",
    ) -> dict[str, Any]:
        """
        Atomically synchronise one successful persistent
        rename into current runtime reference state.

        Historical reports and notifications remain
        untouched because they are event history rather
        than current application truth.
        """
        if entity_type not in {
            "project",
            "design",
        }:
            raise ValueError(
                "rename_runtime_entity_type_not_allowed:"
                f"{entity_type}"
            )

        old_path_text = str(
            old_path
        )

        new_path_text = str(
            new_path
        )

        registry_key = (
            "active_project"
            if entity_type == "project"
            else "active_design"
        )

        if paths_match(
            old_path_text,
            new_path_text,
        ):
            return {
                "entity_type":
                    entity_type,

                "old_path":
                    old_path_text,

                "new_path":
                    new_path_text,

                "session_open":
                    True,

                "session": {
                    "active_project_changed":
                        False,

                    "active_design_changed":
                        False,

                    "open_documents_changed":
                        0,
                },

                "registry_key":
                    registry_key,

                "registry_changed":
                    False,

                "dirty_state_rekeyed":
                    False,

                "runtime_transactional":
                    True,

                "runtime_noop":
                    True,

                "historical_report_refs_rewritten":
                    False,

                "historical_notification_refs_rewritten":
                    False,
            }

        # -------------------------------------------------
        # PRE-MUTATION SNAPSHOTS
        # -------------------------------------------------

        try:
            session_before = (
                self.session_lifecycle
                .snapshot()
            )

        except RuntimeError:
            session_open = False
            session_before = None

        else:
            session_open = True

        registry_before = (
            self.state_registry.get(
                registry_key
            )
        )

        old_dirty = (
            self.dirty_state_manager
            .get_record(
                old_path_text
            )
        )

        new_dirty = (
            self.dirty_state_manager
            .get_record(
                new_path_text
            )
        )

        # Dirty-state path collision must be rejected before
        # any live reference is touched.
        if (
            old_dirty is not None
            and new_dirty is not None
        ):
            raise KeyError(
                "rename_runtime_dirty_state_target_exists:"
                f"{new_path_text}"
            )

        # Prevent rollback ambiguity. A canonical rename
        # target should not already be a live session path.
        if session_before is not None:
            session_paths = [
                session_before.get(
                    "active_project"
                ),
                session_before.get(
                    "active_design"
                ),
            ]

            session_paths.extend(
                document.get(
                    "path"
                )
                for document
                in session_before.get(
                    "open_documents",
                    {}
                ).values()
            )

            if any(
                paths_match(
                    path_value,
                    new_path_text,
                )
                for path_value
                in session_paths
                if path_value
            ):
                raise KeyError(
                    "rename_runtime_target_already_referenced:"
                    f"{new_path_text}"
                )

        if (
            registry_before is not None
            and
            paths_match(
                registry_before,
                new_path_text,
            )
        ):
            raise KeyError(
                "rename_runtime_registry_target_already_referenced:"
                f"{new_path_text}"
            )

        session_result = {
            "active_project_changed":
                False,

            "active_design_changed":
                False,

            "open_documents_changed":
                0,
        }

        registry_changed = False
        dirty_state_rekeyed = False

        try:
            # ---------------------------------------------
            # SESSION
            # ---------------------------------------------

            if session_open:
                session_result = (
                    self.session_lifecycle
                    .replace_path_reference(
                        old_path_text,
                        new_path_text,
                    )
                )

            # ---------------------------------------------
            # RUNTIME STATE REGISTRY
            # ---------------------------------------------

            registry_changed = (
                paths_match(
                    registry_before,
                    old_path_text,
                )
            )

            if registry_changed:
                self.state_registry.set(
                    registry_key,
                    new_path_text,
                    source=source,
                )

            # ---------------------------------------------
            # DIRTY STATE
            #
            # Deliberately last so any failure here proves
            # session + registry rollback.
            # ---------------------------------------------

            dirty_state_rekeyed = (
                self.dirty_state_manager
                .rekey_entity(
                    old_path_text,
                    new_path_text,
                    source=source,
                )
            )

        except Exception as exc:
            rollback_failures: list[str] = []

            # ---------------------------------------------
            # DIRTY STATE ROLLBACK
            # ---------------------------------------------

            try:
                current_old_dirty = (
                    self.dirty_state_manager
                    .get_record(
                        old_path_text
                    )
                )

                current_new_dirty = (
                    self.dirty_state_manager
                    .get_record(
                        new_path_text
                    )
                )

                if (
                    current_old_dirty is None
                    and
                    current_new_dirty is not None
                ):
                    self.dirty_state_manager.rekey_entity(
                        new_path_text,
                        old_path_text,
                        source=
                            f"{source}.rollback",
                    )

            except Exception as rollback_exc:
                rollback_failures.append(
                    "dirty_state_restore_failed:"
                    f"{rollback_exc!r}"
                )

            # ---------------------------------------------
            # REGISTRY ROLLBACK
            # ---------------------------------------------

            try:
                current_registry = (
                    self.state_registry.get(
                        registry_key
                    )
                )

                if (
                    registry_changed
                    and
                    paths_match(
                        current_registry,
                        new_path_text,
                    )
                ):
                    self.state_registry.set(
                        registry_key,
                        registry_before,
                        source=
                            f"{source}.rollback",
                    )

            except Exception as rollback_exc:
                rollback_failures.append(
                    "runtime_registry_restore_failed:"
                    f"{rollback_exc!r}"
                )

            # ---------------------------------------------
            # SESSION ROLLBACK
            # ---------------------------------------------

            try:
                session_changed = (
                    session_result[
                        "active_project_changed"
                    ]
                    or
                    session_result[
                        "active_design_changed"
                    ]
                    or
                    session_result[
                        "open_documents_changed"
                    ]
                    > 0
                )

                if (
                    session_open
                    and session_changed
                ):
                    self.session_lifecycle                        .replace_path_reference(
                            new_path_text,
                            old_path_text,
                        )

            except Exception as rollback_exc:
                rollback_failures.append(
                    "runtime_session_restore_failed:"
                    f"{rollback_exc!r}"
                )

            # ---------------------------------------------
            # VERIFY CURRENT STATE WAS RESTORED
            # ---------------------------------------------

            try:
                if session_before is not None:
                    session_after_rollback = (
                        self.session_lifecycle
                        .snapshot()
                    )

                    if (
                        session_after_rollback
                        != session_before
                    ):
                        rollback_failures.append(
                            "runtime_session_restore_not_exact"
                        )

            except Exception as rollback_exc:
                rollback_failures.append(
                    "runtime_session_restore_verification_failed:"
                    f"{rollback_exc!r}"
                )

            try:
                registry_after_rollback = (
                    self.state_registry.get(
                        registry_key
                    )
                )

                if (
                    registry_after_rollback
                    != registry_before
                ):
                    rollback_failures.append(
                        "runtime_registry_restore_not_exact"
                    )

            except Exception as rollback_exc:
                rollback_failures.append(
                    "runtime_registry_restore_verification_failed:"
                    f"{rollback_exc!r}"
                )

            try:
                restored_old_dirty = (
                    self.dirty_state_manager
                    .get_record(
                        old_path_text
                    )
                )

                restored_new_dirty = (
                    self.dirty_state_manager
                    .get_record(
                        new_path_text
                    )
                )

                if old_dirty is None:
                    dirty_restored = (
                        restored_old_dirty is None
                    )
                else:
                    dirty_restored = (
                        restored_old_dirty
                        is not None
                        and
                        restored_old_dirty.snapshot()
                        ==
                        old_dirty.snapshot()
                    )

                if not dirty_restored:
                    rollback_failures.append(
                        "dirty_state_restore_not_exact"
                    )

                if restored_new_dirty is not None:
                    rollback_failures.append(
                        "dirty_state_target_survived_rollback"
                    )

            except Exception as rollback_exc:
                rollback_failures.append(
                    "dirty_state_restore_verification_failed:"
                    f"{rollback_exc!r}"
                )

            if rollback_failures:
                raise RuntimeError(
                    "rename_runtime_sync_failed_and_"
                    "rollback_incomplete:"
                    + ";".join(
                        rollback_failures
                    )
                ) from exc

            raise

        return {
            "entity_type":
                entity_type,

            "old_path":
                old_path_text,

            "new_path":
                new_path_text,

            "session_open":
                session_open,

            "session":
                session_result,

            "registry_key":
                registry_key,

            "registry_changed":
                registry_changed,

            "dirty_state_rekeyed":
                dirty_state_rekeyed,

            "runtime_transactional":
                True,

            "runtime_noop":
                False,

            "historical_report_refs_rewritten":
                False,

            "historical_notification_refs_rewritten":
                False,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "connects_storage_to_runtime": True,
            "updates_session_lifecycle": True,
            "updates_state_registry": True,
            "updates_dirty_state": True,
            "routes_reports": True,
            "creates_notifications": True,
            "writes_design_manifest": True,
            "writes_project_manifest_links": True,
            "qt_owns_save_load": False,
            "stores_solver_payloads": False,
            "stores_report_payloads": False,
            "stores_validation_payloads": False,
        }

    @staticmethod
    def _write_bytes_atomic(
        path: str | Path,
        payload: bytes,
    ) -> None:
        """
        Atomically replace one file with exact bytes.

        This is the canonical exact-byte persistence primitive
        used by transactional rollback and migration.
        """

        import os
        import secrets


        if not isinstance(
            payload,
            (
                bytes,
                bytearray,
            ),
        ):
            raise TypeError(
                "atomic_byte_payload_must_be_bytes"
            )


        path = Path(
            path
        )


        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        temporary = (
            path.parent
            /
            (
                "."
                +
                path.name
                +
                "."
                +
                secrets.token_hex(
                    8
                )
                +
                ".tmp"
            )
        )


        try:

            with temporary.open(
                "xb"
            ) as handle:

                handle.write(
                    bytes(
                        payload
                    )
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )


            os.replace(
                temporary,
                path,
            )


        except Exception:

            if temporary.exists():

                temporary.unlink()


            raise

    @staticmethod
    def _write_json(
        path: Path,
        payload: dict[str, Any],
        indent: int = 2,
    ) -> None:

        if not isinstance(
            payload,
            dict,
        ):
            raise TypeError(
                "json_payload_must_be_dict"
            )


        path = Path(
            path
        )


        temporary = path.with_name(
            path.name
            +
            f".tmp-{os.getpid()}-{uuid4().hex}"
        )


        try:

            with temporary.open(
                "w",
                encoding="utf-8",
            ) as handle:

                json.dump(
                    payload,
                    handle,
                    indent=indent,
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )


            temporary.replace(
                path
            )


        finally:

            if temporary.exists():

                temporary.unlink()
