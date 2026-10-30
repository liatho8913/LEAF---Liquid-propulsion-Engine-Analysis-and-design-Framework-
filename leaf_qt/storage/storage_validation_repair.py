from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from leaf_qt.storage.canonical_storage import CANONICAL_ROOTS, CanonicalStorageOwner
from leaf_qt.storage.design_manifest import DESIGN_MANIFEST_FILENAME, DesignManifest, DesignManifestValidator
from leaf_qt.storage.project_manifest import PROJECT_MANIFEST_FILENAME, ProjectManifest, ProjectManifestValidator
from leaf_qt.encrypted_container import (
    ENCRYPTION_ALGORITHM,
    PROJECT_ROOT_RESOURCE,
    SCHEMA as ENCRYPTED_CONTAINER_SCHEMA,
)
from leaf_qt.key_envelope import (
    SCHEMA as PORTABLE_KEY_ENVELOPE_SCHEMA,
)
from leaf_qt.security_context import (
    VALID_SECURITY_CLASSIFICATIONS,
)

if TYPE_CHECKING:
    from leaf_qt.security_audit import SecurityAuditOwner
from leaf_qt.encrypted_container import (
    DESIGN_MANIFEST_RESOURCE,
    ENGINEERING_STATE_RESOURCE,
)
from leaf_qt.encrypted_container import (
    ENGINEERING_CACHE_RESOURCE,
    INTERNAL_PROJECT_RESOURCE_TYPES,
    INTERNAL_REPORT_RESOURCE,
    VALIDATION_EVIDENCE_RESOURCE,
)

SCHEMA = "LEAF_STORAGE_VALIDATION_REPAIR_PHASE_25H_V1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class StorageIssue:
    issue_id: str
    severity: str
    issue_type: str
    path: str
    message: str
    repairable: bool = False
    repaired: bool = False
    created_at: str = field(default_factory=utc_now)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_STORAGE_ISSUE_PHASE_25H_V1"
        return payload


class StorageValidationRepairOwner:
    """
    Conservative storage validation and repair owner.

    Allowed repair:
    - create missing canonical folders

    Not allowed:
    - delete files
    - archive files
    - move files
    - overwrite manifests
    - rewrite broken links automatically
    """

    def __init__(
        self,
        root: str | Path | None = None,
        security_audit: SecurityAuditOwner | None = None,
    ) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.storage = CanonicalStorageOwner(self.root)
        self.project_validator = ProjectManifestValidator()
        self.design_validator = DesignManifestValidator()

        if security_audit is None:
            from leaf_qt.security_audit import SecurityAuditOwner

            security_audit = SecurityAuditOwner()

        self.security_audit = security_audit


    def validate(
        self,
        repair: bool = False,
    ):

        result = dict(
            self._validate_plaintext(
                repair=
                    repair
            )
        )


        encrypted_child_paths = {
            str(
                path
            )
            for path
            in (
                self._encrypted_design_manifest_paths()
                +
                self._encrypted_engineering_state_paths()
            )
        }


        base_issues = list(
            result.get(
                "issues",
                [],
            )
        )


        removed_child_issues = [
            issue
            for issue
            in base_issues
            if str(
                issue.get(
                    "path",
                    "",
                )
            )
            in
            encrypted_child_paths
        ]


        retained_base_issues = [
            issue
            for issue
            in base_issues
            if str(
                issue.get(
                    "path",
                    "",
                )
            )
            not in
            encrypted_child_paths
        ]


        project_issues = (
            self
            ._validate_encrypted_project_manifests()
        )


        child_issues = (
            self
            ._validate_encrypted_design_and_state_resources()
        )


        internal_reference_issues = (
            self
            ._validate_protected_internal_references()
        )


        internal_container_issues = (
            self
            ._validate_internal_resource_containers()
        )


        original_error_count = int(
            result.get(
                "error_count",
                0,
            )
        )


        removed_error_count = sum(
            1
            for issue
            in removed_child_issues
            if str(
                issue.get(
                    "severity",
                    "error",
                )
            ).lower()
            ==
            "error"
        )


        retained_base_error_count = max(
            0,
            original_error_count
            -
            removed_error_count,
        )


        security_issues = (
            project_issues
            +
            child_issues
            +
            internal_reference_issues
            +
            internal_container_issues
        )


        security_error_count = sum(
            1
            for issue
            in security_issues
            if str(
                issue.get(
                    "severity",
                    "error",
                )
            ).lower()
            ==
            "error"
        )


        original_pass = result.get(
            "passed"
        )


        if original_pass is None:

            base_pass = (
                retained_base_error_count
                ==
                0
            )

        elif (
            original_pass
            is False
            and
            removed_error_count
            >
            0
            and
            retained_base_error_count
            ==
            0
        ):

            base_pass = True

        else:

            base_pass = bool(
                original_pass
            )


        result[
            "issues"
        ] = (
            retained_base_issues
            +
            security_issues
        )


        result[
            "issue_count"
        ] = len(
            result[
                "issues"
            ]
        )


        result[
            "error_count"
        ] = (
            retained_base_error_count
            +
            security_error_count
        )


        result[
            "passed"
        ] = (
            base_pass
            and
            security_error_count
            ==
            0
        )


        result[
            "encrypted_project_count"
        ] = len(
            self._encrypted_project_manifest_paths()
        )


        result[
            "encrypted_design_count"
        ] = len(
            self._encrypted_design_manifest_paths()
        )


        result[
            "encrypted_engineering_state_count"
        ] = len(
            self._encrypted_engineering_state_paths()
        )


        result[
            "encrypted_internal_resource_count"
        ] = len(
            self._encrypted_internal_resource_records()
        )


        result[
            "protected_internal_reference_count"
        ] = len(
            self._protected_internal_reference_records()
        )


        result[
            "encrypted_project_validation_enabled"
        ] = True


        result[
            "encrypted_child_resource_validation_enabled"
        ] = True


        result[
            "internal_resource_protection_validation_enabled"
        ] = True


        return result


    @staticmethod
    def _is_encrypted_project_payload(
        payload,
    ) -> bool:

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
            and
            payload.get(
                "resource_type"
            )
            ==
            PROJECT_ROOT_RESOURCE
        )


    def _encrypted_project_manifest_paths(
        self,
    ):

        projects_root = (
            self.storage
            .canonical_path(
                "projects"
            )
        )


        if not projects_root.exists():

            return []


        paths = []


        for path in sorted(
            projects_root.rglob(
                PROJECT_MANIFEST_FILENAME
            )
        ):

            try:

                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                continue


            if self._is_encrypted_project_payload(
                payload
            ):

                paths.append(
                    path
                )


        return paths


    @staticmethod
    def _encrypted_issue(
        path,
        message: str,
    ):

        return {
            "severity":
                "error",

            "path":
                str(
                    path
                ),

            "message":
                str(
                    message
                ),

            "repairable":
                False,
        }


    def _validate_encrypted_project_manifests(
        self,
    ):

        issues = []


        plaintext_ids = set()


        for path in self._project_manifest_paths():

            try:

                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                continue


            project_id = str(
                payload.get(
                    "project_id",
                    "",
                )
            ).strip()


            if project_id:

                plaintext_ids.add(
                    project_id
                )


        seen_ids = set(
            plaintext_ids
        )


        sensitive_clear_fields = {
            "project_name",
            "project_notes",
            "active_designs",
            "linked_reports",
            "linked_exports",
            "runtime_schema_version",
        }


        prohibited_secret_fields = {
            "key_reference",
            "local_key_reference",
            "project_key",
            "raw_project_key",
            "recovery_key",
            "recovery_root_key",
        }


        for path in (
            self
            ._encrypted_project_manifest_paths()
        ):

            try:

                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception as exc:

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_json_unreadable:"
                        f"{exc!r}",
                    )
                )

                continue


            project_id = str(
                payload.get(
                    "project_id",
                    "",
                )
            ).strip()


            owner_principal_id = str(
                payload.get(
                    "owner_principal_id",
                    "",
                )
            ).strip()


            classification = str(
                payload.get(
                    "security_classification",
                    "",
                )
            ).strip()


            resource_id = str(
                payload.get(
                    "resource_id",
                    "",
                )
            ).strip()


            if not project_id.startswith(
                "project_"
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_id_invalid",
                    )
                )


            if (
                project_id
                in
                seen_ids
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "duplicate_project_id:"
                        f"{project_id}",
                    )
                )

            else:

                seen_ids.add(
                    project_id
                )


            if (
                project_id
                and
                path.parent.name
                !=
                project_id
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_directory_not_opaque_project_id",
                    )
                )


            if not owner_principal_id.startswith(
                "principal_"
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_owner_invalid",
                    )
                )


            if (
                classification
                not in
                VALID_SECURITY_CLASSIFICATIONS
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_classification_invalid",
                    )
                )


            if (
                payload.get(
                    "encryption_algorithm"
                )
                !=
                ENCRYPTION_ALGORITHM
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_algorithm_invalid",
                    )
                )


            if (
                resource_id
                !=
                project_id
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_resource_identity_mismatch",
                    )
                )


            if not str(
                payload.get(
                    "nonce",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_nonce_missing",
                    )
                )


            if not str(
                payload.get(
                    "ciphertext",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_ciphertext_missing",
                    )
                )


            fingerprint = str(
                payload.get(
                    "portable_key_envelope_fingerprint",
                    "",
                )
            ).strip()


            if (
                len(
                    fingerprint
                )
                !=
                64
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_envelope_fingerprint_invalid",
                    )
                )


            for field in (
                sensitive_clear_fields
                &
                set(
                    payload
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_sensitive_field_exposed:"
                        f"{field}",
                    )
                )


            for field in (
                prohibited_secret_fields
                &
                set(
                    payload
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_project_secret_field_prohibited:"
                        f"{field}",
                    )
                )


            envelope = payload.get(
                "portable_key_envelope"
            )


            if not isinstance(
                envelope,
                dict,
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "portable_key_envelope_missing",
                    )
                )

                continue


            if (
                envelope.get(
                    "schema"
                )
                !=
                PORTABLE_KEY_ENVELOPE_SCHEMA
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "portable_key_envelope_schema_invalid",
                    )
                )


            if (
                envelope.get(
                    "project_id"
                )
                !=
                project_id
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "portable_key_envelope_project_mismatch",
                    )
                )


            if (
                envelope.get(
                    "owner_principal_id"
                )
                !=
                owner_principal_id
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "portable_key_envelope_owner_mismatch",
                    )
                )


            if not str(
                envelope.get(
                    "wrapped_project_key",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "portable_wrapped_project_key_missing",
                    )
                )


            if not str(
                envelope.get(
                    "kdf_salt",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "portable_key_envelope_kdf_salt_missing",
                    )
                )


            for field in (
                prohibited_secret_fields
                &
                set(
                    envelope
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "portable_key_envelope_secret_field_prohibited:"
                        f"{field}",
                    )
                )


        return issues



    def _encrypted_design_manifest_paths(
        self,
    ):

        from leaf_qt.storage.design_manifest import (
            DESIGN_MANIFEST_FILENAME,
        )


        root = (
            self.storage
            .canonical_path(
                "designs"
            )
        )


        if not root.exists():

            return []


        result = []


        for path in sorted(
            root.rglob(
                DESIGN_MANIFEST_FILENAME
            )
        ):

            try:

                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                continue


            if (
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
                and
                payload.get(
                    "resource_type"
                )
                ==
                DESIGN_MANIFEST_RESOURCE
            ):

                result.append(
                    path
                )


        return result


    def _encrypted_engineering_state_paths(
        self,
    ):

        from leaf_qt.storage.save_load_bridge import (
            ENGINEERING_STATE_FILENAME,
        )


        root = (
            self.storage
            .canonical_path(
                "designs"
            )
        )


        if not root.exists():

            return []


        result = []


        for path in sorted(
            root.rglob(
                ENGINEERING_STATE_FILENAME
            )
        ):

            try:

                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                continue


            if (
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
                and
                payload.get(
                    "resource_type"
                )
                ==
                ENGINEERING_STATE_RESOURCE
            ):

                result.append(
                    path
                )


        return result


    def _validate_encrypted_design_and_state_resources(
        self,
    ):

        from leaf_qt.storage.project_manifest import (
            PROJECT_MANIFEST_FILENAME,
        )


        issues = []


        prohibited_fields = {
            "key_reference",
            "local_key_reference",
            "project_key",
            "raw_project_key",
            "recovery_key",
            "recovery_root_key",
        }


        exposed_design_fields = {
            "design_name",
            "engine_type",
            "solver_profile",
            "materials_profile",
            "geometry_profile",
            "validation_refs",
            "report_refs",
            "export_refs",
            "engineering_state_ref",
        }


        design_records = {}
        seen_design_ids = set()


        for path in (
            self._encrypted_design_manifest_paths()
        ):

            payload = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )


            project_id = str(
                payload.get(
                    "project_id",
                    "",
                )
            ).strip()


            design_id = str(
                payload.get(
                    "resource_id",
                    "",
                )
            ).strip()


            principal_id = str(
                payload.get(
                    "owner_principal_id",
                    "",
                )
            ).strip()


            classification = str(
                payload.get(
                    "security_classification",
                    "",
                )
            ).strip()


            if not project_id.startswith(
                "project_"
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_project_id_invalid",
                    )
                )


            if not design_id.startswith(
                "design_"
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_id_invalid",
                    )
                )


            if design_id in seen_design_ids:

                issues.append(
                    self._encrypted_issue(
                        path,
                        "duplicate_design_id:"
                        f"{design_id}",
                    )
                )

            else:

                seen_design_ids.add(
                    design_id
                )


            if (
                design_id
                and
                path.parent.name
                !=
                design_id
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_directory_not_opaque_design_id",
                    )
                )


            if not principal_id.startswith(
                "principal_"
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_owner_invalid",
                    )
                )


            if (
                classification
                not in
                VALID_SECURITY_CLASSIFICATIONS
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_classification_invalid",
                    )
                )


            if (
                payload.get(
                    "encryption_algorithm"
                )
                !=
                ENCRYPTION_ALGORITHM
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_algorithm_invalid",
                    )
                )


            if (
                payload.get(
                    "portable_key_envelope"
                )
                is not None
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_duplicate_recovery_envelope_prohibited",
                    )
                )


            if str(
                payload.get(
                    "portable_key_envelope_fingerprint",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_recovery_fingerprint_must_be_empty",
                    )
                )


            for field in (
                exposed_design_fields
                &
                set(
                    payload
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_sensitive_field_exposed:"
                        f"{field}",
                    )
                )


            for field in (
                prohibited_fields
                &
                set(
                    payload
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_secret_field_prohibited:"
                        f"{field}",
                    )
                )


            project_root = (
                self.storage
                .canonical_path(
                    "projects"
                )
                /
                project_id
                /
                PROJECT_MANIFEST_FILENAME
            )


            if not project_root.is_file():

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_design_parent_project_missing",
                    )
                )


            design_records[
                design_id
            ] = {
                "project_id":
                    project_id,

                "owner_principal_id":
                    principal_id,

                "security_classification":
                    classification,
            }


        for path in (
            self._encrypted_engineering_state_paths()
        ):

            payload = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )


            project_id = str(
                payload.get(
                    "project_id",
                    "",
                )
            ).strip()


            design_id = str(
                payload.get(
                    "resource_id",
                    "",
                )
            ).strip()


            principal_id = str(
                payload.get(
                    "owner_principal_id",
                    "",
                )
            ).strip()


            classification = str(
                payload.get(
                    "security_classification",
                    "",
                )
            ).strip()


            if (
                design_id
                and
                path.parent.name
                !=
                design_id
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_engineering_state_directory_mismatch",
                    )
                )


            if (
                payload.get(
                    "encryption_algorithm"
                )
                !=
                ENCRYPTION_ALGORITHM
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_engineering_state_algorithm_invalid",
                    )
                )


            if (
                payload.get(
                    "portable_key_envelope"
                )
                is not None
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_engineering_state_duplicate_recovery_envelope_prohibited",
                    )
                )


            if str(
                payload.get(
                    "portable_key_envelope_fingerprint",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_engineering_state_recovery_fingerprint_must_be_empty",
                    )
                )


            for field in (
                prohibited_fields
                &
                set(
                    payload
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_engineering_state_secret_field_prohibited:"
                        f"{field}",
                    )
                )


            design_record = (
                design_records.get(
                    design_id
                )
            )


            if design_record is None:

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_engineering_state_design_missing",
                    )
                )

                continue


            if (
                design_record[
                    "project_id"
                ]
                !=
                project_id
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_engineering_state_project_mismatch",
                    )
                )


            if (
                design_record[
                    "owner_principal_id"
                ]
                !=
                principal_id
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_engineering_state_owner_mismatch",
                    )
                )


            if (
                design_record[
                    "security_classification"
                ]
                !=
                classification
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "encrypted_engineering_state_classification_mismatch",
                    )
                )


        return issues



    def _protected_internal_reference_records(
        self,
    ):

        records = []


        project_security = {}


        for path in self._project_manifest_paths():

            try:

                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )


                if (
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
                ):

                    continue


                manifest = (
                    ProjectManifest.from_dict(
                        payload
                    )
                )


            except Exception:

                continue


            project_security[
                manifest.project_id
            ] = {
                "owner_principal_id":
                    manifest.owner_principal_id,

                "security_classification":
                    manifest.security_classification,
            }


            for ref in manifest.linked_reports:

                if not str(
                    ref
                    or ""
                ).strip():

                    continue


                records.append(
                    {
                        "source_path":
                            path,

                        "reference":
                            str(
                                ref
                            ),

                        "reference_kind":
                            "project_linked_report",

                        "expected_resource_type":
                            INTERNAL_REPORT_RESOURCE,

                        "project_id":
                            manifest.project_id,

                        "resource_id":
                            manifest.project_id,

                        "owner_principal_id":
                            manifest.owner_principal_id,

                        "security_classification":
                            manifest.security_classification,
                    }
                )


        for path in self._design_manifest_paths():

            try:

                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )


                if (
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
                ):

                    continue


                manifest = (
                    DesignManifest.from_dict(
                        payload
                    )
                )


            except Exception:

                continue


            security = project_security.get(
                manifest.parent_project_id
            )


            if security is None:

                continue


            for ref in manifest.report_refs:

                if not str(
                    ref
                    or ""
                ).strip():

                    continue


                records.append(
                    {
                        "source_path":
                            path,

                        "reference":
                            str(
                                ref
                            ),

                        "reference_kind":
                            "design_report",

                        "expected_resource_type":
                            INTERNAL_REPORT_RESOURCE,

                        "project_id":
                            manifest.parent_project_id,

                        "resource_id":
                            manifest.design_id,

                        "owner_principal_id":
                            security[
                                "owner_principal_id"
                            ],

                        "security_classification":
                            security[
                                "security_classification"
                            ],
                    }
                )


            for ref in manifest.validation_refs:

                if not str(
                    ref
                    or ""
                ).strip():

                    continue


                records.append(
                    {
                        "source_path":
                            path,

                        "reference":
                            str(
                                ref
                            ),

                        "reference_kind":
                            "design_validation_evidence",

                        "expected_resource_type":
                            VALIDATION_EVIDENCE_RESOURCE,

                        "project_id":
                            manifest.parent_project_id,

                        "resource_id":
                            manifest.design_id,

                        "owner_principal_id":
                            security[
                                "owner_principal_id"
                            ],

                        "security_classification":
                            security[
                                "security_classification"
                            ],
                    }
                )


        return records


    def _validate_protected_internal_references(
        self,
    ):

        issues = []


        for record in (
            self
            ._protected_internal_reference_records()
        ):

            reference = record[
                "reference"
            ]


            try:

                target = (
                    self.storage
                    .resolve_ref(
                        reference
                    )
                )

            except Exception:

                # Existing link validation owns unresolved
                # or malformed references.
                continue


            if not target.is_file():

                # Missing-link ownership already exists in
                # the canonical plaintext validator.
                continue


            try:

                payload = json.loads(
                    target.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                payload = None


            if not (
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
            ):

                issues.append(
                    self._encrypted_issue(
                        target,
                        "protected_internal_reference_not_encrypted:"
                        f"{record['reference_kind']}",
                    )
                )

                continue


            expected_type = record[
                "expected_resource_type"
            ]


            if (
                payload.get(
                    "resource_type"
                )
                !=
                expected_type
            ):

                issues.append(
                    self._encrypted_issue(
                        target,
                        "protected_internal_reference_type_mismatch:"
                        f"{expected_type}",
                    )
                )


            if (
                payload.get(
                    "project_id"
                )
                !=
                record[
                    "project_id"
                ]
            ):

                issues.append(
                    self._encrypted_issue(
                        target,
                        "protected_internal_reference_project_mismatch",
                    )
                )


            if (
                payload.get(
                    "resource_id"
                )
                !=
                record[
                    "resource_id"
                ]
            ):

                issues.append(
                    self._encrypted_issue(
                        target,
                        "protected_internal_reference_resource_mismatch",
                    )
                )


            if (
                payload.get(
                    "owner_principal_id"
                )
                !=
                record[
                    "owner_principal_id"
                ]
            ):

                issues.append(
                    self._encrypted_issue(
                        target,
                        "protected_internal_reference_owner_mismatch",
                    )
                )


            if (
                payload.get(
                    "security_classification"
                )
                !=
                record[
                    "security_classification"
                ]
            ):

                issues.append(
                    self._encrypted_issue(
                        target,
                        "protected_internal_reference_classification_mismatch",
                    )
                )


            if (
                payload.get(
                    "portable_key_envelope"
                )
                is not None
            ):

                issues.append(
                    self._encrypted_issue(
                        target,
                        "protected_internal_child_recovery_envelope_prohibited",
                    )
                )


            if str(
                payload.get(
                    "portable_key_envelope_fingerprint",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        target,
                        "protected_internal_child_recovery_fingerprint_prohibited",
                    )
                )


        return issues


    def _encrypted_internal_resource_records(
        self,
    ):

        records = []


        for root_name in (
            "projects",
            "designs",
            "reports",
            "exports",
        ):

            root = (
                self.storage
                .canonical_path(
                    root_name
                )
            )


            if not root.is_dir():

                continue


            for path in sorted(
                root.rglob(
                    "*.json"
                )
            ):

                try:

                    payload = json.loads(
                        path.read_text(
                            encoding="utf-8"
                        )
                    )

                except Exception:

                    continue


                if not isinstance(
                    payload,
                    dict,
                ):

                    continue


                if (
                    payload.get(
                        "schema"
                    )
                    !=
                    ENCRYPTED_CONTAINER_SCHEMA
                ):

                    continue


                if (
                    payload.get(
                        "resource_type"
                    )
                    not in
                    INTERNAL_PROJECT_RESOURCE_TYPES
                ):

                    continue


                records.append(
                    {
                        "root_name":
                            root_name,

                        "path":
                            path,

                        "payload":
                            payload,
                    }
                )


        return records


    def _validate_internal_resource_containers(
        self,
    ):

        issues = []


        prohibited_secret_fields = {
            "key_reference",
            "local_key_reference",
            "project_key",
            "raw_project_key",
            "recovery_key",
            "recovery_root_key",
        }


        for record in (
            self
            ._encrypted_internal_resource_records()
        ):

            root_name = record[
                "root_name"
            ]

            path = record[
                "path"
            ]

            payload = record[
                "payload"
            ]


            if root_name == "exports":

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_resource_must_not_use_export_root",
                    )
                )


            project_id = str(
                payload.get(
                    "project_id",
                    "",
                )
            ).strip()


            owner_principal_id = str(
                payload.get(
                    "owner_principal_id",
                    "",
                )
            ).strip()


            classification = str(
                payload.get(
                    "security_classification",
                    "",
                )
            ).strip()


            resource_id = str(
                payload.get(
                    "resource_id",
                    "",
                )
            ).strip()


            if not project_id.startswith(
                "project_"
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_project_id_invalid",
                    )
                )


            if not owner_principal_id.startswith(
                "principal_"
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_owner_invalid",
                    )
                )


            if (
                classification
                not in
                VALID_SECURITY_CLASSIFICATIONS
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_classification_invalid",
                    )
                )


            if not resource_id:

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_resource_id_missing",
                    )
                )


            if (
                payload.get(
                    "encryption_algorithm"
                )
                !=
                ENCRYPTION_ALGORITHM
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_algorithm_invalid",
                    )
                )


            if not str(
                payload.get(
                    "nonce",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_nonce_missing",
                    )
                )


            if not str(
                payload.get(
                    "ciphertext",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_ciphertext_missing",
                    )
                )


            if (
                payload.get(
                    "portable_key_envelope"
                )
                is not None
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_recovery_envelope_prohibited",
                    )
                )


            if str(
                payload.get(
                    "portable_key_envelope_fingerprint",
                    "",
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_recovery_fingerprint_prohibited",
                    )
                )


            for field in (
                prohibited_secret_fields
                &
                set(
                    payload
                )
            ):

                issues.append(
                    self._encrypted_issue(
                        path,
                        "protected_internal_secret_field_prohibited:"
                        f"{field}",
                    )
                )


        return issues


    def _validate_plaintext(self, repair: bool = False) -> dict[str, Any]:
        issues: list[StorageIssue] = []

        issues.extend(self._validate_roots(repair=repair))
        issues.extend(self._validate_project_manifests())
        issues.extend(self._validate_design_manifests())
        issues.extend(self._validate_duplicate_ids())
        issues.extend(self._validate_manifest_links())

        return {
            "schema": SCHEMA,
            "passed": not any(issue.severity in {"error", "critical"} for issue in issues),
            "repair_requested": repair,
            "issues": [issue.snapshot() for issue in issues],
            "issue_count": len(issues),
            "error_count": sum(1 for issue in issues if issue.severity in {"error", "critical"}),
            "repaired_count": sum(1 for issue in issues if issue.repaired),
            "auto_delete_enabled": False,
            "auto_archive_enabled": False,
            "auto_move_enabled": False,
            "auto_overwrite_enabled": False,
        }

    def _validate_roots(self, repair: bool) -> list[StorageIssue]:
        issues: list[StorageIssue] = []

        for key, folder in CANONICAL_ROOTS.items():
            path = self.root / folder

            if path.exists() and path.is_dir():
                continue

            repaired = False

            if repair:
                path.mkdir(parents=True, exist_ok=True)
                repaired = path.exists() and path.is_dir()

            issues.append(
                StorageIssue(
                    issue_id=f"missing_root:{key}",
                    severity="warning" if repaired else "error",
                    issue_type="missing_canonical_root",
                    path=str(path),
                    message=f"Canonical storage root missing: {folder}",
                    repairable=True,
                    repaired=repaired,
                )
            )

        return issues

    def _project_manifest_paths(
        self,
    ):

        projects_root = (
            self.storage
            .canonical_path(
                "projects"
            )
        )


        if not projects_root.exists():

            return []


        paths = []


        for path in sorted(
            projects_root.rglob(
                PROJECT_MANIFEST_FILENAME
            )
        ):

            try:

                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                paths.append(
                    path
                )

                continue


            if self._is_encrypted_project_payload(
                payload
            ):

                continue


            paths.append(
                path
            )


        return paths

    def _design_manifest_paths(self) -> list[Path]:
        root = self.storage.canonical_path("designs")
        if not root.exists():
            return []
        return sorted(root.rglob(DESIGN_MANIFEST_FILENAME))

    def _validate_project_manifests(self) -> list[StorageIssue]:
        issues: list[StorageIssue] = []

        for path in self._project_manifest_paths():
            try:
                manifest = ProjectManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
                validation = self.project_validator.validate(manifest)
            except Exception as exc:
                issues.append(
                    StorageIssue(
                        issue_id=f"project_manifest_unreadable:{path}",
                        severity="error",
                        issue_type="project_manifest_unreadable",
                        path=str(path),
                        message=repr(exc),
                    )
                )
                continue

            for failure in validation.get("failures", []):
                issues.append(
                    StorageIssue(
                        issue_id=f"project_manifest_invalid:{path}:{failure}",
                        severity="error",
                        issue_type="project_manifest_invalid",
                        path=str(path),
                        message=str(failure),
                    )
                )

        return issues

    def _validate_design_manifests(self) -> list[StorageIssue]:
        issues: list[StorageIssue] = []

        for path in self._design_manifest_paths():
            try:
                manifest = DesignManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
                validation = self.design_validator.validate(manifest)
            except Exception as exc:
                issues.append(
                    StorageIssue(
                        issue_id=f"design_manifest_unreadable:{path}",
                        severity="error",
                        issue_type="design_manifest_unreadable",
                        path=str(path),
                        message=repr(exc),
                    )
                )
                continue

            for failure in validation.get("failures", []):
                issues.append(
                    StorageIssue(
                        issue_id=f"design_manifest_invalid:{path}:{failure}",
                        severity="error",
                        issue_type="design_manifest_invalid",
                        path=str(path),
                        message=str(failure),
                    )
                )

        return issues

    def _validate_duplicate_ids(self) -> list[StorageIssue]:
        issues: list[StorageIssue] = []
        project_ids: dict[str, list[str]] = {}
        design_ids: dict[str, list[str]] = {}

        for path in self._project_manifest_paths():
            try:
                manifest = ProjectManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
                project_ids.setdefault(manifest.project_id, []).append(str(path))
            except Exception:
                continue

        for path in self._design_manifest_paths():
            try:
                manifest = DesignManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
                design_ids.setdefault(manifest.design_id, []).append(str(path))
            except Exception:
                continue

        for project_id, paths in project_ids.items():
            if len(paths) > 1:
                issues.append(
                    StorageIssue(
                        issue_id=f"duplicate_project_id:{project_id}",
                        severity="error",
                        issue_type="duplicate_project_id",
                        path=" | ".join(paths),
                        message=f"Duplicate project_id found: {project_id}",
                    )
                )

        for design_id, paths in design_ids.items():
            if len(paths) > 1:
                issues.append(
                    StorageIssue(
                        issue_id=f"duplicate_design_id:{design_id}",
                        severity="error",
                        issue_type="duplicate_design_id",
                        path=" | ".join(paths),
                        message=f"Duplicate design_id found: {design_id}",
                    )
                )

        return issues

    def _validate_manifest_links(self) -> list[StorageIssue]:
        issues: list[StorageIssue] = []

        for path in self._project_manifest_paths():
            try:
                project = ProjectManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue

            for design_ref in project.active_designs:
                if not self.storage.resolve_ref(design_ref).exists():
                    issues.append(
                        StorageIssue(
                            issue_id=f"broken_project_design_link:{path}:{design_ref}",
                            severity="error",
                            issue_type="broken_project_design_link",
                            path=str(path),
                            message=f"Linked design missing: {design_ref}",
                        )
                    )

            for report_ref in project.linked_reports:
                if not Path(report_ref).exists():
                    issues.append(
                        StorageIssue(
                            issue_id=f"broken_project_report_link:{path}:{report_ref}",
                            severity="warning",
                            issue_type="broken_project_report_link",
                            path=str(path),
                            message=f"Linked report missing: {report_ref}",
                        )
                    )

            for export_ref in project.linked_exports:
                if not Path(export_ref).exists():
                    issues.append(
                        StorageIssue(
                            issue_id=f"broken_project_export_link:{path}:{export_ref}",
                            severity="warning",
                            issue_type="broken_project_export_link",
                            path=str(path),
                            message=f"Linked export missing: {export_ref}",
                        )
                    )

        for path in self._design_manifest_paths():
            try:
                design = DesignManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue

            for report_ref in design.report_refs:
                if not Path(report_ref).exists():
                    issues.append(
                        StorageIssue(
                            issue_id=f"broken_design_report_link:{path}:{report_ref}",
                            severity="warning",
                            issue_type="broken_design_report_link",
                            path=str(path),
                            message=f"Linked report missing: {report_ref}",
                        )
                    )

            for export_ref in design.export_refs:
                if not Path(export_ref).exists():
                    issues.append(
                        StorageIssue(
                            issue_id=f"broken_design_export_link:{path}:{export_ref}",
                            severity="warning",
                            issue_type="broken_design_export_link",
                            path=str(path),
                            message=f"Linked export missing: {export_ref}",
                        )
                    )

        return issues

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "root": str(self.root),
            "validates_canonical_roots": True,
            "validates_project_manifests": True,
            "validates_design_manifests": True,
            "validates_duplicate_ids": True,
            "validates_manifest_links": True,
            "repairs_missing_roots_only": True,
            "auto_delete_enabled": False,
            "auto_archive_enabled": False,
            "auto_move_enabled": False,
            "auto_overwrite_enabled": False,
            "qt_owns_storage_validation": False,
        }

    def _legacy_encryption_migration_journal_path(
        self,
    ) -> Path:

        return (
            Path(
                self.storage.root
            )
            /
            ".leaf_s1j10_migration_transaction.json"
        )


    @staticmethod
    def _migration_path_under_root(
        root: Path,
        relative_path: str,
    ) -> Path:

        root = root.resolve()


        candidate = (
            root
            /
            str(
                relative_path
            )
        ).resolve()


        if (
            candidate
            !=
            root
            and
            root
            not in
            candidate.parents
        ):

            raise ValueError(
                "migration_journal_path_escapes_storage_root"
            )


        return candidate


    def _write_legacy_encryption_migration_journal(
        self,
        payload: dict,
    ) -> None:

        from leaf_qt.storage.save_load_bridge import (
            SaveLoadRuntimeBridge,
        )


        SaveLoadRuntimeBridge._write_json(
            self._legacy_encryption_migration_journal_path(),
            payload,
        )


    def recover_interrupted_encryption_migration(
        self,
        *,
        key_custody=None,
    ) -> dict:

        import json
        import shutil

        from leaf_qt.key_custody import (
            KeyCustodyOwner,
        )

        from leaf_qt.storage.project_manifest import (
            PROJECT_MANIFEST_FILENAME,
        )

        from leaf_qt.storage.design_manifest import (
            DESIGN_MANIFEST_FILENAME,
        )


        journal_path = (
            self
            ._legacy_encryption_migration_journal_path()
        )


        if not journal_path.is_file():

            return {
                "action":
                    "recover_interrupted_encryption_migration",

                "recovery_performed":
                    False,

                "mode":
                    "NO_TRANSACTION",
            }


        journal = json.loads(
            journal_path.read_text(
                encoding="utf-8"
            )
        )


        if not isinstance(
            journal,
            dict,
        ):

            raise ValueError(
                "migration_journal_payload_invalid"
            )


        if (
            journal.get(
                "schema"
            )
            !=
            "LEAF_S1J10_MIGRATION_TRANSACTION_V1"
        ):

            raise ValueError(
                "migration_journal_schema_invalid"
            )


        root = Path(
            self.storage.root
        ).resolve()


        project_id = str(
            journal.get(
                "project_id",
                "",
            )
        ).strip()


        principal_id = str(
            journal.get(
                "principal_id",
                "",
            )
        ).strip()


        phase = str(journal.get("phase", "")).strip()

        valid_phases = frozenset({
            "PREPARED", "STAGED", "SOURCE_HIDDEN",
            "TARGET_DIRECTORIES", "TARGET_VISIBLE", "COMMIT_READY",
        })
        if phase not in valid_phases:
            raise ValueError("migration_journal_phase_invalid")


        if not project_id.startswith(
            "project_"
        ):

            raise ValueError(
                "migration_journal_project_id_invalid"
            )


        if not principal_id.startswith(
            "principal_"
        ):

            raise ValueError(
                "migration_journal_principal_id_invalid"
            )


        required_paths = (
            "source_project_dir",
            "source_project_manifest",
            "source_project_backup",
            "target_project_dir",
            "target_project_manifest",
            "staging_project_dir",
        )


        for field in required_paths:

            if not str(
                journal.get(
                    field,
                    "",
                )
            ).strip():

                raise ValueError(
                    "migration_journal_required_path_missing:"
                    f"{field}"
                )


        source_project_dir = (
            self._migration_path_under_root(
                root,
                journal[
                    "source_project_dir"
                ],
            )
        )


        source_project_manifest = (
            self._migration_path_under_root(
                root,
                journal[
                    "source_project_manifest"
                ],
            )
        )


        source_project_backup = (
            self._migration_path_under_root(
                root,
                journal[
                    "source_project_backup"
                ],
            )
        )


        target_project_dir = (
            self._migration_path_under_root(
                root,
                journal[
                    "target_project_dir"
                ],
            )
        )


        target_project_manifest = (
            self._migration_path_under_root(
                root,
                journal[
                    "target_project_manifest"
                ],
            )
        )


        staging_project_dir = (
            self._migration_path_under_root(
                root,
                journal[
                    "staging_project_dir"
                ],
            )
        )


        from leaf_qt.storage.canonical_storage import paths_match

        projects_root = self.storage.canonical_path("projects").resolve()
        designs_root = self.storage.canonical_path("designs").resolve()

        def require_path(actual: Path, expected: Path, label: str) -> None:
            if not paths_match(actual, expected):
                raise ValueError(label)

        if source_project_dir.parent != projects_root:
            raise ValueError("migration_journal_source_project_directory_invalid")

        require_path(
            source_project_manifest,
            source_project_dir / PROJECT_MANIFEST_FILENAME,
            "migration_journal_source_project_manifest_invalid",
        )
        require_path(
            source_project_backup,
            source_project_dir / (PROJECT_MANIFEST_FILENAME + ".s1j10-plaintext-backup"),
            "migration_journal_source_project_backup_invalid",
        )
        require_path(
            target_project_dir,
            projects_root / project_id,
            "migration_journal_target_project_directory_invalid",
        )
        require_path(
            target_project_manifest,
            target_project_dir / PROJECT_MANIFEST_FILENAME,
            "migration_journal_target_project_manifest_invalid",
        )
        if paths_match(source_project_dir, target_project_dir):
            raise ValueError("migration_journal_project_source_target_collision")

        staging_prefix = f".s1j10-migrating-{project_id}-"
        if staging_project_dir.parent != projects_root or not staging_project_dir.name.startswith(staging_prefix):
            raise ValueError("migration_journal_staging_project_directory_invalid")
        staging_token = staging_project_dir.name[len(staging_prefix):]
        if len(staging_token) != 16 or any(c not in "0123456789abcdef" for c in staging_token):
            raise ValueError("migration_journal_staging_token_invalid")


        design_records = journal.get(
            "designs",
            [],
        )


        if not isinstance(
            design_records,
            list,
        ):

            raise ValueError(
                "migration_journal_design_records_invalid"
            )


        resolved_designs = []
        seen_design_ids = set()
        seen_source_design_dirs = set()

        required_design_fields = (
            "design_id", "source_dir", "source_manifest", "source_backup",
            "target_dir", "target_manifest", "staging_dir",
        )

        for record in design_records:
            if not isinstance(record, dict):
                raise ValueError("migration_journal_design_record_invalid")
            for field in required_design_fields:
                if not str(record.get(field, "")).strip():
                    raise ValueError(f"migration_journal_design_field_missing:{field}")

            design_id = str(record["design_id"]).strip()
            if not design_id.startswith("design_"):
                raise ValueError("migration_journal_design_id_invalid")
            if design_id in seen_design_ids:
                raise ValueError("migration_journal_duplicate_design_id")
            seen_design_ids.add(design_id)

            resolved = {
                "design_id": design_id,
                **{
                    field: self._migration_path_under_root(root, record[field])
                    for field in required_design_fields
                    if field != "design_id"
                },
            }

            if resolved["source_dir"].parent != designs_root:
                raise ValueError(f"migration_journal_source_design_directory_invalid:{design_id}")
            require_path(
                resolved["source_manifest"],
                resolved["source_dir"] / DESIGN_MANIFEST_FILENAME,
                f"migration_journal_source_design_manifest_invalid:{design_id}",
            )
            require_path(
                resolved["source_backup"],
                resolved["source_dir"] / (DESIGN_MANIFEST_FILENAME + ".s1j10-plaintext-backup"),
                f"migration_journal_source_design_backup_invalid:{design_id}",
            )
            require_path(
                resolved["target_dir"],
                designs_root / design_id,
                f"migration_journal_target_design_directory_invalid:{design_id}",
            )
            require_path(
                resolved["target_manifest"],
                resolved["target_dir"] / DESIGN_MANIFEST_FILENAME,
                f"migration_journal_target_design_manifest_invalid:{design_id}",
            )
            require_path(
                resolved["staging_dir"],
                designs_root / f".s1j10-migrating-{design_id}-{staging_token}",
                f"migration_journal_staging_design_directory_invalid:{design_id}",
            )
            if paths_match(resolved["source_dir"], resolved["target_dir"]):
                raise ValueError(f"migration_journal_design_source_target_collision:{design_id}")

            source_dir_key = str(resolved["source_dir"])
            if source_dir_key in seen_source_design_dirs:
                raise ValueError("migration_journal_duplicate_source_design_directory")
            seen_source_design_dirs.add(source_dir_key)
            resolved_designs.append(resolved)


        if phase == "COMMIT_READY":

            from leaf_qt.encrypted_container import EncryptedContainerOwner
            from leaf_qt.storage.save_load_bridge import ENGINEERING_STATE_FILENAME

            custody = key_custody or KeyCustodyOwner()
            project_key = custody.retrieve_project_key(principal_id, project_id)
            if len(project_key) != 32:
                raise RuntimeError("migration_forward_recovery_project_key_invalid")

            if not target_project_manifest.is_file():

                raise RuntimeError(
                    "migration_forward_recovery_target_project_missing"
                )


            if (
                target_project_manifest.name
                !=
                PROJECT_MANIFEST_FILENAME
            ):

                raise RuntimeError(
                    "migration_forward_recovery_project_filename_invalid"
                )


            for record in resolved_designs:

                target_manifest = record[
                    "target_manifest"
                ]


                if not target_manifest.is_file():

                    raise RuntimeError(
                        "migration_forward_recovery_target_design_missing:"
                        f"{target_manifest}"
                    )


                if (
                    target_manifest.name
                    !=
                    DESIGN_MANIFEST_FILENAME
                ):

                    raise RuntimeError(
                        "migration_forward_recovery_design_filename_invalid"
                    )


            encrypted_container_owner = EncryptedContainerOwner()

            def load_json(path: Path, label: str) -> dict:
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except Exception as exc:
                    raise RuntimeError(label) from exc
                if not isinstance(payload, dict):
                    raise RuntimeError(label)
                return payload

            project_container = load_json(
                target_project_manifest,
                "migration_forward_recovery_project_container_invalid",
            )
            classification = str(project_container.get("security_classification", "")).strip()
            if classification not in VALID_SECURITY_CLASSIFICATIONS:
                raise ValueError("migration_forward_recovery_classification_invalid")

            project_payload = encrypted_container_owner.open(
                container=project_container,
                project_key=project_key,
                expected_project_id=project_id,
                expected_owner_principal_id=principal_id,
                expected_security_classification=classification,
                expected_resource_type=PROJECT_ROOT_RESOURCE,
                expected_resource_id=project_id,
            )
            try:
                authenticated_project = ProjectManifest.from_dict(project_payload)
            except Exception as exc:
                raise RuntimeError("migration_forward_recovery_project_payload_invalid") from exc
            if self.project_validator.validate(authenticated_project).get("passed") is not True:
                raise RuntimeError("migration_forward_recovery_project_payload_validation_failed")
            if (
                authenticated_project.project_id != project_id
                or authenticated_project.owner_principal_id != principal_id
                or authenticated_project.security_classification != classification
            ):
                raise PermissionError("migration_forward_recovery_project_payload_binding_invalid")

            expected_design_refs = [
                self.storage.portable_ref(record["target_manifest"])
                for record in resolved_designs
            ]
            if list(authenticated_project.active_designs) != expected_design_refs:
                raise PermissionError("migration_forward_recovery_design_set_mismatch")

            for record in resolved_designs:
                design_id = record["design_id"]
                design_container = load_json(
                    record["target_manifest"],
                    f"migration_forward_recovery_design_container_invalid:{design_id}",
                )
                design_payload = encrypted_container_owner.open(
                    container=design_container,
                    project_key=project_key,
                    expected_project_id=project_id,
                    expected_owner_principal_id=principal_id,
                    expected_security_classification=classification,
                    expected_resource_type=DESIGN_MANIFEST_RESOURCE,
                    expected_resource_id=design_id,
                )
                try:
                    authenticated_design = DesignManifest.from_dict(design_payload)
                except Exception as exc:
                    raise RuntimeError(
                        f"migration_forward_recovery_design_payload_invalid:{design_id}"
                    ) from exc
                if self.design_validator.validate(authenticated_design).get("passed") is not True:
                    raise RuntimeError(
                        f"migration_forward_recovery_design_payload_validation_failed:{design_id}"
                    )
                if (
                    authenticated_design.design_id != design_id
                    or authenticated_design.parent_project_id != project_id
                ):
                    raise PermissionError(
                        f"migration_forward_recovery_design_payload_binding_invalid:{design_id}"
                    )

                if str(authenticated_design.engineering_state_ref or "").strip():
                    state_path = record["target_dir"] / ENGINEERING_STATE_FILENAME
                    if not state_path.is_file():
                        raise RuntimeError(f"migration_forward_recovery_target_state_missing:{design_id}")
                    encrypted_container_owner.open(
                        container=load_json(
                            state_path,
                            f"migration_forward_recovery_state_container_invalid:{design_id}",
                        ),
                        project_key=project_key,
                        expected_project_id=project_id,
                        expected_owner_principal_id=principal_id,
                        expected_security_classification=classification,
                        expected_resource_type=ENGINEERING_STATE_RESOURCE,
                        expected_resource_id=design_id,
                    )

                if record["source_dir"].exists():
                    source_backup = record["source_backup"]
                    if not source_backup.is_file():
                        raise RuntimeError(
                            f"migration_forward_recovery_source_design_backup_missing:{design_id}"
                        )
                    try:
                        source_design = DesignManifest.from_dict(load_json(
                            source_backup,
                            f"migration_forward_recovery_source_design_backup_invalid:{design_id}",
                        ))
                    except Exception as exc:
                        raise RuntimeError(
                            f"migration_forward_recovery_source_design_backup_invalid:{design_id}"
                        ) from exc
                    if source_design.design_id != design_id or source_design.parent_project_id != project_id:
                        raise PermissionError(
                            f"migration_forward_recovery_source_design_binding_invalid:{design_id}"
                        )

            if source_project_dir.exists():
                if not source_project_backup.is_file():
                    raise RuntimeError("migration_forward_recovery_source_project_backup_missing")
                try:
                    source_project = ProjectManifest.from_dict(load_json(
                        source_project_backup,
                        "migration_forward_recovery_source_project_backup_invalid",
                    ))
                except Exception as exc:
                    raise RuntimeError("migration_forward_recovery_source_project_backup_invalid") from exc
                if (
                    source_project.project_id != project_id
                    or source_project.owner_principal_id != principal_id
                    or source_project.security_classification != classification
                ):
                    raise PermissionError("migration_forward_recovery_source_project_binding_invalid")


            for record in resolved_designs:

                source_dir = record[
                    "source_dir"
                ]


                if (
                    source_dir.exists()
                    and
                    source_dir
                    !=
                    record[
                        "target_dir"
                    ]
                ):

                    shutil.rmtree(
                        source_dir
                    )


                staging_dir = record[
                    "staging_dir"
                ]


                if staging_dir.exists():

                    shutil.rmtree(
                        staging_dir
                    )


            if (
                source_project_dir.exists()
                and
                source_project_dir
                !=
                target_project_dir
            ):

                shutil.rmtree(
                    source_project_dir
                )


            if staging_project_dir.exists():

                shutil.rmtree(
                    staging_project_dir
                )


            self._record_encryption_migration_event(
                action=
                    "recover_complete_forward",

                outcome=
                    "success",

                principal_id=
                    principal_id,

                project_id=
                    project_id,

                classification=
                    None,
            )


            journal_path.unlink()


            return {
                "action":
                    "recover_interrupted_encryption_migration",

                "recovery_performed":
                    True,

                "mode":
                    "COMPLETE_FORWARD",

                "project_id":
                    project_id,
            }


        for record in resolved_designs:

            target_dir = record[
                "target_dir"
            ]


            if target_dir.exists():

                shutil.rmtree(
                    target_dir
                )


            staging_dir = record[
                "staging_dir"
            ]


            if staging_dir.exists():

                shutil.rmtree(
                    staging_dir
                )


            source_manifest = record[
                "source_manifest"
            ]


            source_backup = record[
                "source_backup"
            ]


            if source_backup.is_file():

                if source_manifest.exists():

                    raise RuntimeError(
                        "migration_rollback_design_manifest_conflict:"
                        f"{source_manifest}"
                    )


                source_backup.rename(
                    source_manifest
                )


        if target_project_dir.exists():

            shutil.rmtree(
                target_project_dir
            )


        if staging_project_dir.exists():

            shutil.rmtree(
                staging_project_dir
            )


        if source_project_backup.is_file():

            if source_project_manifest.exists():

                raise RuntimeError(
                    "migration_rollback_project_manifest_conflict:"
                    f"{source_project_manifest}"
                )


            source_project_backup.rename(
                source_project_manifest
            )


        custody = (
            key_custody
            or
            KeyCustodyOwner()
        )


        if custody.project_key_exists(
            principal_id,
            project_id,
        ):

            # The key belongs to an uncommitted migration.
            # Restore pre-transaction state through the existing
            # KeyCustodyOwner rollback primitive.

            custody._rollback_new_project_key_slot(
                principal_id,
                project_id,
            )


        self._record_encryption_migration_event(
            action=
                "recover_rollback_to_plaintext",

            outcome=
                "success",

            principal_id=
                principal_id,

            project_id=
                project_id,

            classification=
                None,
        )


        journal_path.unlink()


        return {
            "action":
                "recover_interrupted_encryption_migration",

            "recovery_performed":
                True,

            "mode":
                "ROLLBACK_TO_PLAINTEXT",

            "project_id":
                project_id,
        }


    @staticmethod
    def _legacy_recovery_confirmation_code(
        project_id: str,
        recovery_fingerprint: str,
    ) -> str:

        project_suffix = (
            str(
                project_id
            )
            .replace(
                "project_",
                "",
                1,
            )
            [-8:]
            .upper()
        )


        fingerprint_prefix = (
            str(
                recovery_fingerprint
            )
            [:12]
            .upper()
        )


        return (
            "ENCRYPT-"
            +
            project_suffix
            +
            "-"
            +
            fingerprint_prefix
        )


    def _validate_external_recovery_path(
        self,
        recovery_export_path,
    ) -> Path:

        storage_root = Path(
            self.storage.root
        ).resolve()


        path = Path(
            recovery_export_path
        ).expanduser().resolve()


        if (
            path
            ==
            storage_root
            or
            storage_root
            in
            path.parents
        ):

            raise PermissionError(
                "recovery_material_must_be_outside_leaf_storage_root"
            )


        if not path.name.endswith(
            ".leaf-recovery.json"
        ):

            raise ValueError(
                "recovery_material_filename_must_end_with_leaf_recovery_json"
            )


        return path


    @staticmethod
    def _recovery_package_checksum(
        payload: dict,
    ) -> str:

        import hashlib
        import json


        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )


        return hashlib.sha256(
            canonical
        ).hexdigest()


    @staticmethod
    def _write_recovery_material_exclusive(
        path: Path,
        payload: bytes,
    ) -> None:
        """
        Write recovery material exactly once.

        This is deliberately separate from normal project
        persistence because recovery material is a master
        secret outside the LEAF storage boundary.

        Existing files are never overwritten.
        """

        import os


        path = Path(
            path
        )


        if not isinstance(
            payload,
            (
                bytes,
                bytearray,
            ),
        ):

            raise TypeError(
                "recovery_material_payload_must_be_bytes"
            )


        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        flags = (
            os.O_WRONLY
            |
            os.O_CREAT
            |
            os.O_EXCL
        )


        descriptor = None


        try:

            descriptor = os.open(
                path,
                flags,
                0o600,
            )


            with os.fdopen(
                descriptor,
                "wb",
                closefd=True,
            ) as handle:

                descriptor = None

                handle.write(
                    bytes(
                        payload
                    )
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )


            if os.name != "nt":

                os.chmod(
                    path,
                    0o600,
                )


        except Exception:

            if descriptor is not None:

                try:
                    os.close(
                        descriptor
                    )

                except OSError:
                    pass


            if path.exists():

                try:
                    path.unlink()

                except OSError:
                    pass


            raise


    def recover_encrypted_project_access(
        self,
        project_manifest_path,
        recovery_export_path,
        *,
        security_context=None,
        key_custody=None,
        key_envelope_owner=None,
    ) -> dict:
        """
        Restore an encrypted project's exact existing DEK into
        approved device-local key custody.

        Project files remain encrypted and unchanged.

        Portable recovery accountability is owned here rather
        than inside PortableKeyEnvelopeOwner. Recovery secrets
        and project-key material never cross the audit boundary.
        """

        import hmac
        import json

        from leaf_qt.encrypted_container import (
            SCHEMA as ENCRYPTED_CONTAINER_SCHEMA,
        )

        from leaf_qt.key_custody import (
            KeyCustodyOwner,
        )

        from leaf_qt.key_envelope import (
            PortableKeyEnvelopeOwner,
        )

        from leaf_qt.security_context import (
            SecurityContextOwner,
        )


        security_context = (
            security_context
            or
            SecurityContextOwner(
                security_audit=
                    self.security_audit
            )
        )


        principal_id = str(
            security_context.principal_id
        ).strip()


        project_id = None


        def record_recovery(
            outcome: str,
        ) -> None:

            self.security_audit.record_event(
                event_type=
                    "portable_recovery.project_key",

                action=
                    "recover",

                outcome=
                    outcome,

                resource_type=
                    "project_key",

                principal_id=
                    principal_id,

                project_id=
                    project_id,
            )


        try:

            project_manifest_path = (
                self.storage.resolve_ref(
                    project_manifest_path
                )
                .resolve()
            )


            if not project_manifest_path.is_file():

                raise FileNotFoundError(
                    "encrypted_project_manifest_not_found:"
                    f"{project_manifest_path}"
                )


            container = json.loads(
                project_manifest_path.read_text(
                    encoding="utf-8"
                )
            )


            if not isinstance(
                container,
                dict,
            ):

                raise ValueError(
                    "encrypted_project_container_invalid"
                )


            if (
                container.get(
                    "schema"
                )
                !=
                ENCRYPTED_CONTAINER_SCHEMA
            ):

                raise ValueError(
                    "project_is_not_encrypted_container"
                )


            portable_envelope = (
                container.get(
                    "portable_key_envelope"
                )
            )


            if not isinstance(
                portable_envelope,
                dict,
            ):

                raise ValueError(
                    "encrypted_project_portable_envelope_missing"
                )


            envelope_project_id = str(
                portable_envelope.get(
                    "project_id",
                    "",
                )
            ).strip()


            if envelope_project_id.startswith(
                "project_"
            ):

                project_id = (
                    envelope_project_id
                )


            key_envelope_owner = (
                key_envelope_owner
                or
                PortableKeyEnvelopeOwner()
            )


            recovery_payload, recovery_key = (
                self._load_legacy_recovery_material(
                    recovery_export_path,

                    key_envelope_owner=
                        key_envelope_owner,
                )
            )


            recovery_project_id = str(
                recovery_payload.get(
                    "project_id",
                    "",
                )
            ).strip()


            recovery_principal_id = str(
                recovery_payload.get(
                    "owner_principal_id",
                    "",
                )
            ).strip()


            if not recovery_project_id:

                raise ValueError(
                    "recovery_material_project_id_missing"
                )


            project_id = (
                recovery_project_id
            )


            if (
                recovery_principal_id
                !=
                principal_id
            ):

                raise PermissionError(
                    "recovery_material_principal_binding_mismatch"
                )


            if (
                portable_envelope.get(
                    "project_id"
                )
                !=
                project_id
            ):

                raise PermissionError(
                    "recovery_material_project_binding_mismatch"
                )




            project_key = (
                key_envelope_owner
                .unwrap_project_key(
                    envelope=
                        portable_envelope,

                    recovery_key=
                        recovery_key,

                    expected_project_id=
                        project_id,

                    expected_owner_principal_id=
                        principal_id,
                )
            )


        except Exception as exc:

            record_recovery(
                (
                    "denied"
                    if isinstance(
                        exc,
                        PermissionError,
                    )
                    else
                    "failure"
                )
            )

            raise


        # The recovery credential and portable envelope have now
        # successfully recovered the project key.
        #
        # Audit BEFORE local key-custody mutation. If audit cannot
        # persist, no recovered key is installed on this device.

        record_recovery(
            "success"
        )


        key_custody = (
            key_custody
            or
            KeyCustodyOwner(
                security_audit=
                    self.security_audit
            )
        )


        security_context.require_trusted_device(
            key_custody
        )


        slot_preexisting = (
            key_custody
            .project_key_exists(
                principal_id,
                project_id,
            )
        )


        try:

            key_custody.store_project_key(
                principal_id,
                project_id,
                project_key,
            )


            persisted = (
                key_custody
                .retrieve_project_key(
                    principal_id,
                    project_id,
                )
            )


            if not hmac.compare_digest(
                persisted,
                project_key,
            ):

                raise RuntimeError(
                    "recovered_project_key_round_trip_mismatch"
                )


        except Exception:

            if not slot_preexisting:

                try:
                    key_custody.revoke_project_key(
                        principal_id,
                        project_id,
                    )

                except Exception as rollback_exc:
                    raise RuntimeError(
                        "recovered_project_key_rollback_failed"
                    ) from rollback_exc


            raise


        return {
            "action":
                "recover_encrypted_project_access",

            "project_id":
                project_id,

            "owner_principal_id":
                principal_id,

            "project_manifest_path":
                str(
                    project_manifest_path
                ),

            "recovery_fingerprint":
                recovery_payload.get(
                    "recovery_key_fingerprint"
                ),

            "project_key_recovered":
                True,

            "project_key_slot_present":
                True,

            "project_key_slot_preexisting":
                slot_preexisting,

            "project_files_modified":
                False,

            "recovery_material_modified":
                False,
        }


    def _record_encryption_activation_event(
        self,
        *,
        action: str,
        outcome: str,
        principal_id: str | None = None,
        project_id: str | None = None,
        classification: str | None = None,
    ) -> None:
        self.security_audit.record_event(
            event_type=
                "encryption_activation.project",

            action=
                action,

            outcome=
                outcome,

            resource_type=
                "project",

            classification=
                classification,

            principal_id=
                principal_id,

            project_id=
                project_id,
        )


    def prepare_legacy_encryption_activation(
        self,
        project_manifest_path,
        recovery_export_path,
        *,
        security_context=None,
        key_envelope_owner=None,
    ) -> dict:
        """
        Prepare explicit encryption activation.

        Recovery material is generated but the project is not
        encrypted or modified.

        The recovery package must live outside the LEAF storage
        root and is treated as a master secret.

        Security accountability is recorded only at this
        lifecycle boundary. Recovery-secret material never
        crosses the audit API.
        """

        import json

        from leaf_qt.encrypted_container import (
            SCHEMA as ENCRYPTED_CONTAINER_SCHEMA,
        )

        from leaf_qt.key_envelope import (
            PortableKeyEnvelopeOwner,
        )

        from leaf_qt.security_context import (
            SecurityContextOwner,
        )

        from leaf_qt.storage.project_manifest import (
            PROJECT_MANIFEST_FILENAME,
            ProjectManifest,
            ProjectManifestValidator,
        )


        audit_principal_id = None
        audit_project_id = None
        audit_classification = None

        prepared_recovery_path = None


        try:

            recovery_export_path = (
                self._validate_external_recovery_path(
                    recovery_export_path
                )
            )


            if recovery_export_path.exists():

                raise FileExistsError(
                    "recovery_material_export_already_exists:"
                    f"{recovery_export_path}"
                )


            project_manifest_path = (
                self.storage.resolve_ref(
                    project_manifest_path
                )
                .resolve()
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


            raw_payload = json.loads(
                project_manifest_path.read_text(
                    encoding="utf-8"
                )
            )


            if not isinstance(
                raw_payload,
                dict,
            ):

                raise ValueError(
                    "project_manifest_payload_invalid"
                )


            if (
                raw_payload.get(
                    "schema"
                )
                ==
                ENCRYPTED_CONTAINER_SCHEMA
            ):

                raise ValueError(
                    "project_already_encrypted"
                )


            manifest = (
                ProjectManifest.from_dict(
                    raw_payload
                )
            )


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
                    "legacy_project_manifest_invalid:"
                    +
                    ",".join(
                        validation.get(
                            "failures",
                            [],
                        )
                    )
                )


            # Only expose validated project metadata to the
            # audit boundary.

            audit_project_id = (
                manifest.project_id
            )

            audit_classification = (
                manifest.security_classification
            )


            security_context = (
                security_context
                or
                SecurityContextOwner(
                    security_audit=
                        self.security_audit
                )
            )


            principal_id = str(
                security_context.principal_id
            ).strip()


            audit_principal_id = (
                principal_id
            )


            if not str(
                manifest.owner_principal_id
                or
                ""
            ).strip():

                raise PermissionError(
                    "legacy_project_must_be_claimed_before_encryption_activation"
                )




            security_context.require_project_modify(
                manifest
            )


            key_envelope_owner = (
                key_envelope_owner
                or
                PortableKeyEnvelopeOwner()
            )


            recovery_key = (
                key_envelope_owner
                .generate_recovery_key()
            )


            if not isinstance(
                recovery_key,
                str,
            ):

                raise TypeError(
                    "recovery_key_must_be_string"
                )


            recovery_key = (
                recovery_key.strip()
            )


            if not recovery_key:

                raise ValueError(
                    "recovery_key_empty"
                )


            recovery_fingerprint = (
                key_envelope_owner
                .recovery_key_fingerprint(
                    recovery_key
                )
            )


            package_core = {
                "schema":
                    "LEAF_RECOVERY_MATERIAL_S1J11_V1",

                "purpose":
                    "LEAF_PROJECT_ENCRYPTION_RECOVERY",

                "project_id":
                    manifest.project_id,

                "owner_principal_id":
                    principal_id,

                "security_classification":
                    manifest.security_classification,

                "recovery_key":
                    recovery_key,

                "recovery_key_fingerprint":
                    recovery_fingerprint,

                "warning":
                    (
                        "SECRET LEAF RECOVERY MATERIAL. "
                        "Anyone possessing this file may be able "
                        "to recover the encrypted project key. "
                        "Keep it offline and separately from the "
                        "encrypted LEAF project."
                    ),
            }


            package = dict(
                package_core
            )


            package[
                "package_checksum_sha256"
            ] = (
                self._recovery_package_checksum(
                    package_core
                )
            )


            encoded = (
                json.dumps(
                    package,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                )
                +
                "\n"
            ).encode(
                "utf-8"
            )


            self._write_recovery_material_exclusive(
                recovery_export_path,
                encoded,
            )


            prepared_recovery_path = (
                recovery_export_path
            )


            # Verify the exact package and recovery secret through
            # the canonical loader before declaring preparation
            # successful.

            try:

                loaded_package, loaded_key = (
                    self._load_legacy_recovery_material(
                        recovery_export_path,

                        key_envelope_owner=
                            key_envelope_owner,
                    )
                )


                if loaded_package != package:

                    raise RuntimeError(
                        "recovery_material_post_write_payload_mismatch"
                    )


                if loaded_key != recovery_key:

                    raise RuntimeError(
                        "recovery_material_post_write_key_mismatch"
                    )


            except Exception:

                recovery_export_path.unlink(
                    missing_ok=True
                )

                prepared_recovery_path = None

                raise


        except Exception as exc:

            self._record_encryption_activation_event(
                action=
                    "prepare",

                outcome=
                    (
                        "denied"
                        if isinstance(
                            exc,
                            PermissionError,
                        )
                        else
                        "failure"
                    ),

                principal_id=
                    audit_principal_id,

                project_id=
                    audit_project_id,

                classification=
                    audit_classification,
            )

            raise


        # The master recovery credential now exists and has passed
        # its own exact read-back verification.
        #
        # Audit is the final commit boundary for PREPARATION.
        #
        # If audit persistence fails, remove the newly generated
        # master credential so LEAF cannot leave an unaudited
        # recovery package behind.

        try:

            self._record_encryption_activation_event(
                action=
                    "prepare",

                outcome=
                    "success",

                principal_id=
                    audit_principal_id,

                project_id=
                    audit_project_id,

                classification=
                    audit_classification,
            )


        except Exception:

            if (
                prepared_recovery_path
                is not None
            ):

                prepared_recovery_path.unlink(
                    missing_ok=True
                )

            raise


        return {
            "action":
                "prepare_legacy_encryption_activation",

            "project_id":
                manifest.project_id,

            "recovery_material_path":
                str(
                    recovery_export_path
                ),

            "recovery_fingerprint":
                recovery_fingerprint,

            "confirmation_code":
                self._legacy_recovery_confirmation_code(
                    manifest.project_id,
                    recovery_fingerprint,
                ),

            "project_modified":
                False,

            "migration_performed":
                False,

            "warning":
                package[
                    "warning"
                ],
        }


    def _load_legacy_recovery_material(
        self,
        recovery_export_path,
        *,
        key_envelope_owner=None,
    ) -> tuple[
        dict,
        str,
    ]:

        import hmac
        import json
        import os
        import stat

        from leaf_qt.key_envelope import (
            PortableKeyEnvelopeOwner,
        )


        path = (
            self._validate_external_recovery_path(
                recovery_export_path
            )
        )


        if not path.is_file():

            raise FileNotFoundError(
                "recovery_material_not_found:"
                f"{path}"
            )


        if os.name != "nt":

            mode = stat.S_IMODE(
                path.stat().st_mode
            )


            if mode & 0o077:

                raise PermissionError(
                    "recovery_material_permissions_not_restrictive"
                )


        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )


        if not isinstance(
            payload,
            dict,
        ):

            raise ValueError(
                "recovery_material_payload_invalid"
            )


        if (
            payload.get(
                "schema"
            )
            !=
            "LEAF_RECOVERY_MATERIAL_S1J11_V1"
        ):

            raise ValueError(
                "recovery_material_schema_invalid"
            )


        if (
            payload.get(
                "purpose"
            )
            !=
            "LEAF_PROJECT_ENCRYPTION_RECOVERY"
        ):

            raise ValueError(
                "recovery_material_purpose_invalid"
            )


        supplied_checksum = str(
            payload.get(
                "package_checksum_sha256",
                "",
            )
        ).strip()


        checksum_payload = dict(
            payload
        )


        checksum_payload.pop(
            "package_checksum_sha256",
            None,
        )


        expected_checksum = (
            self._recovery_package_checksum(
                checksum_payload
            )
        )


        if not hmac.compare_digest(
            supplied_checksum,
            expected_checksum,
        ):

            raise ValueError(
                "recovery_material_checksum_invalid"
            )


        recovery_key = str(
            payload.get(
                "recovery_key",
                "",
            )
        ).strip()


        if not recovery_key:

            raise ValueError(
                "recovery_material_key_missing"
            )


        key_envelope_owner = (
            key_envelope_owner
            or
            PortableKeyEnvelopeOwner()
        )


        expected_fingerprint = (
            key_envelope_owner
            .recovery_key_fingerprint(
                recovery_key
            )
        )


        supplied_fingerprint = str(
            payload.get(
                "recovery_key_fingerprint",
                "",
            )
        ).strip()


        if not hmac.compare_digest(
            supplied_fingerprint,
            expected_fingerprint,
        ):

            raise ValueError(
                "recovery_material_fingerprint_invalid"
            )


        return (
            payload,
            recovery_key,
        )


    def activate_legacy_project_encryption(
        self,
        project_manifest_path,
        recovery_export_path,
        confirmation_code,
        *,
        acknowledge_irrecoverable_loss: bool = False,
        security_context=None,
        key_custody=None,
        key_envelope_owner=None,
        encrypted_container_owner=None,
    ) -> dict:
        """
        Explicit user-confirmed activation wrapper around the
        canonical migration method.

        This boundary audits only the activation confirmation
        decision. Migration commitment remains owned by the
        canonical migration audit boundary.
        """

        import hmac
        import json

        from leaf_qt.encrypted_container import (
            SCHEMA as ENCRYPTED_CONTAINER_SCHEMA,
        )

        from leaf_qt.key_envelope import (
            PortableKeyEnvelopeOwner,
        )

        from leaf_qt.security_context import (
            SecurityContextOwner,
        )

        from leaf_qt.storage.project_manifest import (
            PROJECT_MANIFEST_FILENAME,
            ProjectManifest,
            ProjectManifestValidator,
        )


        audit_principal_id = None
        audit_project_id = None
        audit_classification = None


        if (
            acknowledge_irrecoverable_loss
            is not True
        ):

            self._record_encryption_activation_event(
                action="confirm",
                outcome="denied",
            )

            raise PermissionError(
                "encryption_activation_requires_"
                "explicit_loss_acknowledgement"
            )


        try:

            project_manifest_path = (
                self.storage.resolve_ref(
                    project_manifest_path
                )
                .resolve()
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


            raw_project = json.loads(
                project_manifest_path.read_text(
                    encoding="utf-8"
                )
            )


            if not isinstance(
                raw_project,
                dict,
            ):

                raise ValueError(
                    "project_manifest_payload_invalid"
                )


            if (
                raw_project.get(
                    "schema"
                )
                ==
                ENCRYPTED_CONTAINER_SCHEMA
            ):

                raise ValueError(
                    "project_already_encrypted"
                )


            manifest = (
                ProjectManifest.from_dict(
                    raw_project
                )
            )


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
                    "legacy_project_manifest_invalid:"
                    +
                    ",".join(
                        validation.get(
                            "failures",
                            [],
                        )
                    )
                )


            audit_project_id = (
                manifest.project_id
            )

            audit_classification = (
                manifest.security_classification
            )


            security_context = (
                security_context
                or
                SecurityContextOwner(
                    security_audit=
                        self.security_audit
                )
            )


            principal_id = str(
                security_context.principal_id
            ).strip()


            audit_principal_id = (
                principal_id
            )


            # Project authorization remains canonical.
            security_context.require_project_modify(
                manifest
            )


        except Exception as exc:

            self._record_encryption_activation_event(
                action="confirm",

                outcome=(
                    "denied"
                    if isinstance(
                        exc,
                        PermissionError,
                    )
                    else
                    "failure"
                ),

                principal_id=
                    audit_principal_id,

                project_id=
                    audit_project_id,

                classification=
                    audit_classification,
            )

            raise




        key_envelope_owner = (
            key_envelope_owner
            or
            PortableKeyEnvelopeOwner()
        )


        try:

            recovery_payload, recovery_key = (
                self._load_legacy_recovery_material(
                    recovery_export_path,

                    key_envelope_owner=
                        key_envelope_owner,
                )
            )


            if (
                recovery_payload.get(
                    "project_id"
                )
                !=
                manifest.project_id
            ):

                raise PermissionError(
                    "recovery_material_project_"
                    "binding_mismatch"
                )


            if (
                recovery_payload.get(
                    "owner_principal_id"
                )
                !=
                principal_id
            ):

                raise PermissionError(
                    "recovery_material_principal_"
                    "binding_mismatch"
                )


            if (
                recovery_payload.get(
                    "security_classification"
                )
                !=
                manifest.security_classification
            ):

                raise PermissionError(
                    "recovery_material_classification_"
                    "binding_mismatch"
                )


            expected_confirmation = (
                self._legacy_recovery_confirmation_code(
                    manifest.project_id,

                    recovery_payload[
                        "recovery_key_fingerprint"
                    ],
                )
            )


            if not hmac.compare_digest(
                str(
                    confirmation_code
                ).strip(),
                expected_confirmation,
            ):

                raise PermissionError(
                    "encryption_activation_"
                    "confirmation_code_invalid"
                )


        except Exception as exc:

            self._record_encryption_activation_event(
                action="confirm",

                outcome=(
                    "denied"
                    if isinstance(
                        exc,
                        PermissionError,
                    )
                    else
                    "failure"
                ),

                principal_id=
                    audit_principal_id,

                project_id=
                    audit_project_id,

                classification=
                    audit_classification,
            )

            raise


        # Final confirmation audit barrier.
        #
        # If audit persistence fails here, migration is never
        # entered.

        self._record_encryption_activation_event(
            action="confirm",
            outcome="success",

            principal_id=
                audit_principal_id,

            project_id=
                audit_project_id,

            classification=
                audit_classification,
        )


        result = (
            self.migrate_legacy_project_to_encrypted(
                project_manifest_path,
                recovery_key,

                security_context=
                    security_context,

                key_custody=
                    key_custody,

                key_envelope_owner=
                    key_envelope_owner,

                encrypted_container_owner=
                    encrypted_container_owner,
            )
        )


        return {
            **result,

            "activation":
                "EXPLICIT_USER_CONFIRMED",

            "recovery_material_path":
                str(
                    self._validate_external_recovery_path(
                        recovery_export_path
                    )
                ),

            "recovery_fingerprint":
                recovery_payload[
                    "recovery_key_fingerprint"
                ],

            "loss_acknowledgement":
                True,

            "automatic_activation":
                False,
        }



    def _record_encryption_migration_event(
        self,
        *,
        action: str,
        outcome: str,
        principal_id: str,
        project_id: str,
        classification: str | None = None,
    ) -> None:
        self.security_audit.record_event(
            event_type=
                "encryption_migration.project",

            action=
                action,

            outcome=
                outcome,

            resource_type=
                "project",

            classification=
                classification,

            principal_id=
                principal_id,

            project_id=
                project_id,
        )


    def migrate_legacy_project_to_encrypted(
        self,
        project_manifest_path,
        recovery_key,
        *,
        security_context=None,
        key_custody=None,
        key_envelope_owner=None,
        encrypted_container_owner=None,
    ) -> dict:

        import json
        import secrets
        import shutil

        from leaf_qt.encrypted_container import (
            DESIGN_MANIFEST_RESOURCE,
            ENGINEERING_STATE_RESOURCE,
            PROJECT_ROOT_RESOURCE,
            SCHEMA as ENCRYPTED_CONTAINER_SCHEMA,
            EncryptedContainerOwner,
        )

        from leaf_qt.key_custody import (
            KeyCustodyOwner,
        )

        from leaf_qt.key_envelope import (
            PortableKeyEnvelopeOwner,
        )

        from leaf_qt.security_context import (
            SecurityContextOwner,
        )

        from leaf_qt.storage.design_manifest import (
            DESIGN_MANIFEST_FILENAME,
            DesignManifest,
            DesignManifestValidator,
        )

        from leaf_qt.storage.project_manifest import (
            PROJECT_MANIFEST_FILENAME,
            ProjectManifest,
            ProjectManifestValidator,
        )

        from leaf_qt.storage.save_load_bridge import (
            ENGINEERING_STATE_FILENAME,
            SaveLoadRuntimeBridge,
        )


        journal_path = (
            self
            ._legacy_encryption_migration_journal_path()
        )


        if journal_path.exists():

            raise RuntimeError(
                "interrupted_encryption_migration_recovery_required"
            )


        security_context = (
            security_context
            or
            SecurityContextOwner(
                security_audit=
                    self.security_audit
            )
        )


        key_custody = (
            key_custody
            or
            KeyCustodyOwner(
                security_audit=
                    self.security_audit
            )
        )


        key_envelope_owner = (
            key_envelope_owner
            or
            PortableKeyEnvelopeOwner()
        )


        encrypted_container_owner = (
            encrypted_container_owner
            or
            EncryptedContainerOwner()
        )


        self.storage.ensure_roots()


        storage_root = Path(
            self.storage.root
        ).resolve()


        projects_root = (
            self.storage
            .canonical_path(
                "projects"
            )
            .resolve()
        )


        designs_root = (
            self.storage
            .canonical_path(
                "designs"
            )
            .resolve()
        )


        source_project_manifest = (
            self.storage.resolve_ref(
                project_manifest_path
            )
            .resolve()
        )


        if (
            source_project_manifest.name
            !=
            PROJECT_MANIFEST_FILENAME
        ):

            raise ValueError(
                "project_manifest_filename_invalid"
            )


        if not source_project_manifest.is_file():

            raise FileNotFoundError(
                "project_manifest_not_found:"
                f"{source_project_manifest}"
            )


        source_project_dir = (
            source_project_manifest
            .parent
            .resolve()
        )


        if (
            source_project_dir.parent
            !=
            projects_root
        ):

            raise ValueError(
                "legacy_project_outside_canonical_project_root"
            )


        original_project_bytes = (
            source_project_manifest
            .read_bytes()
        )


        raw_project_payload = json.loads(
            original_project_bytes.decode(
                "utf-8"
            )
        )


        if not isinstance(
            raw_project_payload,
            dict,
        ):

            raise ValueError(
                "legacy_project_manifest_payload_invalid"
            )


        if (
            raw_project_payload.get(
                "schema"
            )
            ==
            ENCRYPTED_CONTAINER_SCHEMA
        ):

            raise ValueError(
                "project_already_encrypted"
            )


        project_manifest = (
            ProjectManifest.from_dict(
                raw_project_payload
            )
        )


        project_validation = (
            ProjectManifestValidator()
            .validate(
                project_manifest
            )
        )


        if (
            project_validation.get(
                "passed"
            )
            is not True
        ):

            raise ValueError(
                "legacy_project_manifest_invalid:"
                +
                ",".join(
                    project_validation.get(
                        "failures",
                        [],
                    )
                )
            )


        principal_id = str(
            security_context.principal_id
        ).strip()


        if not str(
            project_manifest.owner_principal_id
            or
            ""
        ).strip():

            raise PermissionError(
                "legacy_project_must_be_claimed_before_encryption_migration"
            )




        security_context.require_project_modify(
            project_manifest
        )


        project_id = (
            project_manifest.project_id
        )


        classification = (
            project_manifest.security_classification
        )


        if source_project_dir.name == project_id:

            raise ValueError(
                "plaintext_source_already_uses_encrypted_project_identity_directory"
            )


        target_project_dir = (
            projects_root
            /
            project_id
        )


        target_project_manifest = (
            target_project_dir
            /
            PROJECT_MANIFEST_FILENAME
        )


        if target_project_dir.exists():

            raise FileExistsError(
                "encrypted_project_target_directory_already_exists:"
                f"{target_project_dir}"
            )


        if project_manifest.linked_reports:

            raise PermissionError(
                "legacy_migration_blocked_by_project_linked_internal_reports"
            )


        project_extra_files = [
            path
            for path
            in source_project_dir.rglob(
                "*"
            )
            if (
                path.is_file()
                and
                path.resolve()
                !=
                source_project_manifest
                and
                path.name
                !=
                ".DS_Store"
            )
        ]


        project_extra_dirs = [
            path
            for path
            in source_project_dir.rglob(
                "*"
            )
            if path.is_dir()
        ]


        if (
            project_extra_files
            or
            project_extra_dirs
        ):

            raise PermissionError(
                "legacy_migration_unknown_project_local_resources:"
                +
                ",".join(
                    str(
                        path.relative_to(
                            storage_root
                        )
                    )
                    for path
                    in (
                        project_extra_files
                        +
                        project_extra_dirs
                    )
                )
            )


        design_records = []

        seen_design_ids = set()
        seen_source_paths = set()


        for design_reference in (
            project_manifest.active_designs
        ):

            source_design_manifest = (
                self.storage.resolve_ref(
                    design_reference
                )
                .resolve()
            )


            if (
                source_design_manifest
                in
                seen_source_paths
            ):

                raise ValueError(
                    "legacy_migration_duplicate_design_reference"
                )


            seen_source_paths.add(
                source_design_manifest
            )


            if (
                source_design_manifest.name
                !=
                DESIGN_MANIFEST_FILENAME
            ):

                raise ValueError(
                    "legacy_design_manifest_filename_invalid:"
                    f"{source_design_manifest}"
                )


            if not source_design_manifest.is_file():

                raise FileNotFoundError(
                    "legacy_design_manifest_not_found:"
                    f"{source_design_manifest}"
                )


            source_design_dir = (
                source_design_manifest
                .parent
                .resolve()
            )


            if (
                source_design_dir.parent
                !=
                designs_root
            ):

                raise ValueError(
                    "legacy_design_outside_canonical_design_root:"
                    f"{source_design_manifest}"
                )


            original_design_bytes = (
                source_design_manifest
                .read_bytes()
            )


            raw_design_payload = json.loads(
                original_design_bytes.decode(
                    "utf-8"
                )
            )


            if not isinstance(
                raw_design_payload,
                dict,
            ):

                raise ValueError(
                    "legacy_design_manifest_payload_invalid"
                )


            if (
                raw_design_payload.get(
                    "schema"
                )
                ==
                ENCRYPTED_CONTAINER_SCHEMA
            ):

                raise ValueError(
                    "mixed_plaintext_encrypted_legacy_tree_denied"
                )


            design_manifest = (
                DesignManifest.from_dict(
                    raw_design_payload
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
                    "legacy_design_manifest_invalid:"
                    +
                    ",".join(
                        design_validation.get(
                            "failures",
                            [],
                        )
                    )
                )


            if (
                design_manifest.parent_project_id
                !=
                project_id
            ):

                raise ValueError(
                    "legacy_design_parent_project_id_mismatch:"
                    f"{design_manifest.design_id}"
                )


            design_id = (
                design_manifest.design_id
            )


            if design_id in seen_design_ids:

                raise ValueError(
                    "legacy_migration_duplicate_design_id:"
                    f"{design_id}"
                )


            seen_design_ids.add(
                design_id
            )


            if source_design_dir.name == design_id:

                raise ValueError(
                    "plaintext_source_already_uses_encrypted_design_identity_directory:"
                    f"{design_id}"
                )


            target_design_dir = (
                designs_root
                /
                design_id
            )


            target_design_manifest = (
                target_design_dir
                /
                DESIGN_MANIFEST_FILENAME
            )


            if target_design_dir.exists():

                raise FileExistsError(
                    "encrypted_design_target_directory_already_exists:"
                    f"{target_design_dir}"
                )


            if design_manifest.report_refs:

                raise PermissionError(
                    "legacy_migration_blocked_by_design_internal_reports:"
                    f"{design_id}"
                )


            if design_manifest.validation_refs:

                raise PermissionError(
                    "legacy_migration_blocked_by_design_validation_evidence:"
                    f"{design_id}"
                )


            state_payload = None
            source_state_path = None
            original_state_bytes = None


            state_reference = str(
                design_manifest.engineering_state_ref
                or
                ""
            ).strip()


            if state_reference:

                state_reference_path = Path(
                    state_reference
                )


                if (
                    state_reference_path.is_absolute()
                    or
                    state_reference_path.name
                    !=
                    state_reference
                ):

                    raise ValueError(
                        "legacy_engineering_state_reference_must_be_design_local:"
                        f"{design_id}"
                    )


                source_state_path = (
                    source_design_dir
                    /
                    state_reference_path
                )


                if not source_state_path.is_file():

                    raise FileNotFoundError(
                        "legacy_engineering_state_not_found:"
                        f"{source_state_path}"
                    )


                original_state_bytes = (
                    source_state_path
                    .read_bytes()
                )


                state_payload = json.loads(
                    original_state_bytes.decode(
                        "utf-8"
                    )
                )


                if not isinstance(
                    state_payload,
                    dict,
                ):

                    raise ValueError(
                        "legacy_engineering_state_payload_must_be_object:"
                        f"{design_id}"
                    )


            allowed_design_files = {
                source_design_manifest.resolve()
            }


            if source_state_path is not None:

                allowed_design_files.add(
                    source_state_path.resolve()
                )


            design_extra_files = [
                path
                for path
                in source_design_dir.rglob(
                    "*"
                )
                if (
                    path.is_file()
                    and
                    path.resolve()
                    not in
                    allowed_design_files
                    and
                    path.name
                    !=
                    ".DS_Store"
                )
            ]


            design_extra_dirs = [
                path
                for path
                in source_design_dir.rglob(
                    "*"
                )
                if path.is_dir()
            ]


            if (
                design_extra_files
                or
                design_extra_dirs
            ):

                raise PermissionError(
                    "legacy_migration_unknown_design_local_resources:"
                    f"{design_id}:"
                    +
                    ",".join(
                        str(
                            path.relative_to(
                                storage_root
                            )
                        )
                        for path
                        in (
                            design_extra_files
                            +
                            design_extra_dirs
                        )
                    )
                )


            design_records.append(
                {
                    "design_id":
                        design_id,

                    "manifest":
                        design_manifest,

                    "source_dir":
                        source_design_dir,

                    "source_manifest":
                        source_design_manifest,

                    "source_manifest_bytes":
                        original_design_bytes,

                    "source_state_path":
                        source_state_path,

                    "source_state_bytes":
                        original_state_bytes,

                    "state_payload":
                        state_payload,

                    "target_dir":
                        target_design_dir,

                    "target_manifest":
                        target_design_manifest,
                }
            )


        if key_custody.project_key_exists(
            principal_id,
            project_id,
        ):

            raise FileExistsError(
                "legacy_migration_project_key_slot_already_exists:"
                f"{project_id}"
            )


        migrated_project_manifest = (
            ProjectManifest.from_dict(
                project_manifest.snapshot()
            )
        )


        migrated_project_manifest.active_designs = [
            self.storage.portable_ref(
                record[
                    "target_manifest"
                ]
            )
            for record
            in design_records
        ]


        migrated_project_validation = (
            ProjectManifestValidator()
            .validate(
                migrated_project_manifest
            )
        )


        if (
            migrated_project_validation.get(
                "passed"
            )
            is not True
        ):

            raise ValueError(
                "migrated_project_manifest_invalid:"
                +
                ",".join(
                    migrated_project_validation.get(
                        "failures",
                        [],
                    )
                )
            )


        token = secrets.token_hex(
            8
        )


        staging_project_dir = (
            projects_root
            /
            (
                ".s1j10-migrating-"
                +
                project_id
                +
                "-"
                +
                token
            )
        )


        for record in design_records:

            record[
                "staging_dir"
            ] = (
                designs_root
                /
                (
                    ".s1j10-migrating-"
                    +
                    record[
                        "design_id"
                    ]
                    +
                    "-"
                    +
                    token
                )
            )


            record[
                "staging_manifest"
            ] = (
                record[
                    "staging_dir"
                ]
                /
                (
                    DESIGN_MANIFEST_FILENAME
                    +
                    ".s1j10-stage"
                )
            )


            if (
                record[
                    "state_payload"
                ]
                is not None
            ):

                record[
                    "staging_state"
                ] = (
                    record[
                        "staging_dir"
                    ]
                    /
                    (
                        ENGINEERING_STATE_FILENAME
                        +
                        ".s1j10-stage"
                    )
                )

            else:

                record[
                    "staging_state"
                ] = None


        staging_project_manifest = (
            staging_project_dir
            /
            (
                PROJECT_MANIFEST_FILENAME
                +
                ".s1j10-stage"
            )
        )


        source_project_backup = (
            source_project_manifest
            .with_name(
                PROJECT_MANIFEST_FILENAME
                +
                ".s1j10-plaintext-backup"
            )
        )


        if source_project_backup.exists():

            raise FileExistsError(
                "legacy_project_backup_already_exists:"
                f"{source_project_backup}"
            )


        for record in design_records:

            record[
                "source_backup"
            ] = (
                record[
                    "source_manifest"
                ]
                .with_name(
                    DESIGN_MANIFEST_FILENAME
                    +
                    ".s1j10-plaintext-backup"
                )
            )


            if record[
                "source_backup"
            ].exists():

                raise FileExistsError(
                    "legacy_design_backup_already_exists:"
                    f"{record['source_backup']}"
                )


        for path in (
            staging_project_dir,
            *[
                record[
                    "staging_dir"
                ]
                for record
                in design_records
            ],
        ):

            if path.exists():

                raise FileExistsError(
                    "legacy_migration_staging_path_already_exists:"
                    f"{path}"
                )


        def relative(
            path: Path,
        ) -> str:

            return str(
                path.resolve().relative_to(
                    storage_root
                )
            )


        journal = {
            "schema":
                "LEAF_S1J10_MIGRATION_TRANSACTION_V1",

            "phase":
                "PREPARED",

            "project_id":
                project_id,

            "principal_id":
                principal_id,

            "source_project_dir":
                relative(
                    source_project_dir
                ),

            "source_project_manifest":
                relative(
                    source_project_manifest
                ),

            "source_project_backup":
                relative(
                    source_project_backup
                ),

            "target_project_dir":
                relative(
                    target_project_dir
                ),

            "target_project_manifest":
                relative(
                    target_project_manifest
                ),

            "staging_project_dir":
                relative(
                    staging_project_dir
                ),

            "designs":
                [
                    {
                        "design_id":
                            record[
                                "design_id"
                            ],

                        "source_dir":
                            relative(
                                record[
                                    "source_dir"
                                ]
                            ),

                        "source_manifest":
                            relative(
                                record[
                                    "source_manifest"
                                ]
                            ),

                        "source_backup":
                            relative(
                                record[
                                    "source_backup"
                                ]
                            ),

                        "target_dir":
                            relative(
                                record[
                                    "target_dir"
                                ]
                            ),

                        "target_manifest":
                            relative(
                                record[
                                    "target_manifest"
                                ]
                            ),

                        "staging_dir":
                            relative(
                                record[
                                    "staging_dir"
                                ]
                            ),
                    }
                    for record
                    in design_records
                ],
        }


        self._write_legacy_encryption_migration_journal(
            journal
        )


        try:

            key_custody.create_project_key(
                principal_id,
                project_id,
            )


            project_key = (
                key_custody
                .retrieve_project_key(
                    principal_id,
                    project_id,
                )
            )


            if len(
                project_key
            ) != 32:

                raise RuntimeError(
                    "legacy_migration_project_key_not_256_bits"
                )


            portable_key_envelope = (
                key_envelope_owner.wrap_project_key(
                    project_id=project_id,
                    owner_principal_id=principal_id,
                    project_key=project_key,
                    recovery_key=recovery_key,
                )
            )


            if not isinstance(
                portable_key_envelope,
                dict,
            ):

                raise RuntimeError(
                    "portable_project_key_envelope_not_dict"
                )


            project_container = (
                encrypted_container_owner.seal(
                    payload=
                        migrated_project_manifest.snapshot(),

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


            staging_project_dir.mkdir(
                parents=True,
                exist_ok=False,
            )


            SaveLoadRuntimeBridge._write_json(
                staging_project_manifest,
                project_container,
            )


            for record in design_records:

                record[
                    "staging_dir"
                ].mkdir(
                    parents=True,
                    exist_ok=False,
                )


                design_container = (
                    encrypted_container_owner.seal(
                        payload=
                            record[
                                "manifest"
                            ].snapshot(),

                        project_id=
                            project_id,

                        owner_principal_id=
                            principal_id,

                        security_classification=
                            classification,

                        resource_type=
                            DESIGN_MANIFEST_RESOURCE,

                        resource_id=
                            record[
                                "design_id"
                            ],

                        project_key=
                            project_key,

                        portable_key_envelope=
                            None,
                    )
                )


                SaveLoadRuntimeBridge._write_json(
                    record[
                        "staging_manifest"
                    ],
                    design_container,
                )


                if (
                    record[
                        "state_payload"
                    ]
                    is not None
                ):

                    state_container = (
                        encrypted_container_owner.seal(
                            payload=
                                record[
                                    "state_payload"
                                ],

                            project_id=
                                project_id,

                            owner_principal_id=
                                principal_id,

                            security_classification=
                                classification,

                            resource_type=
                                ENGINEERING_STATE_RESOURCE,

                            resource_id=
                                record[
                                    "design_id"
                                ],

                            project_key=
                                project_key,

                            portable_key_envelope=
                                None,
                        )
                    )


                    SaveLoadRuntimeBridge._write_json(
                        record[
                            "staging_state"
                        ],
                        state_container,
                    )


            journal[
                "phase"
            ] = "STAGED"


            self._write_legacy_encryption_migration_journal(
                journal
            )


            staged_project_payload = (
                encrypted_container_owner.open(
                    container=
                        json.loads(
                            staging_project_manifest
                            .read_text(
                                encoding="utf-8"
                            )
                        ),

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


            if (
                staged_project_payload
                !=
                migrated_project_manifest.snapshot()
            ):

                raise RuntimeError(
                    "staged_project_round_trip_not_exact"
                )


            for record in design_records:

                staged_design_payload = (
                    encrypted_container_owner.open(
                        container=
                            json.loads(
                                record[
                                    "staging_manifest"
                                ]
                                .read_text(
                                    encoding="utf-8"
                                )
                            ),

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
                            record[
                                "design_id"
                            ],
                    )
                )


                if (
                    staged_design_payload
                    !=
                    record[
                        "manifest"
                    ].snapshot()
                ):

                    raise RuntimeError(
                        "staged_design_round_trip_not_exact:"
                        f"{record['design_id']}"
                    )


                if (
                    record[
                        "state_payload"
                    ]
                    is not None
                ):

                    staged_state_payload = (
                        encrypted_container_owner.open(
                            container=
                                json.loads(
                                    record[
                                        "staging_state"
                                    ]
                                    .read_text(
                                        encoding="utf-8"
                                    )
                                ),

                            project_key=
                                project_key,

                            expected_project_id=
                                project_id,

                            expected_owner_principal_id=
                                principal_id,

                            expected_security_classification=
                                classification,

                            expected_resource_type=
                                ENGINEERING_STATE_RESOURCE,

                            expected_resource_id=
                                record[
                                    "design_id"
                                ],
                        )
                    )


                    if (
                        staged_state_payload
                        !=
                        record[
                            "state_payload"
                        ]
                    ):

                        raise RuntimeError(
                            "staged_engineering_state_round_trip_not_exact:"
                            f"{record['design_id']}"
                        )


            for record in design_records:

                record[
                    "source_manifest"
                ].rename(
                    record[
                        "source_backup"
                    ]
                )


            source_project_manifest.rename(
                source_project_backup
            )


            journal[
                "phase"
            ] = "SOURCE_HIDDEN"


            self._write_legacy_encryption_migration_journal(
                journal
            )


            staging_project_dir.rename(
                target_project_dir
            )


            for record in design_records:

                record[
                    "staging_dir"
                ].rename(
                    record[
                        "target_dir"
                    ]
                )


            journal[
                "phase"
            ] = "TARGET_DIRECTORIES"


            self._write_legacy_encryption_migration_journal(
                journal
            )


            (
                target_project_dir
                /
                (
                    PROJECT_MANIFEST_FILENAME
                    +
                    ".s1j10-stage"
                )
            ).rename(
                target_project_manifest
            )


            for record in design_records:

                staged_design_in_target = (
                    record[
                        "target_dir"
                    ]
                    /
                    (
                        DESIGN_MANIFEST_FILENAME
                        +
                        ".s1j10-stage"
                    )
                )


                staged_design_in_target.rename(
                    record[
                        "target_manifest"
                    ]
                )


                if (
                    record[
                        "state_payload"
                    ]
                    is not None
                ):

                    staged_state_in_target = (
                        record[
                            "target_dir"
                        ]
                        /
                        (
                            ENGINEERING_STATE_FILENAME
                            +
                            ".s1j10-stage"
                        )
                    )


                    staged_state_in_target.rename(
                        record[
                            "target_dir"
                        ]
                        /
                        ENGINEERING_STATE_FILENAME
                    )


            journal[
                "phase"
            ] = "TARGET_VISIBLE"


            self._write_legacy_encryption_migration_journal(
                journal
            )


            final_project_container = json.loads(
                target_project_manifest
                .read_text(
                    encoding="utf-8"
                )
            )


            final_project_payload = (
                encrypted_container_owner.open(
                    container=
                        final_project_container,

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


            if (
                final_project_payload
                !=
                migrated_project_manifest.snapshot()
            ):

                raise RuntimeError(
                    "final_project_round_trip_not_exact"
                )


            if (
                target_project_dir.name
                !=
                project_id
            ):

                raise RuntimeError(
                    "final_project_directory_not_opaque_project_id"
                )


            if (
                project_manifest.project_name
                in
                target_project_manifest.read_text(
                    encoding="utf-8"
                )
            ):

                raise RuntimeError(
                    "final_project_name_visible_in_plaintext"
                )


            for record in design_records:

                final_design_container = json.loads(
                    record[
                        "target_manifest"
                    ]
                    .read_text(
                        encoding="utf-8"
                    )
                )


                final_design_payload = (
                    encrypted_container_owner.open(
                        container=
                            final_design_container,

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
                            record[
                                "design_id"
                            ],
                    )
                )


                if (
                    final_design_payload
                    !=
                    record[
                        "manifest"
                    ].snapshot()
                ):

                    raise RuntimeError(
                        "final_design_round_trip_not_exact:"
                        f"{record['design_id']}"
                    )


                if (
                    record[
                        "target_dir"
                    ].name
                    !=
                    record[
                        "design_id"
                    ]
                ):

                    raise RuntimeError(
                        "final_design_directory_not_opaque_design_id:"
                        f"{record['design_id']}"
                    )


                if (
                    record[
                        "manifest"
                    ].design_name
                    in
                    record[
                        "target_manifest"
                    ].read_text(
                        encoding="utf-8"
                    )
                ):

                    raise RuntimeError(
                        "final_design_name_visible_in_plaintext:"
                        f"{record['design_id']}"
                    )


                if (
                    record[
                        "state_payload"
                    ]
                    is not None
                ):

                    final_state_path = (
                        record[
                            "target_dir"
                        ]
                        /
                        ENGINEERING_STATE_FILENAME
                    )


                    final_state_payload = (
                        encrypted_container_owner.open(
                            container=
                                json.loads(
                                    final_state_path
                                    .read_text(
                                        encoding="utf-8"
                                    )
                                ),

                            project_key=
                                project_key,

                            expected_project_id=
                                project_id,

                            expected_owner_principal_id=
                                principal_id,

                            expected_security_classification=
                                classification,

                            expected_resource_type=
                                ENGINEERING_STATE_RESOURCE,

                            expected_resource_id=
                                record[
                                    "design_id"
                                ],
                        )
                    )


                    if (
                        final_state_payload
                        !=
                        record[
                            "state_payload"
                        ]
                    ):

                        raise RuntimeError(
                            "final_engineering_state_round_trip_not_exact:"
                            f"{record['design_id']}"
                        )


            # Security-accountability commit barrier.
            #
            # This event means:
            # VALIDATED_AND_AUDITED_READY_FOR_COMMIT.
            #
            # It deliberately does not claim that plaintext has
            # already been retired.

            self._record_encryption_migration_event(
                action=
                    "commit_ready",

                outcome=
                    "success",

                principal_id=
                    principal_id,

                project_id=
                    project_id,

                classification=
                    classification,
            )


            journal[
                "phase"
            ] = "COMMIT_READY"


            self._write_legacy_encryption_migration_journal(
                journal
            )


            for record in design_records:

                if record[
                    "source_dir"
                ].exists():

                    shutil.rmtree(
                        record[
                            "source_dir"
                        ]
                    )


            if source_project_dir.exists():

                shutil.rmtree(
                    source_project_dir
                )


            if journal_path.exists():

                journal_path.unlink()


            return {
                "action":
                    "migrate_legacy_project_to_encrypted",

                "project_id":
                    project_id,

                "owner_principal_id":
                    principal_id,

                "security_classification":
                    classification,

                "project_manifest_path":
                    str(
                        target_project_manifest
                    ),

                "design_manifest_paths":
                    {
                        record[
                            "design_id"
                        ]:
                            str(
                                record[
                                    "target_manifest"
                                ]
                            )
                        for record
                        in design_records
                    },

                "design_count":
                    len(
                        design_records
                    ),

                "project_key_slot_created":
                    True,

                "portable_recovery_envelope_created":
                    True,

                "source_plaintext_retired":
                    True,

                "migration_complete":
                    True,
            }


        except Exception as migration_error:

            try:

                recovery = (
                    self
                    .recover_interrupted_encryption_migration(
                        key_custody=
                            key_custody
                    )
                )


            except Exception as recovery_error:

                raise RuntimeError(
                    "legacy_encryption_migration_failed_and_recovery_failed:"
                    f"migration={migration_error!r}:"
                    f"recovery={recovery_error!r}"
                ) from migration_error


            if (
                recovery.get(
                    "mode"
                )
                ==
                "COMPLETE_FORWARD"
            ):

                return {
                    "action":
                        "migrate_legacy_project_to_encrypted",

                    "project_id":
                        project_id,

                    "owner_principal_id":
                        principal_id,

                    "security_classification":
                        classification,

                    "project_manifest_path":
                        str(
                            target_project_manifest
                        ),

                    "design_manifest_paths":
                        {
                            record[
                                "design_id"
                            ]:
                                str(
                                    record[
                                        "target_manifest"
                                ]
                            )
                            for record
                            in design_records
                        },

                    "design_count":
                        len(
                            design_records
                        ),

                    "project_key_slot_created":
                        True,

                    "portable_recovery_envelope_created":
                        True,

                    "source_plaintext_retired":
                        True,

                    "migration_complete":
                        True,

                    "completed_by_interruption_recovery":
                        True,
                }


            raise

    @staticmethod
    def claim_legacy_project(
        project_manifest_path,
        security_context,
    ):
        """
        Explicitly bind a legacy unowned project to the
        current LEAF principal.

        Existing owned projects cannot be claimed or reassigned
        through this migration path.
        """
        import json
        import os
        from pathlib import Path

        from leaf_qt.storage.project_manifest import (
            PROJECT_MANIFEST_FILENAME,
            ProjectManifest,
            ProjectManifestValidator,
        )

        path = Path(
            project_manifest_path
        )

        if path.name != PROJECT_MANIFEST_FILENAME:
            raise ValueError(
                "project_manifest_filename_invalid"
            )

        if not path.is_file():
            raise FileNotFoundError(
                "project_manifest_not_found:"
                f"{path}"
            )

        original_bytes = path.read_bytes()

        manifest = ProjectManifest.from_dict(
            json.loads(
                original_bytes.decode(
                    "utf-8"
                )
            )
        )

        validation = (
            ProjectManifestValidator()
            .validate(
                manifest
            )
        )

        if validation.get("passed") is not True:
            raise ValueError(
                "legacy_project_manifest_invalid:"
                +
                ",".join(
                    validation.get(
                        "failures",
                        [],
                    )
                )
            )

        security_context.require_legacy_project_claim(
            manifest
        )

        preserved_state = (
            manifest.project_id,
            manifest.project_name,
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
        )

        security_context.bind_new_project(
            manifest
        )

        manifest.touch()

        validation = (
            ProjectManifestValidator()
            .validate(
                manifest
            )
        )

        if validation.get("passed") is not True:
            raise ValueError(
                "claimed_project_manifest_invalid:"
                +
                ",".join(
                    validation.get(
                        "failures",
                        [],
                    )
                )
            )

        temporary = path.with_name(
            path.name
            + f".tmp-{os.getpid()}"
        )

        try:
            temporary.write_text(
                json.dumps(
                    manifest.snapshot(),
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            temporary.replace(
                path
            )

            persisted = (
                ProjectManifest.from_dict(
                    json.loads(
                        path.read_text(
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

            if (
                persisted_validation.get(
                    "passed"
                )
                is not True
            ):
                raise RuntimeError(
                    "claimed_project_persisted_manifest_invalid"
                )

            persisted_state = (
                persisted.project_id,
                persisted.project_name,
                persisted.created_at,
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
            )

            if persisted_state != preserved_state:
                raise RuntimeError(
                    "legacy_project_claim_changed_engineering_project_state"
                )

            if (
                persisted.owner_principal_id
                !=
                security_context.principal_id
            ):
                raise RuntimeError(
                    "legacy_project_claim_owner_not_persisted"
                )

        except Exception:
            path.write_bytes(
                original_bytes
            )

            if temporary.exists():
                temporary.unlink()

            raise

        return {
            "action":
                "claim_legacy_project",
            "project_id":
                manifest.project_id,
            "owner_principal_id":
                manifest.owner_principal_id,
            "security_classification":
                manifest.security_classification,
            "legacy_claim_complete":
                True,
        }


storage_validation_repair_owner = StorageValidationRepairOwner()
