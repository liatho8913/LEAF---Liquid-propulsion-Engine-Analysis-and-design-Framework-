from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from leaf_qt.storage.canonical_storage import CanonicalStorageOwner, paths_match
from leaf_qt.storage.project_manifest import (
    PROJECT_MANIFEST_FILENAME,
    ProjectManifest,
    ProjectManifestValidator,
)
from leaf_qt.storage.design_manifest import (
    DESIGN_MANIFEST_FILENAME,
    DesignManifest,
    DesignManifestValidator,
)
from leaf_qt.storage.project_browser_model import ProjectBrowserModel
from leaf_qt.security_context import SecurityContextOwner
from leaf_qt.encrypted_container import (
    DESIGN_MANIFEST_RESOURCE,
    ENGINEERING_STATE_RESOURCE,
    PROJECT_ROOT_RESOURCE,
    SCHEMA as ENCRYPTED_CONTAINER_SCHEMA,
    EncryptedContainerOwner,
)
from leaf_qt.key_custody import KeyCustodyOwner
from leaf_qt.key_envelope import PortableKeyEnvelopeOwner

SCHEMA = "LEAF_PROJECT_DESIGN_CREATION_OWNER_PHASE_25D_V1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_slug(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "Untitled"


@dataclass(frozen=True)
class CreationResult:
    project_manifest: ProjectManifest
    design_manifest: DesignManifest | None
    project_dir: str
    design_dir: str | None
    project_manifest_path: str
    design_manifest_path: str | None
    created_at: str = field(default_factory=utc_now)

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": "LEAF_PROJECT_DESIGN_CREATION_RESULT_PHASE_25D_V1",
            "project_manifest": self.project_manifest.snapshot(),
            "design_manifest": None if self.design_manifest is None else self.design_manifest.snapshot(),
            "project_dir": self.project_dir,
            "design_dir": self.design_dir,
            "project_manifest_path": self.project_manifest_path,
            "design_manifest_path": self.design_manifest_path,
            "created_at": self.created_at,
        }


class ProjectDesignCreationOwner:
    """
    Reusable owner for canonical LEAF project/design filesystem lifecycle.

    This owns project/design creation and persistent filesystem rename.

    It does not own:
    - Qt widgets
    - runtime session state
    - solver payloads
    - validation payloads
    - report payloads
    """

    def __init__(
        self,
        root: str | Path | None = None,
        security_context: SecurityContextOwner | None = None,
        key_custody: KeyCustodyOwner | None = None,
        key_envelope_owner: PortableKeyEnvelopeOwner | None = None,
        encrypted_container_owner: EncryptedContainerOwner | None = None,
    ) -> None:

        self.storage = (
            CanonicalStorageOwner(
                root
            )
        )


        self.security_context = (
            security_context
            or
            SecurityContextOwner()
        )


        self.key_custody = (
            key_custody
        )


        self.key_envelope_owner = (
            key_envelope_owner
        )


        self.encrypted_container_owner = (
            encrypted_container_owner
        )

    def create_project(
        self,
        project_name: str,
        runtime_schema_version: str = "",
        project_notes: str = "",
        overwrite: bool = False,
    ) -> CreationResult:
        self.storage.ensure_roots()

        project_manifest = ProjectManifest.create(
            project_name=project_name,
            runtime_schema_version=runtime_schema_version,
            project_notes=project_notes,
        )
        self.security_context.bind_new_project(project_manifest)

        project_dir = self.storage.canonical_path("projects") / safe_slug(project_name)
        project_dir.mkdir(parents=True, exist_ok=True)

        project_manifest_path = project_dir / PROJECT_MANIFEST_FILENAME

        if project_manifest_path.exists() and not overwrite:
            raise FileExistsError(f"project_manifest_already_exists:{project_manifest_path}")

        self._write_json(project_manifest_path, project_manifest.snapshot())

        return CreationResult(
            project_manifest=project_manifest,
            design_manifest=None,
            project_dir=str(project_dir),
            design_dir=None,
            project_manifest_path=str(project_manifest_path),
            design_manifest_path=None,
        )


    def create_encrypted_project(
        self,
        project_name: str,
        recovery_key: str,
        runtime_schema_version: str = "",
        project_notes: str = "",
    ) -> CreationResult:
        """
        Explicit encrypted-project creation.

        The normal create_project() path remains plaintext
        compatible during S1J.

        recovery_key is supplied by the security/recovery
        workflow and is never persisted here.
        """

        recovery_key = str(
            recovery_key
            or ""
        ).strip()


        if not recovery_key:

            raise ValueError(
                "recovery_key_required"
            )


        self.storage.ensure_roots()


        project_manifest = (
            ProjectManifest.create(
                project_name=
                    project_name,

                runtime_schema_version=
                    runtime_schema_version,

                project_notes=
                    project_notes,
            )
        )


        self.security_context.bind_new_project(
            project_manifest
        )


        project_id = (
            project_manifest.project_id
        )


        principal_id = (
            project_manifest.owner_principal_id
        )


        project_dir = (
            self.storage
            .canonical_path(
                "projects"
            )
            /
            project_id
        )


        if project_dir.exists():

            raise FileExistsError(
                "encrypted_project_directory_already_exists:"
                f"{project_dir}"
            )


        project_dir.mkdir(
            parents=True,
            exist_ok=False,
        )


        project_manifest_path = (
            project_dir
            /
            PROJECT_MANIFEST_FILENAME
        )


        custody = (
            self._require_key_custody()
        )


        project_key_created = False


        try:

            if custody.project_key_exists(
                principal_id,
                project_id,
            ):

                raise FileExistsError(
                    "encrypted_project_key_slot_already_exists"
                )


            custody.create_project_key(
                principal_id,
                project_id,
            )


            project_key_created = True


            project_key = (
                custody
                .retrieve_project_key(
                    principal_id,
                    project_id,
                )
            )


            portable_envelope = (
                self
                ._require_key_envelope_owner()
                .wrap_project_key(
                    project_id=
                        project_id,

                    owner_principal_id=
                        principal_id,

                    project_key=
                        project_key,

                    recovery_key=
                        recovery_key,
                )
            )


            encrypted_root = (
                self
                ._require_encrypted_container_owner()
                .seal(
                    payload=
                        project_manifest.snapshot(),

                    project_id=
                        project_id,

                    owner_principal_id=
                        principal_id,

                    security_classification=
                        project_manifest
                        .security_classification,

                    resource_type=
                        PROJECT_ROOT_RESOURCE,

                    resource_id=
                        project_id,

                    project_key=
                        project_key,

                    portable_key_envelope=
                        portable_envelope,
                )
            )


            self._write_json(
                project_manifest_path,
                encrypted_root,
            )


        except Exception:

            if (
                project_key_created
                and
                custody.project_key_exists(
                    principal_id,
                    project_id,
                )
            ):

                custody.revoke_project_key(
                    principal_id,
                    project_id,
                )


            if project_manifest_path.exists():

                project_manifest_path.unlink()


            if (
                project_dir.exists()
                and
                not any(
                    project_dir.iterdir()
                )
            ):

                project_dir.rmdir()


            raise


        return CreationResult(
            project_manifest=
                project_manifest,

            design_manifest=
                None,

            project_dir=
                str(
                    project_dir
                ),

            design_dir=
                None,

            project_manifest_path=
                str(
                    project_manifest_path
                ),

            design_manifest_path=
                None,
        )



    def create_encrypted_design_for_project(
        self,
        project_manifest_path: str | Path,
        design_name: str,
        engine_type: str = "liquid_rocket_engine",
        engineering_state: dict[str, Any] | None = None,
    ) -> CreationResult:

        from leaf_qt.storage.save_load_bridge import (
            ENGINEERING_STATE_FILENAME,
        )


        self.storage.ensure_roots()


        project_manifest_path = Path(
            project_manifest_path
        )


        root_container = json.loads(
            project_manifest_path.read_text(
                encoding="utf-8"
            )
        )


        if not isinstance(
            root_container,
            dict,
        ):

            raise ValueError(
                "encrypted_project_root_must_be_json_object"
            )


        project_id = str(
            root_container.get(
                "project_id",
                "",
            )
        ).strip()


        classification = str(
            root_container.get(
                "security_classification",
                "",
            )
        ).strip()


        principal_id = (
            self.security_context
            .principal_id
        )


        if not project_id.startswith(
            "project_"
        ):

            raise ValueError(
                "encrypted_project_id_invalid"
            )




        custody = (
            self._require_key_custody()
        )


        project_key = (
            custody.retrieve_project_key(
                principal_id,
                project_id,
            )
        )


        container_owner = (
            self._require_encrypted_container_owner()
        )


        project_payload = (
            container_owner.open(
                container=
                    root_container,

                project_key=
                    project_key,

                expected_project_id=
                    project_id,

                expected_owner_principal_id=
                    principal_id,

                expected_security_classification=
                    classification,

                expected_resource_type=
                    PROJECT_ROOT_RESOURCE,

                expected_resource_id=
                    project_id,
            )
        )


        project_manifest = (
            ProjectManifest.from_dict(
                project_payload
            )
        )


        self.security_context.require_project_modify(
            project_manifest
        )


        design_manifest = (
            DesignManifest.create(
                design_name=
                    design_name,

                parent_project_id=
                    project_id,

                engine_type=
                    engine_type,
            )
        )


        design_id = (
            design_manifest.design_id
        )


        design_dir = (
            self.storage
            .canonical_path(
                "designs"
            )
            /
            design_id
        )


        if design_dir.exists():

            raise FileExistsError(
                "encrypted_design_directory_already_exists:"
                f"{design_dir}"
            )


        design_dir.mkdir(
            parents=True,
            exist_ok=False,
        )


        design_manifest_path = (
            design_dir
            /
            DESIGN_MANIFEST_FILENAME
        )


        engineering_state_path = (
            design_dir
            /
            ENGINEERING_STATE_FILENAME
        )


        design_written = False
        state_written = False


        try:

            if engineering_state is not None:

                if not isinstance(
                    engineering_state,
                    dict,
                ):

                    raise TypeError(
                        "engineering_state_payload_must_be_dict"
                    )


                design_manifest.engineering_state_ref = (
                    ENGINEERING_STATE_FILENAME
                )


                state_container = (
                    container_owner.seal(
                        payload=
                            engineering_state,

                        project_id=
                            project_id,

                        owner_principal_id=
                            principal_id,

                        security_classification=
                            classification,

                        resource_type=
                            ENGINEERING_STATE_RESOURCE,

                        resource_id=
                            design_id,

                        project_key=
                            project_key,

                        portable_key_envelope=
                            None,
                    )
                )


                self._write_json(
                    engineering_state_path,
                    state_container,
                )

                state_written = True


            design_container = (
                container_owner.seal(
                    payload=
                        design_manifest.snapshot(),

                    project_id=
                        project_id,

                    owner_principal_id=
                        principal_id,

                    security_classification=
                        classification,

                    resource_type=
                        DESIGN_MANIFEST_RESOURCE,

                    resource_id=
                        design_id,

                    project_key=
                        project_key,

                    portable_key_envelope=
                        None,
                )
            )


            self._write_json(
                design_manifest_path,
                design_container,
            )

            design_written = True


            project_manifest.add_design(
                self.storage.portable_ref(
                    design_manifest_path
                )
            )


            encrypted_project_root = (
                container_owner.seal(
                    payload=
                        project_manifest.snapshot(),

                    project_id=
                        project_id,

                    owner_principal_id=
                        principal_id,

                    security_classification=
                        classification,

                    resource_type=
                        PROJECT_ROOT_RESOURCE,

                    resource_id=
                        project_id,

                    project_key=
                        project_key,

                    portable_key_envelope=
                        root_container.get(
                            "portable_key_envelope"
                        ),
                )
            )


            # Root written last so it never points at an
            # incomplete child resource.
            self._write_json(
                project_manifest_path,
                encrypted_project_root,
            )


        except Exception:

            if (
                state_written
                and
                engineering_state_path.exists()
            ):
                engineering_state_path.unlink()


            if (
                design_written
                and
                design_manifest_path.exists()
            ):
                design_manifest_path.unlink()


            if (
                design_dir.exists()
                and
                not any(
                    design_dir.iterdir()
                )
            ):
                design_dir.rmdir()


            raise


        return CreationResult(
            project_manifest=
                project_manifest,

            design_manifest=
                design_manifest,

            project_dir=
                str(
                    project_manifest_path.parent
                ),

            design_dir=
                str(
                    design_dir
                ),

            project_manifest_path=
                str(
                    project_manifest_path
                ),

            design_manifest_path=
                str(
                    design_manifest_path
                ),
        )


    def create_design_for_project(
        self,
        project_manifest_path: str | Path,
        design_name: str,
        engine_type: str = "liquid_rocket_engine",
        overwrite: bool = False,
    ) -> CreationResult:
        self.storage.ensure_roots()

        project_manifest_path = Path(project_manifest_path)
        project_manifest = ProjectManifest.from_dict(
            json.loads(project_manifest_path.read_text(encoding="utf-8"))
        )
        self.security_context.require_project_modify(project_manifest)

        design_manifest = DesignManifest.create(
            design_name=design_name,
            parent_project_id=project_manifest.project_id,
            engine_type=engine_type,
        )

        design_dir = self.storage.canonical_path("designs") / safe_slug(design_name)
        design_dir.mkdir(parents=True, exist_ok=True)

        design_manifest_path = design_dir / DESIGN_MANIFEST_FILENAME

        if design_manifest_path.exists() and not overwrite:
            raise FileExistsError(f"design_manifest_already_exists:{design_manifest_path}")

        self._write_json(design_manifest_path, design_manifest.snapshot())

        project_manifest.add_design(
            self.storage.portable_ref(design_manifest_path)
        )
        self._write_json(project_manifest_path, project_manifest.snapshot())

        return CreationResult(
            project_manifest=project_manifest,
            design_manifest=design_manifest,
            project_dir=str(project_manifest_path.parent),
            design_dir=str(design_dir),
            project_manifest_path=str(project_manifest_path),
            design_manifest_path=str(design_manifest_path),
        )

    def create_project_with_design(
        self,
        project_name: str,
        design_name: str,
        runtime_schema_version: str = "",
        project_notes: str = "",
        engine_type: str = "liquid_rocket_engine",
        overwrite: bool = False,
    ) -> CreationResult:
        project_result = self.create_project(
            project_name=project_name,
            runtime_schema_version=runtime_schema_version,
            project_notes=project_notes,
            overwrite=overwrite,
        )

        return self.create_design_for_project(
            project_manifest_path=project_result.project_manifest_path,
            design_name=design_name,
            engine_type=engine_type,
            overwrite=overwrite,
        )


    def _require_key_custody(
        self,
    ) -> KeyCustodyOwner:

        if self.key_custody is None:

            self.key_custody = (
                KeyCustodyOwner()
            )


        return self.key_custody


    def _require_key_envelope_owner(
        self,
    ) -> PortableKeyEnvelopeOwner:

        if self.key_envelope_owner is None:

            self.key_envelope_owner = (
                PortableKeyEnvelopeOwner()
            )


        return self.key_envelope_owner


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


    def _run_rename_transaction(
        self,
        *,
        source_dir: Path,
        target_dir: Path,
        manifest_filename: str,
        manifest_payload: dict[str, Any],
        original_manifest_bytes: bytes,
        related_writes: list[
            tuple[
                Path,
                dict[str, Any],
                bytes,
            ]
        ],
        verify: Callable[[Path], None],
        after_persist: Callable[[Path], None] | None = None,
    ) -> Path:
        """
        Canonical filesystem rename transaction used by
        project and design lifecycle operations.
        """
        target_manifest_path = (
            target_dir
            / manifest_filename
        )

        moved = False

        try:
            if target_dir != source_dir:
                source_dir.rename(
                    target_dir
                )
                moved = True

            self._write_json(
                target_manifest_path,
                manifest_payload,
            )

            for (
                path,
                payload,
                _,
            ) in related_writes:
                self._write_json(
                    path,
                    payload,
                )

            verify(
                target_manifest_path
            )

            if after_persist is not None:
                after_persist(
                    target_manifest_path
                )

        except Exception as exc:
            rollback_failures: list[str] = []

            # Restore secondary manifests first.
            for (
                path,
                _,
                original_bytes,
            ) in reversed(
                related_writes
            ):
                try:
                    path.write_bytes(
                        original_bytes
                    )
                except Exception as rollback_exc:
                    rollback_failures.append(
                        "related_manifest_restore_failed:"
                        f"{path}:{rollback_exc!r}"
                    )

            restore_manifest_path = (
                target_manifest_path
            )

            # Restore the original directory location.
            if moved:
                try:
                    target_dir.rename(
                        source_dir
                    )

                    restore_manifest_path = (
                        source_dir
                        / manifest_filename
                    )

                except Exception as rollback_exc:
                    rollback_failures.append(
                        "directory_restore_failed:"
                        f"{rollback_exc!r}"
                    )

            # Restore the exact original primary manifest.
            try:
                restore_manifest_path.write_bytes(
                    original_manifest_bytes
                )

            except Exception as rollback_exc:
                rollback_failures.append(
                    "primary_manifest_restore_failed:"
                    f"{rollback_exc!r}"
                )

            if rollback_failures:
                raise RuntimeError(
                    "rename_failed_and_rollback_incomplete:"
                    + ";".join(
                        rollback_failures
                    )
                ) from exc

            raise

        return target_manifest_path

    @staticmethod
    def _is_encrypted_manifest(
        path: str | Path,
    ) -> bool:

        path = Path(
            path
        )


        try:

            payload = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            return False


        return (
            isinstance(
                payload,
                dict,
            )
            and
            payload.get(
                "schema"
            )
            ==
            ENCRYPTED_CONTAINER_SCHEMA
        )


    @staticmethod
    def _project_rename_stable_state(
        manifest: ProjectManifest,
    ):

        return (
            manifest.project_id,
            manifest.created_at,
            list(
                manifest.active_designs
            ),
            list(
                manifest.linked_reports
            ),
            list(
                manifest.linked_exports
            ),
            manifest.project_notes,
            manifest.runtime_schema_version,
            manifest.storage_schema_version,
            manifest.owner_principal_id,
            manifest.security_classification,
        )


    @staticmethod
    def _design_rename_stable_state(
        manifest: DesignManifest,
    ):

        return (
            manifest.design_id,
            manifest.parent_project_id,
            manifest.created_at,
            manifest.engine_type,
            manifest.solver_profile,
            manifest.materials_profile,
            manifest.geometry_profile,
            list(
                manifest.validation_refs
            ),
            list(
                manifest.report_refs
            ),
            list(
                manifest.export_refs
            ),
            manifest.dirty_state,
            manifest.runtime_last_opened,
            manifest.storage_schema_version,
            manifest.engineering_state_ref,
        )


    def _run_encrypted_manifest_transaction(
        self,
        *,
        manifest_path: str | Path,
        manifest_payload: dict[str, Any],
        original_manifest_bytes: bytes,
        verify: Callable[[Path], None],
        after_persist: Callable[[Path], None] | None = None,
    ) -> Path:
        """
        Atomic manifest-only lifecycle transaction.

        Encrypted resources use immutable opaque ID
        directories, so rename updates ciphertext rather
        than moving the filesystem identity.
        """

        from leaf_qt.storage.save_load_bridge import (
            SaveLoadRuntimeBridge,
        )


        manifest_path = Path(
            manifest_path
        )


        try:

            self._write_json(
                manifest_path,
                manifest_payload,
            )


            verify(
                manifest_path
            )


            if after_persist is not None:

                after_persist(
                    manifest_path
                )


            return manifest_path


        except Exception:

            SaveLoadRuntimeBridge._write_bytes_atomic(
                manifest_path,
                original_manifest_bytes,
            )


            raise


    def rename_project(
        self,
        project_manifest_path: str | Path,
        new_name: str,
        *,
        after_persist: Callable[[Path], None] | None = None,
    ) -> Path:

        project_manifest_path = (
            self.storage.resolve_ref(
                project_manifest_path
            )
        )


        if self._is_encrypted_manifest(
            project_manifest_path
        ):

            return (
                self._rename_encrypted_project(
                    project_manifest_path,
                    new_name,
                    after_persist=
                        after_persist,
                )
            )


        return (
            self._rename_plaintext_project(
                project_manifest_path,
                new_name,
                after_persist=
                    after_persist,
            )
        )


    def rename_design(
        self,
        design_manifest_path: str | Path,
        new_name: str,
        *,
        after_persist: Callable[[Path], None] | None = None,
    ) -> Path:

        design_manifest_path = (
            self.storage.resolve_ref(
                design_manifest_path
            )
        )


        if self._is_encrypted_manifest(
            design_manifest_path
        ):

            return (
                self._rename_encrypted_design(
                    design_manifest_path,
                    new_name,
                    after_persist=
                        after_persist,
                )
            )


        return (
            self._rename_plaintext_design(
                design_manifest_path,
                new_name,
                after_persist=
                    after_persist,
            )
        )


    def _rename_encrypted_project(
        self,
        project_manifest_path: str | Path,
        new_name: str,
        *,
        after_persist: Callable[[Path], None] | None = None,
    ) -> Path:

        requested_name = str(
            new_name
        ).strip()


        if not requested_name:

            raise ValueError(
                "project_name_required"
            )


        project_manifest_path = (
            self.storage.resolve_ref(
                project_manifest_path
            )
        )


        if (
            project_manifest_path.name
            !=
            PROJECT_MANIFEST_FILENAME
        ):

            raise ValueError(
                "project_manifest_filename_invalid"
            )


        if not project_manifest_path.is_file():

            raise FileNotFoundError(
                "project_manifest_not_found:"
                f"{project_manifest_path}"
            )


        original_bytes = (
            project_manifest_path
            .read_bytes()
        )


        container = json.loads(
            original_bytes.decode(
                "utf-8"
            )
        )


        if (
            not isinstance(
                container,
                dict,
            )
            or
            container.get(
                "schema"
            )
            !=
            ENCRYPTED_CONTAINER_SCHEMA
            or
            container.get(
                "resource_type"
            )
            !=
            PROJECT_ROOT_RESOURCE
        ):

            raise ValueError(
                "encrypted_project_root_container_required"
            )


        project_id = str(
            container.get(
                "project_id",
                "",
            )
        ).strip()


        owner_principal_id = str(
            container.get(
                "owner_principal_id",
                "",
            )
        ).strip()


        classification = str(
            container.get(
                "security_classification",
                "",
            )
        ).strip()


        if (
            project_manifest_path
            .parent
            .name
            !=
            project_id
        ):

            raise ValueError(
                "encrypted_project_directory_identity_mismatch"
            )


        principal_id = (
            self.security_context
            .principal_id
        )




        custody = (
            self._require_key_custody()
        )


        project_key = (
            custody.retrieve_project_key(
                principal_id,
                project_id,
            )
        )


        container_owner = (
            self._require_encrypted_container_owner()
        )


        manifest = (
            ProjectManifest.from_dict(
                container_owner.open(
                    container=
                        container,

                    project_key=
                        project_key,

                    expected_project_id=
                        project_id,

                    expected_owner_principal_id=
                        principal_id,

                    expected_security_classification=
                        classification,

                    expected_resource_type=
                        PROJECT_ROOT_RESOURCE,

                    expected_resource_id=
                        project_id,
                )
            )
        )


        self.security_context.require_project_modify(
            manifest
        )


        before_validation = (
            ProjectManifestValidator()
            .validate(
                manifest
            )
        )


        if (
            before_validation.get(
                "passed"
            )
            is not True
        ):

            raise ValueError(
                "encrypted_project_manifest_invalid_before_rename:"
                +
                ",".join(
                    before_validation.get(
                        "failures",
                        [],
                    )
                )
            )


        if (
            manifest.project_name
            ==
            requested_name
        ):

            return project_manifest_path


        preserved_state = (
            self._project_rename_stable_state(
                manifest
            )
        )


        manifest.project_name = (
            requested_name
        )


        manifest.touch()


        validation = (
            ProjectManifestValidator()
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
                "encrypted_project_manifest_invalid_after_rename:"
                +
                ",".join(
                    validation.get(
                        "failures",
                        [],
                    )
                )
            )


        portable_key_envelope = (
            container.get(
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


        renamed_container = (
            container_owner.seal(
                payload=
                    manifest.snapshot(),

                project_id=
                    project_id,

                owner_principal_id=
                    principal_id,

                security_classification=
                    classification,

                resource_type=
                    PROJECT_ROOT_RESOURCE,

                resource_id=
                    project_id,

                project_key=
                    project_key,

                portable_key_envelope=
                    portable_key_envelope,
            )
        )


        def verify(
            persisted_path: Path,
        ) -> None:

            persisted_container = json.loads(
                persisted_path.read_text(
                    encoding="utf-8"
                )
            )


            persisted = (
                ProjectManifest.from_dict(
                    container_owner.open(
                        container=
                            persisted_container,

                        project_key=
                            project_key,

                        expected_project_id=
                            project_id,

                        expected_owner_principal_id=
                            principal_id,

                        expected_security_classification=
                            classification,

                        expected_resource_type=
                            PROJECT_ROOT_RESOURCE,

                        expected_resource_id=
                            project_id,
                    )
                )
            )


            if (
                ProjectManifestValidator()
                .validate(
                    persisted
                )
                .get(
                    "passed"
                )
                is not True
            ):

                raise RuntimeError(
                    "encrypted_project_rename_persisted_manifest_invalid"
                )


            if (
                persisted.project_name
                !=
                requested_name
            ):

                raise RuntimeError(
                    "encrypted_project_rename_name_not_persisted"
                )


            if (
                self._project_rename_stable_state(
                    persisted
                )
                !=
                preserved_state
            ):

                raise RuntimeError(
                    "encrypted_project_rename_changed_stable_project_state"
                )


            if (
                persisted_path.parent.name
                !=
                project_id
            ):

                raise RuntimeError(
                    "encrypted_project_rename_changed_opaque_directory_identity"
                )


            if (
                requested_name
                in
                persisted_path.read_text(
                    encoding="utf-8"
                )
            ):

                raise RuntimeError(
                    "encrypted_project_rename_exposed_plaintext_name"
                )


        return (
            self._run_encrypted_manifest_transaction(
                manifest_path=
                    project_manifest_path,

                manifest_payload=
                    renamed_container,

                original_manifest_bytes=
                    original_bytes,

                verify=
                    verify,

                after_persist=
                    after_persist,
            )
        )


    def _rename_encrypted_design(
        self,
        design_manifest_path: str | Path,
        new_name: str,
        *,
        after_persist: Callable[[Path], None] | None = None,
    ) -> Path:

        requested_name = str(
            new_name
        ).strip()


        if not requested_name:

            raise ValueError(
                "design_name_required"
            )


        design_manifest_path = (
            self.storage.resolve_ref(
                design_manifest_path
            )
        )


        if (
            design_manifest_path.name
            !=
            DESIGN_MANIFEST_FILENAME
        ):

            raise ValueError(
                "design_manifest_filename_invalid"
            )


        if not design_manifest_path.is_file():

            raise FileNotFoundError(
                "design_manifest_not_found:"
                f"{design_manifest_path}"
            )


        original_design_bytes = (
            design_manifest_path
            .read_bytes()
        )


        design_container = json.loads(
            original_design_bytes.decode(
                "utf-8"
            )
        )


        if (
            not isinstance(
                design_container,
                dict,
            )
            or
            design_container.get(
                "schema"
            )
            !=
            ENCRYPTED_CONTAINER_SCHEMA
            or
            design_container.get(
                "resource_type"
            )
            !=
            DESIGN_MANIFEST_RESOURCE
        ):

            raise ValueError(
                "encrypted_design_container_required"
            )


        project_id = str(
            design_container.get(
                "project_id",
                "",
            )
        ).strip()


        design_id = str(
            design_container.get(
                "resource_id",
                "",
            )
        ).strip()


        owner_principal_id = str(
            design_container.get(
                "owner_principal_id",
                "",
            )
        ).strip()


        classification = str(
            design_container.get(
                "security_classification",
                "",
            )
        ).strip()


        if (
            design_manifest_path
            .parent
            .name
            !=
            design_id
        ):

            raise ValueError(
                "encrypted_design_directory_identity_mismatch"
            )


        principal_id = (
            self.security_context
            .principal_id
        )




        project_manifest_path = (
            self.storage
            .canonical_path(
                "projects"
            )
            /
            project_id
            /
            PROJECT_MANIFEST_FILENAME
        )


        if not project_manifest_path.is_file():

            raise FileNotFoundError(
                "encrypted_design_parent_project_missing:"
                f"{project_manifest_path}"
            )


        original_project_bytes = (
            project_manifest_path
            .read_bytes()
        )


        project_container = json.loads(
            original_project_bytes.decode(
                "utf-8"
            )
        )


        custody = (
            self._require_key_custody()
        )


        project_key = (
            custody.retrieve_project_key(
                principal_id,
                project_id,
            )
        )


        container_owner = (
            self._require_encrypted_container_owner()
        )


        project_manifest = (
            ProjectManifest.from_dict(
                container_owner.open(
                    container=
                        project_container,

                    project_key=
                        project_key,

                    expected_project_id=
                        project_id,

                    expected_owner_principal_id=
                        principal_id,

                    expected_security_classification=
                        classification,

                    expected_resource_type=
                        PROJECT_ROOT_RESOURCE,

                    expected_resource_id=
                        project_id,
                )
            )
        )


        self.security_context.require_project_modify(
            project_manifest
        )


        design_manifest = (
            DesignManifest.from_dict(
                container_owner.open(
                    container=
                        design_container,

                    project_key=
                        project_key,

                    expected_project_id=
                        project_id,

                    expected_owner_principal_id=
                        principal_id,

                    expected_security_classification=
                        classification,

                    expected_resource_type=
                        DESIGN_MANIFEST_RESOURCE,

                    expected_resource_id=
                        design_id,
                )
            )
        )


        if (
            design_manifest.parent_project_id
            !=
            project_id
        ):

            raise ValueError(
                "encrypted_design_parent_project_id_mismatch"
            )


        before_validation = (
            DesignManifestValidator()
            .validate(
                design_manifest
            )
        )


        if (
            before_validation.get(
                "passed"
            )
            is not True
        ):

            raise ValueError(
                "encrypted_design_manifest_invalid_before_rename:"
                +
                ",".join(
                    before_validation.get(
                        "failures",
                        [],
                    )
                )
            )


        if (
            design_manifest.design_name
            ==
            requested_name
        ):

            return design_manifest_path


        preserved_state = (
            self._design_rename_stable_state(
                design_manifest
            )
        )


        design_manifest.design_name = (
            requested_name
        )


        design_manifest.touch()


        validation = (
            DesignManifestValidator()
            .validate(
                design_manifest
            )
        )


        if (
            validation.get(
                "passed"
            )
            is not True
        ):

            raise ValueError(
                "encrypted_design_manifest_invalid_after_rename:"
                +
                ",".join(
                    validation.get(
                        "failures",
                        [],
                    )
                )
            )


        renamed_container = (
            container_owner.seal(
                payload=
                    design_manifest.snapshot(),

                project_id=
                    project_id,

                owner_principal_id=
                    principal_id,

                security_classification=
                    classification,

                resource_type=
                    DESIGN_MANIFEST_RESOURCE,

                resource_id=
                    design_id,

                project_key=
                    project_key,

                portable_key_envelope=
                    None,
            )
        )


        def verify(
            persisted_path: Path,
        ) -> None:

            persisted_container = json.loads(
                persisted_path.read_text(
                    encoding="utf-8"
                )
            )


            persisted = (
                DesignManifest.from_dict(
                    container_owner.open(
                        container=
                            persisted_container,

                        project_key=
                            project_key,

                        expected_project_id=
                            project_id,

                        expected_owner_principal_id=
                            principal_id,

                        expected_security_classification=
                            classification,

                        expected_resource_type=
                            DESIGN_MANIFEST_RESOURCE,

                        expected_resource_id=
                            design_id,
                    )
                )
            )


            if (
                DesignManifestValidator()
                .validate(
                    persisted
                )
                .get(
                    "passed"
                )
                is not True
            ):

                raise RuntimeError(
                    "encrypted_design_rename_persisted_manifest_invalid"
                )


            if (
                persisted.design_name
                !=
                requested_name
            ):

                raise RuntimeError(
                    "encrypted_design_rename_name_not_persisted"
                )


            if (
                self._design_rename_stable_state(
                    persisted
                )
                !=
                preserved_state
            ):

                raise RuntimeError(
                    "encrypted_design_rename_changed_stable_design_state"
                )


            if (
                persisted_path.parent.name
                !=
                design_id
            ):

                raise RuntimeError(
                    "encrypted_design_rename_changed_opaque_directory_identity"
                )


            if (
                requested_name
                in
                persisted_path.read_text(
                    encoding="utf-8"
                )
            ):

                raise RuntimeError(
                    "encrypted_design_rename_exposed_plaintext_name"
                )


            if (
                project_manifest_path.read_bytes()
                !=
                original_project_bytes
            ):

                raise RuntimeError(
                    "encrypted_design_rename_unnecessarily_modified_project_root"
                )


        return (
            self._run_encrypted_manifest_transaction(
                manifest_path=
                    design_manifest_path,

                manifest_payload=
                    renamed_container,

                original_manifest_bytes=
                    original_design_bytes,

                verify=
                    verify,

                after_persist=
                    after_persist,
            )
        )

    def _rename_plaintext_project(
        self,
        project_manifest_path: str | Path,
        new_name: str,
        *,
        after_persist: Callable[[Path], None] | None = None,
    ) -> Path:
        """
        Rename a canonical project while preserving
        its stable identity.
        """
        self.storage.ensure_roots()

        requested_name = str(
            new_name
        ).strip()

        if not requested_name:
            raise ValueError(
                "project_name_required"
            )

        target_slug = safe_slug(
            requested_name
        )

        if target_slug in {".", ".."}:
            raise ValueError(
                "project_name_resolves_to_invalid_storage_slug"
            )

        project_manifest_path = (
            self.storage.resolve_ref(
                project_manifest_path
            )
        )

        if (
            project_manifest_path.name
            != PROJECT_MANIFEST_FILENAME
        ):
            raise ValueError(
                "project_manifest_filename_invalid"
            )

        if not project_manifest_path.is_file():
            raise FileNotFoundError(
                "project_manifest_not_found:"
                f"{project_manifest_path}"
            )

        projects_root = (
            self.storage
            .canonical_path(
                "projects"
            )
            .resolve()
        )

        source_dir = (
            project_manifest_path
            .parent
            .resolve()
        )

        if (
            source_dir.parent
            != projects_root
        ):
            raise ValueError(
                "project_manifest_outside_canonical_project_root:"
                f"{project_manifest_path}"
            )

        target_dir = (
            projects_root
            / target_slug
        )

        if (
            target_dir != source_dir
            and target_dir.exists()
        ):
            raise FileExistsError(
                "project_rename_target_exists:"
                f"{target_dir}"
            )

        original_bytes = (
            project_manifest_path
            .read_bytes()
        )

        project_manifest = (
            ProjectManifest.from_dict(
                json.loads(
                    original_bytes.decode(
                        "utf-8"
                    )
                )
            )
        )
        self.security_context.require_project_modify(project_manifest)

        preserved_state = (
            project_manifest.project_id,
            list(
                project_manifest.active_designs
            ),
            list(
                project_manifest.linked_reports
            ),
            list(
                project_manifest.linked_exports
            ),
            project_manifest.project_notes,
            project_manifest.runtime_schema_version,
            project_manifest.storage_schema_version,
            project_manifest.owner_principal_id,
            project_manifest.security_classification,
        )

        if (
            project_manifest.project_name
            == requested_name
            and target_dir
            == source_dir
        ):
            return project_manifest_path

        project_manifest.project_name = (
            requested_name
        )

        project_manifest.touch()

        validation = (
            ProjectManifestValidator()
            .validate(
                project_manifest
            )
        )

        if (
            validation.get("passed")
            is not True
        ):
            raise ValueError(
                "project_manifest_invalid_after_rename:"
                + ",".join(
                    validation.get(
                        "failures",
                        [],
                    )
                )
            )

        def verify(
            target_manifest_path: Path,
        ) -> None:
            persisted = (
                ProjectManifest.from_dict(
                    json.loads(
                        target_manifest_path
                        .read_text(
                            encoding="utf-8"
                        )
                    )
                )
            )

            persisted_validation = (
                ProjectManifestValidator()
                .validate(
                    persisted
                )
            )

            persisted_state = (
                persisted.project_id,
                list(
                    persisted.active_designs
                ),
                list(
                    persisted.linked_reports
                ),
                list(
                    persisted.linked_exports
                ),
                persisted.project_notes,
                persisted.runtime_schema_version,
                persisted.storage_schema_version,
                persisted.owner_principal_id,
                persisted.security_classification,
            )

            if (
                persisted_validation.get(
                    "passed"
                )
                is not True
            ):
                raise RuntimeError(
                    "project_rename_persisted_manifest_invalid"
                )

            if (
                persisted.project_name
                != requested_name
            ):
                raise RuntimeError(
                    "project_rename_name_not_persisted"
                )

            if (
                persisted_state
                != preserved_state
            ):
                raise RuntimeError(
                    "project_rename_changed_stable_project_state"
                )

        return self._run_rename_transaction(
            source_dir=source_dir,
            target_dir=target_dir,
            manifest_filename=
                PROJECT_MANIFEST_FILENAME,
            manifest_payload=
                project_manifest.snapshot(),
            original_manifest_bytes=
                original_bytes,
            related_writes=[],
            verify=verify,
            after_persist=after_persist,
        )

    def _rename_plaintext_design(
        self,
        design_manifest_path: str | Path,
        new_name: str,
        *,
        after_persist: Callable[[Path], None] | None = None,
    ) -> Path:
        """
        Rename a canonical design and atomically
        update its owning project reference.
        """
        self.storage.ensure_roots()

        requested_name = str(
            new_name
        ).strip()

        if not requested_name:
            raise ValueError(
                "design_name_required"
            )

        target_slug = safe_slug(
            requested_name
        )

        if target_slug in {".", ".."}:
            raise ValueError(
                "design_name_resolves_to_invalid_storage_slug"
            )

        design_manifest_path = (
            self.storage.resolve_ref(
                design_manifest_path
            )
        )

        if (
            design_manifest_path.name
            != DESIGN_MANIFEST_FILENAME
        ):
            raise ValueError(
                "design_manifest_filename_invalid"
            )

        if not design_manifest_path.is_file():
            raise FileNotFoundError(
                "design_manifest_not_found:"
                f"{design_manifest_path}"
            )

        designs_root = (
            self.storage
            .canonical_path(
                "designs"
            )
            .resolve()
        )

        source_dir = (
            design_manifest_path
            .parent
            .resolve()
        )

        if (
            source_dir.parent
            != designs_root
        ):
            raise ValueError(
                "design_manifest_outside_canonical_design_root:"
                f"{design_manifest_path}"
            )

        target_dir = (
            designs_root
            / target_slug
        )

        target_manifest_path = (
            target_dir
            / DESIGN_MANIFEST_FILENAME
        )

        if (
            target_dir != source_dir
            and target_dir.exists()
        ):
            raise FileExistsError(
                "design_rename_target_exists:"
                f"{target_dir}"
            )

        original_design_bytes = (
            design_manifest_path
            .read_bytes()
        )

        design_manifest = (
            DesignManifest.from_dict(
                json.loads(
                    original_design_bytes.decode(
                        "utf-8"
                    )
                )
            )
        )

        design_validation = (
            DesignManifestValidator()
            .validate(
                design_manifest
            )
        )

        if (
            design_validation.get(
                "passed"
            )
            is not True
        ):
            raise ValueError(
                "design_manifest_invalid_before_rename:"
                + ",".join(
                    design_validation.get(
                        "failures",
                        [],
                    )
                )
            )

        # Exact same name/path is a true no-op.
        if (
            design_manifest.design_name
            == requested_name
            and target_dir
            == source_dir
        ):
            return design_manifest_path

        # Reuse the canonical browser relationship owner.
        browser = ProjectBrowserModel(
            self.storage.root
        )

        project_manifest_path = (
            browser
            .resolve_project_manifest_for_design(
                design_manifest_path
            )
        )

        if project_manifest_path is None:
            raise ValueError(
                "design_parent_project_not_uniquely_resolvable"
            )

        project_manifest_path = (
            project_manifest_path.resolve()
        )

        original_project_bytes = (
            project_manifest_path
            .read_bytes()
        )

        project_manifest = (
            ProjectManifest.from_dict(
                json.loads(
                    original_project_bytes.decode(
                        "utf-8"
                    )
                )
            )
        )
        self.security_context.require_project_modify(project_manifest)

        if (
            project_manifest.project_id
            != design_manifest.parent_project_id
        ):
            raise ValueError(
                "design_parent_project_id_mismatch"
            )

        # Find the explicit project-side relationship
        # by resolved path, preserving compatibility with
        # portable and older absolute references.
        matching_refs = [
            ref
            for ref
            in project_manifest.active_designs
            if paths_match(
                self.storage.resolve_ref(
                    ref
                ),
                design_manifest_path,
            )
        ]

        if len(matching_refs) != 1:
            raise ValueError(
                "design_active_reference_missing_or_ambiguous"
            )

        new_design_ref = (
            self.storage.portable_ref(
                target_manifest_path
            )
        )

        # Do not permit another existing project reference
        # to already claim the requested target.
        for ref in (
            project_manifest.active_designs
        ):
            if ref in matching_refs:
                continue

            if paths_match(
                self.storage.resolve_ref(
                    ref
                ),
                target_manifest_path,
            ):
                raise FileExistsError(
                    "design_target_reference_already_present"
                )

        preserved_design_state = (
            design_manifest.design_id,
            design_manifest.parent_project_id,
            design_manifest.created_at,
            design_manifest.engine_type,
            design_manifest.solver_profile,
            design_manifest.materials_profile,
            design_manifest.geometry_profile,
            list(
                design_manifest.validation_refs
            ),
            list(
                design_manifest.report_refs
            ),
            list(
                design_manifest.export_refs
            ),
            design_manifest.dirty_state,
            design_manifest.runtime_last_opened,
            design_manifest.storage_schema_version,
            design_manifest.engineering_state_ref,
        )

        preserved_project_state = (
            project_manifest.project_id,
            project_manifest.project_name,
            project_manifest.created_at,
            list(
                project_manifest.linked_reports
            ),
            list(
                project_manifest.linked_exports
            ),
            project_manifest.project_notes,
            project_manifest.runtime_schema_version,
            project_manifest.storage_schema_version,
            project_manifest.owner_principal_id,
            project_manifest.security_classification,
        )

        design_manifest.design_name = (
            requested_name
        )

        design_manifest.touch()

        project_manifest.active_designs = [
            (
                new_design_ref
                if ref in matching_refs
                else ref
            )
            for ref
            in project_manifest.active_designs
        ]

        project_manifest.touch()

        design_validation = (
            DesignManifestValidator()
            .validate(
                design_manifest
            )
        )

        project_validation = (
            ProjectManifestValidator()
            .validate(
                project_manifest
            )
        )

        if (
            design_validation.get(
                "passed"
            )
            is not True
        ):
            raise ValueError(
                "design_manifest_invalid_after_rename:"
                + ",".join(
                    design_validation.get(
                        "failures",
                        [],
                    )
                )
            )

        if (
            project_validation.get(
                "passed"
            )
            is not True
        ):
            raise ValueError(
                "project_manifest_invalid_after_design_rename:"
                + ",".join(
                    project_validation.get(
                        "failures",
                        [],
                    )
                )
            )

        expected_active_designs = list(
            project_manifest.active_designs
        )

        def verify(
            persisted_design_path: Path,
        ) -> None:
            persisted_design = (
                DesignManifest.from_dict(
                    json.loads(
                        persisted_design_path
                        .read_text(
                            encoding="utf-8"
                        )
                    )
                )
            )

            persisted_project = (
                ProjectManifest.from_dict(
                    json.loads(
                        project_manifest_path
                        .read_text(
                            encoding="utf-8"
                        )
                    )
                )
            )

            if (
                DesignManifestValidator()
                .validate(
                    persisted_design
                )
                .get("passed")
                is not True
            ):
                raise RuntimeError(
                    "design_rename_persisted_design_invalid"
                )

            if (
                ProjectManifestValidator()
                .validate(
                    persisted_project
                )
                .get("passed")
                is not True
            ):
                raise RuntimeError(
                    "design_rename_persisted_project_invalid"
                )

            persisted_design_state = (
                persisted_design.design_id,
                persisted_design.parent_project_id,
                persisted_design.created_at,
                persisted_design.engine_type,
                persisted_design.solver_profile,
                persisted_design.materials_profile,
                persisted_design.geometry_profile,
                list(
                    persisted_design.validation_refs
                ),
                list(
                    persisted_design.report_refs
                ),
                list(
                    persisted_design.export_refs
                ),
                persisted_design.dirty_state,
                persisted_design.runtime_last_opened,
                persisted_design.storage_schema_version,
                persisted_design.engineering_state_ref,
            )

            persisted_project_state = (
                persisted_project.project_id,
                persisted_project.project_name,
                persisted_project.created_at,
                list(
                    persisted_project.linked_reports
                ),
                list(
                    persisted_project.linked_exports
                ),
                persisted_project.project_notes,
                persisted_project.runtime_schema_version,
                persisted_project.storage_schema_version,
                persisted_project.owner_principal_id,
                persisted_project.security_classification,
            )

            if (
                persisted_design.design_name
                != requested_name
            ):
                raise RuntimeError(
                    "design_rename_name_not_persisted"
                )

            if (
                persisted_design_state
                != preserved_design_state
            ):
                raise RuntimeError(
                    "design_rename_changed_stable_design_state"
                )

            if (
                persisted_project_state
                != preserved_project_state
            ):
                raise RuntimeError(
                    "design_rename_changed_stable_project_state"
                )

            if (
                persisted_project.active_designs
                != expected_active_designs
            ):
                raise RuntimeError(
                    "design_rename_project_reference_not_persisted"
                )

            resolved_project = (
                ProjectBrowserModel(
                    self.storage.root
                )
                .resolve_project_manifest_for_design(
                    persisted_design_path
                )
            )

            if (
                resolved_project is None
                or resolved_project.resolve()
                != project_manifest_path
            ):
                raise RuntimeError(
                    "design_rename_browser_resolution_failed"
                )

        return self._run_rename_transaction(
            source_dir=source_dir,
            target_dir=target_dir,
            manifest_filename=
                DESIGN_MANIFEST_FILENAME,
            manifest_payload=
                design_manifest.snapshot(),
            original_manifest_bytes=
                original_design_bytes,
            related_writes=[
                (
                    project_manifest_path,
                    project_manifest.snapshot(),
                    original_project_bytes,
                )
            ],
            verify=verify,
            after_persist=after_persist,
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "storage": self.storage.snapshot(),
            "creates_project_folders": True,
            "creates_design_folders": True,
            "writes_project_manifest": True,
            "writes_design_manifest": True,
            "links_design_to_project": True,
            "qt_owns_creation_workflow": False,
            "stores_solver_payloads": False,
            "stores_report_payloads": False,
            "stores_validation_payloads": False,
        }

    @staticmethod
    def _write_json(
        path: Path,
        payload: dict[str, Any],
    ) -> None:

        from leaf_qt.storage.save_load_bridge import (
            SaveLoadRuntimeBridge,
        )


        SaveLoadRuntimeBridge._write_json(
            path,
            payload,
        )


project_design_creation_owner = ProjectDesignCreationOwner()
