from __future__ import annotations

import base64
import hmac
import secrets
from typing import TYPE_CHECKING, Any

import keyring

from leaf_qt.platform_capabilities import (
    PlatformCapabilityOwner,
)


if TYPE_CHECKING:
    from leaf_qt.security_audit import SecurityAuditOwner


SCHEMA = "LEAF_KEY_CUSTODY_S1F_V1"

KEY_BYTES = 32
PROJECT_KEY_SERVICE_NAME = "LEAF.ProjectKey.v1"
DEVICE_TRUST_SERVICE_NAME = "LEAF.DeviceTrust.v1"
DEVICE_TRUST_BYTES = 32
INVALIDATED_SECRET_SLOT = "!LEAF_SECRET_SLOT_INVALIDATED_V1!"


APPROVED_BACKEND_MODULES = {
    "macos": frozenset({
        "keyring.backends.macOS",
    }),

    "windows": frozenset({
        "keyring.backends.Windows",
    }),

    "linux": frozenset({
        "keyring.backends.SecretService",
        "keyring.backends.kwallet",
    }),
}


class KeyCustodyOwner:
    """
    Canonical platform-neutral cryptographic-key custody.

    Raw key material exists only transiently in process
    memory and in an approved operating-system protected
    credential store.

    This class does not persist engineering projects and
    does not implement project encryption.
    """

    def __init__(
        self,
        platform_owner: PlatformCapabilityOwner | None = None,
        security_audit: SecurityAuditOwner | None = None,
    ) -> None:
        self.platform_owner = (
            platform_owner
            or
            PlatformCapabilityOwner()
        )

        self.capabilities = (
            self.platform_owner.detect()
        )

        if not self.platform_owner.supported:
            raise RuntimeError(
                "unsupported_platform_for_secure_key_custody:"
                f"{self.capabilities.os_family}"
            )

        if not self.capabilities.secret_store_available:
            raise RuntimeError(
                "secure_secret_store_interface_unavailable"
            )

        self._backend = keyring.get_keyring()

        self._validate_backend()

        if security_audit is None:
            from leaf_qt.security_audit import SecurityAuditOwner
            security_audit = SecurityAuditOwner()

        self.security_audit = security_audit

    @classmethod
    def approved_backend_contract(
        cls,
    ) -> dict[str, tuple[str, ...]]:
        return {
            family: tuple(
                sorted(modules)
            )
            for family, modules
            in APPROVED_BACKEND_MODULES.items()
        }

    @property
    def backend_module(self) -> str:
        return type(
            self._backend
        ).__module__

    @property
    def backend_identity(self) -> str:
        backend_type = type(
            self._backend
        )

        return (
            f"{backend_type.__module__}."
            f"{backend_type.__name__}"
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "os_family":
                self.capabilities.os_family,
            "backend_identity":
                self.backend_identity,
            "backend_approved":
                True,
            "key_bytes":
                KEY_BYTES,
            "raw_key_in_project_storage":
                False,
            "raw_key_in_gui":
                False,
            "project_encryption_implemented":
                False,
        }


    def _record_project_key_event(
        self,
        *,
        action: str,
        outcome: str,
        principal_id: str,
        project_id: str,
    ) -> None:
        self.security_audit.record_event(
            event_type="key_custody.project_key",
            action=action,
            outcome=outcome,
            resource_type="project_key",
            principal_id=principal_id,
            project_id=project_id,
        )

    def _record_device_trust_event(
        self, action: str, outcome: str, principal_id: str,
    ) -> None:
        self.security_audit.record_event(
            event_type="key_custody.device_trust",
            action=action, outcome=outcome,
            resource_type="device_trust", principal_id=principal_id,
        )

    def _clear_failed_secret_slot(
        self, service_name: str, account: str, failure_label: str,
    ) -> str:
        try:
            self._backend.delete_password(service_name, account)
            deleted = True
        except Exception:
            deleted = False

        try:
            remaining = self._backend.get_password(service_name, account)
        except Exception as exc:
            raise RuntimeError(
                f"{failure_label}:secret_slot_state_unverifiable"
            ) from exc

        if remaining is None:
            return "deleted"

        try:
            self._backend.set_password(
                service_name, account, INVALIDATED_SECRET_SLOT
            )
            neutralized = self._backend.get_password(
                service_name, account
            )
        except Exception as exc:
            raise RuntimeError(
                f"{failure_label}:secret_slot_neutralization_failed"
            ) from exc

        if (
            neutralized is None
            or not hmac.compare_digest(
                neutralized,
                INVALIDATED_SECRET_SLOT,
            )
        ):
            raise RuntimeError(
                f"{failure_label}:secret_slot_neutralization_unverified"
            )

        return (
            "neutralized"
            if deleted
            else "neutralized_after_delete_failure"
        )


    def _store_project_key_material(
        self,
        principal_id: str,
        project_id: str,
        key_material: bytes,
    ) -> bool:
        try:
            key_material = bytes(key_material)
        except Exception as exc:
            raise TypeError(
                "project_key_material_must_be_bytes"
            ) from exc

        if len(key_material) != KEY_BYTES:
            raise ValueError(
                "project_key_material_length_invalid"
            )

        account = self._project_account(
            principal_id,
            project_id,
        )

        encoded_secret = base64.urlsafe_b64encode(
            key_material
        ).decode("ascii")

        existing = self._backend.get_password(
            PROJECT_KEY_SERVICE_NAME,
            account,
        )

        if (
            existing is not None
            and hmac.compare_digest(
                existing,
                INVALIDATED_SECRET_SLOT,
            )
        ):
            existing = None

        if existing is not None:
            if hmac.compare_digest(
                existing,
                encoded_secret,
            ):
                return False

            raise PermissionError(
                "project_key_slot_conflict"
            )

        try:
            self._backend.set_password(
                PROJECT_KEY_SERVICE_NAME,
                account,
                encoded_secret,
            )

            persisted = self._backend.get_password(
                PROJECT_KEY_SERVICE_NAME,
                account,
            )

            if (
                persisted is None
                or not hmac.compare_digest(
                    persisted,
                    encoded_secret,
                )
            ):
                raise RuntimeError(
                    "project_key_slot_round_trip_verification_failed"
                )

        except Exception:
            self._clear_failed_secret_slot(
                PROJECT_KEY_SERVICE_NAME,
                account,
                "project_key_write_rollback_failed",
            )
            raise

        return True


    def _rollback_new_project_key_slot(
        self,
        principal_id: str,
        project_id: str,
    ) -> None:
        account = self._project_account(
            principal_id,
            project_id,
        )

        self._clear_failed_secret_slot(
            PROJECT_KEY_SERVICE_NAME,
            account,
            "project_key_audit_rollback_failed",
        )


    def create_project_key(
        self,
        principal_id: str,
        project_id: str,
    ) -> None:
        principal_id = self._validate_principal(
            principal_id
        )
        project_id = self._validate_project_id(
            project_id
        )

        account = self._project_account(
            principal_id,
            project_id,
        )

        try:
            existing = self._backend.get_password(
                PROJECT_KEY_SERVICE_NAME,
                account,
            )
        except Exception:
            self._record_project_key_event(
                action="create",
                outcome="failure",
                principal_id=principal_id,
                project_id=project_id,
            )
            raise

        if existing is not None:
            self._record_project_key_event(
                action="create",
                outcome="failure",
                principal_id=principal_id,
                project_id=project_id,
            )
            raise FileExistsError(
                "project_key_slot_already_exists"
            )

        try:
            created = self._store_project_key_material(
                principal_id,
                project_id,
                secrets.token_bytes(KEY_BYTES),
            )
        except Exception:
            self._record_project_key_event(
                action="create",
                outcome="failure",
                principal_id=principal_id,
                project_id=project_id,
            )
            raise

        try:
            self._record_project_key_event(
                action="create",
                outcome="success",
                principal_id=principal_id,
                project_id=project_id,
            )
        except Exception:
            if created:
                self._rollback_new_project_key_slot(
                    principal_id,
                    project_id,
                )
            raise


    def store_project_key(
        self,
        principal_id: str,
        project_id: str,
        key_material: bytes,
    ) -> None:
        principal_id = self._validate_principal(
            principal_id
        )
        project_id = self._validate_project_id(
            project_id
        )

        try:
            created = self._store_project_key_material(
                principal_id,
                project_id,
                key_material,
            )
        except Exception:
            self._record_project_key_event(
                action="store",
                outcome="failure",
                principal_id=principal_id,
                project_id=project_id,
            )
            raise

        try:
            self._record_project_key_event(
                action="store",
                outcome="success",
                principal_id=principal_id,
                project_id=project_id,
            )
        except Exception:
            if created:
                self._rollback_new_project_key_slot(
                    principal_id,
                    project_id,
                )
            raise


    def retrieve_project_key(
        self,
        principal_id: str,
        project_id: str,
    ) -> bytes:
        principal_id = self._validate_principal(
            principal_id
        )
        project_id = self._validate_project_id(
            project_id
        )

        try:
            encoded_secret = self._backend.get_password(
                PROJECT_KEY_SERVICE_NAME,
                self._project_account(
                    principal_id,
                    project_id,
                ),
            )

            if (
                encoded_secret is None
                or hmac.compare_digest(
                    encoded_secret,
                    INVALIDATED_SECRET_SLOT,
                )
            ):
                raise KeyError(
                    "project_key_slot_not_found"
                )

            try:
                key_material = base64.urlsafe_b64decode(
                    encoded_secret.encode("ascii")
                )
            except Exception as exc:
                raise RuntimeError(
                    "stored_project_key_material_invalid"
                ) from exc

            if len(key_material) != KEY_BYTES:
                raise RuntimeError(
                    "stored_project_key_material_length_invalid"
                )

        except Exception:
            self._record_project_key_event(
                action="retrieve",
                outcome="failure",
                principal_id=principal_id,
                project_id=project_id,
            )
            raise

        self._record_project_key_event(
            action="retrieve",
            outcome="success",
            principal_id=principal_id,
            project_id=project_id,
        )

        return key_material


    def project_key_exists(
        self,
        principal_id: str,
        project_id: str,
    ) -> bool:
        principal_id = self._validate_principal(
            principal_id
        )
        project_id = self._validate_project_id(
            project_id
        )

        encoded_secret = self._backend.get_password(
            PROJECT_KEY_SERVICE_NAME,
            self._project_account(
                principal_id,
                project_id,
            ),
        )

        return (
            encoded_secret is not None
            and not hmac.compare_digest(
                encoded_secret,
                INVALIDATED_SECRET_SLOT,
            )
        )


    def revoke_project_key(
        self,
        principal_id: str,
        project_id: str,
    ) -> bool:
        principal_id = self._validate_principal(
            principal_id
        )
        project_id = self._validate_project_id(
            project_id
        )

        account = self._project_account(
            principal_id,
            project_id,
        )

        encoded_secret = self._backend.get_password(
            PROJECT_KEY_SERVICE_NAME,
            account,
        )

        if (
            encoded_secret is None
            or hmac.compare_digest(
                encoded_secret,
                INVALIDATED_SECRET_SLOT,
            )
        ):
            return False

        self._clear_failed_secret_slot(
            PROJECT_KEY_SERVICE_NAME,
            account,
            "project_key_revoke_failed",
        )

        self._record_project_key_event(
            action="revoke",
            outcome="success",
            principal_id=principal_id,
            project_id=project_id,
        )

        return True


    @staticmethod
    def _validate_device_trust_secret(encoded_secret: str) -> None:
        try:
            secret = base64.b64decode(
                encoded_secret.encode("ascii"), altchars=b"-_", validate=True
            )
        except Exception as exc:
            raise RuntimeError("device_trust_secret_invalid") from exc
        if len(secret) != DEVICE_TRUST_BYTES:
            raise RuntimeError("device_trust_secret_length_invalid")

    def enroll_device_trust(self, principal_id: str) -> bool:
        principal_id = self._validate_principal(principal_id)
        write_attempted = False

        try:
            existing = self._backend.get_password(
                DEVICE_TRUST_SERVICE_NAME,
                principal_id,
            )

            if (
                existing is not None
                and not hmac.compare_digest(
                    existing,
                    INVALIDATED_SECRET_SLOT,
                )
            ):
                self._validate_device_trust_secret(
                    existing
                )
                return False

            encoded = base64.urlsafe_b64encode(
                secrets.token_bytes(
                    DEVICE_TRUST_BYTES
                )
            ).decode("ascii")

            write_attempted = True

            self._backend.set_password(
                DEVICE_TRUST_SERVICE_NAME,
                principal_id,
                encoded,
            )

            persisted = self._backend.get_password(
                DEVICE_TRUST_SERVICE_NAME,
                principal_id,
            )

            if (
                persisted is None
                or not hmac.compare_digest(
                    persisted,
                    encoded,
                )
            ):
                raise RuntimeError(
                    "device_trust_slot_round_trip_verification_failed"
                )

        except Exception as write_exc:

            cleanup_exc = None

            if write_attempted:

                try:
                    self._clear_failed_secret_slot(
                        DEVICE_TRUST_SERVICE_NAME,
                        principal_id,
                        "device_trust_write_rollback_failed",
                    )

                except Exception as exc:
                    cleanup_exc = exc

            self._record_device_trust_event(
                "enroll",
                "failure",
                principal_id,
            )

            if cleanup_exc is not None:
                raise cleanup_exc from write_exc

            raise

        try:
            self._record_device_trust_event(
                "enroll",
                "success",
                principal_id,
            )

        except Exception:
            self._clear_failed_secret_slot(
                DEVICE_TRUST_SERVICE_NAME,
                principal_id,
                "device_trust_audit_rollback_failed",
            )
            raise

        return True

    def device_trust_exists(self, principal_id: str) -> bool:
        principal_id = self._validate_principal(
            principal_id
        )

        encoded = self._backend.get_password(
            DEVICE_TRUST_SERVICE_NAME,
            principal_id,
        )

        if (
            encoded is None
            or hmac.compare_digest(
                encoded,
                INVALIDATED_SECRET_SLOT,
            )
        ):
            return False

        self._validate_device_trust_secret(
            encoded
        )

        return True

    @staticmethod
    def _validate_project_id(
        project_id: str,
    ) -> str:

        project_id = str(
            project_id
            or ""
        ).strip()


        if not project_id.startswith(
            "project_"
        ):
            raise ValueError(
                "project_id_invalid"
            )


        return project_id


    @staticmethod
    def _project_account(
        principal_id: str,
        project_id: str,
    ) -> str:

        return (
            f"{principal_id}:"
            f"{project_id}"
        )


    def _validate_backend(self) -> None:
        family = (
            self.capabilities.os_family
        )

        allowed_modules = (
            APPROVED_BACKEND_MODULES.get(
                family,
                frozenset(),
            )
        )

        if (
            self.backend_module
            not in
            allowed_modules
        ):
            raise RuntimeError(
                "unapproved_keyring_backend:"
                f"{self.backend_identity}"
            )

        try:
            priority = float(
                self._backend.priority
            )
        except Exception as exc:
            raise RuntimeError(
                "native_keyring_backend_unavailable:"
                f"{self.backend_identity}"
            ) from exc

        if priority <= 0:
            raise RuntimeError(
                "native_keyring_backend_not_recommended:"
                f"{self.backend_identity}"
            )

    @staticmethod
    def _validate_principal(
        principal_id: str,
    ) -> str:
        principal_id = str(
            principal_id
            or ""
        ).strip()

        if not principal_id.startswith(
            "principal_"
        ):
            raise ValueError(
                "principal_id_invalid"
            )

        return principal_id


